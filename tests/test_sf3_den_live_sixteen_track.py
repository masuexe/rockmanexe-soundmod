"""Source-specific sixteen-track export and default-capacity rejection."""
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_nds_experiment import build_experiment, pack_converted_experiment
from scan_audio import apply_bps, fingerprint

SOURCE = Path('/home/harp/projects/nds/roms/ssr3b.nds')
BASE = ROOT.parent / 'roms/exe6.gba'


@unittest.skipUnless(SOURCE.exists() and BASE.exists(), 'local pinned ROMs unavailable')
class DenLiveTests(unittest.TestCase):
    def test_public_route_reproduces_private_golden_and_cannot_pack_with_default_capacity(self):
        source, base = SOURCE.read_bytes(), BASE.read_bytes()
        result = build_experiment(source, base, song='sf3-den-live-sixteen-track')
        rom, patch, manifest, conversion, dependency, blob, _, sdat = result
        self.assertEqual(fingerprint(rom)['crc32'], '1991593A')
        self.assertEqual(apply_bps(base, patch)[0], rom)
        self.assertEqual((conversion['source_track_count'], conversion['track_count']), (16, 16))
        self.assertEqual(conversion['track_groups'], [[i] for i in range(16)])
        self.assertEqual(manifest['native_track_capacity']['capacity'], 16)
        with self.assertRaisesRegex(ValueError, 'native capacity is 8'):
            pack_converted_experiment(source, base, 'ssr3b', sdat, 15, 'BGM_DEN_LIVE',
                                      blob, dependency, conversion)
        # An understated supplied report must not bypass the final ROM header check.
        understated = copy.deepcopy(dependency)
        understated['header']['track_count'] = 8
        understated['tracks'] = understated['tracks'][:8]
        with self.assertRaisesRegex(ValueError, 'native capacity is 8'):
            pack_converted_experiment(source, base, 'ssr3b', sdat, 15, 'BGM_DEN_LIVE',
                                      blob, understated, conversion)


if __name__ == '__main__':
    unittest.main()
