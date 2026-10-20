"""Opt-in one-shot tracks, bounded common periods and minimum-depth pitch LFO."""
import copy,csv,json,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nds_music import trace_sequence
from nds_track_merge import assess_groups,convert_merged_song,expand_actions
from nds_lfo import compare_config,map_pitch_lfo
from validate_nds_experiment import check_reference
import test_nds_music as fixtures


def program(long_intro=False,long_loop=False):
    intro=b'\x82\x38' if long_intro else b'\x0C'
    root=bytearray(b'\xFE\x07\x00\x93\x01'+bytes(3)+b'\x93\x02'+bytes(3)+b'\xE1\x78\x00\x81\x02')
    root+=b'\x3E\x5A'+intro;loop=len(root)
    root+=b'\x3E\x64'+(intro if long_loop else b'\x18')+b'\x94'+loop.to_bytes(3,'little')
    second=len(root);root+=b'\x81\x02\x40\x5A'+intro;loop=len(root)
    root+=b'\x40\x64'+(b'\x81\x1C' if long_loop else b'\x0C')+b'\x94'+loop.to_bytes(3,'little')
    finite=len(root)
    root+=b'\x81\x02\x43\x64'+(b'\x82\x2C\x80\x0C' if long_intro else b'\x06\x80\x06')+b'\xFF'
    root[5:8]=second.to_bytes(3,'little');root[10:13]=finite.to_bytes(3,'little')
    return bytes(root)


def convert(raw=None,**flags):
    return convert_merged_song(fixtures.SampleConversionTests.archive_for(raw or program()),0,
                               [(0,),(1,),(2,)],mixed_loop_support=True,**flags)


class MixedLoopTests(unittest.TestCase):
    def test_finite_track_ends_once_and_shorter_loop_is_unfolded(self):
        raw=program();a=fixtures.SampleConversionTests.archive_for(raw)
        with self.assertRaisesRegex(ValueError,'requires looping'):
            convert_merged_song(a,0,[(0,),(1,),(2,)])
        _,dep,c=convert(raw)
        self.assertEqual(c['merged_loop_ticks'],24)
        self.assertEqual(c['mixed_loop_song']['source_loop_periods'],{'0':24,'1':12})
        self.assertEqual([t['termination'] for t in dep['tracks']],['repeated_state','repeated_state','fine'])
        self.assertEqual(dep['tracks'][2]['ticks_before_repeat'],12)
        self.assertEqual(len([n for n in c['note_mapping'] if n['source_track']==2]),1)
        self.assertTrue(c['note_timing_validation'][2]['complete_finite_track'])
        self.assertTrue(all(t['loop_ticks']==24 for t in dep['tracks'][:2]))
        self.assertFalse(c['mixed_loop_song']['finite_tracks_repeated'])

    def test_finite_long_gate_eot_precedes_fine_and_no_goto_is_emitted(self):
        _,dep,c=convert(program(True));t=dep['tracks'][2]
        self.assertEqual([(e['name'],e['ticks']) for e in t['events'] if e['name'] in ('TIE','EOT','FINE')],
                         [('TIE',0),('EOT',300),('FINE',312)])
        self.assertFalse(any(e['name']=='GOTO' for e in t['events']))
        self.assertEqual(c['mixed_loop_song']['finite_track_end_ticks'],{'2':312})

    def test_periodic_long_note_closure_at_entry_stays_inside_loop(self):
        _,dep,c=convert(program(True,True))
        self.assertEqual(c['merged_loop_ticks'],312)
        self.assertTrue(c['note_timing_validation'][0]['complete_loop_cycles']>=2)
        self.assertTrue(c['note_timing_validation'][2]['complete_finite_track'])

    def test_singleton_required_and_finite_modes_cannot_be_combined(self):
        tracks=trace_sequence(program(),analysis_only=True)
        with self.assertRaisesRegex(ValueError,'singleton'):
            assess_groups(tracks,[(0,1),(2,)],mixed_loop_support=True)
        with self.assertRaisesRegex(ValueError,'separate'):
            assess_groups(tracks,[(0,),(1,),(2,)],finite_support=True,mixed_loop_support=True)
        for flag in ('finite_support','finite_release_support','envelope_support','bandlimited_pcm'):
            with self.subTest(flag=flag),self.assertRaisesRegex(ValueError,'excludes finite-only'):
                convert(**{flag:True})

    def test_late_or_overhanging_finite_tracks_are_rejected(self):
        tracks=trace_sequence(program(),analysis_only=True)
        for late,message in [(True,'finish before'),(False,'close their gates')]:
            t=copy.deepcopy(tracks)
            t[2]['end_ticks']=100 if late else 1
            with self.subTest(late=late),self.assertRaisesRegex(ValueError,message):
                assess_groups(t,[(0,),(1,),(2,)],mixed_loop_support=True)

    def test_period_and_repeat_budgets_prevent_unbounded_expansion(self):
        tracks=trace_sequence(program(),analysis_only=True)
        for periods in ((97,101),(20000,20000),(0,24)):
            t=copy.deepcopy(tracks)
            for track,period in zip(t[:2],periods):track['loop_ticks']=period
            with self.subTest(periods=periods),self.assertRaisesRegex(ValueError,'budget|positive'):
                assess_groups(t,[(0,),(1,),(2,)],mixed_loop_support=True)

    def test_mixed_mode_rejects_pure_scores_and_tempo_changes(self):
        t=trace_sequence(program(),analysis_only=True)
        for tracks in (t[:2],t[2:]):
            with self.assertRaisesRegex(ValueError,'both finite and looping'):
                assess_groups(tracks,[(x['track'],) for x in tracks],mixed_loop_support=True)
        # Adding bytes changes branch offsets; isolate the tempo guard using
        # valid traced tracks instead of testing corrupted target addresses.
        t[0]['actions'].insert(0,dict(t[0]['actions'][3],opcode=225,value=121))
        with patch('nds_track_merge.trace_sequence',return_value=t),self.assertRaisesRegex(ValueError,'fixed source tempo'):
            convert()

    def test_reference_compares_entire_finite_track_without_unfolding(self):
        _,_,c=convert();c['samples']=[]
        rows=[(a['ticks'],t['track'],a['instrument'],a['key'],a['velocity'],a['duration'])
              for t in c['tracks'] for a in expand_actions(t,120) if a['name']=='note']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'conversion.json').write_text(json.dumps(c));(p/'source.sdat').write_bytes(b'fixture')
            ref=p/'ref';ref.mkdir();(ref/'reference.json').write_text('{"seconds":10}')
            def write(extra=()):
                with (ref/'notes.csv').open('w') as f:
                    w=csv.writer(f);w.writerow(['tick','track','instrument','key','velocity','duration']);w.writerows(rows+list(extra))
            with patch('validate_nds_experiment.SoundArchive'):
                write();r=check_reference(p,ref)
                self.assertEqual(r['mixed_finite_track_note_schedules_checked'],[2])
                write([(24,2,2,67,100,6)])
                with self.assertRaisesRegex(AssertionError,'finite DS note execution'):
                    check_reference(p,ref)

    def test_minimum_lfo_is_opt_in_and_has_absolute_bound(self):
        state={'mod_depth':3,'mod_speed':28,'mod_range':1,'mod_type':0,'mod_delay':14}
        with self.assertRaisesRegex(ValueError,'cannot be represented'):
            map_pitch_lfo(state,130,True)
        mapped=map_pitch_lfo(state,130,True,True)
        self.assertEqual(mapped['mod'],1)
        self.assertLessEqual(mapped['all_phase_pitch_difference_bound_cents'],10)
        fit=compare_config(state,130,True,True)
        self.assertLessEqual(fit['single_voice_one_second_rms_pitch_error_cents'],5)
        old={**state,'mod_depth':8}
        self.assertEqual(map_pitch_lfo(old,130,True),map_pitch_lfo(old,130,True,True))
        with self.assertRaisesRegex(ValueError,'explicit mixed'):
            convert_merged_song(fixtures.SampleConversionTests.archive_for(program()),0,[(0,),(1,),(2,)],
                                native_pitch_lfo=True,native_pitch_lfo_min_depth=True)


if __name__=='__main__':unittest.main()
