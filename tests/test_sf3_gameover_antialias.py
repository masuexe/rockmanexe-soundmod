"""Pinned SF3 GAMEOVER filtering preserves eight source schedules and exporter bounds."""
import sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path('scripts').resolve())]
from build_nds_experiment import build_experiment,SOURCE_ARCHIVES
from nds_music import SoundArchive,nds_sdat
from nds_track_merge import convert_merged_song
from scan_audio import apply_bps
from analyze_song import analyze
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds');OTHER=SOURCE.with_name('ssr2d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and OTHER.exists() and BASE.exists(),'local verified game inputs unavailable')
class Sf3GameoverAntialiasTests(unittest.TestCase):
 def test_filtered_schedules_controls_and_prefix_preserved(self):
  base=BASE.read_bytes();out,bps,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf3-gameover-antialias',events=('1','21','scene:communication'))
  _,_,plain=convert_merged_song(SoundArchive(sdat),40,[(i,) for i in range(8)],song_gain_db=3.5,finite_support=True)
  for field in ('note_mapping','tracks','track_groups','note_timing_validation','long_note_aliases','long_note_loop_carries','tempo_mapping','voice_context_splits','priority_mapping','song_priority','finite_song','target_schedules'):
   self.assertEqual(c[field],plain[field],field)
  self.assertEqual((c['source_track_count'],c['track_count'],len(c['note_mapping']),len(dep['samples'])),(8,8,83,39))
  self.assertFalse(c['long_note_aliases']);self.assertFalse(c['long_note_loop_carries'])
  ends={str(i):v for i,v in enumerate([239,287,311,311,335,323,287,335])}
  self.assertEqual(c['finite_song']['track_end_ticks'],ends)
  native=analyze(out,m['target_table_file_offset'],474)
  self.assertEqual([t['termination'] for t in native['tracks']],['fine']*8)
  self.assertEqual([t['ticks_before_repeat'] for t in native['tracks']],list(ends.values()))
  self.assertFalse(any(e['name']=='GOTO' for t in native['tracks'] for e in t['events']))
  self.assertTrue(all(n['tick']+n['duration']<=ends[str(n['source_track'])] for n in c['note_mapping']))
  self.assertFalse(c['bandlimited_pcm']['runtime_mixer_changed']);self.assertLess(sum(s['pcm8_bytes'] for s in c['samples']),4_000_000)
  self.assertEqual(apply_bps(base,bps)[0],out);expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=out[start:end]
  self.assertEqual(out[:len(base)],expected);self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
 def test_source_family_capacity_and_merged_opt_in_guards(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(OTHER.read_bytes(),BASE.read_bytes(),song='sf3-gameover-antialias')
  a=SoundArchive(nds_sdat(SOURCE.read_bytes(),SOURCE_ARCHIVES['ssr3']['file_id']))
  with self.assertRaisesRegex(ValueError,'track capacity'):
   convert_merged_song(a,40,[(i,) for i in range(8)],track_capacity=7,bandlimited_pcm=True,finite_support=True)
  with self.assertRaisesRegex(ValueError,'looping source tracks'):
   convert_merged_song(a,40,[(i,) for i in range(8)],bandlimited_pcm=True)
  with self.assertRaisesRegex(ValueError,'Merged bandlimited mode requires'):
   convert_merged_song(a,40,[(i,) for i in range(8)],bandlimited_pcm=True,finite_support=True,merged_bandlimited_support=True)

