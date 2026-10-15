"""Regression checks for independent MPlay loop and tied-gate validation."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze_song import trace_track
from nds_music import note_bytes, wait_bytes
from nds_track_merge import validate_loop_notes
from scan_audio import ROM_BASE


def loop_track(prefix, body):
    raw = prefix + body + b'\xB2' + struct.pack('<I', ROM_BASE + len(prefix))
    return trace_track(raw, 0)


class LoopNoteValidationTests(unittest.TestCase):
    def test_decoder_closes_after_note_at_final_timestamp(self):
        track = loop_track(b'\xBD\x00', note_bytes(60, 90, 12) + wait_bytes(12))
        notes = [e for e in track['events'] if e['name'] == 'NOTE']
        self.assertEqual(notes[-1]['ticks'], track['ticks_before_repeat'])
        result = validate_loop_notes(track, [[0, 0, 60, 90, 12]], 0, 12)
        self.assertEqual(result['note_events_compared'], 2)
        self.assertEqual(result['complete_loop_cycles'], 2)

    def test_tie_ends_after_jump_to_loop_start(self):
        prefix = b'\xBD\x00\xCF\x7F\x40' + wait_bytes(300)
        body = b'\xCE\x7F' + wait_bytes(100) + b'\xCF\x7F\x40' + wait_bytes(200)
        track = loop_track(prefix, body)
        self.assertEqual(track['events'][-1]['name'], 'GOTO')
        result = validate_loop_notes(track, [[0, 0, 127, 64, 300], [400, 0, 127, 64, 200]], 300, 300)
        self.assertEqual(result['note_events_compared'], 3)

    def test_same_tick_intro_note_is_not_repeated(self):
        prefix = b'\xBD\x00' + note_bytes(60, 90, 12)
        track = loop_track(prefix, note_bytes(64, 90, 12) + wait_bytes(12))
        # Musical body starts at tick zero; the expected second iteration
        # includes only its 64, not the same-tick intro's 60.
        base = [[0, 0, 60, 90, 12], [0, 0, 64, 90, 12], [12, 0, 64, 90, 12]]
        validate_loop_notes(track, base, 12, 12)

    def test_wrong_note_gate_and_missing_or_extra_notes_fail(self):
        track = loop_track(b'\xBD\x00', note_bytes(60, 90, 12) + wait_bytes(12))
        for base in ([], [[0, 0, 61, 90, 12]], [[0, 0, 60, 90, 11]],
                     [[0, 0, 60, 90, 12], [1, 0, 60, 90, 12]]):
            with self.subTest(base=base), self.assertRaisesRegex(AssertionError, 'note/gate/timing'):
                validate_loop_notes(track, base, 0, 12)

    def test_unclosed_intro_tie_is_rejected(self):
        track = loop_track(b'\xBD\x00\xCF\x7F\x40' + wait_bytes(300), wait_bytes(100))
        with self.assertRaisesRegex(AssertionError, 'Unclosed tied'):
            validate_loop_notes(track, [[0, 0, 127, 64, 300]], 300, 100)

    def test_alias_reuse_before_eot_is_rejected(self):
        track = loop_track(b'\xBD\x00', b'\xCF\x7F\x40' + wait_bytes(300))
        with self.assertRaisesRegex(AssertionError, 'share a live alias'):
            validate_loop_notes(track, [[0, 0, 127, 64, 300]], 0, 300)

    def test_unmatched_eot_is_rejected(self):
        track = loop_track(b'\xBD\x00', b'\xCE\x7F' + wait_bytes(100))
        with self.assertRaisesRegex(AssertionError, 'no matching tied'):
            validate_loop_notes(track, [], 0, 100)

    def test_wrong_loop_period_is_rejected(self):
        track = loop_track(b'\xBD\x00', note_bytes(60, 90, 12) + wait_bytes(12))
        with self.assertRaisesRegex(AssertionError, 'loop period'):
            validate_loop_notes(track, [[0, 0, 60, 90, 12]], 0, 24)


if __name__ == '__main__':
    unittest.main()
