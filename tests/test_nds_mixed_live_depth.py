import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nds_music import trace_sequence
from nds_track_merge import assess_groups,convert_merged_song
import test_nds_music as fixtures


def varlen(value):
 result=[value&127];value>>=7
 while value:
  result.insert(0,(value&127)|128);value>>=7
 return bytes(result)


def score(end=12,gate=6,period=24,attack=None,change=None):
 raw=bytearray(b'\xFE\x03\x00\x93\x01'+bytes(3)+b'\xE1\x78\x00\xC7\x00\x81\x02\xCB\x1C\xE0\x0E\x00\xCA\x03')
 if attack is not None:raw+=bytes([0xD0,attack])
 loop=len(raw)
 raw+=b'\x3C\x64'+varlen(12)+b'\x80'+varlen(period)
 if change:raw+=change
 raw+=b'\x94'+loop.to_bytes(3,'little')
 finite=len(raw);raw+=b'\xC7\x00\x81\x02\x43\x64'+varlen(gate)+b'\x80'+varlen(end)+b'\xFF'
 raw[5:8]=finite.to_bytes(3,'little')
 return bytes(raw)


def convert(raw=None,**flags):
 options=dict(native_pitch_lfo=True,native_pitch_lfo_delay=True,native_pitch_lfo_live_depth=True,
              native_pitch_lfo_min_depth=True,mixed_loop_support=True,mixed_live_depth_support=True)
 options.update(flags)
 return convert_merged_song(fixtures.SampleConversionTests.archive_for(raw or score()),0,[(0,),(1,)],**options)


class MixedLiveDepthTests(unittest.TestCase):
 def test_later_entry_is_explicit_and_finite_track_still_ends_once(self):
  tracks=trace_sequence(score(),analysis_only=True)
  with self.assertRaisesRegex(ValueError,'finish before'):
   assess_groups(tracks,[(0,),(1,)],mixed_loop_support=True)
  _,dep,c=convert()
  self.assertEqual((c['merged_loop_start_ticks'],c['merged_loop_ticks']),(48,24))
  self.assertEqual(c['mixed_live_depth_extension']['original_shared_loop_start_ticks'],0)
  self.assertEqual(c['mixed_live_depth_extension']['selected_entry_before_lfo_warmup'],24)
  self.assertEqual(c['mixed_live_depth_extension']['later_entry_common_cycles'],1)
  self.assertEqual(dep['tracks'][1]['termination'],'fine')
  self.assertEqual(dep['tracks'][1]['ticks_before_repeat'],12)
  self.assertEqual(len([n for n in c['note_mapping'] if n['source_track']==1]),1)
  self.assertFalse(any(e['name']=='GOTO' for e in dep['tracks'][1]['events']))
  self.assertTrue(c['note_timing_validation'][1]['complete_finite_track'])

 def test_later_entry_budget_is_one_common_period(self):
  with self.assertRaisesRegex(ValueError,'one additional common period'):convert(score(end=25))
  with self.assertRaisesRegex(ValueError,'explicit mixed score'):
   assess_groups(trace_sequence(score(),analysis_only=True),[(0,),(1,)],mixed_later_entry=True)

 def test_finite_gate_must_close_at_its_own_end(self):
  with self.assertRaisesRegex(ValueError,'close their gates'):convert(score(end=3))
  _,dep,c=convert(score(end=12,gate=12))
  self.assertEqual(dep['tracks'][1]['ticks_before_repeat'],12)
  self.assertTrue(c['note_timing_validation'][1]['complete_finite_track'])

 def test_long_finite_note_closes_before_fine_without_repetition(self):
  _,dep,c=convert(score(end=300,gate=300,period=384))
  endings=[(e['name'],e['ticks']) for e in dep['tracks'][1]['events'] if e['name'] in ('TIE','EOT','FINE')]
  self.assertEqual(endings,[('TIE',0),('EOT',300),('FINE',300)])
  self.assertEqual(c['merged_loop_start_ticks'],768)
  self.assertEqual(len([n for n in c['note_mapping'] if n['source_track']==1]),1)

 def test_new_combination_requires_explicit_mixed_delayed_live_mode(self):
  for key,value in (('mixed_loop_support',False),('native_pitch_lfo',False),('native_pitch_lfo_delay',False),
                    ('native_pitch_lfo_live_depth',False),('finite_support',True),('finite_release_support',True),
                    ('bandlimited_pcm',True),('native_pitch_lfo_live_toggle',True)):
   with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Mixed live-depth extension requires'):
    convert(**{key:value})
  with self.assertRaisesRegex(ValueError,'without mixed'):
   convert(mixed_live_depth_support=False)

 def test_attack_fitting_stays_separate_and_weak_depth_bounds_remain(self):
  with self.assertRaisesRegex(ValueError,'effect 0xd0'):convert(score(attack=124))
  _,_,c=convert(score(attack=124),envelope_support=True)
  self.assertTrue(c['mixed_live_depth_extension']['fitted_envelope_explicit'])
  self.assertEqual(c['envelope_approximation']['attack_fits'][0]['ds_attack'],124)
  self.assertEqual(c['native_pitch_lfo']['minimum_depth_quantization']['scope'],'mixed singleton live-depth experiment only')
  with self.assertRaisesRegex(ValueError,'cannot be represented'):
   convert(native_pitch_lfo_min_depth=False)

 def test_parameter_changes_and_singleton_guards_are_preserved(self):
  for change in (b'\xCA\x00',b'\xCB\x18',b'\xCC\x01',b'\xCD\x02',b'\xE0\x0A\x00'):
   with self.subTest(change=change),self.assertRaises(ValueError):convert(score(change=change))
  a=fixtures.SampleConversionTests.archive_for(score())
  with self.assertRaisesRegex(ValueError,'singleton'):
   convert_merged_song(a,0,[(0,1)],native_pitch_lfo=True,native_pitch_lfo_delay=True,
    native_pitch_lfo_live_depth=True,native_pitch_lfo_min_depth=True,mixed_loop_support=True,mixed_live_depth_support=True)


if __name__=='__main__':unittest.main()
