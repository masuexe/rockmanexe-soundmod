import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_unified import build, resolve_pools, Thumb, TABLE_REFERENCES, Relocator
from scan_audio import apply_bps
from unified_catalog import catalog
from validate_song import expected_state
from analyze_song import trace_track, ROM_BASE, analyze


class LoopModelTests(unittest.TestCase):
    def test_running_note_state_across_repeated_loop(self):
        data = bytearray(128)
        sequence = bytes([0xBD, 0, 0xD0, 60, 100, 0x81, 62, 0x81, 0xB2]) + struct.pack('<I', ROM_BASE + 2)
        data[:len(sequence)] = sequence
        data[64:76] = bytes.fromhex('003c000000000000ff00ff00')
        track = trace_track(bytes(data), 0)
        for clock in range(1, 15):
            state = expected_state(track, clock, bytes(data), 64)
            self.assertEqual(state['key'], 60 if clock % 2 else 62)
            self.assertEqual(state['velocity'], 100)
            self.assertFalse(state['ended'])

    def test_identical_pcm_contents_can_share_one_relocated_sample(self):
        data = bytearray(16384)
        struct.pack_into('<IHH', data, 0, ROM_BASE + 32, 0, 0)
        struct.pack_into('<BBBBII', data, 32, 1, 0, 0, 128, ROM_BASE + 128, ROM_BASE + 512)
        sequence = bytes([0xBD, 0, 0xD0, 60, 100, 0x81, 0xBD, 1, 0xD0, 60, 100, 0x81, 0xB1])
        data[512:512 + len(sequence)] = sequence
        for voice, wave in [(0, 4096), (1, 8192)]:
            struct.pack_into('<BBBBI4B', data, 128 + voice * 12, 0, 60, 0, 0, ROM_BASE + wave, 255, 0, 255, 0)
            struct.pack_into('<HHIII', data, wave, 0, 0, 14336000, 0, 4)
            data[wave + 16:wave + 20] = b'abcd'
        source = analyze(bytes(data), 0, 0)
        relocator = Relocator(bytes(64), [('fixture', source)])
        header = relocator.import_song('fixture', bytes(data), source)
        struct.pack_into('<IHH', relocator.output, 0, ROM_BASE + header, 31, 31)
        result = analyze(bytes(relocator.output), 0, 0)
        self.assertEqual(len(source['samples']), 2)
        self.assertEqual(len(result['samples']), 1)
        self.assertEqual(result['voice_key_pairs'], source['voice_key_pairs'])
        self.assertEqual(relocator.stats['resource_cache_hits'], 1)

    def test_branch_range_is_checked(self):
        code = Thumb(0)
        code.branch('distant', condition=0)
        for _ in range(200):
            code.emit(0x46C0)
        code.label('distant')
        with self.assertRaisesRegex(ValueError, 'out of range'):
            code.finish()


@unittest.skipUnless(all((ROOT / path).exists() for path in ['roms/exe45.gba', 'roms/exegp.gba', 'references/exe45_pvp_0.6.0.bps', 'references/exe45_soundmod.bps']), 'local sources unavailable')
class UnifiedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (ROOT / 'roms/exe45.gba').read_bytes()
        cls.gp = (ROOT / 'roms/exegp.gba').read_bytes()
        cls.pvp, _ = apply_bps(cls.base, (ROOT / 'references/exe45_pvp_0.6.0.bps').read_bytes())
        cls.sound, _ = apply_bps(cls.base, (ROOT / 'references/exe45_soundmod.bps').read_bytes())
        cls.config = json.loads((ROOT / 'config/playlist.json').read_text())
        cls.output, cls.value, cls.manifest = build(cls.base, cls.pvp, cls.sound, cls.gp, cls.config)
        cls.rows = {row['key']: row for row in cls.value['entries']}

    def test_stable_ids_and_capacity_reservations(self):
        self.assertEqual(self.value['table_entry_count'], 637)
        self.assertEqual(self.rows['soundmod:0']['target_index'], 499)
        self.assertEqual(self.rows['soundmod:69']['target_index'], 531)
        self.assertEqual(self.rows['exegp:1']['target_index'], 551)
        self.assertEqual(self.rows['exegp:5']['availability'], 'exceeds_target_track_capacity')
        self.assertFalse(self.rows['exegp:5']['playlist_eligible'])
        self.assertFalse(self.rows['exegp:100']['playlist_eligible'])
        self.assertEqual(len(self.manifest['imports']), 67)

    def test_all_original_entries_and_prefix_ranges_preserved(self):
        table = self.manifest['target_table_file_offset']
        self.assertEqual(self.output[table:table + 499 * 8], self.pvp[0x135214:0x1361AC])
        expected = bytearray(self.pvp)
        for a, b in self.manifest['declared_prefix_ranges']:
            expected[a:b] = self.output[a:b]
        self.assertEqual(self.output[:len(self.pvp)], expected)
        for offset in TABLE_REFERENCES:
            self.assertEqual(struct.unpack_from('<I', self.output, offset)[0], ROM_BASE + table)

    def test_pvp_effect_and_soundmod_music_use_distinct_ids(self):
        table = self.manifest['target_table_file_offset']
        native = self.output[table + 69 * 8:table + 70 * 8]
        self.assertEqual(native, self.pvp[0x135214 + 69 * 8:0x135214 + 70 * 8])
        imported = struct.unpack_from('<IHH', self.output, table + self.rows['soundmod:69']['target_index'] * 8)
        self.assertEqual(imported[1:], (31, 31))
        self.assertNotEqual(imported[0], struct.unpack_from('<I', native)[0])

    def test_selector_remaps_conflicting_pool_ids(self):
        rule = next(r for r in self.manifest['hook']['rules'] if r['trigger_id'] == 89)
        self.assertEqual(rule['ids'][3], 531)
        self.assertNotIn(69, rule['ids'])
        self.assertTrue(self.manifest['resource_statistics']['resource_cache_hits'] > 0)

    def test_effects_and_unsupported_music_are_rejected(self):
        for trigger, key in [('69', 'exegp:1'), ('55', 'pvp:69'), ('55', 'exegp:5'), ('55', 'exegp:100')]:
            with self.subTest(trigger=trigger, key=key), self.assertRaises(ValueError):
                resolve_pools({'schema_version': 1, 'pools': {trigger: {'tracks': [key]}}}, self.value)

    def test_arbitrary_three_track_pool_keeps_catalog_ids(self):
        rules = resolve_pools({'schema_version': 1, 'pools': {'55': {'tracks': ['exegp:1', 'soundmod:0', 'soundmod:1']}}}, self.value)
        self.assertEqual(rules[0]['ids'], [551, 499, 500])
        self.assertEqual(self.rows['soundmod:69']['target_index'], 531)

    def test_reserved_foreign_slots_remain_empty(self):
        table = self.manifest['target_table_file_offset']
        for key in ['exegp:5', 'exegp:100']:
            index = self.rows[key]['target_index']
            self.assertEqual(self.output[table + index * 8:table + (index + 1) * 8], self.pvp[0x135214:0x13521C])


if __name__ == '__main__':
    unittest.main()
