import csv,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_nds_compatibility import scan_sequence,summarize,write_reports
REP='DS LFO cannot be represented by the bounded native approximation'
NEW={'live_depth_minimum_pitch_lfo_approximation','envelope_live_depth_minimum_pitch_lfo_approximation'}
POLICY={'all_phase_pitch_difference_bound_cents':10,'isolated_one_second_rms_limit_cents':5}


def run(convert,fit=False,tracks=None,pack_error=None):
 archive=SimpleNamespace(sequence=lambda i:(b'',{}))
 feature={'executed_note_events_in_trace':2,'track_count':2,'nonzero_mod_depth_executed':True,
          'active_delayed_modulation_executed':True,'positive_mod_depth_changes':[{}],
          'noninstant_attack_definitions':int(fit)}
 manifest={'appended_bytes':20,'output_fingerprint':{'sha256':'accepted'}}
 with patch('audit_nds_compatibility.trace_sequence',return_value=tracks or [{'track':0,'termination':'loop'},{'track':1,'termination':'loop'}]), \
      patch('audit_nds_compatibility.features',return_value=feature), \
      patch('audit_nds_compatibility.convert_song',side_effect=ValueError('unsupported')), \
      patch('audit_nds_compatibility.convert_merged_song',side_effect=convert) as converter, \
      patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',manifest),side_effect=pack_error) as packer:
  row=scan_sequence(archive,{'index':32,'name':'LOSE','present':True},'ssr1',b'',b'',b'','ssr1d',8,
   manual_records=[{'family':'ssr1','sequence_index':32,'output_sha256':'accepted'}])
 return row,converter,packer


def convert_for(fit=False,gain=False):
 def convert(*args,**kw):
  if not kw.get('native_pitch_lfo_live_depth'):raise ValueError('unsupported')
  if not kw.get('native_pitch_lfo_min_depth'):raise ValueError(REP)
  if kw['envelope_support']!=fit:raise ValueError('Non-instant DS attack requires envelope fitting')
  if gain and args[4]:raise ValueError('Song gain exceeds MPlay VOL headroom')
  c={'track_count':2,'native_pitch_lfo':{'minimum_depth_quantization':POLICY}}
  if fit:c['envelope_approximation']={'attack_fits':[]}
  return b'blob',{'samples':[]},c
 return convert


class LiveMinimumAuditTests(unittest.TestCase):
 def test_explicit_live_failure_retries_plain_and_fitted_independently(self):
  for fit in (False,True):
   with self.subTest(fit=fit):
    row,converter,_=run(convert_for(fit),fit)
    self.assertEqual(row['status'],'packed_envelope_live_depth_minimum_lfo_approximation' if fit else 'packed_live_depth_minimum_lfo_approximation')
    self.assertEqual(row['approximations']['envelope'],fit)
    self.assertTrue(row['approximations']['live_depth'])
    self.assertTrue(row['manual_matches_packed_variant'])
    self.assertFalse(row['runtime_tested_by_audit'])
    self.assertTrue(any(a.get('error',{}).get('message')==REP for a in row['attempts']))
    last=converter.call_args.kwargs
    self.assertTrue(last['native_pitch_lfo_min_depth'] and last['native_pitch_lfo_delay'])
    self.assertNotIn('mixed_loop_support',last)
    self.assertEqual(row['native_pitch_lfo']['minimum_depth_quantization'],POLICY)

 def test_models_unrelated_errors_and_mixed_tracks_do_not_trigger_live_minimum(self):
  for error,tracks in ((AssertionError(REP),None),(ValueError('fixed tempo'),None),
                       (ValueError(REP),[{'track':0,'termination':'loop'},{'track':1,'termination':'end'}])):
   with self.subTest(error=repr(error),tracks=tracks):
    row,_,packer=run(lambda *a,**k:(_ for _ in ()).throw(error),tracks=tracks)
    self.assertFalse(any(a['route'] in NEW for a in row['attempts']))
    packer.assert_not_called()

 def test_new_mode_keeps_its_own_headroom_retry_and_visible_packing_failure(self):
  row,_,_=run(convert_for(gain=True))
  self.assertEqual(row['gain_db'],0)
  self.assertEqual([a['gain_db'] for a in row['attempts'] if a['route'] in NEW],[3.5,0])
  row,_,_=run(convert_for(),pack_error=AssertionError('BPS differs'))
  self.assertEqual(row['status'],'packing_blocked')
  self.assertEqual(row['attempts'][-1]['packing_error']['message'],'BPS differs')
  self.assertFalse(row['manual_matches_packed_variant'])

 def test_existing_success_remains_first_choice(self):
  row,converter,_=run(lambda *a,**k:(b'blob',{'samples':[]},{'track_count':2}))
  self.assertEqual(row['route'],'singleton_bend_long')
  converter.assert_called_once()
  self.assertNotIn('native_pitch_lfo_min_depth',converter.call_args.kwargs)

 def test_standalone_minimum_report_counts_do_not_inflate_mixed_category(self):
  rows=[run(convert_for(fit),fit)[0] for fit in (False,True)]
  s=summarize(rows)
  self.assertEqual((s['packed'],s['packed_minimum_depth_lfo_variants'],s['packed_mixed_variants']),(2,2,0))
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);write_reports(p,{'rows':rows,'summary':s})
   with (p/'report.csv').open() as stream:items=list(csv.DictReader(stream))
   self.assertTrue(all(i['minimum_depth_lfo_quantization']=='True' and i['mixed_loop_song']=='False' for i in items))
   line=next(l for l in (p/'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
   counts=[int(c.strip()) for c in line.split('|')[2:-1]]
   self.assertEqual(sum(counts[2:-1]),2);self.assertEqual(counts[-1],0)
   self.assertIn('实时深度两列包含', (p/'summary.md').read_text())


if __name__=='__main__':unittest.main()
