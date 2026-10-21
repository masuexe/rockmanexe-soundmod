import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import test_nds_music as fixtures
from nds_track_merge import convert_merged_song
from validate_nds_lfo import LfoModel
from validate_nds_experiment import check_variable_tempo_reference
from nds_variable_lfo import prepare_variable_lfo


def score(change=b'',delay=0,conflict=False,variable=True,first_off=False):
 raw=bytearray(b'\xFE\x03\x00\x93\x01'+bytes(3)+b'\xC7\x00\xE1\x78\x00')
 if conflict:raw+=b'\xE1\x3C\x00'
 loop=len(raw)
 raw+=fixtures.note(length=96)+b'\x80\x30'
 if variable:raw+=b'\xE1\x3C\x00'
 raw+=b'\x80\x30\xE1\x78\x00\x94'+loop.to_bytes(3,'little')
 second=len(raw);raw+=b'\xC7\x00\xCB\x14\xE0'+delay.to_bytes(2,'little')
 if not first_off:raw+=b'\xCA\x0F'
 body=len(raw)
 raw+=fixtures.note(length=64)
 if first_off:raw+=b'\xCA\x0F'
 raw+=b'\x80\x30'+change+b'\x80\x10'+fixtures.note(length=32)+b'\x80\x20\x94'+body.to_bytes(3,'little')
 raw[5:8]=second.to_bytes(3,'little')
 return bytes(raw)


def convert(raw=None,**flags):
 options=dict(native_pitch_lfo=True,native_pitch_lfo_variable_tempo=True)
 options.update(flags)
 return convert_merged_song(fixtures.SampleConversionTests.archive_for(raw or score()),0,[(0,),(1,)],**options)


class VariablePitchLfoTests(unittest.TestCase):
 def test_held_phase_continues_across_tempo_and_frequency_changes(self):
  _,dep,c=convert();model=LfoModel(dep['tracks'][1]['events'])
  before=model.advance(48);after=model.advance(49)
  self.assertGreater(before['speed'],0);self.assertGreater(after['speed'],before['speed'])
  self.assertEqual(after['phase'],(before['phase']+after['speed'])%256)
  self.assertEqual(after['count'],before['count'])
  v=c['native_pitch_lfo']['variable_tempo_approximation']
  self.assertEqual(v['source_tempos'],[60,120]);self.assertFalse(v['live_modulation_or_delays'])
  self.assertTrue(v['positive_speed_writes_preserve_phase_and_count'])

 def test_notes_after_tempo_change_use_current_frequency_and_reset_delay(self):
  _,dep,_=convert();events=dep['tracks'][1]['events']
  speed48=next(e['value'] for e in events if e['ticks']==48 and e['name']=='LFOS')
  speed64=[e['value'] for e in events if e['ticks']==64 and e['name']=='LFOS']
  self.assertEqual(speed64,[0,speed48])
  model=LfoModel(events);state=model.advance(65)
  self.assertEqual((state['phase'],state['count']),(0,0))

 def test_first_note_then_same_tick_initial_enable_keeps_source_order(self):
  _,dep,_=convert(score(first_off=True))
  events=dep['tracks'][1]['events'];note=next(i for i,e in enumerate(events) if e['name']=='NOTE')
  self.assertEqual(events[note+1]['name'],'MOD')
  self.assertGreater(events[note+1]['value'],0)
  self.assertGreater(LfoModel(events).advance(1)['speed'],0)

 def test_old_native_lfo_keeps_variable_tempo_guard(self):
  with self.assertRaisesRegex(ValueError,'requires a fixed tempo'):
   convert(native_pitch_lfo_variable_tempo=False)

 def test_explicit_mode_excludes_delays_and_live_parameter_changes(self):
  with self.assertRaisesRegex(ValueError,'zero-delay'):convert(score(delay=10))
  for command in (b'\xCA\x00',b'\xCA\x0A',b'\xCB\x19',b'\xCC\x01',b'\xCD\x02',b'\xE0\x01\x00'):
   with self.subTest(command=command),self.assertRaisesRegex(ValueError,'live modulation'):
    convert(score(change=command))

 def test_other_approximation_modes_are_excluded(self):
  for flag in ('native_pitch_lfo_delay','native_pitch_lfo_live_depth','native_pitch_lfo_live_toggle',
               'native_pitch_lfo_late_depth','native_pitch_lfo_min_depth','envelope_support','finite_support',
               'finite_release_support','mixed_loop_support','bandlimited_pcm'):
   with self.subTest(flag=flag),self.assertRaisesRegex(ValueError,'Variable-tempo LFO requires'):
    convert(**{flag:True})
  with self.assertRaisesRegex(ValueError,'Variable-tempo LFO requires'):convert(native_pitch_lfo=False)

 def test_conflicting_and_unnecessary_tempo_modes_are_rejected(self):
  with self.assertRaisesRegex(ValueError,'conflicting same-tick'):convert(score(conflict=True))
  with self.assertRaisesRegex(ValueError,'eight tempos'):convert(score(variable=False))

 def test_compensation_covers_loop_body_and_never_changes_mod_depth(self):
  _,dep,c=convert();v=c['native_pitch_lfo']['variable_tempo_approximation']
  self.assertTrue(all(x['source_track']==1 for x in v['lfos_updates']))
  events=dep['tracks'][1]['events']
  for tick in (48,144):
   self.assertTrue(any(e['ticks']==tick and e['name']=='LFOS' and e['value']>0 for e in events))
   self.assertFalse(any(e['ticks']==tick and e['name'] in ('MOD','LFODL') for e in events))
  self.assertEqual(c['note_timing_validation'][1]['complete_loop_cycles'],2)

 def test_variable_reference_requires_the_complete_executed_tempo_schedule(self):
  _,_,c=convert()
  text='tick,track,opcode,value\n0,0,225,120\n48,0,225,60\n96,0,225,120\n144,0,225,60\n192,0,225,120\n'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);f=p/'controls.csv';f.write_text(text)
   self.assertEqual(check_variable_tempo_reference(c,p)['tempo_control_matches'],5)
   for corrupt in (text.replace('144,0,225,60','144,0,225,80'),text.replace('144,0,225,60\n',''),
                   text.replace('192,0,225,120\n',''),text.replace('144,0,225','144,1,225')):
    f.write_text(corrupt)
    with self.assertRaises(AssertionError):check_variable_tempo_reference(c,p)

 def test_tempo_count_and_unfolded_update_budgets_are_bounded(self):
  _,_,c=convert()
  tracks=[dict(t,actions=[dict(a,event_order=i) for i,a in enumerate(t['actions'])]) for t in c['tracks']]
  for tempos in ([40+i for i in range(9)],[60 if i%2 else 120 for i in range(129)]):
   expanded={0:[{'opcode':0xE1,'ticks':i,'value':tempo} for i,tempo in enumerate(tempos)]}
   with self.assertRaisesRegex(ValueError,'eight tempos or 128'):prepare_variable_lfo(tracks,expanded)

if __name__=='__main__':unittest.main()
