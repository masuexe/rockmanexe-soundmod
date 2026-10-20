import csv
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_nds_compatibility import scan_sequence, summarize, write_reports


REPRESENTATION_ERROR = 'DS LFO cannot be represented by the bounded native approximation'
MIXED = {'finite_track_end_ticks': {'1': 12}, 'source_loop_periods': {'0': 24},
         'common_loop_start_ticks': 36, 'common_loop_ticks': 24}
MINIMUM = {'all_phase_pitch_difference_bound_cents': 10, 'isolated_one_second_rms_limit_cents': 5}


def fixture():
    return SimpleNamespace(sequence=lambda index: (b'', {})), [
        {'track': 0, 'termination': 'loop'}, {'track': 1, 'termination': 'end'}]


def scan(archive, **changes):
    args = dict(archive=archive, slot={'index': 20, 'name': 'HOKORA', 'present': True},
                family='ssr1', source=b'', base=b'', raw_sdat=b'', profile='ssr1d', capacity=8)
    args.update(changes)
    return scan_sequence(**args)


class MixedAuditTests(unittest.TestCase):
    def run_scan(self, convert, *, tracks=None, mod=True, direct_error=None, pack_error=None, capacity=8):
        archive, defaults = fixture()
        feature = {'executed_note_events_in_trace': 3, 'track_count': len(tracks or defaults),
                   'nonzero_mod_depth_executed': mod, 'active_delayed_modulation_executed': mod}
        manifest = {'appended_bytes': 24, 'output_fingerprint': {'sha256': 'accepted'}}
        with patch('audit_nds_compatibility.trace_sequence', return_value=tracks or defaults), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=direct_error or ValueError('old path rejected')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=convert) as converter, \
             patch('audit_nds_compatibility.pack_converted_experiment', side_effect=pack_error,
                   return_value=(b'rom', b'bps', manifest)) as packer:
            result = scan(archive, capacity=capacity, manual_records=[
                {'family': 'ssr1', 'sequence_index': 20, 'output_sha256': 'accepted'}])
        return result, converter, packer

    def test_mixed_routes_follow_old_failures_with_explicit_flags(self):
        for mod in (False, True):
            with self.subTest(mod=mod):
                def convert(*args, **kw):
                    if not kw.get('mixed_loop_support') or kw['native_pitch_lfo'] != mod:
                        raise ValueError('old path rejected')
                    self.assertFalse(kw.get('finite_support'))
                    self.assertFalse(kw['envelope_support'])
                    self.assertFalse(kw['native_pitch_lfo_min_depth'])
                    self.assertEqual(kw['native_pitch_lfo_delay'], mod)
                    return b'blob', {'samples': []}, {'track_count': 2, 'mixed_loop_song': MIXED}
                row, _, _ = self.run_scan(convert, mod=mod)
                self.assertEqual(row['status'], 'packed_mixed_delayed_lfo_approximation' if mod else 'packed_mixed_standard')
                self.assertEqual(row['mixed_loop_song'], MIXED)
                self.assertTrue(row['manual_matches_packed_variant'])
                self.assertFalse(row['runtime_tested_by_audit'])
                self.assertGreater(next(i for i,a in enumerate(row['attempts']) if a.get('mixed_loop_support')), 1)

    def test_minimum_depth_retry_keeps_failed_attempt_and_independent_gain_retry(self):
        def convert(*args, **kw):
            if not kw.get('mixed_loop_support'):
                raise ValueError('old path rejected')
            if not kw['native_pitch_lfo']:
                raise ValueError('active modulation')
            if not kw['native_pitch_lfo_min_depth']:
                raise ValueError(REPRESENTATION_ERROR)
            if args[4]:
                raise ValueError('Song gain exceeds MPlay VOL headroom')
            return b'blob', {'samples': []}, {'track_count': 2, 'mixed_loop_song': MIXED,
                                            'native_pitch_lfo': {'minimum_depth_quantization': MINIMUM}}
        row, _, _ = self.run_scan(convert)
        self.assertEqual(row['status'], 'packed_mixed_min_depth_lfo_approximation')
        self.assertEqual(row['gain_db'], 0)
        self.assertEqual(row['attempts'][-3]['error']['message'], REPRESENTATION_ERROR)
        self.assertEqual([a['gain_db'] for a in row['attempts'][-2:]], [3.5, 0])
        self.assertTrue(all(a['native_pitch_lfo_min_depth'] for a in row['attempts'][-2:]))
        self.assertEqual(row['native_pitch_lfo']['minimum_depth_quantization'], MINIMUM)

    def test_model_and_unrelated_failures_do_not_enable_minimum_depth_retry(self):
        for error in (AssertionError(REPRESENTATION_ERROR), ValueError('Live delayed-LFO parameter changes'),
                      ValueError('Minimum-depth LFO exceeds ten-cent absolute pitch difference bound')):
            with self.subTest(error=str(error), kind=type(error)):
                row, _, packer = self.run_scan(lambda *a, **k: (_ for _ in ()).throw(error))
                self.assertFalse(any(a.get('native_pitch_lfo_min_depth') for a in row['attempts']))
                self.assertEqual(row['status'], 'converter_model_blocked' if isinstance(error, AssertionError) else 'conversion_blocked')
                packer.assert_not_called()

    def test_capacity_and_pure_scores_never_try_mixed_mode(self):
        for tracks, capacity in (([{'track': 0, 'termination': 'loop'}], 8),
                                 ([{'track': 0, 'termination': 'end'}], 8),
                                 (fixture()[1], 1)):
            row, converter, _ = self.run_scan(lambda *a, **k: (_ for _ in ()).throw(ValueError('unsupported')),
                                            tracks=tracks, capacity=capacity)
            self.assertFalse(any(a.get('mixed_loop_support') for a in row['attempts']))
            self.assertFalse(any(c.kwargs.get('mixed_loop_support') for c in converter.call_args_list))

    def test_old_success_takes_precedence(self):
        row, converter, _ = self.run_scan(lambda *a, **k: (b'blob', {'samples': []}, {'track_count': 2}))
        self.assertEqual(row['route'], 'singleton_bend_long')
        converter.assert_called_once()
        self.assertNotIn('mixed_loop_support', converter.call_args.kwargs)

    def test_mixed_packing_failure_remains_visible(self):
        def convert(*a, **kw):
            if not kw.get('mixed_loop_support'): raise ValueError('unsupported')
            return b'blob', {'samples': []}, {'track_count': 2, 'mixed_loop_song': MIXED}
        row, _, _ = self.run_scan(convert, mod=False, pack_error=AssertionError('BPS reconstruction mismatch'))
        self.assertEqual(row['status'], 'packing_blocked')
        self.assertTrue(row['attempts'][-1]['conversion_passed'])
        self.assertEqual(row['attempts'][-1]['packing_error']['message'], 'BPS reconstruction mismatch')
        self.assertFalse(row['manual_matches_packed_variant'])

    def test_reports_export_structure_and_quantization_with_exclusive_counts(self):
        def convert(*a, **kw):
            if not kw.get('mixed_loop_support') or not kw['native_pitch_lfo']:
                raise ValueError('unsupported')
            if not kw['native_pitch_lfo_min_depth']: raise ValueError(REPRESENTATION_ERROR)
            return b'blob', {'samples': []}, {'track_count': 2, 'mixed_loop_song': MIXED,
                                            'native_pitch_lfo': {'minimum_depth_quantization': MINIMUM}}
        row, _, _ = self.run_scan(convert)
        total = summarize([row])
        self.assertEqual(total['packed'], 1)
        self.assertEqual(total['packed_mixed_variants'], 1)
        self.assertEqual(total['packed_mixed_exact_manual_matches'], 1)
        self.assertEqual(total['packed_minimum_depth_lfo_variants'], 1)
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            write_reports(p, {'rows': [row], 'summary': total})
            item = next(csv.DictReader((p/'report.csv').read_text().splitlines()))
            self.assertEqual(item['mixed_loop_song'], 'True')
            self.assertEqual(json.loads(item['mixed_finite_track_end_ticks']), MIXED['finite_track_end_ticks'])
            self.assertEqual(json.loads(item['mixed_source_loop_periods']), MIXED['source_loop_periods'])
            self.assertEqual(item['mixed_common_loop_ticks'], '24')
            self.assertEqual(item['minimum_depth_lfo_quantization'], 'True')
            self.assertEqual(json.loads(item['minimum_depth_lfo_policy']), MINIMUM)
            line = next(l for l in (p/'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
            counts = [int(c.strip()) for c in line.split('|')[2:-1]]
            self.assertEqual(sum(counts[2:-1]), 1)
            self.assertEqual(counts[-4:], [0, 0, 1, 0])
            self.assertIn('function structureMatch(r)', (p/'index.html').read_text())


if __name__ == '__main__':
    unittest.main()
