"""Only accepted KINCHO enables upward-pitch preparation in filtered scanning."""
import copy,csv,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from test_nds_antialias_audit import fixture
from audit_nds_compatibility import scan_antialias_variant,summarize,write_reports
from nds_track_merge import SF3_KINCHO_GROUPS


def run(family='ssr3',index=30,capacity=8,ids=tuple(range(8))+(14,15),fit=False,active=False,termination='loop',error=None,pack_error=None,sha='aa'):
 row,c,a,m=fixture();row.update(id=f'{family}:{index}',family=family,index=index)
 row['features'].update(track_count=10,executed_note_events_in_trace=10,noninstant_attack_definitions=int(fit),nonzero_mod_depth_executed=active)
 c['track_count']=8;c['bandlimited_pcm'].update(upward_bound_method='shared maximum',upward_pitch_preparation=True)
 c['samples'][0].update(source_key=60);c['samples'][0]['resampling'].update(preparation_key=67,nominal_cutoff_at_bound_fraction_of_mixer_nyquist=.9)
 m['output_fingerprint']['sha256']=sha;before=copy.deepcopy(row)
 def convert(*args,**kw):
  if error:raise error
  if args[4]:raise ValueError('Song gain exceeds headroom')
  return b'blob',{'samples':[{}]},c
 with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':i,'termination':termination} for i in ids]),patch('audit_nds_compatibility.convert_merged_song',side_effect=convert) as converter,patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m),side_effect=pack_error) as packer:
  r=scan_antialias_variant(a,row,b'',b'',b'','ssr3b',capacity)
 assert row==before
 return row,r,converter,packer


class KinchoUpwardAntialiasAuditTests(unittest.TestCase):
 def test_pinned_groups_and_both_explicit_filter_flags(self):
  _,r,c,_=run();self.assertEqual(r['status'],'packed');self.assertEqual(r['route'],'known_sf3_kincho_upward_antialias')
  self.assertEqual(c.call_args.args[2],SF3_KINCHO_GROUPS)
  self.assertEqual(c.call_args.kwargs,{'finite_support':False,'bandlimited_pcm':True,'envelope_support':False,'finite_release_support':False,'merged_bandlimited_support':True,'bandlimited_upward_support':True})
  self.assertTrue(r['manual_matches_packed_variant']);self.assertFalse(r['runtime_tested_by_audit'])
 def test_identity_structure_and_approximations_remain_bounded(self):
  for kw in ({'family':'ssr2'},{'index':4},{'capacity':7},{'ids':range(14)},{'ids':range(12)},{'fit':True},{'active':True},{'termination':'end'}):
   with self.subTest(kw=kw):
    _,r,c,p=run(**kw);self.assertEqual(r['status'],'capacity_blocked');c.assert_not_called();p.assert_not_called()
 def test_converter_guards_and_model_failures_are_retained_without_fitting(self):
  for error,status in [(ValueError('Merged track volume must remain fixed'),'conversion_blocked'),(ValueError('Upward-bandlimited preparation key exceeds bounded one-octave/key range'),'conversion_blocked'),(ValueError('Non-instant DS attack requires envelope fitting'),'conversion_blocked'),(AssertionError('Merged note/gate/timing model differs'),'converter_model_blocked')]:
   with self.subTest(error=error):
    _,r,c,p=run(error=error);self.assertEqual(r['status'],status);self.assertEqual(len(r['attempts']),1);self.assertEqual(r['attempts'][0]['error']['message'],str(error));p.assert_not_called()
 def test_headroom_and_packing_cannot_inherit_manual_pass(self):
  _,r,_,_=run(sha='different');self.assertEqual([a['gain_db'] for a in r['attempts']],[3.5,0]);self.assertFalse(r['manual_matches_packed_variant'])
  _,r,_,_=run(pack_error=AssertionError('BPS differs'));self.assertEqual(r['status'],'packing_blocked');self.assertFalse(r['manual_matches_packed_variant'])
 def test_conversion_bounds_and_original_observations_have_separate_scopes(self):
  _,r,_,_=run();self.assertEqual(r['upward_pitch_preparation']['shift_semitone_counts'],{'7':1});self.assertEqual(r['upward_pitch_preparation']['maximum_nominal_cutoff_fraction_of_mixer_nyquist'],.9)
  s=r['known_merged_antialias']['standalone_observations'];self.assertEqual((s['observed_note_calls'],s['observed_rejections'],s['held_or_starting_preemptions'],s['release_flagged_reuses_with_nonzero_envelope']),(1194,0,0,477))
  self.assertEqual((s['plain_baseline_release_reuses'],s['slot_choices_different_from_plain']),(476,175))
  self.assertEqual((s['prepared_pcm8_clamped_values'],s['prepared_pcm8_bytes']),(10592,1086559));self.assertEqual(s['zero_velocity_native_calls'],0);self.assertFalse(s['batch_native_remeasured']);self.assertEqual(s['plain_baseline_observation'],'sf3-kincho-plain-native-baseline-v1')
 def test_reports_expose_upward_preparation_and_exclusive_counts(self):
  row,r,_,_=run();row['antialias']=r;s=summarize([row]);self.assertEqual(s['packed'],1);self.assertEqual(s['antialias']['packed_variants'],1);self.assertEqual(s['antialias']['packed_known_merged_variants'],1);self.assertEqual(s['antialias']['packed_upward_preparation_variants'],1)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);write_reports(p,{'rows':[row],'summary':s})
   with (p/'report.csv').open() as f:item=next(csv.DictReader(f))
   self.assertEqual(json.loads(item['antialias_upward_pitch_preparation']),r['upward_pitch_preparation'])
   self.assertIn("k==='upward'",(p/'index.html').read_text())
