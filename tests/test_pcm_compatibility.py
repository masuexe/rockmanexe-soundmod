"""Fixed-step PCM must preserve duration without changing other instruments."""
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from analyze_song import analyze, ROM_BASE
from build_unified import Relocator
from pcm_compatibility import FIXED_PCM_RATES, resample_fixed_pcm


class FixedPCMTests(unittest.TestCase):
    def wave(self, payload=b'\x00\x40\xc0\x00'):
        return struct.pack('<HHIII', 0, 0, 10512*1024, 0, len(payload))+payload

    def test_signed_interpolation_preserves_speed_and_end_time(self):
        result = resample_fixed_pcm(self.wave(), 10512, 15768)
        self.assertEqual(struct.unpack_from('<HHIII', result), (0, 0, 15768*1024, 0, 6))
        self.assertEqual(result[16:], bytes([0, 43, 21, 192, 235, 0]))
        self.assertEqual(4/10512, 6/15768)

    def test_odd_length_duration_error_is_bounded_by_one_target_sample(self):
        result = resample_fixed_pcm(self.wave(b'\x01\xff\x00'), 10512, 15768)
        count = struct.unpack_from('<I', result, 12)[0]
        self.assertGreaterEqual(count/15768, 3/10512)
        self.assertLess(count/15768-3/10512, 1/15768)

    def test_equal_rate_keeps_every_encoded_byte(self):
        original = self.wave()
        self.assertEqual(resample_fixed_pcm(original, 10512, 10512), original)

    def test_invalid_loop_and_malformed_payload_are_rejected(self):
        loop = bytearray(self.wave())
        struct.pack_into('<H', loop, 2, 0x4000)
        struct.pack_into('<I', loop, 8, 4)
        for value in [loop, self.wave()[:-1], b'bad header']:
            with self.assertRaises(ValueError):
                resample_fixed_pcm(value, 10512, 15768)

    def test_loop_period_is_exact_when_one_source_period_cannot_fit(self):
        loop = bytearray(self.wave(bytes([0, 64, 192, 0, 64])))
        struct.pack_into('<H', loop, 2, 0x4000)
        struct.pack_into('<I', loop, 8, 2)
        output = resample_fixed_pcm(loop, 10512, 15768)
        kind, flags, rate, start, size = struct.unpack_from('<HHIII', output)
        self.assertEqual((kind, flags, rate, start, size), (0, 0x4000, 15768*1024, 3, 12))
        self.assertEqual((size-start)/15768, 2*(5-2)/10512)
        self.assertEqual(output[16+start:], bytes([192, 235, 21, 64, 235, 213, 0, 43, 21]))

    def fixture(self):
        data = bytearray(8192)
        struct.pack_into('<IHH', data, 0, ROM_BASE+32, 0, 0)
        struct.pack_into('<BBBBII', data, 32, 1, 0, 0, 128, ROM_BASE+128, ROM_BASE+512)
        sequence = bytes([0xBD, 0, 0xC4, 4, 0xD0, 60, 100, 0x81,
                          0xBD, 1, 0xD0, 60, 100, 0x81, 0xB1])
        data[512:512+len(sequence)] = sequence
        for voice, kind in [(0, 8), (1, 0)]:
            struct.pack_into('<BBBBI4B', data, 128+voice*12, kind, 60, 0, 0,
                             ROM_BASE+4096, 255, 0, 255, 0)
        data[4096:4116] = self.wave()
        return bytes(data)

    def test_shared_wave_is_private_to_fixed_mode_and_reused_across_imports(self):
        donor = self.fixture()
        report = analyze(donor, 0, 0)
        with patch.dict(FIXED_PCM_RATES, {report['rom_fingerprint']['sha256']: 10512}):
            relocator = Relocator(bytes(64), [('fixture', report)], 15768)
            header = relocator.import_song('fixture', donor, report)
            first = relocator.mapping_reports[-1]['audio_adjustments'][0]
            relocator.import_song('fixture', donor, report)
            second = relocator.mapping_reports[-1]['audio_adjustments'][0]
        self.assertEqual(first['target_wave_offset'], second['target_wave_offset'])
        struct.pack_into('<IHH', relocator.output, 0, ROM_BASE+header, 0, 0)
        parsed = analyze(bytes(relocator.output), 0, 0)
        self.assertEqual(sorted(t['type_raw'] for t in parsed['tones']), [0, 8])
        waves = {s['file_offset']: bytes(relocator.output[s['file_offset']:s['file_offset']+s['size_bytes']])
                 for s in parsed['samples']}
        self.assertEqual(set(waves.values()), {self.wave(), resample_fixed_pcm(self.wave(), 10512, 15768)})
        for mapping in relocator.mapping_reports:
            for field in mapping['pointers']:
                self.assertEqual(struct.unpack_from('<I', relocator.output, field['target_site'])[0],
                                 ROM_BASE+field['target_offset'])
        # Keeping type 8 also preserves its original behavior with pitch modulation.
        self.assertEqual(parsed['tracks'][0]['events'][1]['name'], 'MOD')
        self.assertEqual(parsed['tracks'][0]['events'][1]['value'], 4)

    def test_unknown_source_rate_is_not_guessed_from_the_wave_header(self):
        donor = self.fixture()
        report = analyze(donor, 0, 0)
        relocator = Relocator(bytes(64), [('fixture', report)], 15768)
        relocator.import_song('fixture', donor, report)
        self.assertEqual(relocator.mapping_reports[0]['audio_adjustments'], [])


if __name__ == '__main__':
    unittest.main()
