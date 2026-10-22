"""Fourteen source schedules retain multiplicity and explicit fixed-volume mapping."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path('scripts').resolve()))
from build_nds_experiment import build_experiment
from nds_music import SoundArchive,trace_sequence
from nds_track_merge import convert_merged_song
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds');OTHER=SOURCE.with_name('ssr2d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and OTHER.exists() and BASE.exists(),'local verified game inputs unavailable')
class Sf3AjitoMergeTests(unittest.TestCase):
 def test_fourteen_sources_keep_schedule_and_fixed_gain_mapping(self):
  base=BASE.read_bytes();output,patch,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf3-ajito-fourteen-track',events=('1','21','scene:communication'))
  a=SoundArchive(sdat);tracks=trace_sequence(a.sequence(7)[0],analysis_only=True)
  groups=c['track_groups'];self.assertEqual(groups,[[0,4,6,7,8,11,14],[1],[2],[3],[5],[9],[10],[15]])
  self.assertEqual((c['source_track_count'],c['track_count'],len(dep['samples'])),(14,8,33))
  self.assertEqual([t['notes'] for t in c['tracks']],[t['notes'] for t in tracks])
  _,_,single=convert_merged_song(a,7,[(t['track'],) for t in tracks],track_capacity=14,song_gain_db=3.5)
  fields=('tick','source_track','source_instrument','source_key','source_velocity','duration')
  self.assertEqual([tuple(n[k] for k in fields) for n in c['note_mapping']],[tuple(n[k] for k in fields) for n in single['note_mapping']])
  from nds_music import level
  volumes={0:100,4:100,6:90,7:90,8:100,11:90,14:60}
  for n,old in zip(c['note_mapping'],single['note_mapping']):
   ratio=level(volumes[n['source_track']])/level(100) if n['source_track'] in volumes else 1.0
   ideal=127*level(n['source_velocity'])*ratio
   self.assertEqual(n['gba_velocity'],round(ideal))
   self.assertGreater(n['gba_velocity'],0)
   self.assertLessEqual(abs(n['gba_velocity']-ideal),.5)
   if ratio==1:self.assertEqual(n['gba_velocity'],old['gba_velocity'])
  self.assertTrue(all(r['complete_loop_cycles']==2 for r in c['note_timing_validation']))
  self.assertTrue(any(n['long_note'] for n in c['note_mapping']))
  self.assertEqual(c['long_note_aliases'],[{'target_track':2,'source_track':2,'source_key':55,'gba_key':127},{'target_track':2,'source_track':2,'source_key':58,'gba_key':126},{'target_track':2,'source_track':2,'source_key':59,'gba_key':125},{'target_track':6,'source_track':10,'source_key':61,'gba_key':127}])
  self.assertEqual({e['state_after']['volume'] for t in c['tracks'] if t['track']==15 for e in t['actions'] if e['name']=='note'},{70,80})
  self.assertEqual({e['state_after']['expression'] for t in c['tracks'] if t['track']==9 for e in t['actions'] if e['name']=='note'},{30,127})
  self.assertEqual(apply_bps(base,patch)[0],output)
  expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=output[start:end]
  self.assertEqual(output[:len(base)],expected)
  self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
 def test_source_family_and_unmerged_capacity_guards_remain(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(OTHER.read_bytes(),BASE.read_bytes(),song='sf3-ajito-fourteen-track')
  from build_nds_experiment import SOURCE_ARCHIVES
  from nds_music import nds_sdat
  a=SoundArchive(nds_sdat(SOURCE.read_bytes(),SOURCE_ARCHIVES['ssr3']['file_id']))
  with self.assertRaisesRegex(ValueError,'track capacity'):
   convert_merged_song(a,7,[(i,) for i in (0,1,2,3,4,5,6,7,8,9,10,11,14,15)])
