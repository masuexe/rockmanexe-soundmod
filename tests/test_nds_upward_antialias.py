"""Conservative pitch-ceiling preparation without changing played keys or bends."""
import math,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path('scripts').resolve()),str(Path('tests').resolve())]
from nds_track_merge import convert_merged_song,SF3_STUDIO_GROUPS
from nds_music import SoundArchive,nds_sdat
from build_nds_experiment import build_experiment,SOURCE_ARCHIVES
from scan_audio import apply_bps
import test_nds_music as fixtures


def archive(raw):
 a=fixtures.SampleConversionTests.archive_for(raw)
 a.wave=lambda *_:([round(12000*math.sin(2*math.pi*i/512)) for i in range(512)],{'effective_rate_hz':22050,'looped':True,'loop_start_samples':0,'sample_count':512})
 return a


def score(bend=66,key=60,extra=b''):
 intro=b'\xC7\x00\xE1\x78\x00\x81\x02\xC5\x0C'+bytes([0xC4,bend])+extra
 return intro+bytes([key,100,12])+b'\x80\x0C\x94'+len(intro).to_bytes(3,'little')


class UpwardAntialiasTests(unittest.TestCase):
 def test_ceiling_changes_preparation_but_preserves_analytic_sine_pitch(self):
  a=archive(score());_,_,c=convert_merged_song(a,0,[(0,)],bandlimited_pcm=True,bandlimited_upward_support=True)
  s=c['samples'][0];r=s['resampling'];self.assertEqual((s['source_key'],r['preparation_key'],r['positive_pitch_bound_units']),(60,67,396))
  self.assertTrue(all(n['source_key']==n['gba_key']==60 for n in c['note_mapping']))
  actual=(s['gba_frequency_raw']/1024)/r['output_loop_period'];expected=22050/512
  self.assertLess(abs(1200*math.log2(actual/expected)),.001)
  self.assertLessEqual(r['nominal_cutoff_at_bound_fraction_of_mixer_nyquist'],1)
  self.assertEqual(c['bandlimited_pcm']['max_preparation_shift_semitones'],12)
 def test_shared_wave_key_uses_maximum_bound_from_every_source(self):
  header=b'\xFE\x03\x00\x93\x01'+bytes(3)
  def program(start,bend,tempo=b''):
   intro=b'\xC7\x00\x81\x02'+tempo+b'\xC5\x0C'+bytes([0xC4,bend])
   return intro+bytes([60,100,12])+b'\x80\x0C\x94'+(start+len(intro)).to_bytes(3,'little')
  first=program(len(header),0,b'\xE1\x78\x00');second=len(header)+len(first)
  a=archive(header[:5]+second.to_bytes(3,'little')+first+program(second,66))
  _,_,c=convert_merged_song(a,0,[(0,),(1,)],bandlimited_pcm=True,bandlimited_upward_support=True)
  self.assertEqual(len(c['samples']),1);self.assertEqual(c['samples'][0]['resampling']['preparation_key'],67)
  self.assertEqual(c['samples'][0]['resampling']['positive_pitch_bound_units'],396)
  with self.assertRaisesRegex(ValueError,'incompatible pitch'):
   convert_merged_song(a,0,[(0,1)],bandlimited_pcm=True,merged_bandlimited_support=True,bandlimited_upward_support=True)
 def test_explicit_mode_and_other_effect_exclusions_remain(self):
  a=archive(score())
  with self.assertRaisesRegex(ValueError,'upward bend'):
   convert_merged_song(a,0,[(0,)],bandlimited_pcm=True)
  for kw in ({},{'bandlimited_pcm':True,'native_pitch_lfo':True},{'bandlimited_pcm':True,'envelope_support':True},{'bandlimited_pcm':True,'finite_support':True},{'bandlimited_pcm':True,'mixed_loop_support':True}):
   with self.subTest(kw=kw),self.assertRaisesRegex(ValueError,'Upward-bandlimited mode|Mixed experiment excludes'):
    convert_merged_song(a,0,[(0,)],bandlimited_upward_support=True,**kw)
  for extra in (b'\xC3\x01',b'\xCA\x01',b'\xCE\x01'):
   with self.subTest(extra=extra),self.assertRaisesRegex(ValueError,'transpose, modulation and portamento'):
    convert_merged_song(archive(score(extra=extra)),0,[(0,)],bandlimited_pcm=True,bandlimited_upward_support=True)
 def test_one_octave_and_preparation_key_limits_are_not_clamped(self):
  for raw in (score(key=127),score().replace(b'\xC5\x0C\xC4\x42',b'\xC5\x18\xC4\x7F')):
   with self.subTest(raw=raw),self.assertRaisesRegex(ValueError,'bounded one-octave/key range'):
    convert_merged_song(archive(raw),0,[(0,)],bandlimited_pcm=True,bandlimited_upward_support=True)
 @unittest.skipUnless(Path('/home/harp/projects/nds/roms/ssr3b.nds').exists() and Path('../roms/exe6.gba').exists(),'local verified inputs unavailable')
 def test_studio_keeps_all_mappings_aliases_and_original_prefix(self):
  source=Path('/home/harp/projects/nds/roms/ssr3b.nds').read_bytes();base=Path('../roms/exe6.gba').read_bytes()
  out,bps,m,c,*_=build_experiment(source,base,song='sf3-studio-upward-antialias',events=('1','21','scene:communication'))
  a=SoundArchive(nds_sdat(source,SOURCE_ARCHIVES['ssr3']['file_id']));_,_,plain=convert_merged_song(a,4,SF3_STUDIO_GROUPS,song_gain_db=3.5)
  for f in ('note_mapping','track_groups','note_timing_validation','long_note_aliases','long_note_loop_carries','tempo_mapping','voice_context_splits'):
   self.assertEqual(c[f],plain[f],f)
  self.assertEqual((len(c['note_mapping']),len(c['samples'])),(3431,131));self.assertEqual(sum(n['gba_velocity']==0 for n in c['note_mapping']),4)
  self.assertEqual({s['resampling']['positive_pitch_bound_units'] for s in c['samples']},{0,204,396})
  self.assertEqual(max(s['resampling']['preparation_key']-s['source_key'] for s in c['samples']),7)
  self.assertTrue(all(s['resampling']['nominal_cutoff_at_bound_fraction_of_mixer_nyquist']<=1 for s in c['samples']))
  self.assertEqual(apply_bps(base,bps)[0],out);prefix=bytearray(base)
  for start,end in m['declared_prefix_ranges']:prefix[start:end]=out[start:end]
  self.assertEqual(out[:len(base)],prefix)
