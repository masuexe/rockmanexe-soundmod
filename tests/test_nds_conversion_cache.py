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
from nds_conversion_cache import NdsConversionCache, digest
from nds_track_merge import convert_merged_song
from scan_audio import fingerprint
from test_nds_upward_antialias import archive, score

SPEC = ('ssr1', 0, 'fixture', 'Fixture', 0, False)


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
