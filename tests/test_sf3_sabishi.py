"""Local source integration checks for the explicit SF3 SABISHI selector."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path('scripts').resolve()))
from build_nds_experiment import build_experiment
from nds_music import SoundArchive,trace_sequence
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds')
SF1=SOURCE.with_name('ssr1d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and SF1.exists() and BASE.exists(),'local verified game assets unavailable')
class Sf3SabishiTests(unittest.TestCase):
 def test_selected_family_source_schedule_and_patch_reconstruction(self):
  base=BASE.read_bytes();output,patch,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf3-sabishi-variable-late-envelope',events=('1','21','scene:communication'))
  self.assertEqual(apply_bps(base,patch)[0],output)
  self.assertEqual((m['nds_conversion']['source_profile'],c['sequence_index']),('ssr3b',33))
  source_tracks=trace_sequence(SoundArchive(sdat).sequence(33)[0],analysis_only=True)
  self.assertEqual([t['notes'] for t in c['tracks']],[t['notes'] for t in source_tracks])
  self.assertEqual((c['track_count'],len(dep['samples'])),(8,14))
  self.assertTrue(c['native_pitch_lfo']['variable_late_fitted_extension']['enabled'])
  self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
  expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=output[start:end]
  self.assertEqual(output[:len(base)],expected)
 def test_selector_rejects_other_verified_source_family(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(SF1.read_bytes(),BASE.read_bytes(),song='sf3-sabishi-variable-late-envelope')
