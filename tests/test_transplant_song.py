import sys
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_audio import apply_bps
from transplant_song import make_bps, transplant


class BpsExportTests(unittest.TestCase):
    def test_roundtrip_empty_identical_and_extended(self):
        for source, target in [(b'', b''), (b'abc', b'abc'), (b'abcdef', b'aXcdYfmore'), (b'abcdef', b'ab')]:
            with self.subTest(source=source, target=target):
                result, _ = apply_bps(source, make_bps(source, target))
                self.assertEqual(result, target)

    def test_roundtrip_long_literal_varint(self):
        target = bytes(range(256)) * 1000
        self.assertEqual(apply_bps(b'', make_bps(b'', target))[0], target)


@unittest.skipUnless(all((ROOT / p).exists() for p in ['roms/exe45.gba', 'roms/exegp.gba', 'references/exe45_pvp_0.6.0.bps']), 'local ROMs/patch unavailable')
class TransplantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (ROOT / 'roms/exe45.gba').read_bytes()
        cls.donor = (ROOT / 'roms/exegp.gba').read_bytes()
        cls.pvp, _ = apply_bps(cls.base, (ROOT / 'references/exe45_pvp_0.6.0.bps').read_bytes())
        cls.output, cls.manifest, cls.source, cls.target = transplant(cls.donor, cls.pvp)

    def test_only_declared_entry_and_mixer_configuration_change(self):
        a = 0x135214
        expected = bytearray(self.pvp)
        struct.pack_into('<I', expected, 0x504, 0x00930A0D)
        self.assertEqual(self.output[:a], expected[:a])
        self.assertEqual(self.output[a + 8:len(self.pvp)], self.pvp[a + 8:])
        self.assertEqual(struct.unpack_from('<HH', self.output, a + 4), (31, 31))

    def test_existing_nonempty_entry_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not empty'):
            transplant(self.donor, self.pvp, target_id=69)

    def test_samples_and_control_flow_survive(self):
        def sample_content(report, data):
            return sorted(data[s['file_offset']:s['file_offset'] + s['size_bytes']] for s in report['samples'])
        self.assertEqual(sample_content(self.source, self.donor), sample_content(self.target, self.output))
        for before, after in zip(self.source['tracks'], self.target['tracks']):
            self.assertEqual(before['notes'], after['notes'])
            self.assertEqual(before['ticks_before_repeat'], after['ticks_before_repeat'])
            self.assertEqual([e['name'] for e in before['events']], [e['name'] for e in after['events']])
        for pointer in self.manifest['relocated_pointer_fields']:
            actual = struct.unpack_from('<I', self.output, pointer['target_site'])[0]
            self.assertEqual(actual, 0x08000000 + pointer['target_target'])
            self.assertGreaterEqual(pointer['target_target'], len(self.pvp))

    def test_exported_patch_uses_original_exe45(self):
        reconstructed, info = apply_bps(self.base, make_bps(self.base, self.output))
        self.assertEqual(reconstructed, self.output)
        self.assertEqual(info['source_crc32'], 'A646601B')


if __name__ == '__main__':
    unittest.main()
