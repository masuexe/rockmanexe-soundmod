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
from validate_nds_experiment import check_reference, probe_windows
import test_nds_music as fixtures


PROGRAM = b'\xC7\x00\xE1\x78\x00\x81\x02\x3C\x64\x82\x2C\x80\x82\x2C\xFF'


class FiniteSongTests(unittest.TestCase):
    def test_short_finite_probe_observes_live_music_and_retains_loop_defaults(self):
        self.assertEqual(probe_windows({}), dict(warmup=240, effects=30, lifecycle=120, restart=30))
        short = {'finite_song': {'track_end_ticks': {'0': 168, '3': 156, '6': 192}},
                 'tempo_mapping': [{'gba_ticks_per_second': 136.1787012987013}]}
        w = probe_windows(short)
        earliest_frames = 156 / 136.1787012987013 * 59.7275
        self.assertLess(w['warmup'] + w['effects'] + 2, earliest_frames)
        self.assertLess(w['restart'], w['lifecycle'])
        self.assertGreater(w['effects'], 0)
        short['finite_song']['track_end_ticks']['3'] = 1
        with self.assertRaisesRegex(ValueError, 'too short'):
            probe_windows(short)

    def test_bandlimited_finite_cache_and_pitch_control_bounds(self):
        raw = b'\xC7\x00\xE1\x78\x00\x81\x02' + bytes([60, 100, 12, 72, 100, 12, 128, 12, 60, 100, 12, 128, 12, 255])
        archive = fixtures.SampleConversionTests.archive_for(raw)
        archive.wave = lambda *_: ([0, 12000, 0, -12000] * 512,
                                   {'effective_rate_hz': 22050, 'looped': True,
                                    'loop_start_samples': 512, 'sample_count': 2048})
        with self.assertRaisesRegex(ValueError, 'finite singleton'):
            convert_merged_song(archive, 0, [(0,)], bandlimited_pcm=True)
        _, dependency, conversion = convert_merged_song(archive, 0, [(0,)], finite_support=True, bandlimited_pcm=True)
        self.assertEqual(len(dependency['samples']), 2)
        self.assertEqual({s['source_key'] for s in conversion['samples']}, {60, 72})
        self.assertTrue(conversion['note_timing_validation'][0]['complete_finite_track'])
        self.assertTrue(all(abs(s['resampling']['pitch_error_cents']) < .001 for s in conversion['samples']))
        # A live bend between note-ons must be inspected too. Downward bend is
        # conservative for the prepared bandwidth; upward bend is outside scope.
        for bend in (1, 255):
            changed = raw[:-1] + bytes([196, bend, 255])
            archive.sequence = lambda _, changed=changed: (changed, {'bank_id': 0, 'volume': 75})
            if bend == 1:
                with self.assertRaisesRegex(ValueError, 'upward bend'):
                    convert_merged_song(archive, 0, [(0,)], finite_support=True, bandlimited_pcm=True)
            else:
                convert_merged_song(archive, 0, [(0,)], finite_support=True, bandlimited_pcm=True)

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
