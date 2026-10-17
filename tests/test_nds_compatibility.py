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
from audit_nds_compatibility import features, sequence_slots, scan_sequence, summarize, write_reports
from nds_music import trace_sequence
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
    def test_finite_fallback_gain_retry_reports_and_manual_match(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        finite = {'track_end_ticks': {'0': 300}, 'explicit_long_note_eot': True}
        def convert(*args, **kwargs):
            if not kwargs.get('finite_support'):
                raise ValueError('requires looping tracks')
            if args[4]:
                raise ValueError('Song gain exceeds MPlay VOL headroom')
            self.assertFalse(kwargs['native_pitch_lfo'])
            self.assertFalse(kwargs['envelope_support'])
            return b'blob', {'samples': []}, {'track_count': 1, 'finite_song': finite}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0, 'termination': 'end'}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('long gate')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive, manual_records=[{'family': 'ssr1', 'sequence_index': 1, 'output_sha256': 'expected'}])
        self.assertEqual(result['status'], 'packed_finite_standard')
        self.assertEqual(result['gain_db'], 0)
        self.assertTrue(result['gain_adjustment_required'])
        self.assertTrue(result['manual_matches_packed_variant'])
        self.assertFalse(result['runtime_tested_by_audit'])
        self.assertEqual([a['gain_db'] for a in result['attempts'] if a['route'] == 'finite_singleton_long'], [3.5, 0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            write_reports(path, {'rows': [result], 'summary': summarize([result])})
            record = next(csv.DictReader((path / 'report.csv').read_text().splitlines()))
            self.assertEqual(record['finite_song'], 'True')
            self.assertEqual(json.loads(record['finite_track_end_ticks']), {'0': 300})
            line = next(l for l in (path / 'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
            numbers = [int(c.strip()) for c in line.split('|')[2:-1]]
            self.assertEqual(sum(numbers[2:-1]), 1)
            self.assertEqual(numbers[-2:], [1, 0])

    def test_direct_finite_success_keeps_existing_route(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1, 'nonzero_mod_depth_executed': False}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0, 'termination': 'end'}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', return_value=(b'blob', {'samples': []}, {'track_count': 1})), \
             patch('audit_nds_compatibility.convert_merged_song') as merged, \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive)
        self.assertEqual(result['route'], 'direct')
        self.assertEqual(result['status'], 'packed_standard')
        merged.assert_not_called()

    def test_finite_route_cannot_bypass_rejection_or_capacity(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        for count in (1, 9):
            with self.subTest(tracks=count), \
                 patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': i, 'termination': 'end'} for i in range(count)]), \
                 patch('audit_nds_compatibility.features', return_value={'executed_note_events_in_trace': 1, 'track_count': count, 'nonzero_mod_depth_executed': False}), \
                 patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
                 patch('audit_nds_compatibility.convert_merged_song', side_effect=ValueError('unsupported')) as merged, \
                 patch('audit_nds_compatibility.pack_converted_experiment') as pack:
                result = scan(archive)
                self.assertEqual(result['status'], 'conversion_blocked' if count == 1 else 'capacity_blocked')
                pack.assert_not_called()
                if count == 9:
                    merged.assert_not_called()
                else:
                    self.assertTrue(any(a['route'] == 'finite_singleton_long' for a in result['attempts']))

    def test_toggle_features_include_controls_after_last_note(self):
        class NoBank:
            def bank(self, index):
                raise ValueError('No resource inspection in this fixture')
        raw = b'\xC7\x00\x3C\x64\x30\x80\x0C\xCA\x23\x80\x0C\xCA\x00\x80\x18\xFF'
        result = features(NoBank(), {'bank_id': 0}, trace_sequence(raw, analysis_only=True))
        self.assertEqual(result['mod_depth_toggles'],
                         [{'source_track': 0, 'ticks': 12, 'before': 0, 'after': 35},
                          {'source_track': 0, 'ticks': 24, 'before': 35, 'after': 0}])
        self.assertEqual(result['modulation_configs_at_note_on'], [])
        self.assertTrue(result['nonzero_mod_depth_executed'])

    def test_toggle_fallbacks_reports_and_manual_matching(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        toggles = [{'source_track': 0, 'ticks': 12, 'before': 0, 'after': 35},
                   {'source_track': 0, 'ticks': 24, 'before': 35, 'after': 0}]
        setup = [{'source_track': 0, 'activation_tick': 12, 'first_note_tick': 0, 'depth': 35}]
        for needs_envelope in (False, True):
            with self.subTest(envelope=needs_envelope):
                feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                           'nonzero_mod_depth_executed': True, 'active_delayed_modulation_executed': True,
                           'positive_mod_depth_changes': [{}], 'mod_depth_toggles': toggles,
                           'noninstant_attack_definitions': int(needs_envelope)}
                def convert(*args, **kwargs):
                    if not kwargs.get('native_pitch_lfo_live_toggle') or kwargs['envelope_support'] != needs_envelope:
                        raise ValueError('unsupported feature')
                    self.assertTrue(kwargs['native_pitch_lfo'])
                    self.assertTrue(kwargs['native_pitch_lfo_delay'])
                    self.assertFalse(kwargs.get('native_pitch_lfo_live_depth', False))
                    return b'blob', {'samples': []}, {'track_count': 1,
                        'envelope_approximation': {'attack_fits': []},
                        'native_pitch_lfo': {'live_toggle_approximation': {'source_depth_toggles': toggles},
                                             'delay_approximation': {'initializations': setup}}}
                with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
                     patch('audit_nds_compatibility.features', return_value=feature), \
                     patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
                     patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
                     patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
                    result = scan(archive, manual_records=[{'family': 'ssr1', 'sequence_index': 1,
                                                           'output_sha256': 'expected'}])
                self.assertEqual(result['status'], 'packed_envelope_live_toggle_lfo_approximation'
                                 if needs_envelope else 'packed_live_toggle_lfo_approximation')
                self.assertEqual(result['approximations'], {'native_pitch_lfo': True, 'envelope': needs_envelope,
                                                            'fixed_delay': True, 'live_depth': False, 'live_toggle': True})
                self.assertTrue(result['manual_matches_packed_variant'])
                self.assertFalse(result['runtime_tested_by_audit'])
                routes = [a['route'] for a in result['attempts']]
                self.assertLess(routes.index('live_depth_pitch_lfo_approximation'),
                                routes.index('live_toggle_pitch_lfo_approximation'))
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory)
                    write_reports(path, {'rows': [result], 'summary': summarize([result])})
                    record = next(csv.DictReader((path / 'report.csv').read_text().splitlines()))
                    self.assertEqual(record['live_toggle_approximation'], 'True')
                    self.assertEqual(json.loads(record['source_depth_toggles']), toggles)
                    self.assertEqual(json.loads(record['modulation_initializations']), setup)
                    line = next(l for l in (path / 'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
                    numbers = [int(c.strip()) for c in line.split('|')[2:-1]]
                    self.assertEqual(sum(numbers[2:12]), 1)
                    self.assertEqual(numbers[2:12][9 if needs_envelope else 8], 1)
                    self.assertEqual(numbers[-1], 0)

    def test_fixed_delay_success_precedes_new_toggle_mode(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                   'nonzero_mod_depth_executed': True, 'active_delayed_modulation_executed': True}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        def convert(*args, **kwargs):
            self.assertFalse(kwargs.get('native_pitch_lfo_live_toggle', False))
            if not kwargs['native_pitch_lfo_delay']:
                raise ValueError('unsupported delay')
            return b'blob', {'samples': []}, {'track_count': 1}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive)
        self.assertEqual(result['route'], 'fixed_delay_pitch_lfo_approximation')
        self.assertFalse(result['approximations']['live_toggle'])

    def test_live_depth_feature_includes_changes_after_last_note(self):
        class NoBank:
            def bank(self, index):
                raise ValueError('No resource inspection in this fixture')
        raw = b'\xC7\x00\xCA\x0A\x3C\x64\x18\xCA\x14\x80\x18\xFF'
        result = features(NoBank(), {'bank_id': 0}, trace_sequence(raw, analysis_only=True))
        self.assertEqual(result['modulation_configs_at_note_on'][0]['depth'], 10)
        self.assertEqual(result['positive_mod_depth_changes'],
                         [{'source_track': 0, 'ticks': 0, 'before': 10, 'after': 20}])

    def test_live_depth_routes_are_fallbacks_with_distinct_reports(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        changes = [{'source_track': 0, 'ticks': 12, 'before': 10, 'after': 20}]
        for needs_envelope in (False, True):
            with self.subTest(envelope=needs_envelope):
                feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                           'nonzero_mod_depth_executed': True, 'active_delayed_modulation_executed': True,
                           'positive_mod_depth_changes': changes,
                           'noninstant_attack_definitions': int(needs_envelope)}
                def convert(*args, **kwargs):
                    if not kwargs.get('native_pitch_lfo_live_depth') or kwargs['envelope_support'] != needs_envelope:
                        raise ValueError('unsupported feature')
                    self.assertTrue(kwargs['native_pitch_lfo'])
                    self.assertTrue(kwargs['native_pitch_lfo_delay'])
                    return b'blob', {'samples': []}, {'track_count': 1,
                        'envelope_approximation': {'attack_fits': []},
                        'native_pitch_lfo': {'live_depth_approximation': {'source_depth_changes': changes}}}
                with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
                     patch('audit_nds_compatibility.features', return_value=feature), \
                     patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
                     patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
                     patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
                    result = scan(archive, manual_records=[{'family': 'ssr1', 'sequence_index': 1,
                                                           'output_sha256': 'expected'}])
                self.assertEqual(result['status'], 'packed_envelope_live_depth_lfo_approximation'
                                 if needs_envelope else 'packed_live_depth_lfo_approximation')
                self.assertEqual(result['approximations'], {'native_pitch_lfo': True, 'envelope': needs_envelope,
                                                            'fixed_delay': True, 'live_depth': True, 'live_toggle': False})
                self.assertTrue(result['manual_matches_packed_variant'])
                self.assertFalse(result['runtime_tested_by_audit'])
                routes = [a['route'] for a in result['attempts']]
                self.assertLess(routes.index('fixed_delay_pitch_lfo_approximation'),
                                routes.index('live_depth_pitch_lfo_approximation'))
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory)
                    write_reports(path, {'rows': [result], 'summary': summarize([result])})
                    record = next(csv.DictReader((path / 'report.csv').read_text().splitlines()))
                    self.assertEqual(record['live_depth_approximation'], 'True')
                    self.assertEqual(json.loads(record['source_depth_changes']), changes)
                    line = next(l for l in (path / 'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
                    numbers = [int(c.strip()) for c in line.split('|')[2:-1]]
                    categories = numbers[2:12]
                    self.assertEqual(sum(categories), 1)
                    self.assertEqual(categories[7 if needs_envelope else 6], 1)
                    self.assertEqual(numbers[-1], 0)
                    self.assertIn(result['status'], (path / 'index.html').read_text())

    def test_existing_success_takes_precedence_over_live_depth_route(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                   'nonzero_mod_depth_executed': True, 'positive_mod_depth_changes': [{}]}
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
             patch('audit_nds_compatibility.convert_merged_song', return_value=(b'blob', {'samples': []}, {'track_count': 1})) as converter, \
             patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
            result = scan(archive)
        self.assertEqual(result['route'], 'singleton_bend_long')
        self.assertFalse(result['approximations']['live_depth'])
        converter.assert_called_once()
        self.assertNotIn('native_pitch_lfo_live_depth', converter.call_args.kwargs)

    def test_delay_feature_includes_activation_after_last_note_at_same_tick(self):
        class NoBank:
            def bank(self, index):
                raise ValueError('No resource inspection in this fixture')
        raw = b'\xC7\x00\xCB\x19\xE0\x0A\x00\x3C\x64\x0C\xCA\x0F\x80\x0C\xFF'
        result = features(NoBank(), {'bank_id': 0}, trace_sequence(raw, analysis_only=True))
        self.assertEqual(result['modulation_configs_at_note_on'], [])
        self.assertTrue(result['active_delayed_modulation_executed'])

    def test_delay_routes_flags_statuses_and_report_categories(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        manifest = {'appended_bytes': 20, 'output_fingerprint': {'sha256': 'expected'}}
        mapping = {'lfodl': 6, 'phase_delay_ticks': 5}
        for needs_envelope in (False, True):
            with self.subTest(envelope=needs_envelope):
                feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                           'nonzero_mod_depth_executed': True, 'active_delayed_modulation_executed': True,
                           'noninstant_attack_definitions': int(needs_envelope)}
                def convert(*args, **kwargs):
                    if not kwargs['native_pitch_lfo_delay'] or kwargs['envelope_support'] != needs_envelope:
                        raise ValueError('unsupported feature')
                    self.assertTrue(kwargs['native_pitch_lfo'])
                    return b'blob', {'samples': []}, {'track_count': 1, 'envelope_approximation': {'attack_fits': []},
                            'native_pitch_lfo': {'configs': [{'delay_mapping': mapping}], 'delay_approximation': {}}}
                with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
                     patch('audit_nds_compatibility.features', return_value=feature), \
                     patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported pitch')), \
                     patch('audit_nds_compatibility.convert_merged_song', side_effect=convert), \
                     patch('audit_nds_compatibility.pack_converted_experiment', return_value=(b'rom', b'bps', manifest)):
                    result = scan(archive, manual_records=[{'family': 'ssr1', 'sequence_index': 1,
                                                            'output_sha256': 'expected'}])
                self.assertEqual(result['status'], 'packed_envelope_delayed_lfo_approximation'
                                 if needs_envelope else 'packed_delayed_lfo_approximation')
                self.assertEqual(result['approximations'], {'native_pitch_lfo': True,
                                                            'envelope': needs_envelope, 'fixed_delay': True,
                                                            'live_depth': False, 'live_toggle': False})
                self.assertTrue(result['manual_matches_packed_variant'])
                self.assertFalse(result['runtime_tested_by_audit'])
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory)
                    write_reports(path, {'rows': [result], 'summary': summarize([result])})
                    record = next(csv.DictReader((path / 'report.csv').read_text().splitlines()))
                    self.assertEqual(record['fixed_delay_approximation'], 'True')
                    self.assertEqual(json.loads(record['delay_mappings']), [mapping])
                    line = next(l for l in (path / 'summary.md').read_text().splitlines() if l.startswith('| ssr1 |'))
                    numbers = [int(c.strip()) for c in line.split('|')[2:-1]]
                    categories = numbers[2:12]
                    self.assertEqual(sum(categories), 1)
                    self.assertEqual(categories[5 if needs_envelope else 4], 1)
                    self.assertEqual(numbers[-1], 0)

    def test_unsupported_live_delay_change_does_not_become_a_pass(self):
        archive = SimpleNamespace(sequence=lambda index: (b'', {}))
        feature = {'executed_note_events_in_trace': 1, 'track_count': 1,
                   'nonzero_mod_depth_executed': True, 'active_delayed_modulation_executed': True,
                   'positive_mod_depth_changes': [{}]}
        with patch('audit_nds_compatibility.trace_sequence', return_value=[{'track': 0}]), \
             patch('audit_nds_compatibility.features', return_value=feature), \
             patch('audit_nds_compatibility.convert_song', side_effect=ValueError('unsupported')), \
             patch('audit_nds_compatibility.convert_merged_song', side_effect=ValueError('Live delayed-LFO parameter changes')), \
             patch('audit_nds_compatibility.pack_converted_experiment') as packer:
            result = scan(archive)
        self.assertEqual(result['status'], 'conversion_blocked')
        self.assertEqual(result['attempts'][-1]['route'], 'live_toggle_pitch_lfo_approximation')
        packer.assert_not_called()

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
                   'noninstant_attack_definitions': 1, 'envelope_override_controls': ['0xD3'],
                   'active_delayed_modulation_executed': True, 'positive_mod_depth_changes': [{}]}
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
                self.assertEqual(result['approximations'], {'native_pitch_lfo': active_pitch, 'envelope': True,
                                                            'fixed_delay': False, 'live_depth': False, 'live_toggle': False})
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
