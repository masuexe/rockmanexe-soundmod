"""Finite singleton long gates, explicit END and reference completeness."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze_song import trace_track
from nds_music import wait_bytes
from nds_track_merge import convert_merged_song, validate_finite_notes
from validate_nds_experiment import check_reference
import test_nds_music as fixtures


PROGRAM = b'\xC7\x00\xE1\x78\x00\x81\x02\x3C\x64\x82\x2C\x80\x82\x2C\xFF'


class FiniteSongTests(unittest.TestCase):
    def test_finite_long_gate_closes_before_same_tick_fine(self):
        _, dependency, conversion = convert_merged_song(
            fixtures.SampleConversionTests.archive_for(PROGRAM), 0, [(0,)], finite_support=True)
        track = dependency['tracks'][0]
        self.assertEqual(track['termination'], 'fine')
        self.assertEqual(track['ticks_before_repeat'], 300)
        self.assertEqual([(e['name'], e['ticks']) for e in track['events'] if e['name'] in ('TIE', 'EOT', 'FINE')],
                         [('TIE', 0), ('EOT', 300), ('FINE', 300)])
        self.assertTrue(conversion['note_timing_validation'][0]['complete_finite_track'])
        self.assertEqual(conversion['finite_song']['track_end_ticks'], {'0': 300})
        self.assertIsNone(conversion['merged_loop_ticks'])

    def test_invalid_gates_missing_eot_and_wrong_end_fail(self):
        prefix = b'\xBD\x00\xCF\x7F\x5A'
        expected = [[0, 0, 127, 90, 300]]
        cases = [(prefix + wait_bytes(300) + b'\xB1', 'Unclosed tied'),
                 (prefix + wait_bytes(299) + b'\xCE\x7F\xB1', 'end differs'),
                 (prefix + wait_bytes(299) + b'\xCE\x7F' + wait_bytes(1) + b'\xB1', 'note/gate/timing')]
        for raw, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(AssertionError, message):
                validate_finite_notes(trace_track(raw, 0), expected, 300)

    def test_finite_mode_is_explicit_and_rejects_unbounded_cases(self):
        archive = fixtures.SampleConversionTests.archive_for(PROGRAM)
        with self.assertRaisesRegex(ValueError, 'looping source tracks'):
            convert_merged_song(archive, 0, [(0,)])
        early_end = PROGRAM.replace(b'\x80\x82\x2C', b'\x80\x64')
        with self.assertRaisesRegex(ValueError, 'finish their gates'):
            convert_merged_song(fixtures.SampleConversionTests.archive_for(early_end), 0, [(0,)], finite_support=True)
        loop = PROGRAM[:-1] + b'\x94\x07\x00\x00'
        with self.assertRaisesRegex(ValueError, 'entirely finite'):
            convert_merged_song(fixtures.SampleConversionTests.archive_for(loop), 0, [(0,)], finite_support=True)
        for option in ('native_pitch_lfo', 'envelope_support'):
            with self.subTest(option=option), self.assertRaisesRegex(ValueError, 'excludes'):
                convert_merged_song(archive, 0, [(0,)], finite_support=True, **{option: True})

    def test_reference_requires_exact_finite_notes_and_tail_duration(self):
        _, _, conversion = convert_merged_song(
            fixtures.SampleConversionTests.archive_for(PROGRAM), 0, [(0,)], finite_support=True)
        conversion['samples'] = []  # This fixture isolates execution, not PCM decoding.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'conversion.json').write_text(json.dumps(conversion))
            (root / 'source.sdat').write_bytes(b'fixture')
            ref = root / 'reference'; ref.mkdir()
            (ref / 'reference.json').write_text(json.dumps({'seconds': 10}))
            header = 'tick,track,instrument,key,velocity,duration\n'
            note = '0,0,2,60,100,300\n'
            with patch('validate_nds_experiment.SoundArchive'):
                (ref / 'notes.csv').write_text(header + note)
                self.assertTrue(check_reference(root, ref)['finite_complete_note_schedule_checked'])
                (ref / 'notes.csv').write_text(header + note + note)
                with self.assertRaisesRegex(AssertionError, 'finite DS note'):
                    check_reference(root, ref)
                (ref / 'notes.csv').write_text(header + note)
                (ref / 'reference.json').write_text(json.dumps({'seconds': 1}))
                with self.assertRaisesRegex(AssertionError, 'source END'):
                    check_reference(root, ref)


if __name__ == '__main__':
    unittest.main()
