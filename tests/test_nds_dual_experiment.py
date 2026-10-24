"""Same-source converted banks must remain distinct in a dual-song ROM."""
import copy
import json
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
from build_nds_dual_experiment import build_dual_experiment, validate_plan
from scan_audio import apply_bps, fingerprint
from analyze_song import analyze

PLAN = Path('examples/nds-dual-ura-henkan.json')


class DualNdsTests(unittest.TestCase):
    def test_fixed_role_plan_rejects_missing_or_ambiguous_routing(self):
        valid = json.loads(PLAN.read_text())
        validate_plan(valid)
        for change in ({'schema_version': 2}, {'communication': 'random'}, {'unexpected': True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_plan({**valid, **change})
        with self.assertRaises(ValueError):
            validate_plan({'schema_version': 1, 'title': valid['title']})
        bad = copy.deepcopy(valid)
        bad['battle'].pop('song')
        with self.assertRaises(ValueError):
            validate_plan(bad)

    @unittest.skipUnless(Path('/home/harp/projects/nds/roms/ssr1d.nds').exists()
                         and Path('../roms/exe6.gba').exists(), 'local verified game inputs unavailable')
    def test_two_same_source_banks_routes_and_original_prefix(self):
        base = Path('../roms/exe6.gba').read_bytes()
        out, bps, m, catalog, songs = build_dual_experiment(base, json.loads(PLAN.read_text()))
        self.assertEqual(apply_bps(base, bps)[0], out)
        self.assertEqual(m['table_entry_count'], 476)
        self.assertEqual({r['trigger_id']: r['ids'] for r in m['hook']['rules']},
                         {1: [474], 21: [475], 65534: [474]})
        metadata = m['nds_dual_conversion']['songs']
        self.assertNotEqual(metadata['title']['source_key'], metadata['battle']['source_key'])
        self.assertEqual(metadata['title']['source_rom_fingerprint'], metadata['battle']['source_rom_fingerprint'])
        self.assertEqual([metadata[x]['song_gain_db'] for x in ('title', 'battle')], [3.5, 0])
        headers, banks, wave_sets = [], [], []
        for role, slot in [('title', 474), ('battle', 475)]:
            dep = analyze(out, m['target_table_file_offset'], slot)
            headers.append(dep['header']['file_offset'])
            banks.append(dep['header']['tone_bank']['file_offset'])
            wave_sets.append({s['file_offset'] for s in dep['samples']})
            self.assertEqual(metadata[role]['generated_mplay_fingerprint'], fingerprint(songs[role]['blob']))
            for packed, original in zip(dep['tracks'], songs[role]['dependency']['tracks']):
                self.assertEqual([(e['ticks'], e['name'], e.get('key'), e.get('value')) for e in packed['events']],
                                 [(e['ticks'], e['name'], e.get('key'), e.get('value')) for e in original['events']])
                self.assertEqual(packed['termination'], original['termination'])
        self.assertEqual(len(set(headers)), 2)
        self.assertEqual(len(set(banks)), 2)
        self.assertFalse(wave_sets[0] & wave_sets[1])
        self.assertEqual([len(s) for s in wave_sets], [22, 2])
        self.assertEqual(out[m['target_table_file_offset']:m['target_table_file_offset'] + 474 * 8],
                         base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in m['declared_prefix_ranges']:
            expected[start:end] = out[start:end]
        self.assertEqual(out[:len(base)], expected)
