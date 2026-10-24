"""Pinned SF1 ANTENNA filtering preserves seven source schedules and exporter bounds."""
import sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path('scripts').resolve())]
from build_nds_experiment import build_experiment,SOURCE_ARCHIVES
from nds_music import SoundArchive,nds_sdat
from nds_track_merge import convert_merged_song
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr1d.nds');OTHER=SOURCE.with_name('ssr2d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and OTHER.exists() and BASE.exists(),'local verified game inputs unavailable')
class Sf1AntennaAntialiasTests(unittest.TestCase):
 def test_filtered_schedules_controls_and_prefix_preserved(self):
  base=BASE.read_bytes();out,bps,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf1-antenna-antialias',events=('1','21','scene:communication'))
  _,_,plain=convert_merged_song(SoundArchive(sdat),16,[(i,) for i in range(7)],song_gain_db=3.5)
  for field in ('note_mapping','tracks','track_groups','note_timing_validation','long_note_aliases','long_note_loop_carries','tempo_mapping','voice_context_splits','priority_mapping','song_priority'):
   self.assertEqual(c[field],plain[field],field)
  self.assertEqual((c['source_track_count'],c['track_count'],len(c['note_mapping']),len(dep['samples'])),(7,7,2165,135))
  self.assertEqual(c['long_note_aliases'],[{'target_track':1,'source_track':1,'source_key':52,'gba_key':127},{'target_track':5,'source_track':5,'source_key':59,'gba_key':127}]);self.assertFalse(c['long_note_loop_carries'])
  self.assertFalse(c['bandlimited_pcm']['runtime_mixer_changed']);self.assertLess(sum(s['pcm8_bytes'] for s in c['samples']),4_000_000)
  self.assertEqual(apply_bps(base,bps)[0],out);expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=out[start:end]
  self.assertEqual(out[:len(base)],expected);self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
 def test_source_family_capacity_and_merged_opt_in_guards(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(OTHER.read_bytes(),BASE.read_bytes(),song='sf1-antenna-antialias')
  a=SoundArchive(nds_sdat(SOURCE.read_bytes(),SOURCE_ARCHIVES['ssr1']['file_id']))
  with self.assertRaisesRegex(ValueError,'track capacity'):
   convert_merged_song(a,16,[(i,) for i in range(7)],track_capacity=6,bandlimited_pcm=True)
  with self.assertRaisesRegex(ValueError,'Merged bandlimited mode requires'):
   convert_merged_song(a,16,[(i,) for i in range(7)],bandlimited_pcm=True,merged_bandlimited_support=True)
