"""Accepted CHANGE grouping retains aliases, dynamics and mappings under filtering."""
import sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path('scripts').resolve())]
from build_nds_experiment import build_experiment,SOURCE_ARCHIVES
from nds_music import SoundArchive,nds_sdat
from nds_track_merge import convert_merged_song,SF3_CHANGE_GROUPS
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds');OTHER=SOURCE.with_name('ssr2d.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and OTHER.exists() and BASE.exists(),'local verified game inputs unavailable')
class Sf3ChangeUpwardAntialiasTests(unittest.TestCase):
 def test_filtering_preserves_all_mappings_aliases_controls_and_prefix(self):
  base=BASE.read_bytes();out,bps,m,c,dep,blob,_,sdat=build_experiment(SOURCE.read_bytes(),base,song='sf3-change-upward-antialias',events=('1','21','scene:communication'))
  _,_,plain=convert_merged_song(SoundArchive(sdat),47,SF3_CHANGE_GROUPS,song_gain_db=3.5)
  for field in ('note_mapping','tracks','track_groups','note_timing_validation','long_note_aliases','long_note_loop_carries','tempo_mapping','voice_context_splits','priority_mapping','song_priority'):
   self.assertEqual(c[field],plain[field],field)
  self.assertEqual((c['source_track_count'],c['track_count'],len(c['note_mapping']),len(dep['samples'])),(13,8,855,78))
  self.assertEqual(len(c['long_note_aliases']),1);self.assertTrue(all(n['gba_velocity']>0 for n in c['note_mapping']))
  self.assertTrue(c['bandlimited_pcm']['upward_pitch_preparation']);self.assertTrue(c['bandlimited_pcm']['merged_tracks']);self.assertFalse(c['bandlimited_pcm']['runtime_mixer_changed'])
  self.assertLess(sum(s['pcm8_bytes'] for s in c['samples']),4_000_000)
  self.assertEqual(max(s['resampling']['preparation_key']-s['source_key'] for s in c['samples']),12)
  self.assertTrue(all(s['resampling']['nominal_cutoff_at_bound_fraction_of_mixer_nyquist']<=1 for s in c['samples']))
  intro=[v for v in c['note_mapping'] if v['source_track']==9]
  self.assertEqual(len(intro),6)
  source=next(t for t in c['tracks'] if t['track']==9)
  self.assertFalse(any(v['name']=='note' for v in source['actions'][source['loop_action']:]))
  self.assertEqual(apply_bps(base,bps)[0],out);expected=bytearray(base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=out[start:end]
  self.assertEqual(out[:len(base)],expected);self.assertEqual({r['trigger_id'] for r in m['hook']['rules']},{1,21,65534})
 def test_source_family_and_unmerged_capacity_guards_remain(self):
  with self.assertRaisesRegex(ValueError,'selected source game'):
   build_experiment(OTHER.read_bytes(),BASE.read_bytes(),song='sf3-change-upward-antialias')
  a=SoundArchive(nds_sdat(SOURCE.read_bytes(),SOURCE_ARCHIVES['ssr3']['file_id']))
  with self.assertRaisesRegex(ValueError,'track capacity'):
   convert_merged_song(a,47,[(i,) for g in SF3_CHANGE_GROUPS for i in g],bandlimited_pcm=True,bandlimited_upward_support=True)
