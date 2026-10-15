from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from nds_lfo import ds_sine, ds_pitch_units, gba_lfo_value, map_pitch_lfo, note_lfo_commands
from validate_nds_lfo import LfoModel


def state(**changes):
    return {'mod_type': 0, 'mod_depth': 20, 'mod_speed': 16, 'mod_range': 1,
            'mod_delay': 0, **changes}


class PitchLfoTests(unittest.TestCase):
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
