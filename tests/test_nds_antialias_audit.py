"""Separate antialias audit variants and exact-version acceptance evidence."""
import copy,csv,json
from pathlib import Path
import sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_nds_compatibility import scan_antialias_variant,summarize,write_reports,manual_evidence
from scan_audio import fingerprint


def fixture():
    row={'id':'ssr1:1','family':'ssr1','index':1,'name':'BGM_TEST','status':'packed_standard',
         'features':{'track_count':1},'attempts':[],'appended_bytes':10,
         'manual_matches_packed_variant':False,
         'related_manual_records':[{'family':'ssr1','sequence_index':1,'output_sha256':'aa'}]}
    sample={'pcm8_bytes':8,'resampling':{'pcm8_clipped_samples':0,'source_pitched_rate_hz':21024}}
    conversion={'track_count':1,'samples':[sample],'bandlimited_pcm':{'mixing_rate_hz':10512}}
    archive=SimpleNamespace(sequence=lambda _: (b'',{}))
    manifest={'appended_bytes':20,'output_fingerprint':{'sha256':'aa'}}
    return row,conversion,archive,manifest


def scan(row,archive):
    return scan_antialias_variant(archive,row,b'',b'',b'','ssr1d',8)


class AntialiasAuditTests(unittest.TestCase):
    def test_variant_preserves_primary_and_matches_only_its_own_rom(self):
        for end in ('loop','end'):
            with self.subTest(end=end):
                row,c,archive,m=fixture();before=copy.deepcopy(row)
                with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':end}]), \
                     patch('audit_nds_compatibility.convert_merged_song',return_value=(b'blob',{'samples':[{}]},c)) as convert, \
                     patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m)):
                    result=scan(row,archive)
                self.assertEqual(row,before)
                self.assertEqual(result['status'],'packed')
                self.assertTrue(result['manual_matches_packed_variant'])
                self.assertFalse(result['runtime_tested_by_audit'])
                self.assertTrue(convert.call_args.kwargs['bandlimited_pcm'])
                self.assertEqual(convert.call_args.kwargs['finite_support'],end=='end')
                self.assertEqual(result['appended_bytes_delta_vs_primary'],10)

    def test_headroom_retry_can_succeed_at_zero_without_inheriting_manual_pass(self):
        row,c,archive,m=fixture();m['output_fingerprint']['sha256']='different'
        def convert(*args,**kwargs):
            if args[4]:raise ValueError('Song gain exceeds headroom')
            return b'blob',{'samples':[{}]},c
        with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'end'}]), \
             patch('audit_nds_compatibility.convert_merged_song',side_effect=convert), \
             patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m)):
            result=scan(row,archive)
        self.assertEqual([a['gain_db'] for a in result['attempts']],[3.5,0])
        self.assertTrue(result['gain_adjustment_required'])
        self.assertFalse(result['manual_matches_packed_variant'])
        self.assertIn('headroom',result['attempts'][0]['error']['message'])

    def test_looping_attack_requirement_gets_explicit_fitted_retry_and_records_both_modes(self):
        row,c,archive,m=fixture();before=copy.deepcopy(row)
        c['envelope_approximation']={'attack_fits':[{'ds_attack':100,'gba_attack':74}]}
        def convert(*args,**kwargs):
            if not kwargs['envelope_support']:
                raise ValueError('Non-instant DS attack requires envelope fitting')
            return b'blob',{'samples':[{}]},c
        with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'loop'}]), \
             patch('audit_nds_compatibility.convert_merged_song',side_effect=convert) as converter, \
             patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m)):
            result=scan(row,archive)
        self.assertEqual(row,before)
        self.assertEqual(result['route'],'looping_singleton_antialias_envelope')
        self.assertEqual([call.kwargs['envelope_support'] for call in converter.call_args_list],[False,True])
        self.assertEqual([a['envelope_approximation'] for a in result['attempts']],[False,True])
        self.assertFalse(result['attempts'][0]['conversion_passed'])
        self.assertTrue(result['attempts'][1]['packing_passed'])
        self.assertEqual(result['envelope_approximation'],c['envelope_approximation'])
        self.assertTrue(result['manual_matches_packed_variant'])
        self.assertFalse(result['runtime_tested_by_audit'])

    def test_finite_or_non_attack_failure_never_enables_fitted_retry(self):
        row,c,archive,m=fixture()
        for termination,error in [('end',ValueError('Non-instant DS attack requires envelope fitting')),
                                  ('loop',ValueError('Bandlimited PCM excludes modulation')),
                                  ('loop',AssertionError('Non-instant DS attack requires envelope fitting'))]:
            with self.subTest(termination=termination,error=error), \
                 patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':termination}]), \
                 patch('audit_nds_compatibility.convert_merged_song',side_effect=error) as converter:
                result=scan(row,archive)
            self.assertEqual(len(result['attempts']),1)
            self.assertFalse(converter.call_args.kwargs['envelope_support'])
            self.assertNotEqual(result['status'],'packed')

    def test_fitted_route_keeps_own_headroom_retry_without_inheriting_acceptance(self):
        row,c,archive,m=fixture();m['output_fingerprint']['sha256']='different'
        c['envelope_approximation']={'attack_fits':[{'ds_attack':100,'gba_attack':74}]}
        def convert(*args,**kwargs):
            if not kwargs['envelope_support']:raise ValueError('Non-instant DS attack requires envelope fitting')
            if args[4]:raise ValueError('Song gain exceeds headroom')
            return b'blob',{'samples':[{}]},c
        with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'loop'}]), \
             patch('audit_nds_compatibility.convert_merged_song',side_effect=convert), \
             patch('audit_nds_compatibility.pack_converted_experiment',return_value=(b'rom',b'bps',m)):
            result=scan(row,archive)
        self.assertEqual([(a['envelope_approximation'],a['gain_db']) for a in result['attempts']],
                         [(False,3.5),(True,3.5),(True,0)])
        self.assertTrue(result['gain_adjustment_required'])
        self.assertFalse(result['manual_matches_packed_variant'])

    def test_fitted_retry_keeps_fit_model_and_packing_failures_visible(self):
        row,c,archive,m=fixture();c['envelope_approximation']={'attack_fits':[]}
        for error,status in [(ValueError('Attack fit exceeds error limits'),'conversion_blocked'),
                             (AssertionError('note gates differ'),'converter_model_blocked'),
                             (None,'packing_blocked')]:
            def convert(*args,**kwargs):
                if not kwargs['envelope_support']:raise ValueError('Non-instant DS attack requires envelope fitting')
                if error is not None:raise error
                return b'blob',{'samples':[{}]},c
            with self.subTest(status=status), \
                 patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'loop'}]), \
                 patch('audit_nds_compatibility.convert_merged_song',side_effect=convert), \
                 patch('audit_nds_compatibility.pack_converted_experiment',side_effect=ValueError('ROM budget')):
                result=scan(row,archive)
            self.assertEqual(result['status'],status)
            self.assertEqual(len(result['attempts']),2)
            self.assertFalse(result['manual_matches_packed_variant'])

    def test_skipped_or_capacity_blocked_variants_do_not_convert(self):
        for status in ('empty_slot','silent_sequence','analysis_blocked','packed_standard'):
            row,c,archive,m=fixture();row['status']=status;row['features']['track_count']=9
            with patch('audit_nds_compatibility.convert_merged_song') as convert:
                result=scan(row,archive)
            convert.assert_not_called()
            self.assertEqual(result['status'],'capacity_blocked' if status=='packed_standard' else status)

    def test_conversion_model_and_packing_failures_remain_distinct(self):
        row,c,archive,m=fixture()
        for error,status in [(ValueError('upward bend'),'conversion_blocked'),
                             (AssertionError('gate differs'),'converter_model_blocked')]:
            with self.subTest(status=status), \
                 patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'loop'}]), \
                 patch('audit_nds_compatibility.convert_merged_song',side_effect=error), \
                 patch('audit_nds_compatibility.pack_converted_experiment') as packer:
                self.assertEqual(scan(row,archive)['status'],status);packer.assert_not_called()
        with patch('audit_nds_compatibility.trace_sequence',return_value=[{'track':0,'termination':'loop'}]), \
             patch('audit_nds_compatibility.convert_merged_song',return_value=(b'',{'samples':[]},c)), \
             patch('audit_nds_compatibility.pack_converted_experiment',side_effect=ValueError('ROM budget')):
            result=scan(row,archive)
        self.assertEqual(result['status'],'packing_blocked')
        self.assertTrue(result['attempts'][0]['conversion_passed'])
        self.assertFalse(result['attempts'][0]['packing_passed'])

    def test_summary_and_reports_do_not_count_variants_as_extra_sequences(self):
        row,c,archive,m=fixture();row['manual_matches_packed_variant']=True
        row['antialias']={'status':'packed','manual_matches_packed_variant':True,'attempts':[],
                          'route':'looping_singleton_antialias_envelope','gain_db':3.5,'target_sample_count':2,
                          'envelope_approximation':{'attack_fits':[{'ds_attack':100,'gba_attack':74}]}}
        total=summarize([row])
        self.assertEqual((total['slots'],total['packed']),(1,1))
        self.assertEqual(total['antialias']['packed_variants'],1)
        self.assertEqual(total['antialias']['packed_fitted_envelope_variants'],1)
        self.assertEqual(total['antialias']['packed_fitted_envelope_exact_manual_matches'],1)
        self.assertEqual(total['antialias']['unique_sequences_any_exact_manual_match'],1)
        self.assertEqual(total['antialias']['antialias_only_packed'],0)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d);write_reports(path,{'rows':[row],'summary':total})
            item=next(csv.DictReader((path/'report.csv').read_text().splitlines()))
            self.assertEqual(item['antialias_manual_exact_match'],'True')
            self.assertEqual(item['antialias_samples'],'2')
            self.assertEqual(item['antialias_envelope_approximation'],'True')
            self.assertEqual(json.loads(item['antialias_attack_fits']),[{'ds_attack':100,'gba_attack':74}])
            self.assertIn('渐入组合通过',(path/'index.html').read_text())
            self.assertIn('独立抗混叠版本',(path/'summary.md').read_text())
            self.assertIn('aaMatch',(path/'index.html').read_text())

    def test_manual_loader_rejects_manifest_mismatch_and_ignores_nonpass_feedback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);artifact=root/'experiment';artifact.mkdir()
            actual=fingerprint(b'rom');(artifact/'unified.gba').write_bytes(b'rom')
            record={'status':'user_reported_improvement','expected_build_fingerprint':actual}
            (artifact/'manual-testing.json').write_text(json.dumps(record))
            self.assertEqual(manual_evidence(root),[])
            record['status']='user_reported_pass'
            (artifact/'manual-testing.json').write_text(json.dumps(record))
            manifest={'output_fingerprint':fingerprint(b'other'),'nds_conversion':{'source_profile':'ssr1d','sequence_index':1}}
            (artifact/'build.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'manifest fingerprints differ'):
                manual_evidence(root)
            manifest['output_fingerprint']=actual
            (artifact/'build.json').write_text(json.dumps(manifest))
            self.assertEqual(manual_evidence(root)[0]['output_sha256'],actual['sha256'])


if __name__=='__main__':unittest.main()
