"""Intro notes followed by silent loops still require exact notes and loop coverage."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from validate_nds_experiment import check_reference

class IntroOnlyReferenceTests(unittest.TestCase):
 def fixture(self,p):
  note={'name':'note','opcode':60,'ticks':0,'instrument':2,'key':60,'velocity':100,'duration':12}
  actions=[note,{'name':'control','opcode':225,'ticks':12,'value':120},{'name':'control','opcode':192,'ticks':24,'value':64}]
  c={'samples':[],'tempo_mapping':[{'nds_ticks_per_second':120}], 'tracks':[{'track':0,'termination':'loop','loop_action':1,'loop_ticks':24,'loop_start_ticks':12,'end_ticks':36,'actions':actions}]}
  (p/'conversion.json').write_text(json.dumps(c));(p/'source.sdat').write_bytes(b'fixture')
  q=p/'reference';q.mkdir();(q/'reference.json').write_text(json.dumps({'seconds':1}))
  (q/'notes.csv').write_text('tick,track,instrument,key,velocity,duration\n0,0,2,60,100,12\n')
  (q/'controls.csv').write_text('tick,track,opcode,value\n12,0,225,120\n36,0,225,120\n60,0,225,120\n24,0,192,64\n48,0,192,64\n72,0,192,64\n')
  return q,c
 def test_intro_notes_are_not_required_to_repeat_in_silent_loop(self):
  with tempfile.TemporaryDirectory() as d,patch('validate_nds_experiment.SoundArchive'):
   p=Path(d);q,_=self.fixture(p);r=check_reference(p,q)
   self.assertEqual(r['per_track_note_matches'],{'0':1})
   self.assertEqual(r['intro_only_loop_track_checks'],[{'source_track':0,'intro_note_events':1,'required_coverage_ticks':60,'tempo_matches':3}])
 def test_changed_extra_missing_intro_notes_and_short_duration_fail(self):
  with tempfile.TemporaryDirectory() as d,patch('validate_nds_experiment.SoundArchive'):
   p=Path(d);q,_=self.fixture(p);original=(q/'notes.csv').read_text()
   for notes in (original.replace(',100,12',',101,12'),original+'24,0,2,60,100,12\n',original.splitlines()[0]+'\n'):
    (q/'notes.csv').write_text(notes)
    with self.subTest(notes=notes),self.assertRaises(AssertionError):check_reference(p,q)
   (q/'notes.csv').write_text(original);(q/'reference.json').write_text(json.dumps({'seconds':.49}))
   with self.assertRaisesRegex(AssertionError,'Intro-only reference must cover'):check_reference(p,q)
 def test_loop_controls_cannot_pass_by_truncating_their_log(self):
  with tempfile.TemporaryDirectory() as d,patch('validate_nds_experiment.SoundArchive'):
   p=Path(d);q,_=self.fixture(p);original=(q/'controls.csv').read_text()
   for controls in ('tick,track,opcode,value\n', 'tick,track,opcode,value\n12,0,225,120\n24,0,192,64\n',original.replace('48,0,192,64','48,0,192,63')):
    (q/'controls.csv').write_text(controls)
    with self.subTest(controls=controls),self.assertRaises(AssertionError):check_reference(p,q)
   (q/'controls.csv').unlink()
   with self.assertRaisesRegex(AssertionError,'independent control'):check_reference(p,q)
 def test_normal_sounding_loop_still_requires_repeated_notes(self):
  with tempfile.TemporaryDirectory() as d,patch('validate_nds_experiment.SoundArchive'):
   p=Path(d);q,c=self.fixture(p);c['tracks'][0]['actions'].append({**c['tracks'][0]['actions'][0],'ticks':24});(p/'conversion.json').write_text(json.dumps(c))
   with self.assertRaisesRegex(AssertionError,'Reference must cover two complete loops'):check_reference(p,q)
