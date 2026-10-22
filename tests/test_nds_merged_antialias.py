"""Explicit merged filtering preserves schedules and source-key tone identity."""
import hashlib,sys,unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path('scripts').resolve())]
from build_nds_experiment import build_experiment,SOURCE_ARCHIVES
from nds_music import SoundArchive,nds_sdat,trace_sequence
from nds_track_merge import convert_merged_song,SF3_BOSSMAE_GROUPS,SF3_STUDIO_GROUPS
from scan_audio import apply_bps
SOURCE=Path('/home/harp/projects/nds/roms/ssr3b.nds');BASE=Path('../roms/exe6.gba')
@unittest.skipUnless(SOURCE.exists() and BASE.exists(),'local verified game inputs unavailable')
class MergedAntialiasTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=SOURCE.read_bytes();cls.base=BASE.read_bytes()
  cls.a=SoundArchive(nds_sdat(cls.source,SOURCE_ARCHIVES['ssr3']['file_id']))
 def test_explicit_route_preserves_every_mapping_and_compiled_schedule(self):
  output,patch,m,c,dep,blob,*_=build_experiment(self.source,self.base,song='sf3-bossmae-merged-antialias',events=('1','21','scene:communication'))
  _,_,plain=convert_merged_song(self.a,27,SF3_BOSSMAE_GROUPS,song_gain_db=3.5)
  for field in ('note_mapping','note_timing_validation','track_groups','long_note_aliases','long_note_loop_carries','tempo_mapping','priority_mapping','song_priority'):
   self.assertEqual(c[field],plain[field],field)
  self.assertEqual(c['source_track_count'],12);self.assertEqual(c['track_count'],8)
  self.assertEqual(len(c['samples']),81);self.assertEqual(len(c['note_mapping']),974)
  self.assertTrue(c['bandlimited_pcm']['merged_tracks'])
  self.assertFalse(c['bandlimited_pcm']['runtime_mixer_changed'])
  self.assertLess(sum(s['pcm8_bytes'] for s in c['samples']),4_000_000)
  self.assertEqual(len({(s['archive_id'],s['wave_id'],s['root_key'],s['source_key']) for s in c['samples']}),81)
  self.assertTrue(all(abs(s['resampling']['pitch_error_cents'])<.001 for s in c['samples']))
  self.assertEqual(apply_bps(self.base,patch)[0],output)
  expected=bytearray(self.base)
  for start,end in m['declared_prefix_ranges']:expected[start:end]=output[start:end]
  self.assertEqual(output[:len(self.base)],expected)
 def test_default_and_mixed_mode_opt_in_guards_remain(self):
  with self.assertRaisesRegex(ValueError,'singleton'):
   convert_merged_song(self.a,27,SF3_BOSSMAE_GROUPS,bandlimited_pcm=True)
  for kw in ({},{'bandlimited_pcm':True,'envelope_support':True},{'bandlimited_pcm':True,'native_pitch_lfo':True},{'bandlimited_pcm':True,'finite_support':True},{'bandlimited_pcm':True,'mixed_loop_support':True}):
   with self.subTest(kw=kw),self.assertRaisesRegex(ValueError,'Merged bandlimited mode|Mixed experiment excludes'):
    convert_merged_song(self.a,27,SF3_BOSSMAE_GROUPS,merged_bandlimited_support=True,**kw)
  with self.assertRaisesRegex(ValueError,'Merged bandlimited mode'):
   convert_merged_song(self.a,27,[(i,) for g in SF3_BOSSMAE_GROUPS for i in g],track_capacity=12,bandlimited_pcm=True,merged_bandlimited_support=True)
 def test_pitch_and_existing_shared_control_guards_are_not_waived(self):
  with self.assertRaisesRegex(ValueError,'upward bend'):
   convert_merged_song(self.a,4,SF3_STUDIO_GROUPS,bandlimited_pcm=True,merged_bandlimited_support=True)
  changed=deepcopy(trace_sequence(self.a.sequence(27)[0],analysis_only=True))
  source=next(t for t in changed if t['track']==3)
  for action in source['actions']:
   if action['ticks']>=96 and 'state_after' in action:
    action['state_after']={**action['state_after'],'volume':99}
  with patch('nds_track_merge.trace_sequence',return_value=changed),self.assertRaisesRegex(ValueError,'volume must remain fixed'):
   convert_merged_song(self.a,27,SF3_BOSSMAE_GROUPS,bandlimited_pcm=True,merged_bandlimited_support=True)
 def test_accepted_plain_rom_is_byte_identical(self):
  output,patch,*_=build_experiment(self.source,self.base,song='sf3-bossmae-twelve-track',events=('1','21','scene:communication'))
  self.assertEqual(hashlib.sha256(output).hexdigest(),'1ada1a4ed7c64d5279021b69e6ceacc49f14b78a6ee012fe17de1870bdacc935')
  self.assertEqual(hashlib.sha256(patch).hexdigest(),'a5c52e2dc1a2bf7abf4d4bdd15d94b136b1e9d83ce6d42787a4fdc59a123bdf6')
