import csv
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze_song import Reader
from audit_nds_compatibility import sequence_slots, scan_sequence, summarize, write_reports
from nds_track_merge import BATTLE_GROUPS


def catalog_fixture(padded=True):
    info = bytearray(80)
    struct.pack_into('<I', info, 8, 48)
    struct.pack_into('<3I', info, 48, 2, 64, 0)
    symbols = bytearray(48)
    struct.pack_into('<I', symbols, 8, 32)
    struct.pack_into('<3I', symbols, 32, 2, 48, 0)
    symbols.extend(b'BGM_A\0')
    size = len(symbols)
    symbols.extend(bytes(-size % 4))
    symbols[:4] = b'SYMB'
    struct.pack_into('<I', symbols, 4, len(symbols))
    raw = bytearray(64) + symbols
    struct.pack_into('<II', raw, 16, 64, size if padded else len(symbols))
    return SimpleNamespace(reader=Reader(bytes(raw)), blocks={'INFO': Reader(bytes(info))})


def row(**changes):
    return {'id': 'ssr1:1', 'family': 'ssr1', 'index': 1, 'name': 'BGM_TEST',
            'status': 'empty_slot', 'attempts': [], 'manual_matches_packed_variant': False,
            'related_manual_records': [], **changes}


def scan(archive, **changes):
    args = {'archive': archive, 'slot': {'index': 1, 'name': 'BGM_TEST', 'present': True},
            'family': 'ssr1', 'source': b'', 'base': b'', 'raw_sdat': b'',
            'profile': 'ssr1d', 'capacity': 8}
    args.update(changes)
    return scan_sequence(**args)


class CompatibilityAuditTests(unittest.TestCase):
    def test_symbol_directory_alignment_and_empty_slots(self):
        expected = [{'index': 0, 'name': 'BGM_A', 'present': True},
                    {'index': 1, 'name': None, 'present': False}]
        self.assertEqual(sequence_slots(catalog_fixture(True)), expected)
        self.assertEqual(sequence_slots(catalog_fixture(False)), expected)

    def test_invalid_symbol_padding_is_rejected(self):
        archive = catalog_fixture(True)
        raw = bytearray(archive.reader.data)
        raw[-1] = 1
        archive.reader = Reader(bytes(raw))
        with self.assertRaisesRegex(ValueError, 'alignment padding'):
            sequence_slots(archive)

    def test_empty_and_silent_sequences_are_not_convertible_music(self):
        self.assertEqual(scan(None, slot={'index': 1, 'name': None, 'present': False})['status'], 'empty_slot')
        class Silent:
            def sequence(self, index):
                return b'\xFF', {'bank_id': 0}
            def bank(self, index):
                raise ValueError('no bank needed')
        with patch('audit_nds_compatibility.pack_converted_experiment') as packer:
            self.assertEqual(scan(Silent())['status'], 'silent_sequence')
            packer.assert_not_called()

    def test_unknown_overcapacity_song_does_not_receive_guessed_mapping(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 9, 'nonzero_mod_depth_executed': False,
                   'noninstant_attack_definitions': 1, 'envelope_override_controls': ['0xD3']}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': i} for i in range(9)]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_merged_song') as converter:
            result = scan(archive)
        self.assertEqual(result['status'], 'capacity_blocked')
        converter.assert_not_called()

    def test_only_known_sf3_battle_uses_verified_merge_groups(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 11, 'nonzero_mod_depth_executed': False}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': i} for i in range(11)]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_merged_song', return_value=(b'blob', {'samples': []}, {'track_count': 8})) as converter, \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive, family='ssr3', slot={'index': 35, 'name': 'BGM_BATTLE', 'present': True})
        self.assertEqual(result['status'], 'packed_standard')
        self.assertEqual(result['route'], 'known_sf3_battle_merge')
        self.assertEqual(converter.call_args.args[2], BATTLE_GROUPS)
        self.assertFalse(converter.call_args.kwargs['native_pitch_lfo'])

    def test_failed_model_assertion_is_not_counted_as_conversion_success(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=AssertionError('note model differs')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=ValueError('unsupported effect')), \
             patch('audit_nds_compatibility.pack_converted_experiment') as packer:
            result = scan(archive)
        self.assertEqual(result['status'], 'converter_model_blocked')
        self.assertEqual(summarize([result])['packed'], 0)
        packer.assert_not_called()

    def test_zero_gain_retry_and_exact_manual_match_are_explicit(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        def conversion(*args, **kwargs):
            if kwargs['song_gain_db']:
                raise ValueError('Song gain exceeds VOL headroom')
            return b'blob', {'samples': []}, {'track_count': 1}
        evidence = [{'family': 'ssr1', 'sequence_index': 1, 'output_sha256': 'expected'}]
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=conversion), \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive, manual_records=evidence)
        self.assertEqual(result['gain_db'], 0)
        self.assertTrue(result['gain_adjustment_required'])
        self.assertTrue(result['manual_matches_packed_variant'])
        self.assertFalse(result['runtime_tested_by_audit'])
        self.assertEqual([a['gain_db'] for a in result['attempts']], [3.5, 0])

    def test_report_html_escapes_data_and_csv_preserves_names(self):
        name = '</script><script>alert("test")</script>'
        report = {'rows': [row(name=name)], 'summary': summarize([row(name=name)])}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            write_reports(path, report)
            page = (path / 'index.html').read_text()
            payload = re.search(r'<script type="application/json" id="data">(.*?)</script>', page, re.S).group(1)
            self.assertEqual(json.loads(payload)['report']['rows'][0]['name'], name)
            self.assertNotIn(name, page)
            with (path / 'report.csv').open() as stream:
                self.assertEqual(next(csv.DictReader(stream))['name'], name)

    def test_envelope_and_combined_routes_have_distinct_labels_and_manual_matches(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        fit = {'attack_fits': [{'ds_attack': 100, 'gba_attack': 74, 'rms_amplitude_error': 0.102}]}
        for active_pitch in (False, True):
            with self.subTest(active_pitch=active_pitch):
                feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                           'nonzero_mod_depth_executed': active_pitch, 'noninstant_attack_definitions': 1}
                def convert(*args, **kwargs):
                    if not kwargs['envelope_support'] or kwargs['native_pitch_lfo'] != active_pitch:
                        raise ValueError('unsupported effect')
                    return b'blob', {'samples': []}, {'track_count': 1, 'envelope_approximation': fit}
                with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
                     patch('audit_nds_compatibility.features', return_value=feature), \
                     patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported envelope')), \
                     patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
                     patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
                    result = scan(archive, manual_records=[{'family': 'ssr1', 'sequence_index': 1,
                                                            'output_sha256': 'expected'}])
                expected = 'packed_envelope_lfo_approximation' if active_pitch else 'packed_envelope_approximation'
                self.assertEqual(result['status'], expected)
                self.assertEqual(result['approximations'], {'native_pitch_lfo': active_pitch, 'envelope': True})
                self.assertEqual(result['envelope_approximation'], fit)
                self.assertTrue(result['manual_matches_packed_variant'])
                self.assertFalse(result['runtime_tested_by_audit'])
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory)
                    write_reports(path, {'rows': [result], 'summary': summarize([result])})
                    csv_row = next(csv.DictReader((path / 'report.csv').read_text().splitlines()))
                    self.assertEqual(csv_row['envelope_approximation'], 'True')
                    self.assertEqual(csv_row['native_pitch_lfo_approximation'], str(active_pitch))
                    self.assertEqual(json.loads(csv_row['attack_fits']), fit['attack_fits'])
                    self.assertIn('| 0 | 0 | ' + ('0 | 1 | 0 |' if active_pitch else '1 | 0 | 0 |'),
                                  (path / 'summary.md').read_text())

    def test_unneeded_envelope_route_is_not_attempted(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=ValueError('unsupported')) as convert:
            result = scan(archive)
        self.assertEqual([a['route'] for a in result['attempts']], ['direct', 'singleton_bend_long'])
        self.assertFalse(convert.call_args.kwargs['envelope_support'])

    def test_failed_attack_fit_remains_blocked(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False,
                   'noninstant_attack_definitions': 1}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('noninstant attack')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=ValueError('attack fitting error limits')), \
             patch('audit_nds_compatibility.pack_converted_experiment') as packer:
            result = scan(archive)
        self.assertEqual(result['status'], 'conversion_blocked')
        self.assertEqual(summarize([result])['packed'], 0)
        packer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
