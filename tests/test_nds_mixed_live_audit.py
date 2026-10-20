import csv
import json
import tempfile
import unittest
from pathlib import Path

from test_nds_live_min_audit import run
from audit_nds_compatibility import summarize, write_reports

FAILURE = 'Delayed LFO requires fixed per-track modulation after initial activation'
TRACKS = [{'track': 0, 'termination': 'loop'}, {'track': 15, 'termination': 'end'}]
ROUTES = {'mixed_live_depth_minimum_pitch_lfo_approximation',
          'mixed_envelope_live_depth_minimum_pitch_lfo_approximation'}


def conversion(fit=False, headroom=False):
    def convert(*args, **options):
        if not options.get('mixed_live_depth_support'):
            raise ValueError(FAILURE)
        if options['envelope_support'] != fit:
            raise ValueError('Non-instant DS attack requires envelope fitting')
        if headroom and args[4]:
            raise ValueError('Song gain exceeds MPlay VOL headroom')
        return b'blob', {'samples': []}, {
            'track_count': 2, 'mixed_loop_song': {'finite_tracks_repeated': False},
            'mixed_live_depth_extension': {'later_entry_common_cycles': 1},
            'native_pitch_lfo': {'minimum_depth_quantization': {'native_minimum_mod': 1}},
            'envelope_approximation': {'attack_fits': []}}
    return convert


class MixedLiveAuditTests(unittest.TestCase):
    def test_explicit_plain_and_fitted_modes_match_acceptance(self):
        for fit in (False, True):
            row, converter, _ = run(conversion(fit), fit=fit, tracks=TRACKS)
            self.assertEqual(row['route'], 'mixed_' + ('envelope_' if fit else '') +
                             'live_depth_minimum_pitch_lfo_approximation')
            self.assertEqual(row['status'], 'packed_mixed_' + ('envelope_' if fit else '') +
                             'live_depth_minimum_lfo_approximation')
            self.assertTrue(row['manual_matches_packed_variant'])
            self.assertFalse(row['runtime_tested_by_audit'])
            options = converter.call_args.kwargs
            for flag in ('mixed_loop_support', 'mixed_live_depth_support', 'native_pitch_lfo',
                         'native_pitch_lfo_delay', 'native_pitch_lfo_live_depth', 'native_pitch_lfo_min_depth'):
                self.assertTrue(options[flag], flag)
            self.assertEqual(options['envelope_support'], fit)
            self.assertTrue(row['attempts'][-1]['mixed_live_depth_support'])

    def test_unrelated_and_assertion_errors_do_not_enable_route(self):
        for error in (AssertionError(FAILURE), ValueError('fixed tempo'),
                      ValueError('DS LFO cannot be represented by the bounded native approximation')):
            row, _, _ = run(lambda *a, **k: (_ for _ in ()).throw(error), tracks=TRACKS)
            self.assertFalse(any(a['route'] in ROUTES for a in row['attempts']))

    def test_all_loop_and_finite_scores_keep_existing_routes(self):
        for tracks in ([{'track': 0, 'termination': 'loop'}],
                       [{'track': 0, 'termination': 'end'}]):
            row, _, _ = run(conversion(), tracks=tracks)
            self.assertFalse(any(a['route'] in ROUTES for a in row['attempts']))

    def test_gain_and_packing_failure_are_recorded_separately(self):
        row, _, _ = run(conversion(headroom=True), tracks=TRACKS)
        self.assertEqual(row['gain_db'], 0)
        self.assertEqual([a['gain_db'] for a in row['attempts'] if a['route'] in ROUTES], [3.5, 0])
        row, _, _ = run(conversion(), tracks=TRACKS, pack_error=AssertionError('BPS mismatch'))
        self.assertEqual(row['status'], 'packing_blocked')
        self.assertFalse(row['manual_matches_packed_variant'])

    def test_summary_categories_remain_exclusive_and_csv_retains_policy(self):
        rows = [run(conversion(fit), fit=fit, tracks=TRACKS)[0] for fit in (False, True)]
        summary = summarize(rows)
        self.assertEqual(summary['packed_mixed_variants'], 2)
        self.assertEqual(summary['packed_minimum_depth_lfo_variants'], 2)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            write_reports(p, {'rows': rows, 'summary': summary})
            with (p / 'report.csv').open() as stream:
                items = list(csv.DictReader(stream))
            self.assertTrue(all(json.loads(x['mixed_live_depth_extension']) ==
                                {'later_entry_common_cycles': 1} for x in items))
            line = next(l for l in (p / 'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
            counts = [int(c.strip()) for c in line.split('|')[2:-1]]
            self.assertEqual(sum(counts[2:-1]), 2)
            self.assertEqual(counts[-1], 0)


if __name__ == '__main__':
    unittest.main()
