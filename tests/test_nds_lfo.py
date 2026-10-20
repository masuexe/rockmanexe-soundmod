from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from nds_lfo import ds_sine, ds_pitch_units, gba_lfo_value, map_pitch_lfo, note_lfo_commands, map_pitch_delay
from validate_nds_lfo import LfoModel, compare_reference_window


def state(**changes):
    return {'mod_type': 0, 'mod_depth': 20, 'mod_speed': 16, 'mod_range': 1,
            'mod_delay': 0, **changes}


class PitchLfoTests(unittest.TestCase):
    def test_fixed_delay_mapping_retains_zero_delay_commands(self):
        self.assertEqual(note_lfo_commands(state(), 148), note_lfo_commands(state(), 148, True))
        delayed = state(mod_delay=10, mod_speed=25, mod_depth=15)
        with self.assertRaises(ValueError):
            map_pitch_lfo(delayed, 116)
        self.assertEqual(map_pitch_lfo(delayed, 116, True), {'lfos': 26, 'mod': 2})
        mapping = map_pitch_delay(delayed, 116)
        self.assertEqual(mapping['lfodl'], 6)
        self.assertEqual(mapping['phase_delay_ticks'], 5)
        self.assertAlmostEqual(mapping['source_delay_ms'], 52.095, delta=0.01)
        self.assertIn(bytes([0xC3, 6]), note_lfo_commands(delayed, 116, True))

    def test_delayed_count_holds_phase_then_restarts_on_next_note(self):
        commands = [('LFOS', 0), ('MODT', 0), ('LFODL', 6), ('MOD', 2), ('LFOS', 26)]
        events = [{'ticks': t, 'name': name, 'value': value} for t in (0, 8) for name, value in commands]
        events += [{'ticks': t, 'name': 'NOTE'} for t in (0, 8)]
        events.sort(key=lambda e: e['ticks'])
        model = LfoModel(events)
        self.assertEqual((model.advance(6)['count'], model.value, model.phase), (0, 0, 0))
        self.assertEqual(model.advance(7)['phase'], 26)
        self.assertEqual(model.advance(8)['value'], 1)
        self.assertEqual((model.advance(9)['count'], model.value, model.phase), (5, 0, 0))

    def test_invalid_and_overflowing_delays_are_rejected(self):
        for value in (-1, 65536, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                map_pitch_delay(state(mod_delay=value), 116)
        with self.assertRaisesRegex(ValueError, 'LFODL capacity'):
            map_pitch_lfo(state(mod_delay=65535), 116, True)

    def test_reference_comparison_uses_the_actual_active_tracks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracks = [{'value': 1}, {'value': 0}, {'value': 0}, {'value': 0}, {'value': -2}]
            report = {'complete': True, 'active_modulation_tracks': [0, 4],
                      'snapshots': [{'clock': 10, 'tracks': tracks}]}
            (root / 'validation.json').write_text(json.dumps(report))
            reference = root / 'reference'
            reference.mkdir()
            header = 'timer_frame,tick,track,type,value\n'
            (reference / 'modulation.csv').write_text(header + '20,10,0,0,4\n20,10,4,0,-8\n')
            result = compare_reference_window(root, reference)
            self.assertEqual(set(result['tracks']), {'0', '4'})
            self.assertTrue(all(t['rms_pitch_difference_cents'] == 0 for t in result['tracks'].values()))
            (reference / 'modulation.csv').write_text(header + '20,10,0,0,4\n')
            with self.assertRaisesRegex(ValueError, 'all active'):
                compare_reference_window(root, reference)

    def test_lfodl_changes_reload_without_reset_and_dropped_note_keeps_counter(self):
        events = [{'ticks': 0, 'name': 'LFOS', 'value': 32},
                  {'ticks': 0, 'name': 'MOD', 'value': 2},
                  {'ticks': 0, 'name': 'LFODL', 'value': 3},
                  {'ticks': 0, 'name': 'NOTE'},
                  {'ticks': 1, 'name': 'LFODL', 'value': 7},
                  {'ticks': 1, 'name': 'NOTE', 'allocated': False},
                  {'ticks': 4, 'name': 'NOTE', 'allocated': True}]
        model = LfoModel(events)
        self.assertEqual(model.advance(1)['count'], 2)
        self.assertEqual(model.advance(2)['count'], 1)
        self.assertEqual(model.advance(4)['phase'], 32)
        after = model.advance(5)
        self.assertEqual((after['count'], after['phase'], after['value']), (6, 0, 0))
        with self.assertRaisesRegex(ValueError, 'boolean'):
            LfoModel([{'ticks': 0, 'name': 'NOTE', 'allocated': 0}]).advance(1)

    def test_reference_comparison_maps_sparse_source_ids_and_rejects_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = {'complete': True, 'active_modulation_tracks': [0, 1],
                      'source_track_ids': [5, 15],
                      'snapshots': [{'clock': 10, 'tracks': [{'value': 1}, {'value': -2}]}]}
            (root / 'validation.json').write_text(json.dumps(report))
            reference = root / 'reference'
            reference.mkdir()
            (reference / 'modulation.csv').write_text(
                'timer_frame,tick,track,type,value\n20,10,5,0,4\n20,10,15,0,-8\n20,10,0,0,127\n')
            result = compare_reference_window(root, reference)
            self.assertTrue(all(t['rms_pitch_difference_cents'] == 0 for t in result['tracks'].values()))
            self.assertEqual(result['source_track_ids'], [5, 15])
            report['source_track_ids'] = [5, 5]
            (root / 'validation.json').write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'unique singleton'):
                compare_reference_window(root, reference)

    def test_ds_sine_quadrants_and_signed_pitch_rounding(self):
        self.assertEqual([ds_sine(i) for i in (0, 32, 64, 96)], [0, 127, 0, -127])
        self.assertEqual([ds_pitch_units(i, 20) for i in (0, 1024, 2048, 8192, 24576)],
                         [0, 1, 3, 9, -10])
        with self.assertRaises(ValueError):
            ds_sine(128)

    def test_gba_triangle_and_native_probe_observations(self):
        # Actual EXE6 RAM probe: LFOS=10, MOD=3, delay=0.
        for ticks, phase, value in [(1, 10, 0), (3, 30, 1), (5, 50, 2), (6, 60, 2),
                                     (8, 80, 2), (10, 100, 1), (31, 54, 2), (33, 74, 2)]:
            with self.subTest(ticks=ticks):
                model = LfoModel([{'ticks': 0, 'name': 'LFOS', 'value': 10},
                                  {'ticks': 0, 'name': 'MOD', 'value': 3}])
                actual = model.advance(ticks)
                self.assertEqual((actual['phase'], actual['value']), (phase, value))
        self.assertEqual([gba_lfo_value(i, 3) for i in (64, 128, 192, 255)], [3, 0, -3, -1])

    def test_mapping_uses_sequence_tick_rate_and_quantized_depth(self):
        self.assertEqual(map_pitch_lfo(state(), 148), {'lfos': 13, 'mod': 2})
        self.assertEqual(map_pitch_lfo(state(mod_speed=20, mod_depth=25), 148), {'lfos': 16, 'mod': 3})
        self.assertEqual(map_pitch_lfo(state(mod_depth=0), 148), {'lfos': 0, 'mod': 0})
        self.assertEqual(note_lfo_commands(state(), 148), bytes([0xC2, 0, 0xC5, 0, 0xC3, 1, 0xC4, 2, 0xC2, 13]))

    def test_unsupported_active_effects_and_unrepresentable_values_fail(self):
        for changes in ({'mod_type': 1}, {'mod_type': 2}, {'mod_delay': 10}, {'mod_speed': 0},
                        {'mod_range': 0}, {'mod_depth': 128}, {'mod_depth': 1},
                        {'mod_depth': 127, 'mod_range': 127}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                map_pitch_lfo(state(**changes), 148)

    def test_onset_delay_and_new_note_reset_shared_phase(self):
        events = [{'ticks': 0, 'name': name, 'value': value}
                  for name, value in [('LFOS', 0), ('MODT', 0), ('LFODL', 1), ('MOD', 2), ('LFOS', 13)]]
        events += [{'ticks': 0, 'name': 'NOTE'}, {'ticks': 5, 'name': 'NOTE'}]
        model = LfoModel(events)
        self.assertEqual(model.advance(1)['phase'], 0)
        self.assertEqual(model.advance(5)['phase'], 52)
        self.assertEqual(model.advance(6)['phase'], 0)
        self.assertEqual(model.advance(7)['phase'], 13)


if __name__ == '__main__':
    unittest.main()
