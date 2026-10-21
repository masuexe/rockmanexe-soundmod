import csv,json,tempfile,unittest
from pathlib import Path
from test_nds_live_min_audit import run
from audit_nds_compatibility import summarize,write_reports
FAILURE='Native pitch LFO experiment requires a fixed tempo'
ROUTE='variable_late_fitted_pitch_lfo_approximation'
POLICY={'source_tempos':[80,120],'conductor_modulation':False,'max_source_tempos':8}

def convert(*args,**options):
 if not options.get('variable_late_fitted_support'):raise ValueError(FAILURE)
 return b'blob',{'samples':[]},{'track_count':2,'envelope_approximation':{'attack_fits':[]},'native_pitch_lfo':{'variable_tempo_approximation':POLICY,'variable_late_fitted_extension':{'enabled':True,'initializations':[]}}}

class VariableLateFittedAuditTests(unittest.TestCase):
 def test_explicit_fixed_tempo_failure_enables_separate_zero_delay_route(self):
  row,converter,_=run(convert,fit=True)
  self.assertEqual(row['route'],ROUTE)
  self.assertEqual(row['status'],'packed_variable_late_fitted_lfo_approximation')
  self.assertTrue(row['manual_matches_packed_variant'])
  self.assertFalse(row['runtime_tested_by_audit'])
  self.assertTrue(row['attempts'][-1]['native_pitch_lfo_variable_tempo'])
  options=converter.call_args.kwargs
  self.assertTrue(options['native_pitch_lfo'] and options['native_pitch_lfo_variable_tempo'])
  self.assertTrue(options['envelope_support'] and options['variable_late_fitted_support'])
  self.assertFalse(options['native_pitch_lfo_delay'])
  for flag in ('native_pitch_lfo_min_depth','mixed_loop_support','native_pitch_lfo_live_depth','native_pitch_lfo_late_depth'):
   self.assertNotIn(flag,options)

 def test_error_types_and_unrelated_failures_do_not_retry(self):
  for error in (AssertionError(FAILURE),ValueError('tempo initialization'),ValueError('DS LFO cannot be represented by the bounded native approximation')):
   with self.subTest(error=repr(error)):
    row,_,_=run(lambda *a,**k:(_ for _ in ()).throw(error),fit=True)
    self.assertFalse(any(a['route']==ROUTE for a in row['attempts']))

 def test_nonfitted_and_nonloop_scores_are_excluded(self):
  for fit,tracks in ((False,None),(True,[{'track':0,'termination':'end'}]),
                     (True,[{'track':0,'termination':'loop'},{'track':1,'termination':'end'}])):
   with self.subTest(fit=fit,tracks=tracks):
    row,_,_=run(convert,fit=fit,tracks=tracks)
    self.assertFalse(any(a['route']==ROUTE for a in row['attempts']))

 def test_headroom_retry_and_packing_failures_stay_visible(self):
  def gain(*a,**k):
   if k.get('variable_late_fitted_support') and a[4]:raise ValueError('Song gain exceeds MPlay VOL headroom')
   return convert(*a,**k)
  row,_,_=run(gain,fit=True)
  self.assertEqual(row['gain_db'],0)
  self.assertEqual([a['gain_db'] for a in row['attempts'] if a['route']==ROUTE],[3.5,0])
  row,_,_=run(convert,fit=True,pack_error=AssertionError('BPS differs'))
  self.assertEqual(row['status'],'packing_blocked')
  self.assertFalse(row['manual_matches_packed_variant'])

 def test_existing_success_has_precedence(self):
  row,converter,_=run(lambda *a,**k:(b'blob',{'samples':[]},{'track_count':2}))
  converter.assert_called_once();self.assertEqual(row['route'],'singleton_bend_long')

 def test_summary_csv_and_html_retain_separate_policy(self):
  row,_,_=run(convert,fit=True);summary=summarize([row])
  self.assertEqual(summary['packed'],1)
  self.assertEqual(summary['packed_mixed_variants'],0)
  self.assertEqual(summary['packed_minimum_depth_lfo_variants'],0)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);write_reports(p,{'rows':[row],'summary':summary})
   with (p/'report.csv').open() as stream:item=next(csv.DictReader(stream))
   self.assertEqual(json.loads(item['variable_tempo_approximation']),POLICY)
   self.assertTrue(json.loads(item['variable_late_fitted_extension'])['enabled'])
   line=next(l for l in (p/'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
   counts=[int(x.strip()) for x in line.split('|')[2:-1]]
   self.assertEqual(sum(counts[2:-1]),1);self.assertEqual(counts[-1],0)
   self.assertIn("k==='variable_fitted'",(p/'index.html').read_text())

if __name__=='__main__':unittest.main()
