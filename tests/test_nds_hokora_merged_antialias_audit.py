"""Only the pinned accepted HOKORA merged-filter variant bypasses capacity."""
import copy,csv,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from test_nds_antialias_audit import fixture
from audit_nds_compatibility import scan_antialias_variant,summarize,write_reports
from nds_track_merge import SF2_HOKORA_GROUPS


def run(family='ssr2',index=20,capacity=8,ids=tuple(range(9)),fit=False,active=False,termination='loop',error=None,pack_error=None,sha='aa'):
 row,c,a,m=fixture();row.update(id=f'{family}:{index}',family=family,index=index)
 row['features'].update(track_count=9,executed_note_events_in_trace=9,noninstant_attack_definitions=int(fit),nonzero_mod_depth_executed=active)
 c['track_count']=8;m['output_fingerprint']['sha256']=sha;before=copy.deepcopy(row)
 def convert(*args,**kw):
  if error:raise error
  if args[4]:raise ValueError('Song gain exceeds headroom')
  return b'blob',{'samples':[{}]},c
 with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':i,'termination':termination} for i in ids]),patch('audit_nds_compatibility.convert_merged_song',side_effect=convert) as converter,patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m),side_effect=pack_error) as packer:
  result=scan_antialias_variant(a,row,b'',b'',b'','ssr2d',capacity)
 assert row==before
 return row,result,converter,packer


class HokoraMergedAntialiasAuditTests(unittest.TestCase):
 def test_pinned_groups_and_explicit_flags_are_used(self):
  _,r,c,_=run();self.assertEqual(r['status'],'packed');self.assertEqual(r['route'],'known_sf2_hokora_merged_antialias')
  self.assertEqual(c.call_args.args[2],SF2_HOKORA_GROUPS)
  self.assertEqual(c.call_args.kwargs,{'finite_support':False,'bandlimited_pcm':True,'envelope_support':False,'finite_release_support':False,'merged_bandlimited_support':True})
  self.assertFalse(r['runtime_tested_by_audit']);self.assertTrue(r['manual_matches_packed_variant'])
 def test_other_identity_structure_and_approximations_stay_blocked(self):
  for kw in ({'family':'ssr3'},{'index':26},{'capacity':7},{'ids':range(12)},{'ids':(0,1,2)},{'fit':True},{'active':True},{'termination':'end'}):
   with self.subTest(kw=kw):
    _,r,c,p=run(**kw);self.assertEqual(r['status'],'capacity_blocked');c.assert_not_called();p.assert_not_called()
 def test_model_and_conversion_failures_are_preserved_without_fitted_retry(self):
  for error,status in [(ValueError('Merged track volume must remain fixed'),'conversion_blocked'),(ValueError('Non-instant DS attack requires envelope fitting'),'conversion_blocked'),(AssertionError('Merged note/gate/timing model differs'),'converter_model_blocked')]:
   with self.subTest(error=error):
    _,r,c,p=run(error=error);self.assertEqual(r['status'],status);self.assertEqual(len(r['attempts']),1);self.assertEqual(r['attempts'][0]['error']['message'],str(error));p.assert_not_called()
 def test_gain_retry_and_packing_require_exact_manual_bytes(self):
  _,r,_,_=run(sha='different');self.assertEqual([a['gain_db'] for a in r['attempts']],[3.5,0]);self.assertFalse(r['manual_matches_packed_variant'])
  _,r,_,_=run(pack_error=AssertionError('BPS differs'));self.assertEqual(r['status'],'packing_blocked');self.assertFalse(r['manual_matches_packed_variant'])
 def test_limits_are_attributed_to_standalone_not_remeasured(self):
  _,r,_,_=run();m=r['known_merged_antialias'];self.assertEqual(m['track_groups'],[list(g) for g in SF2_HOKORA_GROUPS]);s=m['standalone_observations']
  self.assertEqual((s['observed_note_calls'],s['observed_rejections'],s['held_or_starting_preemptions'],s['release_flagged_reuses_with_nonzero_envelope']),(1555,0,0,384))
  self.assertEqual((s['prepared_pcm8_clamped_values'],s['prepared_pcm8_bytes']),(1197,748395));self.assertEqual(len(s['rom_sha256']),64);self.assertFalse(s['batch_native_remeasured']);self.assertEqual((s['plain_baseline_release_reuses'],s['slot_choices_different_from_plain']),(385,354));self.assertEqual(s['plain_baseline_observation'],'sf2-hokora-plain-native-baseline-v1');self.assertNotIn('upward_pitch_preparation',r)
 def test_reports_keep_primary_and_filtered_accounting_separate(self):
  row,r,_,_=run();row['antialias']=r;s=summarize([row]);self.assertEqual(s['packed'],1);self.assertEqual(s['antialias']['packed_variants'],1);self.assertEqual(s['antialias']['packed_known_merged_variants'],1)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);write_reports(p,{'rows':[row],'summary':s})
   with (p/'report.csv').open() as f:item=next(csv.DictReader(f))
   self.assertEqual(json.loads(item['antialias_known_merged']),r['known_merged_antialias'])
   self.assertIn("k==='merged'",(p/'index.html').read_text())
