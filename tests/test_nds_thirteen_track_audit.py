import csv,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from audit_nds_compatibility import scan_sequence,summarize,write_reports
from nds_track_merge import SF3_CHANGE_GROUPS


def run(family='ssr3',index=47,capacity=8,ids=tuple(range(10))+(13,14,15),fit=False,active=False,termination='loop',convert_error=None,pack_error=None):
 tracks=[{'track':i,'termination':termination} for i in ids]
 features={'executed_note_events_in_trace':13,'track_count':len(tracks),'nonzero_mod_depth_executed':active,'active_delayed_modulation_executed':False,'positive_mod_depth_changes':[],'noninstant_attack_definitions':int(fit)}
 def convert(*args,**kw):
  if convert_error:raise convert_error
  if args[4]:raise ValueError('Song gain exceeds MPlay VOL headroom')
  return b'blob',{'samples':[]},{'track_count':8}
 with patch('audit_nds_compatibility.trace_sequence',return_value=tracks),patch('audit_nds_compatibility.features',return_value=features),patch('audit_nds_compatibility.convert_merged_song',side_effect=convert) as converter,patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',{'appended_bytes':42,'output_fingerprint':{'sha256':'accepted'}}),side_effect=pack_error) as packer:
  row=scan_sequence(SimpleNamespace(sequence=lambda i:(b'',{})),{'index':index,'name':'CHANGE','present':True},family,b'',b'',b'','ssr3b',capacity,manual_records=[{'family':'ssr3','sequence_index':47,'output_sha256':'accepted'}])
 return row,converter,packer

class ThirteenTrackAuditTests(unittest.TestCase):
 def test_only_known_route_uses_exact_accepted_groups_and_plain_flags(self):
  row,converter,_=run();self.assertEqual(row['status'],'packed_known_thirteen_track_merge')
  self.assertEqual(converter.call_args.args[2],SF3_CHANGE_GROUPS)
  self.assertFalse(any(converter.call_args.kwargs.values()))
  self.assertTrue(row['manual_matches_packed_variant']);self.assertFalse(row['runtime_tested_by_audit'])
  self.assertEqual(row['known_thirteen_track_merge']['track_groups'],[list(g) for g in SF3_CHANGE_GROUPS])
  limit=row['known_thirteen_track_merge']['standalone_native_voice_budget_limit']
  self.assertEqual((limit['observed_note_calls'],limit['observed_rejections']),(1339,0))
  self.assertFalse(limit['batch_remeasured'])
  self.assertEqual(limit['held_or_starting_voice_preemptions'],4)
  self.assertEqual(limit['release_flagged_channel_reuses_with_nonzero_envelope'],183)
  self.assertEqual(len(limit['rom_sha256']),64)
  self.assertEqual(limit['held_preemption_clocks'],[352,360,372,376])
  self.assertTrue(row['known_thirteen_track_merge']['additional_velocity_ratio_quantization'])
 def test_identity_structure_and_approximation_exclusions_keep_capacity_block(self):
  for kw in ({'family':'ssr2'},{'index':19},{'capacity':7},{'ids':range(1,10)},{'ids':range(13)},{'fit':True},{'active':True},{'termination':'end'}):
   with self.subTest(kw=kw):
    row,converter,packer=run(**kw);self.assertEqual(row['status'],'capacity_blocked');converter.assert_not_called();packer.assert_not_called()
 def test_original_converter_guards_are_not_waived(self):
  error=ValueError('Merged track volume must remain fixed');row,converter,packer=run(convert_error=error)
  self.assertEqual(row['status'],'conversion_blocked');self.assertEqual(row['attempts'][0]['error']['message'],str(error));packer.assert_not_called()
 def test_headroom_retry_is_per_route_and_manual_match_requires_packing(self):
  row,_,_=run();self.assertEqual([a['gain_db'] for a in row['attempts']],[3.5,0]);self.assertEqual(row['gain_db'],0)
  row,_,_=run(pack_error=AssertionError('BPS differs'));self.assertEqual(row['status'],'packing_blocked');self.assertFalse(row['manual_matches_packed_variant'])
 def test_failure_in_model_remains_visible(self):
  row,_,_=run(convert_error=AssertionError('Merged note/gate/timing model differs'))
  self.assertEqual(row['status'],'converter_model_blocked');self.assertTrue(row['attempts'][0]['error']['model_assertion'])
 def test_report_policy_and_exclusive_summary_count(self):
  row,_,_=run();summary=summarize([row]);self.assertEqual(summary['packed'],1)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);write_reports(p,{'rows':[row],'summary':summary})
   with (p/'report.csv').open() as stream:item=next(csv.DictReader(stream))
   self.assertEqual(json.loads(item['known_thirteen_track_merge']),row['known_thirteen_track_merge'])
   line=next(l for l in (p/'summary.md').read_text().splitlines() if l.startswith('| ssr3 |'))
   counts=[int(x.strip()) for x in line.split('|')[2:-1]];self.assertEqual(sum(counts[2:-1]),1);self.assertEqual(counts[-1],0)
   self.assertIn("k==='thirteen'",(p/'index.html').read_text())
