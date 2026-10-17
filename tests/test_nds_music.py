from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze_song import analyze, trace_track
from build_nds_experiment import build_experiment
from nds_music import (NoteDefinition, SoundArchive, convert_song, decode_adpcm,
                       nds_sdat, note_bytes, read_event, trace_sequence, wait_bytes)
from nds_track_merge import BATTLE_GROUPS, assess_groups, convert_merged_song, expand_actions, pitch_commands
from scan_audio import apply_bps


def note(key=60, velocity=100, length=12):
    return bytes([key, velocity, length])


class SequenceConversionTests(unittest.TestCase):
    def test_mod_delay_is_u16_and_does_not_create_phantom_note(self):
        raw = b'\xE0\x00\x00\xCC\x00\xC7\x00\x81\x02' + note() + b'\x80\x0C\xFF'
        event = read_event(raw, 0)
        self.assertEqual(event['next'], 3)
        self.assertEqual(read_event(raw, 3)['opcode'], 0xCC)
        track = trace_sequence(raw)[0]
        self.assertEqual(track['notes'], [(2, 60)])
        self.assertEqual(track['end_ticks'], 12)

    def test_note_wait_and_polyphonic_chord_have_different_timing(self):
        waited = trace_sequence(b'\x81\x02' + note() + note(64) + b'\xFF')[0]
        poly = trace_sequence(b'\xC7\x00\x81\x02' + note() + note(64) + b'\x80\x0C\xFF')[0]
        self.assertEqual([a['ticks'] for a in waited['actions'] if a['name'] == 'note'], [0, 12])
        self.assertEqual([a['ticks'] for a in poly['actions'] if a['name'] == 'note'], [0, 0])
        self.assertEqual((waited['end_ticks'], poly['end_ticks']), (24, 12))

    def test_calls_and_finite_loops_execute_exactly(self):
        raw = bytearray(b'\xC7\x00\x81\x02\xD4\x02\x95\x10\x00\x00\xFC\xFF')
        raw.extend(bytes(16 - len(raw)))
        raw.extend(note() + b'\x80\x0C\xFD')
        track = trace_sequence(bytes(raw))[0]
        self.assertEqual(track['end_ticks'], 24)
        self.assertEqual([a['ticks'] for a in track['actions'] if a['name'] == 'note'], [0, 12])

    def test_repeat_state_keeps_controller_state(self):
        raw = b'\xC7\x00\x81\x02' + note() + b'\x80\x0C\x94\x04\x00\x00'
        track = trace_sequence(raw)[0]
        self.assertEqual((track['loop_start_ticks'], track['loop_ticks']), (0, 12))

    def test_unsupported_executed_controls_and_bad_paths_fail(self):
        for raw in [b'\xA0\x00', b'\xD3\x7F\xFF', b'\xFD',
                    b'\x94\xFF\xFF\xFF', b'\x94\x00\x00\x00',
                    b'\x81\x81\x00\xFF', b'\xCA\x01' + note() + b'\xFF',
                    note() + b'\xCA\x01\xFF']:
            with self.subTest(raw=raw.hex()), self.assertRaises(ValueError):
                trace_sequence(raw)

    def test_argument_bounds_and_truncation_fail(self):
        for raw in [b'\xE0\x00', b'\x80\x80\x80\x80\x80', note(60, 200), note(length=0)]:
            with self.subTest(raw=raw.hex()), self.assertRaises(ValueError):
                trace_sequence(raw)

    def test_mplay_lengths_preserve_odd_gate_and_long_wait(self):
        for duration in [1, 11, 23, 43, 95, 127, 223]:
            raw = b'\xBD\x00' + note_bytes(60, 90, duration) + wait_bytes(321) + b'\xB1'
            decoded = trace_track(raw, 0)
            played = next(e for e in decoded['events'] if e['name'] == 'NOTE')
            self.assertEqual(played['duration_ticks'], duration)
            self.assertEqual(decoded['ticks_before_repeat'], 321)


class SampleConversionTests(unittest.TestCase):
    @staticmethod
    def archive_for(raw):
        class Fixture:
            def sequence(self, index):
                return raw, {'bank_id': 0, 'volume': 75}
            def bank(self, index):
                return None, [0]
            def note_definition(self, bank, instrument, key):
                return NoteDefinition(0, 0, 60, 127, 127, 127, 127, 64)
            def wave(self, archive, index):
                return [0, 32767, 0, -32768], {'effective_rate_hz': 22050, 'looped': True,
                                              'loop_start_samples': 0, 'sample_count': 4}
        return Fixture()

    def test_high_tempo_and_optional_music_priority_headroom(self):
        raw = b'\xC7\x00\xE1\x96\x00\xC6\x7F\x81\x02' + note() + b'\x80\x0C\x94\x09\x00\x00'
        _, dependency, report = convert_song(self.archive_for(raw), 0, native_effect_headroom=True)
        self.assertEqual(report['tempo_mapping'][0]['gba_parameter'], 151)
        self.assertEqual(dependency['header']['priority'], 20)
        self.assertEqual(report['priority_mapping'], {'127': 0})
        self.assertEqual([e['value'] for e in dependency['tracks'][0]['events'] if e['name'] == 'PRIO'], [0])
        with self.assertRaisesRegex(ValueError, 'Tempo outside'):
            convert_song(self.archive_for(raw.replace(b'\xE1\x96\x00', b'\xE1\xFF\x00')), 0)

    def test_direct_conversion_repeat_excludes_simultaneous_prefix_note(self):
        raw = b'\xC7\x00\xE1\x78\x00\x81\x02' + note(60) + note(64) + b'\x80\x0C\x94\x0A\x00\x00'
        _, dependency, report = convert_song(self.archive_for(raw), 0)
        self.assertTrue(report['note_timing_check'])
        notes = [(e['ticks'], e['key']) for e in dependency['tracks'][0]['events'] if e['name'] == 'NOTE']
        self.assertEqual(notes, [(0, 60), (0, 64), (12, 64)])

    def test_invalid_song_gain_fails_before_reading_source(self):
        for gain in [float('nan'), float('inf'), -25, 13, '3.5', True]:
            with self.subTest(gain=gain), self.assertRaisesRegex(ValueError, 'Song gain'):
                convert_song(None, 0, song_gain_db=gain)

    def test_signed_header_and_low_nibble_first(self):
        self.assertEqual(decode_adpcm(struct.pack('<hH', -100, 0) + bytes(4)), [-100] * 8)
        self.assertEqual(decode_adpcm(bytes(4) + b'\x71\x00\x00\x00'), [1, 12, 14, 15, 16, 17, 18, 19])

    def test_predictor_clamps_and_malformed_headers_fail(self):
        self.assertEqual(decode_adpcm(struct.pack('<hH', 32760, 88) + b'\x77' * 4), [32767] * 8)
        for raw in [bytes(3), bytes(5), struct.pack('<hH', 0, 89) + bytes(4)]:
            with self.subTest(raw=raw.hex()), self.assertRaises(ValueError):
                decode_adpcm(raw)

    def test_generated_pcm_header_tuning_pan_loop_and_gba_reparse(self):
        class Fixture:
            def sequence(self, index):
                return b'\xC7\x00\xE1\x78\x00\x81\x02' + note() + b'\x80\x0C\x94\x07\x00\x00', {'bank_id': 0, 'volume': 127}
            def bank(self, index):
                return None, [0]
            def note_definition(self, bank, instrument, key):
                return NoteDefinition(0, 0, 72, 127, 127, 127, 127, 90)
            def wave(self, archive, index):
                return [-32768, 0, 32767, 0], {'effective_rate_hz': 22050, 'looped': True,
                                             'loop_start_samples': 1, 'sample_count': 4}
        blob, dependency, report = convert_song(Fixture(), 0)
        wave = dependency['samples'][0]
        self.assertEqual(wave['frequency_raw'], 11025 * 1024)
        self.assertEqual((wave['loop_start'], wave['sample_count']), (1, 4))
        self.assertEqual(blob[wave['file_offset'] + 16:wave['file_offset'] + 20], b'\x80\x00\x7F\x00')
        child = next(t for t in dependency['tones'] if t['type_raw'] == 0)
        raw = bytes.fromhex(child['raw_hex'])
        self.assertEqual((raw[1], raw[3]), (60, 218))
        self.assertTrue(report['note_timing_check'])


class TrackMergingTests(unittest.TestCase):
    def test_shared_instrument_splits_only_conflicting_track_local_alias(self):
        for second_key in (60, 96):
            with self.subTest(second_key=second_key):
                header = b'\xFE\x03\x00\x93\x01' + bytes(3)
                setup = b'\xC7\x00\x81\x02'
                def program(start, key, tempo=b''):
                    intro = setup + tempo
                    return (intro + bytes([key, 100, 0x82, 0x2C]) + b'\x80\x83\x00\x94'
                            + (start + len(intro)).to_bytes(3, 'little'))
                first = program(len(header), 60, b'\xE1\x78\x00')
                second_offset = len(header) + len(first)
                raw = header[:5] + second_offset.to_bytes(3, 'little') + first + program(second_offset, second_key)
                blob, dep, report = convert_merged_song(SampleConversionTests.archive_for(raw), 0, [(0,), (1,)])
                self.assertEqual(len(report['instruments']), 1 if second_key == 60 else 2)
                self.assertEqual(len(report['voice_context_splits']), int(second_key != 60))
                bank = dep['header']['tone_bank']['file_offset']
                for track, source_key in enumerate((60, second_key)):
                    n = next(n for n in report['note_mapping'] if n['target_track'] == track)
                    self.assertEqual(n['gba_key'], 127)
                    child = struct.unpack_from('<I', blob, bank + n['gba_voice'] * 12 + 4)[0] - 0x08000000
                    self.assertEqual(blob[child + 127 * 12 + 1], source_key)
                    self.assertTrue(any(e['name'] == 'EOT' and e['ticks'] == 300 for e in dep['tracks'][track]['events']))

    def test_long_note_carries_across_jump_without_retrigger(self):
        # 500-tick cycle, 300-tick gate beginning at 400. Native LFO's
        # warmup gives a matching carried voice at both loop boundaries.
        intro = b'\xC7\x00\xE1\x78\x00\x81\x02'
        body = b'\x80\x83\x10\x3C\x64\x82\x2C\x80\x64'
        raw = intro + body + b'\x94' + len(intro).to_bytes(3, 'little')
        archive = SampleConversionTests.archive_for(raw)
        _, dep, report = convert_merged_song(archive, 0, [(0,)], native_pitch_lfo=True)
        carry = report['long_note_loop_carries'][0]
        self.assertEqual((carry['note_start_relative_ticks'], carry['eot_relative_ticks']), (-100, 200))
        events = dep['tracks'][0]['events']
        self.assertFalse(any(e['name'] == 'TIE' and e['ticks'] == 500 for e in events))
        self.assertTrue(any(e['name'] == 'EOT' and e['ticks'] == 700 for e in events))
        with self.assertRaisesRegex(ValueError, 'matching carry'):
            convert_merged_song(archive, 0, [(0,)])
        # Increasing the gate beyond a complete period aliases two voices.
        overlapping = raw.replace(b'\x82\x2C', b'\x84\x58')
        with self.assertRaisesRegex(ValueError, 'Overlapping long notes'):
            convert_merged_song(SampleConversionTests.archive_for(overlapping), 0, [(0,)], native_pitch_lfo=True)

    def test_loop_between_simultaneous_events_does_not_repeat_prefix_note(self):
        track = {'termination': 'loop', 'loop_action': 1, 'loop_ticks': 12,
                 'actions': [{'ticks': 0, 'name': 'note', 'key': 60},
                             {'ticks': 0, 'name': 'note', 'key': 64}]}
        self.assertEqual([(a['ticks'], a['key']) for a in expand_actions(track, 25)],
                         [(0, 60), (0, 64), (12, 64), (24, 64)])

    def test_bend_and_tune_encode_every_source_battle_bend_exactly(self):
        for source_range in (2, 12):
            for bend in range(-128, 128):
                units = (bend * source_range) >> 1
                raw = pitch_commands(units)
                self.assertEqual((raw[0], raw[2], raw[4]), (0xC1, 0xC0, 0xC8))
                self.assertTrue(all(0 <= x <= 127 for x in (raw[3], raw[5])))
                self.assertEqual((raw[3] - 64) * raw[1] + raw[5] - 64, units)

    @staticmethod
    def track(index, expression=127, bend=0, pan_change=False):
        state = {'volume': 100, 'expression': expression, 'bend': bend,
                 'bend_range': 2, 'pan': 64}
        actions = [{'ticks': 0, 'name': 'control', 'state_after': state},
                   {'ticks': 0, 'name': 'note', 'duration': 10}]
        if pan_change:
            actions.append({'ticks': 5, 'name': 'control',
                            'state_after': {**state, 'pan': 80}})
        return {'track': index, 'termination': 'loop', 'loop_action': 0,
                'loop_ticks': 12, 'loop_start_ticks': 0, 'actions': actions}

    def test_incompatible_live_controls_and_held_pan_are_rejected(self):
        for changes, message in [({'expression': 100}, 'expression'),
                                 ({'bend': 12}, 'pitch'),
                                 ({'pan_change': True}, 'held note')]:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, message):
                assess_groups([self.track(0), self.track(1, **changes)], [(0, 1)])
        self.assertEqual(assess_groups([self.track(0), self.track(1)], [(0, 1)])[:2], (0, 12))

    def test_each_source_track_must_be_included_exactly_once(self):
        for groups in [((0,),), ((0, 1), (1,))]:
            with self.assertRaisesRegex(ValueError, 'exactly once'):
                assess_groups([self.track(0), self.track(1)], groups)


NDS = Path('/home/harp/projects/nds/roms/ssr3b.nds')
BASE = ROOT.parent / 'roms/exe6.gba'


@unittest.skipUnless(NDS.exists() and BASE.exists(), 'local NDS/EXE6 inputs unavailable')
class LocalNdsExperimentTests(unittest.TestCase):
    def test_envelope_experiments_preserve_native_data_and_explicit_policy(self):
        source, base = NDS.read_bytes(), BASE.read_bytes()
        for song, index, samples in [('sf3-hokora-envelope', 10, 18), ('sf3-friend-envelope', 29, 23)]:
            with self.subTest(song=song):
                output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
                    source, base, events=('1', '21', 'scene:communication'), song=song)
                self.assertEqual(apply_bps(base, patch)[0], output)
                self.assertEqual(manifest['nds_conversion']['sequence_index'], index)
                self.assertTrue(manifest['nds_conversion']['envelope_approximation'])
                self.assertEqual(conversion['track_count'], 8)
                self.assertEqual(len(dependency['samples']), samples)
                self.assertFalse(conversion['envelope_approximation']['overrides_affect_existing_voices'])
                if index == 10:
                    self.assertNotIn('native_pitch_lfo_approximation', manifest['nds_conversion'])
                    self.assertTrue(any(a['ds_attack'] == 100 and a['gba_attack'] == 74
                                        for a in conversion['envelope_approximation']['attack_fits']))
                else:
                    self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_approximation'])
                    self.assertTrue(conversion['native_pitch_lfo']['configs'])
                    self.assertTrue(any(n['source_envelope']['release'] == 115 for n in conversion['note_mapping']))
                table = manifest['target_table_file_offset']
                self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
                expected = bytearray(base)
                for start, end in manifest['declared_prefix_ranges']:
                    expected[start:end] = output[start:end]
                self.assertEqual(output[:len(base)], expected)

    def test_kando_keeps_seven_tracks_and_preserves_original_data(self):
        source, base = NDS.read_bytes(), BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            source, base, events=('1', '21', 'scene:communication'), song='kando')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(conversion['track_count'], 7)
        self.assertEqual(len(dependency['samples']), 14)
        self.assertEqual({t['loop_ticks'] for t in conversion['tracks']}, {3072})
        self.assertEqual(conversion['tempo_mapping'][0]['gba_parameter'], 151)
        self.assertTrue(conversion['note_timing_check'])
        self.assertLess(conversion['song_priority'] + max(conversion['priority_mapping'].values()), 112)
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_battle_merges_all_notes_and_keeps_long_echoes_independent(self):
        source, base = NDS.read_bytes(), BASE.read_bytes()
        output, patch, manifest, conversion, dependency, blob, _, _ = build_experiment(
            source, base, events=('1', '21', 'scene:communication'), song='battle')
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual((conversion['source_track_count'], conversion['track_count']), (11, 8))
        self.assertEqual(conversion['track_groups'], [list(g) for g in BATTLE_GROUPS])
        self.assertEqual(len(dependency['samples']), 28)
        self.assertTrue(conversion['note_timing_check'])
        self.assertEqual(conversion['merged_loop_ticks'], 5760)
        aliases = conversion['long_note_aliases']
        self.assertEqual({a['source_track'] for a in aliases}, {2, 15})
        self.assertEqual(len({a['gba_key'] for a in aliases}), 2)
        for alias in aliases:
            voice = next(a['gba_voice'] for a in conversion['note_mapping']
                         if a['source_track'] == alias['source_track'] and a['long_note'])
            bank = dependency['header']['tone_bank']['file_offset']
            child = struct.unpack_from('<I', blob, bank + voice * 12 + 4)[0] - 0x08000000
            self.assertEqual(blob[child + alias['gba_key'] * 12 + 1], alias['source_key'])
        target_table = manifest['target_table_file_offset']
        self.assertEqual(output[target_table:target_table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_room_execution_and_bps_preserve_native_target(self):
        source, base = NDS.read_bytes(), BASE.read_bytes()
        output, patch, manifest, conversion, dependency, blob, catalog, sdat = build_experiment(source, base, song_gain_db=0)
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(conversion['track_count'], 6)
        self.assertEqual(len(dependency['samples']), 15)
        self.assertEqual({t['loop_ticks'] for t in conversion['tracks']}, {1536})
        self.assertTrue(all(a['duration'] > 0 for t in conversion['tracks'] for a in t['actions'] if a['name'] == 'note'))
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)
        original_table = base[0x164E0C:0x164E0C + 474 * 8]
        target_table = manifest['target_table_file_offset']
        self.assertEqual(output[target_table:target_table + len(original_table)], original_table)
        with self.assertRaisesRegex(ValueError, 'capacity'):
            convert_song(SoundArchive(sdat), 2, track_capacity=5)

    def test_wrong_source_revision_rejected(self):
        raw = bytearray(NDS.read_bytes())
        raw[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'verified'):
            build_experiment(bytes(raw), BASE.read_bytes())

    def test_calibrated_gain_changes_only_imported_volume_operands(self):
        source, base = NDS.read_bytes(), BASE.read_bytes()
        old, _, old_manifest, _, _, _, _, _ = build_experiment(source, base, song_gain_db=0)
        new, patch, manifest, conversion, _, _, _, _ = build_experiment(source, base)
        self.assertEqual(conversion['song_gain_db'], 3.5)
        self.assertEqual(len(old), len(new))
        self.assertEqual(old[:len(base)], new[:len(base)])
        self.assertEqual(old_manifest['sound_mode_change'], manifest['sound_mode_change'])
        old_dep = analyze(old, old_manifest['target_table_file_offset'], 474)
        new_dep = analyze(new, manifest['target_table_file_offset'], 474)
        allowed = set()
        for old_track, new_track in zip(old_dep['tracks'], new_dep['tracks']):
            self.assertEqual(old_track['notes'], new_track['notes'])
            self.assertEqual(old_track['loop_ticks'], new_track['loop_ticks'])
            for old_event, new_event in zip(old_track['events'], new_track['events']):
                if old_event['name'] == 'VOL':
                    self.assertGreaterEqual(new_event['value'], old_event['value'])
                    self.assertLessEqual(new_event['value'], 127)
                    allowed.add(old_event['file_offset'] + 1)
                else:
                    self.assertEqual(old_event, new_event)
        changed = {i for i, (a, b) in enumerate(zip(old, new)) if a != b}
        self.assertTrue(changed)
        self.assertLessEqual(changed, allowed)
        self.assertEqual(apply_bps(base, patch)[0], new)
        with self.assertRaisesRegex(ValueError, 'headroom'):
            build_experiment(source, base, song_gain_db=12)


SF1 = Path('/home/harp/projects/nds/roms/ssr1d.nds')


@unittest.skipUnless(SF1.exists() and BASE.exists(), 'local Star Force 1/EXE6 inputs unavailable')
class LocalStarForce1Tests(unittest.TestCase):
    def test_ura_splits_shared_percussion_alias_and_preserves_native_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, blob, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-ura')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 18)
        self.assertNotIn('native_pitch_lfo_approximation', manifest['nds_conversion'])
        self.assertNotIn('envelope_approximation', manifest['nds_conversion'])
        self.assertEqual((conversion['track_count'], len(dependency['samples']), len(conversion['instruments'])), (8, 10, 6))
        self.assertEqual(conversion['voice_context_splits'], [
            {'gba_voice': 5, 'existing_voices': [4], 'source_track': 3, 'tick': 791,
             'source_instrument': 123, 'gba_key': 127, 'source_key': 60, 'conflicting_source_keys': [96]}])
        bank = dependency['header']['tone_bank']['file_offset']
        for track, voice, source_key in [(3, 5, 60), (7, 4, 96)]:
            long_notes = [n for n in conversion['note_mapping'] if n['source_track'] == track and n['long_note']]
            self.assertTrue(long_notes)
            self.assertEqual({(n['gba_voice'], n['gba_key']) for n in long_notes}, {(voice, 127)})
            child = struct.unpack_from('<I', blob, bank + voice * 12 + 4)[0] - 0x08000000
            self.assertEqual(blob[child + 127 * 12 + 1], source_key)
        self.assertEqual(len(conversion['long_note_loop_carries']), 5)
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_planetarium_carries_long_note_and_preserves_original_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-planetarium-delay')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 13)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_delay_approximation'])
        self.assertEqual((conversion['track_count'], len(dependency['samples'])), (8, 29))
        self.assertEqual(conversion['long_note_loop_carries'], [
            {'target_track': 7, 'source_track': 7, 'source_key': 53, 'gba_key': 126,
             'note_start_relative_ticks': -192, 'eot_relative_ticks': 192}])
        self.assertTrue(all(r['complete_loop_cycles'] == 2 for r in conversion['note_timing_validation']))
        self.assertEqual(conversion['note_timing_validation'][7]['gate_checked_until_ticks'], 22176)
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_boss_toggle_preserves_order_and_original_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-boss-toggle')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 28)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_live_toggle_approximation'])
        self.assertNotIn('envelope_approximation', manifest['nds_conversion'])
        self.assertEqual(conversion['track_count'], 7)
        self.assertEqual(len(dependency['samples']), 21)
        toggles = conversion['native_pitch_lfo']['live_toggle_approximation']['source_depth_toggles']
        self.assertEqual([(r['source_track'], r['ticks'], r['before'], r['after']) for r in toggles],
                         [(4, 3840, 0, 35), (4, 5952, 35, 0)])
        events = [e for e in dependency['tracks'][4]['events'] if e['ticks'] == 3840 and e['name'] != 'WAIT']
        index = next(i for i, e in enumerate(events) if e['name'] == 'NOTE')
        self.assertEqual([(e['name'], e.get('value')) for e in events[index + 1:]
                          if e['name'] in ('MOD', 'LFOS', 'LFODL', 'MODT')],
                         [('MOD', 4), ('LFOS', conversion['native_pitch_lfo']['configs'][0]['lfos'])])
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_gowaiincho_initializes_before_first_note_and_preserves_original_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-gowaiincho-delay')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 7)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_delay_approximation'])
        self.assertNotIn('envelope_approximation', manifest['nds_conversion'])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 24)
        lfo = conversion['native_pitch_lfo']
        self.assertEqual(lfo['delay_approximation']['initializations'],
                         [{'source_track': 2, 'activation_tick': 24, 'first_note_tick': 688, 'depth': 20}])
        self.assertEqual(lfo['configs'][0]['delay_mapping']['lfodl'], 5)
        events = dependency['tracks'][2]['events']
        self.assertEqual(min(e['ticks'] for e in events if e['name'] == 'NOTE'), 688)
        self.assertTrue(any(e['name'] == 'MOD' and e['ticks'] == 24 and e['value'] == 2 for e in events))
        self.assertTrue(any(e['name'] == 'LFODL' and e['ticks'] == 688 and e['value'] == 5 for e in events))
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_hometown_live_depth_preserves_same_tick_order_and_original_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-hometown-depth')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 3)
        for flag in ('native_pitch_lfo_live_depth_approximation', 'native_pitch_lfo_delay_approximation',
                     'envelope_approximation'):
            self.assertTrue(manifest['nds_conversion'][flag])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 19)
        events = [e for e in dependency['tracks'][2]['events'] if e['ticks'] == 3072 and e['name'] != 'WAIT']
        note_index = next(i for i, e in enumerate(events) if e['name'] == 'NOTE')
        self.assertEqual([(e['name'], e.get('value')) for e in events[note_index + 1:]], [('MOD', 2)])
        changes = conversion['native_pitch_lfo']['live_depth_approximation']['source_depth_changes']
        self.assertEqual([(c['ticks'], c['before'], c['after']) for c in changes],
                         [(3072, 10, 20), (6912, 20, 10)])
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_fmplanet_delay_is_explicit_and_preserves_original_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-fmplanet-delay')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 2)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_delay_approximation'])
        self.assertEqual(conversion['track_count'], 7)
        self.assertEqual(len(dependency['samples']), 16)
        config = conversion['native_pitch_lfo']['configs'][0]
        self.assertEqual(config['mod_delay'], 10)
        self.assertEqual(config['delay_mapping']['lfodl'], 6)
        self.assertEqual(conversion['merged_loop_ticks'], 2304)
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_last_preserves_boundary_tied_gate_and_native_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, blob, _, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-last')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 17)
        self.assertNotIn('native_pitch_lfo_approximation', manifest['nds_conversion'])
        self.assertEqual(conversion['track_groups'], [[i] for i in range(8)])
        self.assertEqual(len(dependency['samples']), 29)
        self.assertEqual(conversion['merged_loop_start_ticks'], 3072)
        self.assertEqual(conversion['merged_loop_ticks'], 7104)
        self.assertTrue(all(v['complete_loop_cycles'] == 2 for v in conversion['note_timing_validation']))
        alias = next(a for a in conversion['long_note_aliases']
                     if a['target_track'] == 7 and a['source_key'] == 59)
        events = dependency['tracks'][7]['events']
        self.assertTrue(any(e['name'] == 'TIE' and e['ticks'] == 9792 and e['key'] == alias['gba_key']
                            for e in events))
        self.assertEqual(events[dependency['tracks'][7]['loop_start_event']]['name'], 'EOT')
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_battle_pitch_lfo_is_explicit_and_keeps_long_gates(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, blob, _, sdat = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-battle-lfo')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_approximation'])
        self.assertTrue(conversion['native_pitch_lfo']['approximation'])
        self.assertEqual(conversion['track_groups'], [[i] for i in range(7)])
        self.assertEqual(len(dependency['samples']), 22)
        self.assertEqual({t['loop_ticks'] for t in conversion['tracks']}, {4608})
        self.assertEqual(conversion['merged_loop_start_ticks'], 9216)
        self.assertEqual({c['lfos'] for c in conversion['native_pitch_lfo']['configs']}, {13, 16})
        self.assertEqual({c['mod'] for c in conversion['native_pitch_lfo']['configs']}, {2, 3})
        # These source depth changes occur AFTER a note at the same tick.
        # Moving all controls before notes would restore stale per-note depth.
        for track, tick, depth in [(1, 0, 2), (2, 3072, 3), (3, 2304, 2)]:
            events = [e for e in dependency['tracks'][track]['events'] if e['ticks'] == tick]
            self.assertEqual([e['value'] for e in events if e['name'] == 'MOD'][-1], depth)
        self.assertEqual({a['source_key'] for a in conversion['long_note_aliases']}, {72, 74})
        bank = dependency['header']['tone_bank']['file_offset']
        for alias in conversion['long_note_aliases']:
            voice = next(a['gba_voice'] for a in conversion['note_mapping']
                         if a['source_key'] == alias['source_key'] and a['long_note'])
            children = struct.unpack_from('<I', blob, bank + voice * 12 + 4)[0] - 0x08000000
            self.assertEqual(blob[children + alias['gba_key'] * 12 + 1], alias['source_key'])
        with self.assertRaisesRegex(ValueError, 'Unsupported merged-conversion effect'):
            convert_merged_song(SoundArchive(sdat), 27, [(i,) for i in range(7)])
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_kincho_archive_conversion_and_original_data_preservation(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, catalog, _ = build_experiment(
            SF1.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf1-kincho')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['nds_file_id'], 667)
        self.assertEqual(manifest['nds_conversion']['source_profile'], 'ssr1d')
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 23)
        self.assertEqual(manifest['nds_conversion']['sequence_name'], 'BGM23KINCHO')
        self.assertIn('Star Force 1', catalog['source_labels']['nds-ssr1d'])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 15)
        self.assertEqual({t['loop_ticks'] for t in conversion['tracks']}, {2304})
        self.assertEqual(conversion['tempo_mapping'][0]['gba_parameter'], 115)
        self.assertTrue(conversion['note_timing_check'])
        self.assertLess(conversion['song_priority'] + max(conversion['priority_mapping'].values()), 112)
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    @unittest.skipUnless(all((SF1.parent / (key + '.nds')).exists() for key in ('ssr1l', 'ssr1p')),
                         'local Leo/Pegasus inputs unavailable')
    def test_three_source_variants_produce_identical_mplay_and_target(self):
        base, previous = BASE.read_bytes(), None
        for key in ('ssr1d', 'ssr1l', 'ssr1p'):
            output, _, manifest, _, _, blob, _, sdat = build_experiment(
                (SF1.parent / (key + '.nds')).read_bytes(), base, song='sf1-kincho')
            self.assertEqual(manifest['nds_conversion']['source_profile'], key)
            current = output, blob, sdat
            if previous is not None:
                self.assertEqual(current, previous)
            previous = current

    def test_source_game_and_song_must_match(self):
        with self.assertRaisesRegex(ValueError, 'selected source game'):
            build_experiment(SF1.read_bytes(), BASE.read_bytes(), song='room')
        if NDS.exists():
            with self.assertRaisesRegex(ValueError, 'selected source game'):
                build_experiment(NDS.read_bytes(), BASE.read_bytes(), song='sf1-kincho')

    def test_unverified_source_revision_rejected(self):
        raw = bytearray(SF1.read_bytes())
        raw[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'verified'):
            build_experiment(bytes(raw), BASE.read_bytes(), song='sf1-kincho')


SF2 = Path('/home/harp/projects/nds/roms/ssr2d.nds')


@unittest.skipUnless(SF2.exists() and BASE.exists(), 'local Star Force 2/EXE6 inputs unavailable')
class LocalStarForce2Tests(unittest.TestCase):
    def test_dempajiken_combines_envelope_and_loop_carry(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF2.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf2-dempajiken-envelope')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 11)
        self.assertTrue(manifest['nds_conversion']['envelope_approximation'])
        self.assertNotIn('native_pitch_lfo_approximation', manifest['nds_conversion'])
        self.assertEqual((conversion['track_count'], len(dependency['samples'])), (8, 19))
        self.assertEqual(conversion['long_note_loop_carries'], [
            {'target_track': 2, 'source_track': 2, 'source_key': 86, 'gba_key': 127,
             'note_start_relative_ticks': -120, 'eot_relative_ticks': 119}])
        self.assertEqual(conversion['note_timing_validation'][2]['gate_checked_until_ticks'], 6079)
        self.assertEqual([(r['ds_attack'], r['gba_attack'])
                          for r in conversion['envelope_approximation']['attack_fits']], [(100, 74), (127, 255)])
        self.assertEqual(min(n['tick'] for n in conversion['note_mapping']
                             if n['source_envelope']['attack'] == 100), 1536)
        self.assertEqual(manifest['output_fingerprint']['sha256'],
                         '0a727bac00d6a4b393a9d6f2b1c18a5eb3b23d585141d5121af38c59896d3982')
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_kaicyou_combines_envelope_and_both_initialization_orders(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF2.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf2-kaicyou-toggle')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 16)
        for flag in ('native_pitch_lfo_approximation', 'native_pitch_lfo_delay_approximation',
                     'native_pitch_lfo_live_toggle_approximation', 'envelope_approximation'):
            self.assertTrue(manifest['nds_conversion'][flag])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 24)
        self.assertEqual(conversion['native_pitch_lfo']['delay_approximation']['initializations'],
                         [{'source_track': 2, 'activation_tick': 768, 'first_note_tick': 48, 'depth': 10},
                          {'source_track': 4, 'activation_tick': 768, 'first_note_tick': 1056, 'depth': 10}])
        fits = conversion['envelope_approximation']['attack_fits']
        self.assertEqual([(r['ds_attack'], r['gba_attack']) for r in fits], [(100, 74), (127, 255)])
        events = [e for e in dependency['tracks'][2]['events'] if e['ticks'] == 768 and e['name'] != 'WAIT']
        note_index = next(i for i, e in enumerate(events) if e['name'] == 'NOTE')
        self.assertTrue(any(e['name'] == 'MOD' and e['value'] == 1 for e in events[note_index + 1:]))
        self.assertEqual(manifest['output_fingerprint']['sha256'],
                         '739726a97c9005ff4905258348c656836802fefc2847b0cdc6ff88b400c86aa5')
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_battle_delay_maps_faster_tempo_without_expanding_tracks(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF2.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf2-battle-delay')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 27)
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_delay_approximation'])
        self.assertNotIn('envelope_approximation', manifest['nds_conversion'])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 24)
        config = conversion['native_pitch_lfo']['configs'][0]
        self.assertEqual(config['gba_tempo'], 151)
        self.assertEqual(config['mod_delay'], 10)
        self.assertEqual(config['delay_mapping']['lfodl'], 7)
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_nessie_combines_slower_attack_and_lfo_and_preserves_native_data(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, _, _ = build_experiment(
            SF2.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf2-nessie-envelope')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 15)
        self.assertTrue(manifest['nds_conversion']['envelope_approximation'])
        self.assertTrue(manifest['nds_conversion']['native_pitch_lfo_approximation'])
        self.assertEqual(conversion['track_count'], 8)
        self.assertEqual(len(dependency['samples']), 29)
        self.assertEqual({a['ds_attack']: a['gba_attack']
                          for a in conversion['envelope_approximation']['attack_fits']},
                         {90: 66, 100: 74, 127: 255})
        self.assertTrue(conversion['native_pitch_lfo']['configs'])
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    def test_win_archive_conversion_and_original_data_preservation(self):
        base = BASE.read_bytes()
        output, patch, manifest, conversion, dependency, _, catalog, _ = build_experiment(
            SF2.read_bytes(), base, events=('1', '21', 'scene:communication'), song='sf2-win')
        self.assertEqual(apply_bps(base, patch)[0], output)
        self.assertEqual(manifest['nds_conversion']['nds_file_id'], 975)
        self.assertEqual(manifest['nds_conversion']['source_profile'], 'ssr2d')
        self.assertEqual(manifest['nds_conversion']['sequence_index'], 30)
        self.assertEqual(manifest['nds_conversion']['sequence_name'], 'BGM_WIN')
        self.assertIn('Star Force 2', catalog['source_labels']['nds-ssr2d'])
        self.assertEqual(conversion['track_count'], 7)
        self.assertEqual(len(dependency['samples']), 15)
        self.assertEqual({t['loop_ticks'] for t in conversion['tracks']}, {1536})
        self.assertEqual(conversion['tempo_mapping'][0]['gba_parameter'], 171)
        self.assertTrue(conversion['note_timing_check'])
        self.assertLess(conversion['song_priority'] + max(conversion['priority_mapping'].values()), 112)
        self.assertEqual({r['trigger_id']: r['ids'] for r in manifest['hook']['rules']},
                         {1: [474], 21: [474], 65534: [474]})
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table + 474 * 8], base[0x164E0C:0x164E0C + 474 * 8])
        expected = bytearray(base)
        for start, end in manifest['declared_prefix_ranges']:
            expected[start:end] = output[start:end]
        self.assertEqual(output[:len(base)], expected)

    @unittest.skipUnless((SF2.parent / 'ssr2s.nds').exists(), 'local second Star Force 2 input unavailable')
    def test_both_source_variants_produce_identical_mplay_and_target(self):
        base, previous = BASE.read_bytes(), None
        for key in ('ssr2d', 'ssr2s'):
            output, _, manifest, _, _, blob, _, sdat = build_experiment(
                (SF2.parent / (key + '.nds')).read_bytes(), base, song='sf2-win')
            self.assertEqual(manifest['nds_conversion']['source_profile'], key)
            current = output, blob, sdat
            if previous is not None:
                self.assertEqual(current, previous)
            previous = current

    def test_source_game_and_song_must_match(self):
        base = BASE.read_bytes()
        source = SF2.read_bytes()
        for song in ('room', 'battle', 'kando', 'sf1-kincho', 'sf1-battle-lfo'):
            with self.subTest(song=song), self.assertRaisesRegex(ValueError, 'selected source game'):
                build_experiment(source, base, song=song)
        for path in (NDS, SF1):
            if path.exists():
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'selected source game'):
                    build_experiment(path.read_bytes(), base, song='sf2-win')

    def test_unverified_source_revision_rejected(self):
        raw = bytearray(SF2.read_bytes())
        raw[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'verified'):
            build_experiment(bytes(raw), BASE.read_bytes(), song='sf2-win')


if __name__ == '__main__':
    unittest.main()
