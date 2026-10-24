"""Explicit finite/future-use filtering retains tiny detunes, shared waves and END."""
import sys
import unittest
from pathlib import Path

sys.path[:0] = [str(Path('scripts').resolve()), str(Path('tests').resolve())]
from nds_track_merge import convert_merged_song
from build_nds_experiment import build_experiment
from scan_audio import apply_bps
from test_nds_upward_antialias import archive, score


def finite_program(bend=1, wait=12, delay=0, tempo=True):
    return (b'\xC7\x00' + (b'\xE1\x78\x00' if tempo else b'')
            + b'\x81\x02\xC5\x02' + bytes([0xC4, bend])
            + (bytes([0x80, delay]) if delay else b'')
            + bytes([60, 100, 12, 0x80, wait, 0xFF]))


OPTIONS = dict(bandlimited_pcm=True, bandlimited_upward_support=True,
               bandlimited_upward_future_support=True, finite_support=True)


class FiniteUpwardTests(unittest.TestCase):
    def test_one_unit_detune_and_exact_fine_are_preserved(self):
        _, dep, c = convert_merged_song(archive(finite_program()), 0, [(0,)], **OPTIONS)
        r = c['samples'][0]['resampling']
        self.assertEqual((r['source_key'], r['preparation_key'], r['positive_pitch_bound_units']),
                         (60, 61, 1))
        self.assertEqual(c['finite_song']['track_end_ticks'], {'0': 12})
        self.assertTrue(c['bandlimited_pcm']['finite_upward_preparation'])
        self.assertEqual(dep['tracks'][0]['termination'], 'fine')
        self.assertFalse(any(e['name'] == 'GOTO' for e in dep['tracks'][0]['events']))
        self.assertIn(65, [e['value'] for e in dep['tracks'][0]['events'] if e['name'] == 'TUNE'])

    def test_old_finite_opt_in_and_other_mode_guards_remain(self):
        with self.assertRaisesRegex(ValueError, 'plain looping filtered tracks'):
            convert_merged_song(archive(finite_program()), 0, [(0,)],
                                bandlimited_pcm=True, bandlimited_upward_support=True,
                                finite_support=True)
        with self.assertRaisesRegex(ValueError, 'upward bend'):
            convert_merged_song(archive(finite_program()), 0, [(0,)],
                                bandlimited_pcm=True, finite_support=True)
        for flag in ('native_pitch_lfo', 'envelope_support', 'finite_release_support'):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                convert_merged_song(archive(finite_program()), 0, [(0,)], **OPTIONS, **{flag: True})

    def test_looping_source_and_gate_after_end_still_fail(self):
        with self.assertRaisesRegex(ValueError, 'entirely finite'):
            convert_merged_song(archive(score()), 0, [(0,)], **OPTIONS)
        with self.assertRaises(ValueError):
            convert_merged_song(archive(finite_program(wait=6)), 0, [(0,)], **OPTIONS)

    def test_shared_wave_retains_the_later_echo_detune(self):
        header = b'\xFE\x03\x00\x93\x01' + bytes(3)
        first = finite_program(bend=0)
        second = len(header) + len(first)
        raw = header[:5] + second.to_bytes(3, 'little') + first + finite_program(delay=20, tempo=False)
        _, _, c = convert_merged_song(archive(raw), 0, [(0,), (1,)], **OPTIONS)
        self.assertEqual(len(c['samples']), 1)
        r = c['samples'][0]['resampling']
        self.assertEqual(r['earliest_use_ticks_by_source_track'], {'0': 0, '1': 20})
        self.assertEqual((r['positive_pitch_bound_units'], r['preparation_key']), (1, 61))
        self.assertEqual(c['finite_song']['track_end_ticks'], {'0': 12, '1': 32})

    @unittest.skipUnless(Path('/home/harp/projects/nds/roms/ssr1d.nds').exists()
                         and Path('../roms/exe6.gba').exists(), 'local verified game inputs unavailable')
    def test_henkan_four_long_gates_tiny_echo_pitch_and_zero_gain_headroom(self):
        source = Path('/home/harp/projects/nds/roms/ssr1d.nds').read_bytes()
        base = Path('../roms/exe6.gba').read_bytes()
        with self.assertRaisesRegex(ValueError, 'headroom'):
            build_experiment(source, base, song='sf1-henkan-antialias')
        out, bps, m, c, dep, *_ = build_experiment(
            source, base, song='sf1-henkan-antialias', song_gain_db=0,
            events=('1', '21', 'scene:communication'))
        self.assertEqual((c['source_track_count'], c['track_count'], len(c['note_mapping']),
                          len(c['samples'])), (4, 4, 4, 2))
        self.assertEqual([(n['tick'], n['duration'], n['source_key'], n['gba_key'])
                          for n in c['note_mapping']],
                         [(0, 534, 48, 127), (0, 534, 48, 127),
                          (20, 534, 48, 127), (20, 534, 48, 127)])
        self.assertEqual(c['finite_song']['track_end_ticks'], {'0': 534, '1': 534, '2': 554, '3': 554})
        self.assertTrue(all(s['resampling']['positive_pitch_bound_units'] == 1
                            and s['resampling']['preparation_key'] == 49 for s in c['samples']))
        self.assertEqual(len(c['long_note_aliases']), 4)
        self.assertTrue(all(t['termination'] == 'fine' for t in dep['tracks']))
        self.assertTrue(all([e['name'] for e in t['events']][-2:] == ['EOT', 'FINE'] for t in dep['tracks']))
        self.assertEqual(c['song_gain_db'], 0)
        self.assertEqual(apply_bps(base, bps)[0], out)
        expected = bytearray(base)
        for start, end in m['declared_prefix_ranges']:
            expected[start:end] = out[start:end]
        self.assertEqual(out[:len(base)], expected)
