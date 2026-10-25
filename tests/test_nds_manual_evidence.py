"""Composite acceptance cannot become standalone-song acceptance in the audit."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_nds_compatibility import collect_manual_evidence, manual_evidence, summarize, write_reports
from scan_audio import fingerprint


def artifact(root, name, *, dual=False, status='user_reported_pass', scope='Only the requested checks'):
    path = root / name
    path.mkdir()
    rom, patch = (name + ' ROM').encode(), (name + ' patch').encode()
    fp = fingerprint(rom)
    manifest = {'output_fingerprint': fp}
    if dual:
        manifest['nds_dual_conversion'] = {
            'songs': {'title': {'source_profile': 'ssr1d', 'sequence_index': 18, 'target_index': 474},
                      'battle': {'source_profile': 'ssr1d', 'sequence_index': 26, 'target_index': 475}},
            'communication_role': 'title'}
    else:
        manifest['nds_conversion'] = {'source_profile': 'ssr1d', 'sequence_index': 18, 'bandlimited_pcm': True}
    manual = {'status': status, 'expected_build_fingerprint': fp,
              'expected_bps_fingerprint': fingerprint(patch), 'acceptance_scope': scope}
    for filename, data in [('build.json', manifest), ('manual-testing.json', manual)]:
        (path / filename).write_text(json.dumps(data))
    (path / 'unified.gba').write_bytes(rom)
    (path / 'unified.bps').write_bytes(patch)
    return path


class ManualEvidenceTests(unittest.TestCase):
    def test_composite_is_separate_and_cannot_accept_either_standalone_role(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = artifact(root, 'dual', dual=True)
            standalone, composites = collect_manual_evidence(root)
            self.assertEqual(standalone, [])
            self.assertEqual(manual_evidence(root), [])
            self.assertEqual(len(composites), 1)
            record = composites[0]
            self.assertEqual(record['output_fingerprint'], fingerprint((path / 'unified.gba').read_bytes()))
            self.assertEqual(record['bps_fingerprint'], fingerprint((path / 'unified.bps').read_bytes()))
            self.assertEqual(record['songs']['battle']['target_index'], 475)
            self.assertEqual(record['reported_acceptance_scope'], 'Only the requested checks')

    def test_standalone_keeps_source_identity_and_partial_acceptance_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            artifact(root, 'single', scope='Four-accent issue resolved; other checks not separately reported')
            artifact(root, 'dual', dual=True)
            records, composites = collect_manual_evidence(root)
            self.assertEqual(len(records), 1)
            self.assertEqual(len(composites), 1)
            self.assertEqual(manual_evidence(root), records)
            self.assertEqual((records[0]['family'], records[0]['sequence_index']), ('ssr1', 18))
            self.assertIn('other checks not separately reported', records[0]['reported_acceptance_scope'])

    def test_pending_and_issue_records_do_not_need_or_inherit_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name, status in [('pending', 'pending'), ('issue', 'user_reported_issue')]:
                p = root / name
                p.mkdir()
                (p / 'manual-testing.json').write_text(json.dumps({'status': status}))
            self.assertEqual(collect_manual_evidence(root), ([], []))

    def test_changed_rom_manifest_or_patch_cannot_become_accepted_composite(self):
        for file in ('unified.gba', 'unified.bps', 'build.json'):
            with self.subTest(file=file), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                p = artifact(root, 'dual', dual=True)
                if file == 'build.json':
                    data = json.loads((p / file).read_text())
                    data['output_fingerprint'] = fingerprint(b'changed')
                    (p / file).write_text(json.dumps(data))
                else:
                    (p / file).write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    collect_manual_evidence(root)

    def test_invalid_roles_fail_closed_and_summary_keeps_composite_out_of_counts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = artifact(root, 'dual', dual=True)
            _, composites = collect_manual_evidence(root)
            report = {'rows': [], 'summary': summarize([]), 'composite_manual_records': composites}
            write_reports(root, report)
            self.assertEqual(report['summary']['packed_exact_manual_matches'], 0)
            self.assertEqual(report['summary']['antialias']['packed_exact_manual_matches'], 0)
            text = (root / 'summary.md').read_text()
            self.assertIn('组合 ROM 的独立验收记录', text)
            self.assertIn('Only the requested checks', text)
            self.assertIn(composites[0]['output_fingerprint']['crc32'], text)
            manifest = json.loads((p / 'build.json').read_text())
            manifest['nds_dual_conversion']['communication_role'] = 'random'
            (p / 'build.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'roles'):
                collect_manual_evidence(root)
