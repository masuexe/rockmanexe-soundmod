"""Fixed DS delay mapping and independent counter/phase regressions."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import test_nds_music as fixtures
from nds_track_merge import convert_merged_song
from validate_nds_experiment import check_delay_reference, check_live_depth_reference, check_toggle_reference
from validate_nds_lfo import LfoModel


def archive_for(body):
    intro = b'\xC7\x00\xE1\x78\x00\x81\x02\xCB\x19\xE0\x0A\x00'
    raw = intro + body + b'\x94' + len(intro).to_bytes(3, 'little')
    return fixtures.SampleConversionTests.archive_for(raw)


class DelayedPitchLfoTests(unittest.TestCase):
    def test_enable_only_reference_does_not_claim_disable_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'controls.csv').write_text('tick,track,opcode,value\n12,0,202,10\n')
            (root / 'modulation-changes.csv').write_text(
                'tick,track,channel,before_depth,depth,phase_before,phase_after,counter_before,counter_after\n'
                '12,0,0,0,10,0,0,0,0\n')
            report = check_toggle_reference(root, require_disable=False)
            self.assertTrue(report['complete'])
            self.assertFalse(report['disable_controls_required'])
            self.assertEqual(report['disable_controls'], 0)
            self.assertFalse(report['carried_disable_covered'])
            with self.assertRaisesRegex(AssertionError, 'required toggle'):
                check_toggle_reference(root)

    def test_toggle_preserves_initial_wait_and_models_disable_phase_approximation(self):
        body = (fixtures.note(length=96) + b'\x80\x0C\xCA\x14\x80\x18\xCA\x00'
                + b'\x80\x0C\xCA\x14\x80\x30\xCA\x00')
        with self.assertRaises(ValueError):
            convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_delay=True)
        _, dep, report = convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_delay=True, native_pitch_lfo_live_toggle=True)
        model = LfoModel(dep['tracks'][0]['events'])
        before = model.advance(12)
        self.assertEqual((before['phase'], before['count']), (0, 6))
        after = model.advance(13)
        self.assertEqual((after['phase'], after['count'], after['depth']), (0, 5, 2))
        off_before = model.advance(36)
        self.assertNotEqual(off_before['phase'], 0)
        off = model.advance(37)
        self.assertEqual((off['phase'], off['value'], off['depth'], off['count']), (0, 0, 0, off_before['count']))
        resumed = model.advance(49)
        self.assertEqual(resumed['phase'], resumed['speed'])
        changes = report['native_pitch_lfo']['live_toggle_approximation']['source_depth_toggles']
        self.assertEqual([(c['ticks'], c['before'], c['after']) for c in changes],
                         [(12, 0, 20), (36, 20, 0), (48, 0, 20), (96, 20, 0)])

    def test_toggle_rejects_other_parameter_changes_and_flag_combinations(self):
        for control in (b'\xCA\x0A', b'\xCB\x14', b'\xCC\x01', b'\xCD\x02', b'\xE0\x14\x00'):
            body = fixtures.note(length=96) + b'\x80\x0C\xCA\x14\x80\x0C' + control + b'\x80\x48'
            with self.subTest(control=control), self.assertRaises(ValueError):
                convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                    native_pitch_lfo_delay=True, native_pitch_lfo_live_toggle=True)
        for options in ({'native_pitch_lfo_live_toggle': True},
                        {'native_pitch_lfo': True, 'native_pitch_lfo_delay': True,
                         'native_pitch_lfo_live_depth': True, 'native_pitch_lfo_live_toggle': True}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                convert_merged_song(archive_for(fixtures.note() + b'\x80\x0C'), 0, [(0,)], **options)

    def test_independent_toggle_updates_preserve_both_counters(self):
        header = 'tick,track,channel,before_depth,depth,phase_before,phase_after,counter_before,counter_after\n'
        on = '12,0,0,0,20,0,0,0,0\n'
        off = '36,0,0,20,0,1600,1600,10,10\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);file = root / 'modulation-changes.csv'
            (root / 'controls.csv').write_text('tick,track,opcode,value\n12,0,202,20\n36,0,202,0\n')
            file.write_text(header + on + off)
            self.assertEqual(check_toggle_reference(root, require_carried_disable=True)['disable_updates_with_carried_state'], 1)
            file.write_text(header + on)
            self.assertFalse(check_toggle_reference(root)['carried_disable_covered'])
            with self.assertRaisesRegex(AssertionError, 'required toggle'):
                check_toggle_reference(root, require_carried_disable=True)
            file.write_text(header + on + off.replace(',1600,1600,', ',1600,0,'))
            with self.assertRaisesRegex(AssertionError, 'phase/counter'):
                check_toggle_reference(root)

    def test_setup_in_rest_before_first_note_keeps_note_on_delay_reset(self):
        body = b'\x80\x04\xCA\x14\x80\x10' + fixtures.note(length=36) + b'\x80\x24'
        _, dep, report = convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                           native_pitch_lfo_delay=True)
        events = dep['tracks'][0]['events']
        self.assertEqual(min(e['ticks'] for e in events if e['name'] == 'NOTE'), 20)
        self.assertEqual(report['native_pitch_lfo']['delay_approximation']['initializations'],
                         [{'source_track': 0, 'activation_tick': 4, 'first_note_tick': 20, 'depth': 20}])
        model = LfoModel(events)
        self.assertNotEqual(model.advance(20)['phase'], 0)
        state = model.advance(21)
        self.assertEqual((state['phase'], state['value'], state['count']), (0, 0, state['delay'] - 1))
        self.assertTrue(report['note_timing_check'])

    def test_pre_note_setup_does_not_allow_later_fixed_parameter_changes(self):
        body = b'\x80\x04\xCA\x14\x80\x04\xE0\x14\x00\x80\x0C' + fixtures.note() + b'\x80\x0C'
        with self.assertRaises(ValueError):
            convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_delay=True)

    def test_independent_live_depth_update_must_preserve_phase_and_counter(self):
        header = 'tick,track,channel,before_depth,depth,phase_before,phase_after,counter_before,counter_after\n'
        row = '12,0,0,10,20,1600,1600,10,10\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / 'modulation-changes.csv'
            file.write_text(header + row)
            result = check_live_depth_reference({}, root)
            self.assertEqual(result['positive_voice_depth_changes'], 1)
            for corrupted in ('12,0,0,10,20,1600,0,10,10\n',
                              '12,0,0,10,20,1600,1600,10,0\n'):
                file.write_text(header + corrupted)
                with self.assertRaisesRegex(AssertionError, 'phase/counter'):
                    check_live_depth_reference({}, root)

    def test_live_depth_preserves_held_note_phase_and_delay_count(self):
        for change_tick in (2, 12):
            with self.subTest(change_tick=change_tick):
                body = (b'\xCA\x0A' + fixtures.note(length=96) + bytes([0x80, change_tick])
                        + b'\xCA\x14\x80' + bytes([96 - change_tick]) + b'\xCA\x0A')
                archive = archive_for(body)
                with self.assertRaises(ValueError):
                    convert_merged_song(archive, 0, [(0,)], native_pitch_lfo=True,
                                        native_pitch_lfo_delay=True)
                _, dep, report = convert_merged_song(archive, 0, [(0,)], native_pitch_lfo=True,
                    native_pitch_lfo_delay=True, native_pitch_lfo_live_depth=True)
                events = dep['tracks'][0]['events']
                at_change = [e for e in events if e['ticks'] == change_tick and e['name'] != 'WAIT']
                self.assertEqual([(e['name'], e.get('value')) for e in at_change], [('MOD', 2)])
                model = LfoModel(events)
                before = model.advance(change_tick)
                after = model.advance(change_tick + 1)
                self.assertEqual(after['depth'], 2)
                self.assertEqual(after['count'], max(0, before['count'] - 1))
                self.assertEqual(after['phase'], before['phase'] if before['count'] else
                                 (before['phase'] + before['speed']) % 256)
                self.assertTrue(report['note_timing_check'])
                self.assertEqual(report['native_pitch_lfo']['live_depth_approximation']['source_depth_changes'][0],
                                 {'source_track': 0, 'ticks': change_tick, 'before': 10, 'after': 20})

    def test_live_depth_keeps_unsupported_changes_rejected(self):
        for control in (b'\xCA\x00', b'\xCB\x14', b'\xCC\x01', b'\xCD\x02', b'\xE0\x14\x00'):
            body = b'\xCA\x0A' + fixtures.note(length=96) + b'\x80\x0C' + control + b'\x80\x54'
            with self.subTest(control=control), self.assertRaises(ValueError):
                convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                    native_pitch_lfo_delay=True, native_pitch_lfo_live_depth=True)

    def test_live_depth_does_not_allow_late_activation(self):
        body = fixtures.note(length=96) + b'\x80\x0C\xCA\x0A\x80\x54'
        with self.assertRaisesRegex(ValueError, 'first note timestamp'):
            convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                native_pitch_lfo_delay=True, native_pitch_lfo_live_depth=True)

    def test_live_depth_requires_explicit_delay_mode(self):
        with self.assertRaisesRegex(ValueError, 'requires native pitch LFO delay'):
            convert_merged_song(archive_for(fixtures.note() + b'\x80\x0C'), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_live_depth=True)

    def test_activation_after_first_note_at_same_tick_is_preserved(self):
        body = fixtures.note(length=36) + b'\xCA\x0F\x80\x24' + fixtures.note(64, length=36) + b'\x80\x24'
        archive = archive_for(body)
        with self.assertRaises(ValueError):
            convert_merged_song(archive, 0, [(0,)], native_pitch_lfo=True)
        _, dependency, report = convert_merged_song(archive, 0, [(0,)], native_pitch_lfo=True,
                                                    native_pitch_lfo_delay=True)
        events = dependency['tracks'][0]['events']
        at_start = [e for e in events if e['ticks'] == 0]
        first_note = next(i for i, e in enumerate(at_start) if e['name'] == 'NOTE')
        self.assertTrue(any(e['name'] == 'MOD' and e['value'] > 0 for e in at_start[first_note + 1:]))
        self.assertEqual({e['value'] for e in events if e['name'] == 'LFODL'}, {6})
        self.assertTrue(report['native_pitch_lfo']['delay_approximation'])
        self.assertTrue(report['note_timing_check'])

    def test_delay_cannot_be_enabled_without_native_pitch_mode(self):
        with self.assertRaisesRegex(ValueError, 'requires native pitch'):
            convert_merged_song(archive_for(fixtures.note() + b'\x80\x0C'), 0, [(0,)],
                                native_pitch_lfo_delay=True)

    def test_live_delay_change_during_a_held_note_is_rejected(self):
        body = b'\xCA\x0F' + fixtures.note(length=96) + b'\x80\x0C\xE0\x14\x00\x80\x54\xE0\x0A\x00'
        with self.assertRaisesRegex(ValueError, 'Live delayed-LFO'):
            convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_delay=True)

    def test_activation_at_a_later_tick_is_rejected(self):
        body = fixtures.note() + b'\x80\x0C\xCA\x0F' + fixtures.note(64) + b'\x80\x0C'
        with self.assertRaisesRegex(ValueError, 'first note timestamp'):
            convert_merged_song(archive_for(body), 0, [(0,)], native_pitch_lfo=True,
                                native_pitch_lfo_delay=True)

    def test_independent_delay_counter_and_frozen_phase_are_required(self):
        conversion = {'native_pitch_lfo': {'configs': [{'mod_type': 0, 'mod_speed': 25,
                       'mod_depth': 15, 'mod_range': 1, 'mod_delay': 1}]}}
        header = 'timer_frame,tick,track,channel,key,depth,speed,type,range,delay,counter_before,counter_after,phase_before,phase_after,active\n'
        waiting = '0,0,0,0,60,15,25,0,1,1,0,1,0,0,0\n'
        active = '1,0,0,0,60,15,25,0,1,1,1,1,0,1600,1\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            file = path / 'modulation-delay.csv'
            file.write_text(header + waiting + active)
            result = check_delay_reference(conversion, path)
            self.assertEqual(result['waiting_updates'], 1)
            self.assertEqual(result['active_after_delay_updates'], 1)
            for corrupted in (waiting.replace(',0,0,0\n', ',0,1600,0\n') + active,
                              waiting + active.replace(',1600,1\n', ',0,1\n')):
                file.write_text(header + corrupted)
                with self.assertRaisesRegex(AssertionError, 'counter/phase'):
                    check_delay_reference(conversion, path)


if __name__ == '__main__':
    unittest.main()
