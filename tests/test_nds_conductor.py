"""Note-free looping conductors retain tempo without pretending notes exist."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nds_track_merge import convert_merged_song
from validate_nds_experiment import check_reference
import test_nds_music as fixtures


def conductor_archive():
    header = b'\xFE\x03\x00\x93\x01' + bytes(3)
    start = len(header)
    control = b'\xC7\x00\xE1\x78\x00\x80\x0C\xD5\x64\x80\x0C\x94' + start.to_bytes(3, 'little')
    second = start + len(control)
    music = b'\xC7\x00\x81\x02\x3C\x64\x0C\x80\x18\x94' + second.to_bytes(3, 'little')
    archive = fixtures.SampleConversionTests.archive_for(header[:5] + second.to_bytes(3, 'little') + control + music)
    archive.wave = lambda *_: ([0, 12000, 0, -12000] * 512,
                               {'effective_rate_hz': 22050, 'looped': True,
                                'loop_start_samples': 512, 'sample_count': 2048})
    return archive


class ConductorTests(unittest.TestCase):
    def test_silent_track_keeps_loop_tempo_and_expression_in_both_routes(self):
        for filtered in (False, True):
            with self.subTest(filtered=filtered):
                _, dependency, conversion = convert_merged_song(
                    conductor_archive(), 0, [(0,), (1,)], bandlimited_pcm=filtered)
                silent = dependency['tracks'][0]
                self.assertEqual(len(dependency['tracks']), 2)
                self.assertEqual(silent['termination'], 'repeated_state')
                self.assertEqual(silent['loop_ticks'], 24)
                self.assertFalse(any(e['name'] in ('NOTE', 'TIE', 'EOT') for e in silent['events']))
                self.assertTrue(any(e['name'] == 'TEMPO' for e in silent['events']))
                self.assertTrue(any(e['name'] == 'VOL' and e['ticks'] == 12 for e in silent['events']))
                self.assertEqual(conversion['note_timing_validation'][0]['note_events_compared'], 0)
                self.assertEqual(conversion['note_timing_validation'][0]['complete_loop_cycles'], 2)
                self.assertTrue(all(n['source_track'] == 1 for n in conversion['note_mapping']))

    def reference_fixture(self, root):
        # Isolate reference coverage checks from PCM decoding.
        _, _, conversion = convert_merged_song(conductor_archive(), 0, [(0,), (1,)])
        conversion['samples'] = []
        (root / 'conversion.json').write_text(json.dumps(conversion))
        (root / 'source.sdat').write_bytes(b'fixture')
        ref = root / 'reference'; ref.mkdir()
        (ref / 'reference.json').write_text(json.dumps({'seconds': 10}))
        notes = 'tick,track,instrument,key,velocity,duration\n' + ''.join(
            f'{tick},1,2,60,100,12\n' for tick in range(0, 121, 24))
        (ref / 'notes.csv').write_text(notes)
        controls = 'tick,track,opcode,value\n' + ''.join(
            f'{tick},0,225,120\n{tick+12},0,213,100\n' for tick in range(0, 121, 24))
        (ref / 'controls.csv').write_text(controls)
        return ref

    def test_reference_checks_note_free_tempo_and_rejects_missing_or_wrong_controls(self):
        with tempfile.TemporaryDirectory() as directory, patch('validate_nds_experiment.SoundArchive'):
            root = Path(directory); ref = self.reference_fixture(root)
            result = check_reference(root, ref)
            self.assertEqual(result['per_track_note_matches']['0'], 0)
            self.assertGreater(result['note_free_track_checks'][0]['tempo_matches'], 0)
            controls = (ref / 'controls.csv').read_text()
            for changed, message in [(controls.replace(',225,120', ',225,119'), 'control 0xe1 differs'),
                                     ('\n'.join(line for line in controls.splitlines()
                                                if ',225,' not in line or line.startswith('0,')) + '\n',
                                      'control 0xe1 differs'),
                                     ('tick,track,opcode,value\n', 'controls are missing')]:
                (ref / 'controls.csv').write_text(changed)
                with self.subTest(message=message), self.assertRaisesRegex(AssertionError, message):
                    check_reference(root, ref)
            (ref / 'controls.csv').unlink()
            with self.assertRaisesRegex(AssertionError, 'independent control'):
                check_reference(root, ref)

    def test_reference_rejects_missing_sounding_track_unexpected_silent_note_and_short_capture(self):
        with tempfile.TemporaryDirectory() as directory, patch('validate_nds_experiment.SoundArchive'):
            root = Path(directory); ref = self.reference_fixture(root)
            original = (ref / 'notes.csv').read_text()
            for changed in [original.splitlines()[0] + '\n', original + '0,0,2,60,100,12\n']:
                (ref / 'notes.csv').write_text(changed)
                with self.assertRaisesRegex(AssertionError, 'sounding tracks'):
                    check_reference(root, ref)
            (ref / 'notes.csv').write_text(original)
            (ref / 'reference.json').write_text(json.dumps({'seconds': .01}))
            with self.assertRaisesRegex(AssertionError, 'Note-free reference must cover'):
                check_reference(root, ref)


if __name__ == '__main__':
    unittest.main()
