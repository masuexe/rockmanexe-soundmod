"""EXE4.5 originals can be music donors as well as pre-patch inputs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from manager_backend import Manager
from original_catalog import catalog_originals, identify
from scan_audio import apply_bps
from test_manager import finish

ROMS = ROOT.parent/'roms'


@unittest.skipUnless(all((ROMS/name).is_file() for name in ['exe45.gba', 'exegp.gba', 'exe1.gba']),
                     'Original donor ROMs unavailable')
class Exe45SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (ROMS/'exe45.gba').read_bytes()
        cls.gp = (ROMS/'exegp.gba').read_bytes()
        cls.exe1 = (ROMS/'exe1.gba').read_bytes()

    def test_identity_accepts_original_and_rejects_modified_revision(self):
        self.assertEqual(identify(self.original), 'exe45')
        modified = bytearray(self.original)
        modified[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'original music ROM revision'):
            identify(modified)

    def test_appended_donor_range_preserves_existing_keys_and_table_span(self):
        old, _ = catalog_originals(self.gp, self.gp, {'exe1': self.exe1})
        new, _ = catalog_originals(self.gp, self.gp, {'exe1': self.exe1, 'exe45': self.original})
        self.assertEqual(old['table_entry_count'], 8455)
        self.assertEqual(new['table_entry_count'], 8954)
        before = {r['key']:r['target_index'] for r in old['entries']}
        after = {r['key']:r['target_index'] for r in new['entries']}
        self.assertTrue(all(after[key]==index for key, index in before.items()))
        self.assertEqual(after['exe45:55'], 8455+55)
        self.assertEqual(after['exe45:498'], 8953)
        self.assertEqual(len(set(after.values())), len(after))

    def test_upload_discovery_and_export_use_music_source_role(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = Manager(temp, target='exegp')
            try:
                self.assertIn('exe45', {r['key'] for r in manager.state()['source_options']})
                target = manager.inputs['base']
                state = manager.upload('rom', 'renamed-exe45.gba', self.original)
                self.assertEqual(state['added_source'], 'exe45')
                self.assertEqual(manager.inputs['base'], target)
                finish(manager, manager.load(['exe45']))
                self.assertEqual(manager.selected_target, 'exegp')
                row = next(r for r in manager.value['entries'] if r['key']=='exe45:55')
                self.assertTrue(row['playlist_eligible'])
                project = {'schema_version':1,'target_profile':'exegp','pools':{'1':{'tracks':['exe45:55']}}}
                job = finish(manager, manager.export(project))
                image = manager.file(job['id'], 'unified.gba').read_bytes()
                self.assertEqual(apply_bps(self.gp, manager.file(job['id'], 'unified.bps').read_bytes())[0], image)
                manifest = json.loads((Path(job['result']['directory'])/'build.json').read_text())
                self.assertEqual(manifest['imports'][0]['key'], 'exe45:55')
                self.assertEqual(len(manifest['imports'][0]['audio_adjustments']), 3)
            finally:
                manager.close()
            restored = Manager(temp, target='exegp')
            try:
                self.assertIn('exe45', restored.selected_sources)
                self.assertEqual(restored.source_paths['exe45'][1].read_bytes(), self.original)
            finally:
                restored.close()


if __name__ == '__main__':
    unittest.main()
