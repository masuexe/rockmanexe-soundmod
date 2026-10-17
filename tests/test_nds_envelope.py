"""Envelope snapshots and bounded DS-to-GBA attack approximation."""
from dataclasses import replace
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nds_music import NoteDefinition, attack_curve, convert_envelope, fit_attack_parameter
from nds_track_merge import convert_merged_song
from validate_nds_envelope import envelope_step, note_started_between
from analyze_song import trace_track
from nds_music import note_bytes, wait_bytes, ROM_BASE
import test_nds_music as fixtures

note = fixtures.note


class EnvelopeTests(unittest.TestCase):
    def test_native_retrigger_detection_unfolds_only_loop_body(self):
        prefix = b'\xBD\x00' + note_bytes(60, 90, 12) + wait_bytes(24)
        body = note_bytes(64, 90, 12) + wait_bytes(96)
        track = trace_track(prefix + body + b'\xB2' + struct.pack('<I', ROM_BASE + len(prefix)), 0)
        for start in (24, 120, 216, 984):
            self.assertTrue(note_started_between(track, 64, start, start + 1))
            self.assertFalse(note_started_between(track, 64, start - 1, start))
            self.assertFalse(note_started_between(track, 64, start + 1, start + 12))
            self.assertFalse(note_started_between(track, 60, start, start + 1))
        self.assertTrue(note_started_between(track, 60, 0, 1))
        self.assertTrue(note_started_between(track, 64, 500, 1000))

    def test_native_step_crosses_attack_decay_and_release_boundaries(self):
        adsr = (74, 128, 80, 128)
        self.assertEqual(envelope_step(0x13, 222, adsr), (0x12, 255))
        self.assertEqual(envelope_step(0x12, 100, adsr), (0x11, 80))
        self.assertEqual(envelope_step(0x51, 100, adsr), (0x51, 50))
        self.assertEqual(envelope_step(0x51, 1, adsr), (0, 0))

    def test_attack_uses_signed_truncation_and_reaches_peak(self):
        self.assertEqual(attack_curve(127), [0])
        curve = attack_curve(100)
        self.assertEqual(curve[:3], [-56032, -33925, -20540])
        self.assertEqual(len(curve), 14)
        self.assertEqual(curve[-1], 0)
        self.assertTrue(all(a < b for a, b in zip(curve, curve[1:])))

    def test_noninstant_attack_requires_explicit_approximation(self):
        definition = NoteDefinition(0, 0, 60, 100, 127, 100, 98, 64)
        with self.assertRaisesRegex(ValueError, 'Non-instant'):
            convert_envelope(definition)
        parameter, rms, peak, updates = fit_attack_parameter(100)
        self.assertEqual(parameter, 74)
        self.assertLess(rms, 0.12)
        self.assertLess(peak, 0.30)
        self.assertEqual(updates, 14)
        self.assertEqual(convert_envelope(definition, True)[0], parameter)
        self.assertEqual(convert_envelope(replace(definition, attack=127)),
                         convert_envelope(replace(definition, attack=127), True))

    def test_poor_attack_fit_and_invalid_values_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'error limits'):
            fit_attack_parameter(0)
        for value in (-1, 128, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                attack_curve(value)

    def test_same_tick_release_change_preserves_both_note_snapshots(self):
        intro = b'\xC7\x00\xE1\x78\x00\x81\x02'
        body = b'\xD3\x73' + note(length=96) + b'\xD3\x78' + note() + b'\x80\x60'
        raw = intro + body + b'\x94' + len(intro).to_bytes(3, 'little')
        archive = fixtures.SampleConversionTests.archive_for(raw)
        with self.assertRaisesRegex(ValueError, 'effect 0xd3'):
            convert_merged_song(archive, 0, [(0,)])
        blob, dependency, report = convert_merged_song(archive, 0, [(0,)], envelope_support=True)
        notes = report['note_mapping'][:2]
        self.assertEqual([n['source_envelope']['release'] for n in notes], [115, 120])
        self.assertNotEqual(notes[0]['gba_voice'], notes[1]['gba_voice'])
        bank = dependency['header']['tone_bank']['file_offset']
        for n in notes:
            children = struct.unpack_from('<I', blob, bank + n['gba_voice'] * 12 + 4)[0] - 0x08000000
            actual = tuple(blob[children + n['gba_key'] * 12 + 8:children + n['gba_key'] * 12 + 12])
            expected = convert_envelope(NoteDefinition(0, 0, 60, 127, 127, 127,
                                                       n['source_envelope']['release'], 64), True)
            self.assertEqual(actual, expected)
        self.assertFalse(report['envelope_approximation']['overrides_affect_existing_voices'])

    def test_invalid_override_is_not_silently_accepted(self):
        raw = b'\xC7\x00\xE1\x78\x00\x81\x02\xD3\x80' + note() + b'\x80\x0C\x94\x07\x00\x00'
        with self.assertRaisesRegex(ValueError, 'override outside'):
            convert_merged_song(fixtures.SampleConversionTests.archive_for(raw), 0, [(0,)], envelope_support=True)

    def test_all_four_overrides_are_snapshotted_at_note_on(self):
        intro = b'\xC7\x00\xE1\x78\x00\x81\x02'
        body = b'\xD0\x64\xD1\x50\xD2\x5A\xD3\x73' + note(length=96)
        body += b'\xD0\x7F\xD1\x7F\xD2\x7F\xD3\x7F' + note() + b'\x80\x60'
        raw = intro + body + b'\x94' + len(intro).to_bytes(3, 'little')
        _, _, report = convert_merged_song(fixtures.SampleConversionTests.archive_for(raw), 0, [(0,)],
                                           envelope_support=True)
        notes = report['note_mapping'][:2]
        self.assertEqual(list(notes[0]['source_envelope'].values()), [100, 80, 90, 115])
        self.assertEqual(list(notes[1]['source_envelope'].values()), [127] * 4)
        self.assertNotEqual(notes[0]['gba_voice'], notes[1]['gba_voice'])


if __name__ == '__main__':
    unittest.main()
