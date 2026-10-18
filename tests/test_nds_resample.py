"""DSP properties: alias suppression, periodic joins, pitch and finite tails."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nds_resample import resample_wave


def signed(data):
    return [v if v < 128 else v - 256 for v in data]


def rms(data):
    return math.sqrt(sum(v * v for v in data) / len(data))


class OfflineResampleTests(unittest.TestCase):
    def test_alias_rejection_preserves_passband_without_gain_normalization(self):
        rate, target = 32000, 8000
        def sine(hz):
            return [round(12000 * math.sin(2 * math.pi * hz * i / rate)) for i in range(4096)]
        low = signed(resample_wave(sine(500), rate, 60, 60, mixing_rate=target)[0])[50:900]
        high = signed(resample_wave(sine(9000), rate, 60, 60, mixing_rate=target)[0])[50:900]
        self.assertAlmostEqual(rms(low), 12000 / 256 / math.sqrt(2), delta=1)
        self.assertLess(rms(high), .6)

    def test_periodic_filter_guard_preserves_loop_phase_and_tuning(self):
        prefix, period = 137, 997
        # An unrelated intro must not pollute the stored periodic loop.
        pcm = [0] * prefix + [round(10000 * math.sin(2 * math.pi * 5 * i / period)) for i in range(period)]
        data, frequency, start, report = resample_wave(pcm, 32000, 72, 60, True, prefix)
        decoded = signed(data)
        loop = decoded[start:]
        self.assertGreater(start, round(prefix / report['source_samples_per_output']))
        self.assertEqual(len(loop), report['output_loop_period'])
        self.assertLess(abs(report['pitch_error_cents']), .001)
        self.assertGreater(frequency, 0)
        step = report['source_samples_per_output']
        phase = report['initial_source_phase_samples']
        # Independent analytic periodic sine at all stored loop points.
        ideal = [10000 / 256 * math.sin(2 * math.pi * 5 * (phase + i * step - prefix) / period)
                 for i in range(start, len(decoded))]
        self.assertLess(rms([a - b for a, b in zip(loop, ideal)]), .6)
        wrap_step = abs(loop[0] - loop[-1])
        maximum_neighbor = max(abs(a - b) for a, b in zip(loop, loop[1:]))
        self.assertLessEqual(wrap_step, maximum_neighbor + 1)

    def test_constant_loop_has_unity_dc_and_no_join_fade(self):
        data, _, start, report = resample_wave([8192] * 4096, 22050, 60, 60, True, 1024)
        self.assertEqual(set(signed(data[start:])), {32})
        self.assertEqual(report['pcm8_clipped_samples'], 0)

    def test_one_shot_zero_extension_retains_filter_tail_without_looping(self):
        data, _, start, report = resample_wave([12000] * 128, 22050, 60, 60)
        self.assertEqual(start, 0)
        self.assertIsNone(report['output_loop_period'])
        self.assertGreater(len(data), math.ceil(128 * 10512 / 22050))
        self.assertEqual(set(signed(data[-8:])), {0})

    def test_high_pitch_ratio_24_filters_aliases_and_keeps_periodic_dc(self):
        # LAST reaches a source step near 23; use 24 to exercise the extended
        # finite FIR support independently of actual ROM sample contents.
        rate = 10512 * 24
        data, _, start, report = resample_wave([8192] * 6144, rate, 60, 60, True, 1536)
        self.assertEqual(set(signed(data[start:])), {32})
        self.assertEqual(report['output_loop_period'], 192)
        self.assertLess(abs(report['pitch_error_cents']), .001)
        high = [round(12000 * math.sin(2 * math.pi * i / 12)) for i in range(6144)]
        out = signed(resample_wave(high, rate, 60, 60, True, 1536)[0])
        self.assertLess(rms(out[start:]), .6)

    def test_invalid_inputs_and_resource_bounds_fail_explicitly(self):
        for kwargs in ({'source_rate': float('nan')}, {'key': 128}, {'loop_start': 64},
                       {'mixing_rate': 0}, {'source_rate': 1_000_000}):
            params = dict(source_rate=22050, key=60, root_key=60)
            params.update(kwargs)
            with self.assertRaises(ValueError):
                resample_wave([0] * 64, **params)
        with self.assertRaisesRegex(ValueError, 'too short'):
            resample_wave([0] * 16, 32000, 72, 60, True)
        with self.assertRaisesRegex(ValueError, 'sample budget'):
            resample_wave([0] * 1_000_000, 8000, 60, 60)


if __name__ == '__main__':
    unittest.main()
