"""Guardrails for same-emulator diagnostics and research-only mixer variants."""
import copy
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from compare_fidelity import mixer_experiment, source_driver, normalize_wav
from original_catalog import PROFILES
from scan_audio import fingerprint
from target_profiles import target_profile


class MixerTests(unittest.TestCase):
    def setUp(self):
        self.layout = target_profile('exegp')['layout']
        self.image = bytearray(self.layout['sound_mode_offset']+16)
        struct.pack_into('<I', self.image, self.layout['sound_mode_offset'], self.layout['sound_mode'])
        self.manifest = {'target_profile': 'exegp', 'audio_layout': 'exegp-audio-v1',
                         'target_base_fingerprint': target_profile('exegp')['fingerprint'],
                         'sound_mode_change': {}}
        self.config = {'frequency_selector': 3, 'master_volume': 13, 'pcm_channels': 4}

    def test_experiment_only_changes_declared_literal(self):
        for mode, expected in [('source-rate-volume', 0x0093DA00), ('source-all', 0x0093D400)]:
            manifest = copy.deepcopy(self.manifest)
            output = mixer_experiment(self.image, manifest, self.config, mode)
            offset = self.layout['sound_mode_offset']
            self.assertEqual(output[:offset], self.image[:offset])
            self.assertEqual(output[offset+4:], self.image[offset+4:])
            self.assertEqual(struct.unpack_from('<I', output, offset)[0], expected)
            self.assertEqual(manifest['output_fingerprint'], fingerprint(output))
            self.assertIn('Global', manifest['experimental_mixer']['scope'])
            self.assertEqual(struct.unpack_from('<I', self.image, offset)[0], self.layout['sound_mode'])

    def test_invalid_mixer_settings_are_rejected_before_writing(self):
        for key, value in [('frequency_selector', 0), ('frequency_selector', 13),
                           ('master_volume', 16), ('pcm_channels', 13)]:
            with self.assertRaises(ValueError):
                mixer_experiment(self.image, self.manifest, {**self.config, key: value}, 'source-all')

    def test_normalization_preserves_stereo_and_avoids_clipping(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp)/'source.wav', Path(tmp)/'target.wav'
            with wave.open(str(source), 'wb') as f:
                f.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
                f.writeframes(struct.pack('<hhhh', 30000, -30000, 1000, -1000)*100)
            metrics = normalize_wav(source, target)
            with wave.open(str(target), 'rb') as f:
                self.assertEqual(f.getnchannels(), 2)
                samples = struct.unpack('<'+'h'*f.getnframes()*2, f.readframes(f.getnframes()))
            self.assertLessEqual(max(abs(v) for v in samples), 31129)
            self.assertEqual(samples[0], -samples[1])
            self.assertAlmostEqual(metrics['normalized_rms_dbfs'], -20)


@unittest.skipUnless(all((ROOT.parent/'roms'/PROFILES[k]['filename']).is_file()
                        for k in ['exe1', 'bn2', 'exe6']), 'Original inputs unavailable')
class SourceDriverTests(unittest.TestCase):
    def test_verified_start_entries_and_player_tables(self):
        for key, entry, core, table in [('exe1', 0x9C914, 0x9CF90, 0xA0D7C),
                                         ('bn2', 0xE71C0, 0xE78F4, 0xF3718),
                                         ('exe6', 0x15B338, 0x15BB18, 0x164C8C)]:
            data = (ROOT.parent/'roms'/PROFILES[key]['filename']).read_bytes()
            self.assertEqual(source_driver(data, PROFILES[key]),
                             {'entry_offset': entry, 'core_offset': core, 'player_table_offset': table})

    def test_near_matches_are_not_accepted_as_a_driver(self):
        profile = PROFILES['exe1']
        original = (ROOT.parent/'roms'/profile['filename']).read_bytes()
        driver = source_driver(original, profile)
        for offset in [driver['entry_offset'], driver['entry_offset']+28]:
            modified = bytearray(original)
            modified[offset:offset+2] = b'\x00\x00'
            with self.assertRaises(ValueError):
                source_driver(modified, profile)


if __name__ == '__main__':
    unittest.main()
