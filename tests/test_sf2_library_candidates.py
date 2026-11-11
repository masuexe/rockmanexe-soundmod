"""Public routes must preserve the independently checked SF2 candidate ROMs."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_nds_experiment import build_experiment
from scan_audio import apply_bps, fingerprint

SOURCE = Path('/home/harp/projects/nds/roms/ssr2d.nds')
BASE = ROOT.parent / 'roms/exe6.gba'


@unittest.skipUnless(SOURCE.exists() and BASE.exists(), 'local pinned originals unavailable')
class Sf2LibraryCandidateTests(unittest.TestCase):
    def test_named_routes_keep_independent_candidate_goldens_and_effect_headroom(self):
        source, base = SOURCE.read_bytes(), BASE.read_bytes()
        cases = [('sf2-teki-delay', 1, '724F3B97', False),
                 ('sf2-burai-envelope-delay', 2, 'CB386A07', True),
                 ('sf2-ski-envelope-delay', 5, '9F70F669', True)]
        for selector, index, crc, envelope in cases:
            with self.subTest(selector=selector):
                rom, patch, manifest, conversion, dependency, *_ = build_experiment(
                    source, base, song=selector, events=('1', '21', 'scene:communication'))
                self.assertEqual(fingerprint(rom)['crc32'], crc)
                self.assertEqual(apply_bps(base, patch)[0], rom)
                self.assertEqual(conversion['sequence_index'], index)
                self.assertEqual(conversion['track_groups'], [[i] for i in range(8)])
                self.assertEqual(len(dependency['tracks']), 8)
                self.assertEqual('envelope_approximation' in conversion, envelope)
                self.assertIn('delay_approximation', conversion['native_pitch_lfo'])
                self.assertNotIn('native_track_capacity', manifest)
                self.assertEqual(manifest['sound_mode_change']['pcm_channels'], 10)


if __name__ == '__main__':
    unittest.main()
