"""Explicit weak-depth/live-depth combination, with held and same-tick ordering."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nds_track_merge import convert_merged_song
from validate_nds_lfo import LfoModel
from test_nds_lfo_delay import archive_for
import test_nds_music as fixtures


def convert(body,**flags):
    options=dict(native_pitch_lfo=True,native_pitch_lfo_delay=True,
                 native_pitch_lfo_live_depth=True,native_pitch_lfo_min_depth=True)
    options.update(flags)
    return convert_merged_song(archive_for(body),0,[(0,)],**options)


def body(change_tick=12):
    return (b'\xCA\x03'+fixtures.note(length=96)+bytes([0x80,change_tick])+b'\xCA\x14'
            +bytes([0x80,96-change_tick])+b'\xCA\x03')


class LiveMinimumDepthTests(unittest.TestCase):
    def test_default_live_depth_still_rejects_weak_depth_and_opt_in_preserves_counters(self):
        for tick in (2,12):
            with self.subTest(tick=tick):
                with self.assertRaisesRegex(ValueError,'cannot be represented'):
                    convert(body(tick),native_pitch_lfo_min_depth=False)
                _,dep,c=convert(body(tick))
                events=dep['tracks'][0]['events']
                updates=[e for e in events if e['ticks']==tick and e['name']!='WAIT']
                self.assertEqual([(e['name'],e.get('value')) for e in updates],[('MOD',2)])
                model=LfoModel(events);before=model.advance(tick);after=model.advance(tick+1)
                self.assertEqual(before['depth'],1);self.assertEqual(after['depth'],2)
                self.assertEqual(after['count'],max(0,before['count']-1))
                self.assertEqual(after['phase'],before['phase'] if before['count'] else (before['phase']+before['speed'])%256)
                self.assertEqual(c['native_pitch_lfo']['minimum_depth_quantization']['scope'],
                                 'looping singleton live-depth experiment only')
                weak=[x for x in c['native_pitch_lfo']['configs'] if x.get('minimum_depth_quantized')]
                self.assertEqual(len(weak),1)
                self.assertLessEqual(weak[0]['single_voice_one_second_rms_pitch_error_cents'],5)
                self.assertTrue(c['note_timing_check'])

    def test_same_tick_new_note_precedes_depth_update(self):
        score=(b'\xCA\x03'+fixtures.note(length=96)+b'\x80\x0C'+fixtures.note(length=72)
               +b'\xCA\x14\x80\x54\xCA\x03')
        _,dep,_=convert(score);events=dep['tracks'][0]['events']
        at=[e for e in events if e['ticks']==12]
        note=next(i for i,e in enumerate(at) if e['name']=='NOTE')
        changes=[(i,e['value']) for i,e in enumerate(at) if e['name']=='MOD']
        self.assertTrue(any(i<note and value==1 for i,value in changes))
        self.assertTrue(any(i>note and value==2 for i,value in changes))
        self.assertEqual(LfoModel(events).advance(13)['depth'],2)

    def test_combination_excludes_unvalidated_modes_and_requires_live_delay(self):
        for flag in ('mixed_loop_support','finite_support','finite_release_support',
                     'bandlimited_pcm','native_pitch_lfo_live_toggle'):
            with self.subTest(flag=flag),self.assertRaisesRegex(ValueError,'without mixed'):
                convert(body(),**{flag:True})
        with self.assertRaisesRegex(ValueError,'requires native pitch LFO delay'):
            convert(body(),native_pitch_lfo_delay=False)
        with self.assertRaisesRegex(ValueError,'explicit mixed'):
            convert(body(),native_pitch_lfo_live_depth=False)

    def test_depth_disable_late_activation_other_parameters_and_variable_tempo_remain_rejected(self):
        for control in (b'\xCA\x00',b'\xCB\x14',b'\xCC\x01',b'\xCD\x02',b'\xE0\x14\x00'):
            score=b'\xCA\x03'+fixtures.note(length=96)+b'\x80\x0C'+control+b'\x80\x54'
            with self.subTest(control=control),self.assertRaises(ValueError):convert(score)
        with self.assertRaisesRegex(ValueError,'first note timestamp'):
            convert(fixtures.note(length=96)+b'\x80\x0C\xCA\x03\x80\x54')
        with self.assertRaisesRegex(ValueError,'fixed tempo'):
            convert(b'\xCA\x03'+fixtures.note(length=96)+b'\x80\x0C\xE1\x64\x00\x80\x54')

    def test_absolute_and_isolated_rms_guards_apply_to_new_route(self):
        with patch('nds_lfo.ds_pitch_units',return_value=64):
            with self.assertRaisesRegex(ValueError,'ten-cent'):convert(body())
        with patch('nds_track_merge.compare_config',return_value={
                'minimum_depth_quantized':True,'single_voice_one_second_rms_pitch_error_cents':5.1}):
            with self.assertRaisesRegex(ValueError,'five-cent'):convert(body())

    def test_existing_representable_live_mapping_has_identical_blob(self):
        score=b'\xCA\x0A'+fixtures.note(length=96)+b'\x80\x0C\xCA\x14\x80\x54\xCA\x0A'
        old,_,a=convert(score,native_pitch_lfo_min_depth=False)
        new,_,b=convert(score)
        self.assertEqual(old,new)
        self.assertEqual(a['native_pitch_lfo']['configs'],b['native_pitch_lfo']['configs'])

    def test_fitted_attack_remains_explicit_and_bounded_with_live_weak_depth(self):
        score=b'\xD0\x7C'+body()
        with self.assertRaisesRegex(ValueError,'effect 0xd0'):convert(score)
        _,dep,c=convert(score,envelope_support=True)
        self.assertTrue(c['note_timing_check'])
        self.assertTrue(c['native_pitch_lfo']['minimum_depth_quantization'])
        fit=c['envelope_approximation']['attack_fits'][0]
        self.assertEqual(fit['ds_attack'],124)
        self.assertLessEqual(fit['rms_amplitude_error'],0.12)
        self.assertLessEqual(fit['max_amplitude_error'],0.30)
        self.assertTrue(all(n['source_envelope']['attack']==124 for n in c['note_mapping']))
        self.assertEqual(LfoModel(dep['tracks'][0]['events']).advance(13)['depth'],2)
        with self.assertRaisesRegex(ValueError,'error limits'):
            convert(b'\xD0\x00'+body(),envelope_support=True)


if __name__=='__main__':unittest.main()
