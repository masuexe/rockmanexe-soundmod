import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path('tests').resolve()))
from test_nds_variable_lfo import score, convert
from nds_music import trace_sequence
from nds_track_merge import expand_actions
from nds_variable_lfo import prepare_variable_lfo
from validate_nds_lfo import LfoModel

class VariableLateFittedTests(unittest.TestCase):
 def test_combination_requires_both_explicit_modes(self):
  for flags in ({'envelope_support':False},{'native_pitch_lfo_variable_tempo':False}):
   with self.assertRaisesRegex(ValueError,'requires'):
    convert(variable_late_fitted_support=True,envelope_support=flags.get('envelope_support',True),native_pitch_lfo_variable_tempo=flags.get('native_pitch_lfo_variable_tempo',True))
 def test_late_initialization_is_opt_in_and_keeps_fixed_parameters(self):
  tracks=trace_sequence(score(first_off=True),analysis_only=True)
  # Move initial enable after the first note; preserve event order and all other parameters.
  for track in tracks:
   for i,a in enumerate(track["actions"]):a["event_order"]=i
  t=tracks[1]
  enable=next(a for a in t['actions'] if a['opcode']==0xCA)
  enable['ticks']=12
  expanded={0:tracks[0]['actions']}
  with self.assertRaisesRegex(ValueError,'late activation'):prepare_variable_lfo(tracks,expanded)
  baselines,_,_=prepare_variable_lfo(tracks,expanded,late_activation=True)
  self.assertEqual(baselines[1]['mod_depth'],15)
  enable['state_after']['mod_delay']=1
  with self.assertRaisesRegex(ValueError,'zero-delay'):prepare_variable_lfo(tracks,expanded,late_activation=True)
 def test_explicit_extension_preserves_existing_variable_rom_bytes(self):
  old,_,_=convert()
  new,_,c=convert(envelope_support=True,variable_late_fitted_support=True)
  self.assertEqual(old,new)
  policy=c['native_pitch_lfo']['variable_late_fitted_extension']
  self.assertTrue(policy['enabled']);self.assertFalse(policy['disabling_after_activation'])
 def test_extension_still_rejects_positive_changes_and_disabling(self):
  for command in (b'\xCA\x00',b'\xCA\x0A',b'\xCB\x19',b'\xCC\x01'):
   with self.subTest(command=command),self.assertRaisesRegex(ValueError,'live modulation'):
    convert(score(change=command),envelope_support=True,variable_late_fitted_support=True)
 def test_extension_does_not_enable_other_approximation_modes(self):
  for flag in ('native_pitch_lfo_delay','native_pitch_lfo_live_depth','native_pitch_lfo_live_toggle','native_pitch_lfo_min_depth','finite_support','mixed_loop_support','bandlimited_pcm'):
   with self.subTest(flag=flag),self.assertRaises(ValueError):
    convert(envelope_support=True,variable_late_fitted_support=True,**{flag:True})
