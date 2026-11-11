"""Capacity policy and prefix preservation for the explicit EXE6 experiment."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from native_track_capacity import capacity_plan, check_import_capacity, install_capacity
from target_profiles import target_profile


class CapacityPolicyTests(unittest.TestCase):
    def test_parsed_track_count_and_model_must_fit(self):
        report = lambda n, records: {'header': {'track_count': n}, 'tracks': [{}] * records}
        check_import_capacity({'song': report(8, 8)}, 8)
        check_import_capacity({'song': report(16, 16)}, 16)
        for count, records, capacity in ((9, 9, 8), (16, 16, 8), (17, 17, 16), (8, 7, 8), (0, 0, 8)):
            with self.subTest(count=count, records=records, capacity=capacity):
                with self.assertRaises(ValueError):
                    check_import_capacity({'song': report(count, records)}, capacity)

    def test_option_rejects_other_capacities_and_other_targets(self):
        target = target_profile('exegp')
        entry = target['layout']['player_table_offset'] + target['layout']['music_player'] * 12
        rom = bytearray(entry + 12)
        rom[entry + 8] = 8
        self.assertEqual(capacity_plan(rom, target), (8, None))
        for value in (True, 8, 17, 16.0, 16):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    capacity_plan(rom, target, value)


@unittest.skipUnless(all((ROOT.parent / 'roms' / (key + '.gba')).exists()
                        for key in ('exe6', 'exe6f')), 'local pinned EXE6 originals unavailable')
class PinnedCapacityTests(unittest.TestCase):
    def test_both_targets_preserve_every_effect_entry_and_all_other_prefix_bytes(self):
        for key in ('exe6', 'exe6f'):
            with self.subTest(key=key):
                rom = (ROOT.parent / 'roms' / (key + '.gba')).read_bytes()
                target = target_profile(key)
                self.assertEqual(capacity_plan(rom, target), (8, None))
                count, plan = capacity_plan(rom, target, 16)
                self.assertEqual(count, 16)
                output = bytearray(rom)
                def allocate(raw):
                    output.extend(bytes(-len(output) % 4))
                    offset = len(output)
                    output.extend(raw)
                    return offset
                ranges, metadata = install_capacity(output, plan, allocate)
                expected = bytearray(rom)
                for a, b in ranges:
                    expected[a:b] = output[a:b]
                self.assertEqual(output[:len(rom)], expected)
                table = target['layout']['player_table_offset']
                self.assertEqual(output[table:table + 31 * 12], rom[table:table + 31 * 12])
                self.assertEqual(struct.unpack_from('<IB', output, table + 31 * 12 + 4), (0x0203FA00, 16))
                self.assertEqual(output[0x2BC4:0x2BCC], rom[0x2BC4:0x2BCC])
                self.assertEqual(metadata['track_memory']['size_bytes'], 1280)
                self.assertEqual(metadata['battle_clear']['stub_size'], 56)

    def test_modified_original_and_conflicting_hook_are_rejected_before_allocation(self):
        rom = (ROOT.parent / 'roms/exe6.gba').read_bytes()
        target = target_profile('exe6')
        changed = bytearray(rom)
        changed[0x71E0] ^= 1
        with self.assertRaises(ValueError):
            capacity_plan(changed, target, 16)
        _, plan = capacity_plan(rom, target, 16)
        for site in (0x71E0, plan['entry_offset'] + 4):
            changed = bytearray(rom)
            changed[site] ^= 1
            def allocate(raw):
                self.fail('Conflicting prefix must fail before allocation')
            with self.assertRaises(ValueError):
                install_capacity(changed, plan, allocate)


if __name__ == '__main__':
    unittest.main()
