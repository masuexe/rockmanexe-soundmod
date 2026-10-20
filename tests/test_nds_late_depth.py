"""Late initial enable plus positive depth changes, with unchanged default guards."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from test_nds_lfo_delay import archive_for
import test_nds_music as fixtures
from nds_track_merge import convert_merged_song
from validate_nds_lfo import LfoModel
from validate_nds_experiment import check_late_depth_reference, check_live_depth_reference


def convert(body, **flags):
    options = dict(native_pitch_lfo=True, native_pitch_lfo_delay=True,
                   native_pitch_lfo_live_depth=True, native_pitch_lfo_late_depth=True)
    options.update(flags)
    return convert_merged_song(archive_for(body), 0, [(0,)], **options)


def body(at=12, change=36):
    return (fixtures.note(length=96) + bytes([0x80, at]) + b'\xCA\x0A' +
            bytes([0x80, change-at]) + b'\xCA\x14' + bytes([0x80, 96-change]))


class LateDepthTests(unittest.TestCase):
    def test_late_enable_and_positive_update_preserve_delay_and_phase(self):
        for tick in (2, 12):
            with self.subTest(tick=tick):
                _, dep, c = convert(body(at=tick))
                self.assertEqual(c['native_pitch_lfo']['late_depth_activation']['initializations'],
                                 [{'source_track': 0, 'activation_tick': tick, 'first_note_tick': 0, 'depth': 10}])
                model = LfoModel(dep['tracks'][0]['events'])
                before = model.advance(tick)
                self.assertEqual((before['speed'], before['depth'], before['phase']), (0, 0, 0))
                on = model.advance(tick+1)
                self.assertGreater(on['speed'], 0)
                self.assertGreater(on['depth'], 0)
                self.assertEqual(on['count'], max(0, before['count']-1))
                old = model.advance(36)
                new = model.advance(37)
                self.assertGreater(new['depth'], old['depth'])
                self.assertEqual(new['phase'], (old['phase']+old['speed'])%256)
                self.assertEqual(new['count'], old['count'])

    def test_default_live_depth_and_fixed_delay_still_reject_late_enable(self):
        with self.assertRaisesRegex(ValueError, 'activation before'):
            convert(body(), native_pitch_lfo_late_depth=False)
        with self.assertRaises(ValueError):
            convert(body(), native_pitch_lfo_late_depth=False, native_pitch_lfo_live_depth=False)

    def test_new_flag_requires_explicit_live_mode_and_excludes_other_structures(self):
        for flag, value in (('native_pitch_lfo', False), ('native_pitch_lfo_delay', False),
                            ('native_pitch_lfo_live_depth', False), ('mixed_loop_support', True),
                            ('finite_support', True), ('finite_release_support', True),
                            ('bandlimited_pcm', True), ('native_pitch_lfo_live_toggle', True),
                            ('envelope_support', True), ('native_pitch_lfo_min_depth', True)):
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'Late positive-depth activation requires'):
                convert(body(), **{flag: value})

    def test_disabling_and_other_live_parameter_changes_stay_rejected(self):
        for command in (b'\xCA\x00', b'\xCB\x14', b'\xCC\x01', b'\xCD\x02', b'\xE0\x14\x00'):
            score = fixtures.note(length=96)+b'\x80\x0C\xCA\x0A\x80\x18'+command+b'\x80\x3C'
            with self.subTest(command=command), self.assertRaises(ValueError):
                convert(score)

    def test_reference_reports_missing_carried_positive_coverage_and_rejects_reset(self):
        header = 'tick,track,channel,before_depth,depth,phase_before,phase_after,counter_before,counter_after\n'
        c = {'native_pitch_lfo': {'late_depth_activation': {'enabled': True, 'initializations':
             [{'source_track': 0, 'activation_tick': 12, 'first_note_tick': 0, 'depth': 10}]}}}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/'controls.csv').write_text('tick,track,opcode,value\n12,0,202,10\n36,0,202,20\n')
            updates = p/'modulation-changes.csv'
            updates.write_text(header+'12,0,0,0,10,0,0,0,0\n36,0,0,10,20,0,0,0,0\n')
            report = check_late_depth_reference(c, p)
            self.assertTrue(report['complete'])
            self.assertFalse(report['carried_positive_depth_covered'])
            self.assertEqual(report['positive_control_voice_updates'], 1)
            with self.assertRaisesRegex(AssertionError, 'carried state'):
                check_live_depth_reference(c, p)
            # A reused voice's note initialization is not a CA-control update.
            with updates.open('a') as stream:
                stream.write('38,0,0,10,20,1200,1200,10,10\n')
            report = check_late_depth_reference(c, p)
            self.assertEqual(report['positive_control_voice_updates'], 1)
            self.assertFalse(report['carried_positive_depth_covered'])
            updates.write_text(header+'12,0,0,0,10,0,0,3,0\n')
            with self.assertRaisesRegex(AssertionError, 'phase/counter'):
                check_late_depth_reference(c, p)
            updates.write_text(header+'11,0,0,0,10,0,0,0,0\n')
            with self.assertRaisesRegex(AssertionError, 'no allocated voice'):
                check_late_depth_reference(c, p)

    def test_repeated_depth_control_restores_speed_but_does_not_reset_phase(self):
        _, dep, _ = convert(body())
        events = dep['tracks'][0]['events']
        for tick in (12, 36):
            self.assertTrue(any(e['ticks']==tick and e['name']=='LFOS' and e['value']>0 for e in events))
        self.assertFalse(any(e['ticks'] in (12,36) and e['name']=='LFODL' for e in events))


if __name__ == '__main__':
    unittest.main()
