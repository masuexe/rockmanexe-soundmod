"""Filtered SF2 public routes preserve independently checked candidate images."""
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
class Sf2FilteredLibraryCandidateTests(unittest.TestCase):
    def test_filtered_routes_keep_independent_goldens_and_singleton_schedules(self):
        source, base = SOURCE.read_bytes(), BASE.read_bytes()
        cases = [('sf2-room-antialias', 4, 'A9FF0FF4', 6),
                 ('sf2-comical-antialias', 21, '1FD0E6D4', 8),
                 ('sf2-kando-antialias', 24, '557C2017', 7)]
        for selector, index, crc, count in cases:
            with self.subTest(selector=selector):
                rom, patch, manifest, conversion, dependency, *_ = build_experiment(
                    source, base, song=selector, events=('1', '21', 'scene:communication'))
                self.assertEqual(fingerprint(rom)['crc32'], crc)
                self.assertEqual(apply_bps(base, patch)[0], rom)
                self.assertEqual(conversion['sequence_index'], index)
                self.assertEqual(conversion['track_groups'], [[i] for i in range(count)])
                self.assertEqual(len(dependency['tracks']), count)
                self.assertIn('bandlimited_pcm', conversion)
                self.assertTrue(all('resampling' in s for s in conversion['samples']))
                self.assertNotIn('native_pitch_lfo', conversion)
                self.assertNotIn('envelope_approximation', conversion)
                self.assertNotIn('native_track_capacity', manifest)
                self.assertEqual(manifest['sound_mode_change']['pcm_channels'], 10)


if __name__ == '__main__':
    unittest.main()
