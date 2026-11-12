"""Preserve source-specific candidate images with recorded native voice limits."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_nds_experiment import build_experiment
from scan_audio import apply_bps, fingerprint

DIRECTORY = Path('/home/harp/projects/nds/roms')
BASE = ROOT.parent / 'roms/exe6.gba'
CASES = [('ssr1d', 'sf1-yumenoshima-lfo', 8, 'B9ACC156', False),
         ('ssr1d', 'sf1-kakushi-lfo', 19, '8F1D7055', False),
         ('ssr2d', 'sf2-friend-envelope', 14, '21D3206C', True)]


@unittest.skipUnless(BASE.exists() and all((DIRECTORY / (c[0] + '.nds')).exists()
                                         for c in CASES), 'local pinned originals unavailable')
class VoicePressureCandidateTests(unittest.TestCase):
    def test_named_routes_preserve_independent_goldens_without_new_modulation_modes(self):
        base = BASE.read_bytes()
        for profile, selector, index, crc, envelope in CASES:
            with self.subTest(selector=selector):
                source = (DIRECTORY / (profile + '.nds')).read_bytes()
                rom, patch, manifest, conversion, dependency, *_ = build_experiment(
                    source, base, song=selector, events=('1', '21', 'scene:communication'))
                self.assertEqual(fingerprint(rom)['crc32'], crc)
                self.assertEqual(apply_bps(base, patch)[0], rom)
                self.assertEqual(conversion['sequence_index'], index)
                source_tracks = list(range(7)) + [9] if selector == 'sf2-friend-envelope' else list(range(8))
                self.assertEqual(conversion['track_groups'], [[i] for i in source_tracks])
                self.assertEqual(len(dependency['tracks']), 8)
                self.assertIn('native_pitch_lfo', conversion)
                self.assertNotIn('delay_approximation', conversion['native_pitch_lfo'])
                self.assertEqual('envelope_approximation' in conversion, envelope)
                self.assertNotIn('bandlimited_pcm', conversion)
                self.assertNotIn('native_track_capacity', manifest)
                self.assertEqual(manifest['sound_mode_change']['pcm_channels'], 10)


if __name__ == '__main__':
    unittest.main()
