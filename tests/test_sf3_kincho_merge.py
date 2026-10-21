"""Local integration: merge three equal-volume tracks without changing source notes."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path('scripts').resolve()))
from build_nds_experiment import build_experiment
from nds_music import SoundArchive,trace_sequence
from nds_track_merge import convert_merged_song
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds');OTHER=SOURCE.with_name('ssr2d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and OTHER.exists() and BASE.exists(),'local verified game inputs unavailable')
class Sf3KinchoMergeTests(unittest.TestCase):
 def test_ten_sources_preserved_and_three_way_merge_keeps_velocities(self):
  base=BASE.read_bytes();output,patch,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf3-kincho-ten-track',events=('1','21','scene:communication'))
  a=SoundArchive(sdat);tracks=trace_sequence(a.sequence(30)[0],analysis_only=True)
  groups=c['track_groups'];self.assertEqual(groups,[[0],[1],[2,4,6],[3],[5],[7],[14],[15]])
  self.assertEqual((c['source_track_count'],c['track_count'],len(dep['samples'])),(10,8,23))
  self.assertEqual([t['notes'] for t in c['tracks']],[t['notes'] for t in tracks])
  _,_,single=convert_merged_song(a,30,[(t['track'],) for t in tracks],track_capacity=10,song_gain_db=3.5)
  fields=('tick','source_track','source_instrument','source_key','source_velocity','duration','gba_velocity')
  self.assertEqual([tuple(n[k] for k in fields) for n in c['note_mapping']],[tuple(n[k] for k in fields) for n in single['note_mapping']])
  self.assertTrue(all(r['complete_loop_cycles']==2 for r in c['note_timing_validation']))
  self.assertEqual(apply_bps(base,patch)[0],output)
  expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=output[start:end]
  self.assertEqual(output[:len(base)],expected)
  self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
 def test_source_family_and_unmerged_capacity_guards_remain(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(OTHER.read_bytes(),BASE.read_bytes(),song='sf3-kincho-ten-track')
  from build_nds_experiment import SOURCE_ARCHIVES
  from nds_music import nds_sdat
  a=SoundArchive(nds_sdat(SOURCE.read_bytes(),SOURCE_ARCHIVES['ssr3']['file_id']))
  with self.assertRaisesRegex(ValueError,'track capacity'):
   convert_merged_song(a,30,[(i,) for i in (0,1,2,3,4,5,6,7,14,15)])
