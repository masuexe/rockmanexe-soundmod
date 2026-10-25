"""Cache integrity, input/config invalidation, native report types and failures."""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path('scripts').resolve()), str(Path('tests').resolve())]
from nds_conversion_cache import NdsConversionCache, conversion_files, digest, toolchain_fingerprint
from nds_track_merge import convert_merged_song
from scan_audio import fingerprint
from test_nds_upward_antialias import archive, score

SPEC = ('ssr1', 0, 'fixture', 'Fixture', 0, False)


class ConversionDependencyTests(unittest.TestCase):
    def test_registry_and_manager_edits_keep_keys_but_nested_converter_edits_do_not(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            scripts = root / 'scripts'
            scripts.mkdir()
            (root / 'config').mkdir()
            (scripts / 'converter.py').write_text('from helpers import value\n')
            (scripts / 'helpers.py').write_text('def optional():\n import dsp\n')
            (scripts / 'dsp.py').write_text('import converter\nvalue=1\n')
            key = toolchain_fingerprint(root, ('converter',))
            (scripts / 'nds_catalog.py').write_text('SONGS = ["new registration"]\n')
            (scripts / 'manager_backend.py').write_text('label = "new UI"\n')
            self.assertEqual(toolchain_fingerprint(root, ('converter',)), key)
            (scripts / 'dsp.py').write_text('import converter\nvalue=2\n')
            self.assertNotEqual(toolchain_fingerprint(root, ('converter',)), key)

    def test_configuration_and_environment_still_invalidate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'scripts').mkdir()
            (root / 'config').mkdir()
            (root / 'scripts/converter.py').write_text('value=1\n')
            key = toolchain_fingerprint(root, ('converter',))
            (root / 'config/target.json').write_text('{"rate": 10512}')
            changed = toolchain_fingerprint(root, ('converter',))
            self.assertNotEqual(changed, key)
            with patch('nds_conversion_cache.platform.machine', return_value='changed-machine'):
                self.assertNotEqual(toolchain_fingerprint(root, ('converter',)), changed)

    def test_missing_or_invalid_conversion_dependencies_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'scripts').mkdir()
            with self.assertRaises(FileNotFoundError):
                toolchain_fingerprint(root, ('converter',))
            (root / 'scripts/converter.py').write_text('def invalid(')
            with self.assertRaises(SyntaxError):
                toolchain_fingerprint(root, ('converter',))

    def test_real_dependency_closure_keeps_audio_modules_and_excludes_manager(self):
        names = {p.name for p in conversion_files()}
        self.assertTrue({'build_nds_experiment.py', 'nds_music.py', 'nds_resample.py',
                         'nds_track_merge.py', 'nds_lfo.py', 'nds_variable_lfo.py',
                         'target_profiles.py', 'rom-profiles.json'} <= names)
        self.assertFalse({'nds_catalog.py', 'manager_backend.py', 'manage_sound.py',
                          'nds_conversion_cache.py'} & names)


class NdsConversionCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.blob, _, conversion = convert_merged_song(archive(score(bend=0)), 0, [(0,)])
        self.conversion = {**conversion, 'song_gain_db': 0, 'numeric_keys': {2:'two',10:'ten'}}
        self.identity = {'schema_version':1, 'toolchain':'v1', 'source':fingerprint(b'source'),
                         'source_profile':'ssr1d', 'sdat':fingerprint(b'sdat'), 'target':fingerprint(b'base'),
                         'target_profile':'exe6', 'selector':'fixture', 'sequence_index':0, 'gain_db':0,
                         'finite':False, 'track_count':1, 'pcm_channels':10}
        self.origin = {'source_profile':'ssr1d', 'source_rom_fingerprint':self.identity['source'],
                       'sdat_fingerprint':self.identity['sdat'], 'sequence_index':0, 'song_gain_db':0,
                       'generated_mplay_fingerprint':fingerprint(self.blob)}
        self.identity_patch = patch('nds_conversion_cache.conversion_identity', side_effect=lambda *a:copy.deepcopy(self.identity))
        self.identity_patch.start()
        self.builder = patch('nds_conversion_cache.build_experiment', side_effect=self.build).start()

    def tearDown(self):
        patch.stopall()
        self.temp.cleanup()

    def build(self, *args, **kwargs):
        c = {**self.conversion, 'song_gain_db':self.identity['gain_db']}
        o = {**self.origin, 'source_rom_fingerprint':self.identity['source'],
             'song_gain_db':self.identity['gain_db']}
        return None, None, {'nds_conversion':o}, c, None, self.blob, None, None

    def get(self, cache):
        return cache.get(b'source', b'base', SPEC, 1)

    def test_cold_memory_and_restarted_disk_results_keep_note_tuples(self):
        first = NdsConversionCache(self.directory)
        result = self.get(first)
        self.assertEqual(self.get(first), result)
        self.assertEqual(self.builder.call_count, 1)
        second = NdsConversionCache(self.directory)
        cached = self.get(second)
        self.assertEqual(cached[0], result[0])
        self.assertEqual(cached[1], result[1])
        self.assertTrue(all(isinstance(pair, tuple) and all(isinstance(k, int) for k in pair) for pair in cached[1]['tracks'][0]['notes']))
        self.assertEqual(second.stats['disk_hits'], 1)
        self.assertEqual(self.builder.call_count, 1)

    def test_truncated_and_checksum_mismatched_entries_rebuild(self):
        self.get(NdsConversionCache(self.directory))
        path = next(self.directory.glob('*.json'))
        for raw in (b'{broken', b'{}'):
            path.write_bytes(raw)
            cache = NdsConversionCache(self.directory)
            self.get(cache)
            self.assertEqual(cache.stats['invalid_entries'], 1)
            self.assertEqual(cache.stats['conversions'], 1)
        record = json.loads(path.read_bytes())
        record['payload']['conversion']['song_gain_db'] = 12
        path.write_text(json.dumps(record))
        self.get(NdsConversionCache(self.directory))
        self.assertEqual(self.builder.call_count, 4)

    def test_valid_checksum_cannot_hide_invalid_pcm_container_or_configuration(self):
        self.get(NdsConversionCache(self.directory))
        path = next(self.directory.glob('*.json'))
        record = json.loads(path.read_bytes())
        record['payload']['blob'] = base64.b64encode(b'bad container').decode()
        record['payload']['origin']['generated_mplay_fingerprint'] = fingerprint(b'bad container')
        record['payload_digest'] = digest(record['payload'])
        path.write_text(json.dumps(record))
        cache = NdsConversionCache(self.directory)
        self.get(cache)
        self.assertEqual(cache.stats['invalid_entries'], 1)
        record = json.loads(path.read_bytes())
        record['payload']['conversion']['finite_song'] = {'unexpected': True}
        record['payload_digest'] = digest(record['payload'])
        path.write_text(json.dumps(record))
        self.get(NdsConversionCache(self.directory))
        self.assertEqual(self.builder.call_count, 3)

    def test_source_target_toolchain_and_gain_changes_miss_old_entries(self):
        self.get(NdsConversionCache(self.directory))
        for change in ({'source':fingerprint(b'changed original')},
                       {'target':fingerprint(b'falzar'), 'target_profile':'exe6f'},
                       {'toolchain':'v2'}, {'gain_db':3.5}):
            self.identity.update(change)
            cache = NdsConversionCache(self.directory)
            self.get(cache)
            self.assertEqual(cache.stats['disk_hits'], 0)
            self.assertEqual(cache.stats['conversions'], 1)
        self.assertEqual(self.builder.call_count, 5)

    def test_interrupted_atomic_write_does_not_block_valid_output_or_leave_temp(self):
        cache = NdsConversionCache(self.directory)
        with patch('nds_conversion_cache.os.replace', side_effect=OSError('read only')):
            result = self.get(cache)
        self.assertEqual(result[0], self.blob)
        self.assertEqual(list(self.directory.iterdir()), [])
        self.get(cache)
        self.assertEqual(self.builder.call_count, 1)

    def test_converter_failures_propagate_without_creating_a_cache_entry(self):
        self.builder.side_effect = ValueError('headroom guard')
        with self.assertRaisesRegex(ValueError, 'headroom guard'):
            self.get(NdsConversionCache(self.directory))
        self.assertEqual(list(self.directory.iterdir()), [])
