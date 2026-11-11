"""Public SF1 routes preserve independently checked candidate ROMs."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_nds_experiment import build_experiment
from scan_audio import apply_bps, fingerprint

SOURCE = Path('/home/harp/projects/nds/roms/ssr1d.nds')
BASE = ROOT.parent / 'roms/exe6.gba'


@unittest.skipUnless(SOURCE.exists() and BASE.exists(), 'local pinned originals unavailable')
class Sf1LibraryCandidateTests(unittest.TestCase):
    def test_routes_preserve_independent_goldens_tracks_and_lfo_modes(self):
        source, base = SOURCE.read_bytes(), BASE.read_bytes()
        cases = [('sf1-dempa-delay', 10, '831E7C9F', 7, True),
                 ('sf1-truck-delay', 12, '48BD254D', 8, True),
                 ('sf1-gowadenno-lfo', 15, '7FCD4EDB', 8, False)]
        for selector, index, crc, count, delayed in cases:
            with self.subTest(selector=selector):
                rom, patch, manifest, conversion, dependency, *_ = build_experiment(
                    source, base, song=selector, events=('1', '21', 'scene:communication'))
                self.assertEqual(fingerprint(rom)['crc32'], crc)
                self.assertEqual(apply_bps(base, patch)[0], rom)
                self.assertEqual(conversion['sequence_index'], index)
                self.assertEqual(conversion['track_groups'], [[i] for i in range(count)])
                self.assertEqual(len(dependency['tracks']), count)
                self.assertEqual('delay_approximation' in conversion['native_pitch_lfo'], delayed)
                self.assertNotIn('envelope_approximation', conversion)
                self.assertNotIn('native_track_capacity', manifest)
                self.assertEqual(manifest['sound_mode_change']['pcm_channels'], 10)


if __name__ == '__main__':
    unittest.main()
