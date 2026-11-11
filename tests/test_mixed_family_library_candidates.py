"""Three source-specific public routes preserve independent candidate images."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_nds_experiment import build_experiment
from scan_audio import apply_bps, fingerprint

DIRECTORY = Path('/home/harp/projects/nds/roms')
BASE = ROOT.parent / 'roms/exe6.gba'
CASES = [('ssr1d', 'sf1-lastboss-delay', 29, '2859C9A7', 7, False),
         ('ssr2d', 'sf2-wifi-envelope-delay', 38, 'AB504353', 8, True),
         ('ssr3b', 'sf3-burai-envelope-delay', 24, '370026F7', 8, True)]


@unittest.skipUnless(BASE.exists() and all((DIRECTORY / (c[0] + '.nds')).exists()
                                         for c in CASES), 'local pinned originals unavailable')
class MixedFamilyLibraryCandidateTests(unittest.TestCase):
    def test_source_specific_routes_keep_independent_goldens_and_delay_modes(self):
        base = BASE.read_bytes()
        for profile, selector, index, crc, count, envelope in CASES:
            with self.subTest(selector=selector):
                source = (DIRECTORY / (profile + '.nds')).read_bytes()
                rom, patch, manifest, conversion, dependency, *_ = build_experiment(
                    source, base, song=selector, events=('1', '21', 'scene:communication'))
                self.assertEqual(fingerprint(rom)['crc32'], crc)
                self.assertEqual(apply_bps(base, patch)[0], rom)
                self.assertEqual(conversion['sequence_index'], index)
                self.assertEqual(conversion['track_groups'], [[i] for i in range(count)])
                self.assertEqual(len(dependency['tracks']), count)
                self.assertIn('delay_approximation', conversion['native_pitch_lfo'])
                self.assertEqual('envelope_approximation' in conversion, envelope)
                self.assertNotIn('bandlimited_pcm', conversion)
                self.assertNotIn('native_track_capacity', manifest)
                self.assertEqual(manifest['sound_mode_change']['pcm_channels'], 10)


if __name__ == '__main__':
    unittest.main()
