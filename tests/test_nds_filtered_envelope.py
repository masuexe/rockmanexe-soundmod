"""Filtered PCM identity is independent of note-on envelope voice contexts."""
from dataclasses import replace
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nds_music import NoteDefinition, ROM_BASE, convert_envelope
from nds_track_merge import convert_merged_song
import test_nds_music as fixtures

INTRO=b'\xC7\x00\xE1\x78\x00\x81\x02'


def archive_for(body):
    archive=fixtures.SampleConversionTests.archive_for(INTRO+body+b'\x94'+len(INTRO).to_bytes(3,'little'))
    archive.wave=lambda *_:([0,12000,0,-12000]*512,{'effective_rate_hz':22050,'looped':True,
                           'loop_start_samples':512,'sample_count':2048})
    return archive


def tone(blob,dep,n):
    bank=dep['header']['tone_bank']['file_offset']
    children=struct.unpack_from('<I',blob,bank+n['gba_voice']*12+4)[0]-ROM_BASE
    start=children+n['gba_key']*12
    return blob[start:start+12]


class FilteredEnvelopeTests(unittest.TestCase):
    def test_same_wave_and_key_share_pcm_but_keep_distinct_attack_release_snapshots(self):
        body=b'\xD0\x64\xD3\x73'+fixtures.note()+b'\x80\x0C'
        body+=b'\xD0\x7F\xD3\x78'+fixtures.note()+b'\x80\x0C'
        blob,dep,c=convert_merged_song(archive_for(body),0,[(0,)],envelope_support=True,bandlimited_pcm=True)
        notes=c['note_mapping'][:2];tones=[tone(blob,dep,n) for n in notes]
        self.assertEqual(len(dep['samples']),1)
        self.assertNotEqual(notes[0]['gba_voice'],notes[1]['gba_voice'])
        self.assertEqual(tones[0][4:8],tones[1][4:8])
        self.assertEqual([t[8] for t in tones],[74,255])
        for n,t in zip(notes,tones):
            definition=replace(NoteDefinition(0,0,60,127,127,127,127,64),**n['source_envelope'])
            self.assertEqual(tuple(t[8:12]),convert_envelope(definition,True))
        self.assertNotEqual(tones[0][11],tones[1][11])
        self.assertTrue(c['bandlimited_pcm']['fitted_attack_envelopes'])
        self.assertFalse(c['envelope_approximation']['overrides_affect_existing_voices'])

    def test_same_wave_and_key_with_different_roots_get_independent_tuning(self):
        body=fixtures.note()+b'\x80\x0C\x81\x03'+fixtures.note()+b'\x80\x0C'
        a=archive_for(body)
        a.note_definition=lambda bank,instrument,key:NoteDefinition(0,0,60 if instrument==2 else 72,100,127,127,127,64)
        _,dep,c=convert_merged_song(a,0,[(0,)],envelope_support=True,bandlimited_pcm=True)
        self.assertEqual(len(dep['samples']),2)
        self.assertEqual({s['root_key'] for s in c['samples']},{60,72})
        self.assertEqual({s['source_key'] for s in c['samples']},{60})
        rates={s['root_key']:s['resampling']['source_pitched_rate_hz'] for s in c['samples']}
        self.assertAlmostEqual(rates[60]/rates[72],2)
        self.assertTrue(all(abs(s['resampling']['pitch_error_cents'])<.001 for s in c['samples']))

    def test_long_note_alias_keeps_original_filter_pitch_and_fitted_attack(self):
        a=archive_for(bytes([60,100,0x82,0x2C,128,0x82,0x38])) # gate 300, period 312
        a.note_definition=lambda *_:NoteDefinition(0,0,60,100,127,127,127,64)
        blob,dep,c=convert_merged_song(a,0,[(0,)],envelope_support=True,bandlimited_pcm=True)
        n=c['note_mapping'][0];t=tone(blob,dep,n)
        self.assertEqual((n['source_key'],n['gba_key'],n['duration']),(60,127,300))
        self.assertEqual((c['samples'][0]['source_key'],t[1],t[8]),(60,60,74))
        self.assertTrue(c['note_timing_validation'][0]['boundary_eot_included'])
        self.assertEqual(c['note_timing_validation'][0]['complete_loop_cycles'],2)

    def test_finite_lfo_merged_pitch_and_poor_fit_guards_remain(self):
        a=archive_for(fixtures.note()+b'\x80\x0C')
        for flags,message in [({'native_pitch_lfo':True},'excludes native LFO'),
                              ({'finite_support':True},'Finite experiment currently excludes')]:
            with self.subTest(flags=flags),self.assertRaisesRegex(ValueError,message):
                convert_merged_song(a,0,[(0,)],envelope_support=True,bandlimited_pcm=True,**flags)
        with self.assertRaisesRegex(ValueError,'singleton'):
            convert_merged_song(a,0,[(0,1)],envelope_support=True,bandlimited_pcm=True)
        for control in (b'\xC4\x01',b'\xC3\x01',b'\xCA\x01',b'\xCE\x01'):
            with self.subTest(control=control),self.assertRaisesRegex(ValueError,'upward bend, transpose, modulation and portamento'):
                convert_merged_song(archive_for(control+fixtures.note()+b'\x80\x0C'),0,[(0,)],
                                    envelope_support=True,bandlimited_pcm=True)
        a.note_definition=lambda *_:NoteDefinition(0,0,60,0,127,127,127,64)
        with self.assertRaisesRegex(ValueError,'error limits'):
            convert_merged_song(a,0,[(0,)],envelope_support=True,bandlimited_pcm=True)


if __name__=='__main__':unittest.main()
