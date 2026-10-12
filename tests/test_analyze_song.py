import sys
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze_song import ROM_BASE, analyze, trace_track


class SequenceTests(unittest.TestCase):
    def test_patterns_running_notes_and_controller_status(self):
        data = bytearray(100)
        data[:17] = bytes([0xBD, 2, 0xB3]) + struct.pack('<I', ROM_BASE + 32) + bytes([0xB3]) + struct.pack('<I', ROM_BASE + 32) + bytes([0xC4, 1, 0x81, 4, 0xB1])
        data[32:40] = bytes([0xD0, 60, 100, 0x81, 62, 0x81, 0xB4, 0xB1])
        result = trace_track(bytes(data), 0)
        self.assertEqual(result['termination'], 'fine')
        self.assertEqual(result['notes'], [(2, 60), (2, 62)])
        self.assertEqual(result['ticks_before_repeat'], 5)
        self.assertEqual(len(result['pointer_fields']), 2)
        running = [e for e in result['events'] if e['running']]
        self.assertEqual([e['name'] for e in running], ['NOTE', 'NOTE', 'MOD'])

    def test_inline_pattern_end_falls_through(self):
        result = trace_track(bytes([0xBD, 0, 0xB4, 0xD0, 60, 100, 0x81, 0xB1]), 0)
        self.assertEqual(result['notes'], [(0, 60)])

    def test_timed_loop_closes(self):
        data = bytes([0xBD, 0, 0xD0, 60, 100, 0x81, 0xB2]) + struct.pack('<I', ROM_BASE + 2)
        result = trace_track(data, 0)
        self.assertEqual(result['termination'], 'repeated_state')
        self.assertEqual(result['loop_ticks'], 1)

    def test_zero_time_loop_fails(self):
        with self.assertRaisesRegex(ValueError, 'Zero-time'):
            trace_track(bytes([0xB2]) + struct.pack('<I', ROM_BASE), 0)

    def test_unknown_commands_fail(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported command'):
            trace_track(bytes([0xB9, 0, 0, 0, 0xB1]), 0)

    def test_note_without_voice_fails(self):
        with self.assertRaisesRegex(ValueError, 'before VOICE'):
            trace_track(bytes([0xD0, 60, 100, 0x81, 0xB1]), 0)

    def test_branch_outside_rom_fails(self):
        with self.assertRaisesRegex(ValueError, 'outside ROM'):
            trace_track(bytes([0xB3]) + struct.pack('<I', ROM_BASE + 100), 0)


class DependencyTests(unittest.TestCase):
    def fixture(self):
        data = bytearray(8192)
        struct.pack_into('<IHH', data, 0, ROM_BASE + 32, 0, 0)
        struct.pack_into('<BBBBII', data, 32, 1, 0, 0, 128, ROM_BASE + 128, ROM_BASE + 512)
        data[512:520] = bytes([0xBD, 5, 0xDB, 36, 100, 0x8C, 0xB1, 0])
        struct.pack_into('<BBBBI4B', data, 128 + 5 * 12, 0x80, 0, 0, 0, ROM_BASE + 1536, 0, 0, 0, 0)
        struct.pack_into('<BBBBI4B', data, 1536 + 36 * 12, 0, 60, 0, 192, ROM_BASE + 4096, 255, 0, 255, 0)
        struct.pack_into('<HHIII', data, 4096, 0, 0, 14336000, 0, 4)
        data[4112:4116] = b'abcd'
        return data

    def test_only_used_drum_key_is_resolved(self):
        report = analyze(bytes(self.fixture()), 0, 0)
        self.assertEqual(len(report['tones']), 2)
        self.assertEqual(len(report['samples']), 1)
        self.assertEqual(report['samples'][0]['size_bytes'], 20)
        self.assertEqual(report['voice_key_pairs'], [(5, 36)])
        self.assertEqual(len(report['pointer_fields']), 4)

    def test_sample_size_must_fit_rom(self):
        data = self.fixture()
        struct.pack_into('<I', data, 4096 + 12, len(data))
        with self.assertRaisesRegex(ValueError, 'outside ROM'):
            analyze(bytes(data), 0, 0)

    def test_invalid_pcm_loop_rejected(self):
        data = self.fixture()
        struct.pack_into('<H', data, 4096 + 2, 0x4000)
        struct.pack_into('<I', data, 4096 + 8, 4)
        with self.assertRaisesRegex(ValueError, 'malformed PCM'):
            analyze(bytes(data), 0, 0)

    @unittest.skipUnless((ROOT / 'roms/exegp.gba').exists(), 'local donor unavailable')
    def test_local_exegp_song1_closure(self):
        report = analyze((ROOT / 'roms/exegp.gba').read_bytes(), 0x160658, 1)
        self.assertEqual(len(report['tracks']), 7)
        self.assertEqual(len(report['tones']), 13)
        self.assertEqual(len(report['samples']), 9)
        self.assertEqual({voice for voice, key in report['voice_key_pairs']}, set(range(6)))
        self.assertTrue(all(t['termination'] == 'fine' for t in report['tracks']))


if __name__ == '__main__':
    unittest.main()
