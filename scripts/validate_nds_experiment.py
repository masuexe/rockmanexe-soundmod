#!/usr/bin/env python3
"""Independent DS reference checks and controlled EXE6 SFX/queue/stop probes.

Sustained natural playback is checked separately with validate_song.py.
Runtime helper calls here explicitly inject PC/LR/arguments into a disposable
emulator. They do not establish a complete gameplay or communication session.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import struct

from nds_music import SoundArchive, SUSTAIN_DB
from nds_lfo import ds_pitch_units
from render_preview import runtime_sound_config, start_preview_song
from scan_audio import ROM_BASE, fingerprint
from target_profiles import manifest_layout, valid_manifest_target
from validate_playback import Debugger
from validate_song import memory


def check_envelope_reference(conversion, archive, reference):
    """Compare note-on ADSR and per-voice DS updates with independent logs."""
    fields = ('attack', 'decay', 'sustain', 'release')
    with (reference / 'note-envelopes.csv').open() as stream:
        actual = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
    bank, _ = archive.bank(conversion['sequence_info']['bank_id'])
    checked = 0
    for track in conversion['tracks']:
        rows = [r for r in actual if r['track'] == track['track']]
        if not rows:
            raise AssertionError('DS envelope reference does not cover all tracks')
        last = rows[-1]['tick']
        basis = [a for a in track['actions'] if a['name'] == 'note']
        body = [a for a in track['actions'][track['loop_action']:] if a['name'] == 'note']
        expanded = basis + [{**a, 'ticks': a['ticks'] + turn * track['loop_ticks']}
                            for turn in range(1, 1 + last // track['loop_ticks']) for a in body]
        expected = []
        for a in expanded:
            if a['ticks'] > last:
                continue
            definition = archive.note_definition(bank, a['instrument'], a['key'])
            values = [a['state_after'][f] if a['state_after'][f] is not None else getattr(definition, f)
                      for f in fields]
            expected.append((a['ticks'], a['instrument'], a['key'], a['velocity'], a['duration'], *values))
        observed = [tuple(r[f] for f in ('tick', 'instrument', 'key', 'velocity', 'duration', *fields)) for r in rows]
        if observed != expected:
            raise AssertionError(f'Independent note-on envelope differs on track {track["track"]}')
        checked += len(rows)
    updates = attacks = 0
    with (reference / 'envelopes.csv').open() as stream:
        for raw in csv.DictReader(stream):
            r = {k: int(v) for k, v in raw.items()}
            before, state, amplitude = r['before_state'], r['before_state'], r['before_ampl']
            if before in (1, 2):
                amplitude = -723 * 128 if before == 1 else amplitude
                old = amplitude >> 7
                while True:
                    amplitude = -((-amplitude * r['attack_coefficient']) // 256)
                    if amplitude >> 7 != old:
                        break
                state = 3 if amplitude == 0 else 2
                attacks += int(r['attack_coefficient'] != 0)
            elif before == 3:
                amplitude -= r['decay_rate']
                sustain = SUSTAIN_DB[r['sustain']] << 7
                if amplitude <= sustain:
                    amplitude, state = sustain, 4
            elif before == 5:
                amplitude -= r['release_rate']
            elif before != 4:
                raise AssertionError('Unexpected live DS envelope stage')
            if (amplitude, state) != (r['ampl'], r['state']):
                raise AssertionError('Independent DS envelope update differs')
            updates += 1
    if not updates:
        raise AssertionError('Empty DS envelope update reference')
    return {'note_on_snapshots': checked, 'per_voice_timer_updates': updates,
            'noninstant_attack_updates': attacks, 'complete': True}


def check_delay_reference(conversion, reference):
    configs = {tuple(c[k] for k in ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay'))
               for c in conversion['native_pitch_lfo']['configs']}
    updates = waiting = active = first_active = 0
    delays = set()
    previous = {}
    with (reference / 'modulation-delay.csv').open() as stream:
        for raw in csv.DictReader(stream):
            r = {k: int(v) for k, v in raw.items()}
            if r['delay'] and (r['type'], r['speed'], r['depth'], r['range'], r['delay']) not in configs:
                raise AssertionError('Independent delayed modulation configuration differs')
            enabled = r['counter_before'] >= r['delay']
            count = r['counter_before'] if enabled else r['counter_before'] + 1
            phase = (r['phase_before'] + r['speed'] * 64) % 32768 if enabled else r['phase_before']
            if (count, phase, int(enabled)) != (r['counter_after'], r['phase_after'], r['active']):
                raise AssertionError('Independent DS delay counter/phase transition differs')
            updates += 1
            if r['delay']:
                delays.add(r['delay'])
                waiting += not enabled
                active += enabled
                before = previous.get((r['track'], r['channel']))
                first_active += bool(enabled and r['phase_before'] == 0 and before
                                     and not before['active'] and before['counter_after'] == r['delay']
                                     and before['timer_frame'] + 1 == r['timer_frame'])
            previous[r['track'], r['channel']] = r
    if not waiting or not active or not first_active:
        raise AssertionError('Reference does not cover delayed holds and activation')
    return {'complete': True, 'voice_timer_updates': updates, 'waiting_updates': waiting,
            'active_after_delay_updates': active, 'zero_phase_activation_observations': first_active,
            'source_delays_observed': sorted(delays)}


def check_live_depth_reference(conversion, reference):
    """Independent UpdateMod observations must retain voice phase and counter."""
    transitions = carried = 0
    with (reference / 'modulation-changes.csv').open() as stream:
        for raw in csv.DictReader(stream):
            r = {k: int(v) for k, v in raw.items()}
            if (r['phase_before'], r['counter_before']) != (r['phase_after'], r['counter_after']):
                raise AssertionError('Independent DS live depth update resets phase/counter')
            if r['before_depth'] > 0 and r['depth'] > 0:
                transitions += 1
                carried += bool(r['phase_before'] or r['counter_before'])
    if not transitions or not carried:
        raise AssertionError('Reference does not cover positive live depth changes with carried state')
    return {'complete': True, 'positive_voice_depth_changes': transitions,
            'changes_with_nonzero_phase_or_counter': carried,
            'phase_and_delay_count_preserved': True}


def check_reference(experiment, reference):
    conversion = json.loads((experiment / 'conversion.json').read_text())
    archive = SoundArchive((experiment / 'source.sdat').read_bytes())
    sample_checks = []
    for sample in conversion['samples']:
        pcm, info = archive.wave(sample['archive_id'], sample['wave_id'])
        expected = struct.pack('<' + 'h' * len(pcm), *pcm)
        slot = conversion['sequence_info']['bank_id']
        _, archive_ids = archive.bank(slot)
        archive_slot = archive_ids.index(sample['archive_id'])
        raw = (reference / f'wave-{archive_slot}-{sample["wave_id"]}.pcm16').read_bytes()
        if raw != expected:
            raise AssertionError(f'Independent ADPCM decoder differs for wave {sample["wave_id"]}')
        sample_checks.append({'wave_id': sample['wave_id'], 'sample_count': len(pcm),
                              'exact_pcm16_match': True})
    with (reference / 'notes.csv').open() as stream:
        notes = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
    if not notes or {n['track'] for n in notes} != {t['track'] for t in conversion['tracks']}:
        raise AssertionError('Independent DS reference does not cover all tracks')
    counts = {}
    for track in conversion['tracks']:
        actual = [(n['tick'], n['instrument'], n['key'], n['velocity'], n['duration'])
                  for n in notes if n['track'] == track['track']]
        last = actual[-1][0]
        basis = [(a['ticks'], a['instrument'], a['key'], a['velocity'], a['duration'])
                 for a in track['actions'] if a['name'] == 'note']
        if track['termination'] != 'loop' or last < track['end_ticks'] + track['loop_ticks']:
            raise AssertionError('Reference must cover two complete loops')
        expected = basis[:]
        # A repeat can start between simultaneous events at the same tick.
        # Use the recorded action index, not only the tick boundary.
        body = [(a['ticks'], a['instrument'], a['key'], a['velocity'], a['duration'])
                for a in track['actions'][track['loop_action']:] if a['name'] == 'note']
        for turn in range(1, last // track['loop_ticks'] + 1):
            expected.extend((tick + turn * track['loop_ticks'], instrument, key, velocity, duration)
                            for tick, instrument, key, velocity, duration in body)
        expected = [n for n in expected if n[0] <= last]
        if actual != expected:
            raise AssertionError(f'Independent DS note execution differs on track {track["track"]}')
        counts[str(track['track'])] = len(actual)
    control_matches = depth_control_matches = 0
    live_depth = conversion.get('native_pitch_lfo', {}).get('live_depth_approximation')
    if live_depth and not (reference / 'controls.csv').is_file():
        raise AssertionError('Live depth conversion needs independent control observations')
    if (reference / 'controls.csv').is_file():
        with (reference / 'controls.csv').open() as stream:
            controls = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        for track in conversion['tracks']:
            for opcode in (0xC0, 0xC4, 0xD5, 0xE0) + ((0xCA,) if live_depth else ()):
                actual = [(a['tick'], a['value']) for a in controls
                          if a['track'] == track['track'] and a['opcode'] == opcode]
                if not actual:
                    if opcode == 0xCA and any(a['opcode'] == opcode for a in track['actions']):
                        raise AssertionError('Independent DS live depth controls are missing')
                    continue
                last = actual[-1][0]
                def value(action):
                    raw = action['value']
                    return raw - 256 if opcode == 0xC4 and raw >= 128 else raw
                basis = [(a['ticks'], value(a)) for a in track['actions'] if a['opcode'] == opcode]
                body = [(a['ticks'], value(a)) for a in track['actions'][track['loop_action']:] if a['opcode'] == opcode]
                expected = basis[:]
                for turn in range(1, 1 + last // track['loop_ticks']):
                    expected.extend((tick + turn * track['loop_ticks'], v) for tick, v in body)
                expected = [a for a in expected if a[0] <= last]
                if actual != expected:
                    raise AssertionError(f'Independent DS control {opcode:#x} differs on track {track["track"]}')
                if opcode == 0xCA:
                    depth_control_matches += len(actual)
                else:
                    control_matches += len(actual)
    modulation_matches = 0
    modulation_file = reference / 'modulation.csv'
    if conversion.get('native_pitch_lfo') and not modulation_file.is_file():
        raise AssertionError('LFO conversion needs a per-voice modulation reference')
    if modulation_file.is_file():
        with modulation_file.open() as stream:
            for raw in csv.DictReader(stream):
                row = {k: int(v) for k, v in raw.items()}
                if row['type'] != 0:
                    raise AssertionError('Only pitch modulation reference is currently checked')
                if ds_pitch_units(row['phase'], row['depth'], row['range']) != row['value']:
                    raise AssertionError('Independent DS sine modulation value differs')
                modulation_matches += 1
    if conversion.get('native_pitch_lfo') and not modulation_matches:
        raise AssertionError('No active DS modulation observed')
    envelope = (check_envelope_reference(conversion, archive, reference)
                if conversion.get('envelope_approximation') else None)
    delay = (check_delay_reference(conversion, reference)
             if conversion.get('native_pitch_lfo', {}).get('delay_approximation') else None)
    return {'capture': 'software DS reference, not hardware/emulator recording',
            'reference_metadata': json.loads((reference / 'reference.json').read_text()),
            'sequence_note_matches': len(notes), 'per_track_note_matches': counts,
            'decoded_sample_comparisons': sample_checks, 'pan_bend_expression_matches': control_matches,
            'source_pitch_modulation_matches': modulation_matches,
            'live_depth_control_matches': depth_control_matches,
            'live_depth_reference': check_live_depth_reference(conversion, reference) if live_depth else None,
            'envelope_reference': envelope, 'delay_reference': delay, 'complete': True}


def probe_runtime(data, manifest, directory, mgba, lifecycle=False):
    layout = manifest_layout(manifest)
    if manifest['target_profile'] not in ('exe6', 'exe6f') or not manifest.get('nds_conversion'):
        raise ValueError('Requires the Japanese EXE6 NDS experiment manifest')
    directory.mkdir(parents=True, exist_ok=False)
    rom = directory / 'test.gba'
    rom.write_bytes(data)
    table = manifest['target_table_file_offset']
    title = next(rule for rule in manifest['hook']['rules'] if rule['trigger_id'] == 1)
    song = title['ids'][0]
    header = struct.unpack_from('<I', data, table + song * 8)[0]
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory.resolve() / 'config'))
    env.pop('LD_PRELOAD', None)
    report = {'complete': False, 'controlled_helper_calls': True,
              'natural_music_start': True, 'two_peer_gameplay_tested': False,
              'effects': []}
    with (directory / 'debugger.txt').open('w') as transcript:
        debugger = Debugger([mgba, '-d', str(rom.resolve())], env, transcript)
        try:
            debugger.prompt()
            player = start_preview_song(debugger, data, manifest, song)
            config = runtime_sound_config(debugger)
            report['sound_config'] = config
            track_base = debugger.read(4, player + 44)
            count = debugger.read(1, player + 8)
            sound = int(config['sound_info'], 16)
            max_music_voices = 0

            def voices():
                raw = memory(debugger, sound + 80, 12 * 64)
                return sum(bool(raw[i] & 0xC7) and track_base <= struct.unpack_from('<I', raw, i + 44)[0] < track_base + count * 80
                           for i in range(0, len(raw), 64))

            for _ in range(240):
                debugger.command('frame')
                if debugger.read(4, player) != header:
                    raise AssertionError('Game replaced imported music during short probe')
                max_music_voices = max(max_music_voices, voices())
            report['max_music_voices_first_240_frames'] = max_music_voices
            report['music_clock_before_effects'] = debugger.read(4, player + 12)
            # Known original queue helper context, reached through normal play.
            debugger.command('break/t 0x080007BE')
            registers = debugger.hit(0x080007BE)
            toolkit, stack = registers[10], registers[13]
            state = debugger.read(4, toolkit + 0x3C)
            debugger.command('delete 4')
            debugger.command('break/t 0x0800940A')

            def call(address, argument=None):
                if argument is not None:
                    debugger.command(f'w/r r0 {argument}')
                debugger.command('w/r lr 0x0800940B')
                debugger.command(f'w/r pc 0x{address:08X}')
                result = debugger.hit(0x0800940A)
                if result[10] != toolkit or result[13] != stack:
                    raise AssertionError('Native helper failed Toolkit/stack preservation')
                return result

            for effect in (100, 129):
                expected_header, index = struct.unpack_from('<IH', data, table + effect * 8)
                effect_player = struct.unpack_from('<I', data, layout['player_table_offset'] + index * 12)[0]
                if effect_player == player:
                    raise AssertionError('Preservation effect unexpectedly uses music player')
                call(0x080005CC, effect)
                call(0x080007BE)
                if debugger.read(4, effect_player) != expected_header or debugger.read(4, player) != header:
                    raise AssertionError('Native effect or imported music header differs')
                report['effects'].append({'id': effect, 'native_player_initialized': True,
                                          'imported_music_preserved': True})
            # Restore the original queue-function CPU context; game resumes normally.
            debugger.command('delete 5')
            for register in range(15):
                debugger.command(f'w/r r{register} 0x{registers[register]:08X}')
            # Debugger r15 includes the Thumb pipeline offset. Resume the actual
            # function entry, which recomputes flags, instead of skipping an opcode.
            debugger.command('w/r pc 0x080007BE')
            for _ in range(30):
                debugger.command('frame')
                max_music_voices = max(max_music_voices, voices())
            after_clock = debugger.read(4, player + 12)
            if debugger.read(4, player) != header or after_clock <= report['music_clock_before_effects'] or not voices():
                raise AssertionError('Music did not continue with original effects active')
            report.update(music_clock_after_effects=after_clock, music_advances_after_effects=True)
            # Restore a valid queue-helper context for the original queued all-stop.
            debugger.command('break/t 0x080007BE')
            registers = debugger.hit(0x080007BE)
            toolkit, stack = registers[10], registers[13]
            debugger.command('delete 6')
            debugger.command('break/t 0x0800940A')
            # Exercise the real scene branch with a synthetic battle descriptor.
            # This tests dispatch/rematch/restoration, not a live linked battle.
            scene_rule = next((r for r in manifest['hook']['rules'] if r['trigger_id'] == 65534), None)
            if scene_rule:
                descriptor_pointer = debugger.read(4, 0x020348BC)
                scratch = debugger.read(4, 0x02001000)
                ordinary_rule = next((r for r in manifest['hook']['rules'] if r['trigger_id'] == 21), None)
                if ordinary_rule:
                    descriptor_offset = 0xB4B18 if manifest['target_profile'] == 'exe6' else 0xB32B8
                    if data[descriptor_offset + 2] != 21:
                        raise AssertionError('Original first battle descriptor no longer requests music 21')
                    debugger.command(f'w/4 0x020348BC {ROM_BASE + descriptor_offset:#x}')
                    debugger.command('w/r r5 0x02034880')
                    call(0x080093F4, 0)
                    call(0x080007BE)
                    expected = struct.unpack_from('<I', data, table + ordinary_rule['ids'][0] * 8)[0]
                    if debugger.read(4, player) != expected or debugger.read(1, state + 15) != 21:
                        raise AssertionError('Ordinary battle descriptor did not select numbered music pool')
                    report['ordinary_battle_dispatch'] = {'complete': True, 'flags': 0,
                                                         'original_descriptor_offset': descriptor_offset,
                                                         'music_id': 21, 'controlled_helper_call': True}
                debugger.command('w/4 0x020348BC 0x02001000')
                debugger.command('w/1 0x02001002 21')
                scene_header = struct.unpack_from('<I', data, table + scene_rule['ids'][0] * 8)[0]
                for _ in range(2):
                    debugger.command('w/r r5 0x02034880')
                    call(0x080093F4, 8)
                    call(0x080007BE)
                    if debugger.read(4, player) != scene_header or debugger.read(1, state + 15) != 254:
                        raise AssertionError('Communication scene/rematch dispatch differs')
                report.update(scene_dispatch=True, scene_rematch=True,
                              scene_descriptor='synthetic music ID 21, communication flag 8')
                restore_id = 2 if any(r['trigger_id'] == 21 for r in manifest['hook']['rules']) else 21
                call(0x080005D4, restore_id)
                call(0x080007BE)
                native_header = struct.unpack_from('<I', data, table + restore_id * 8)[0]
                if debugger.read(4, player) != native_header or debugger.read(1, state + 15) != restore_id:
                    raise AssertionError('Ordinary music request did not restore native song')
                report['native_music_restored'] = True
                report['native_restore_id'] = restore_id
                # Stop must be checked against the imported song again.
                debugger.command('w/r r5 0x02034880')
                call(0x080093F4, 8)
                call(0x080007BE)
                debugger.command(f'w/4 0x020348BC {descriptor_pointer:#x}')
                debugger.command(f'w/4 0x02001000 {scratch:#x}')
            call(0x08000784)
            call(0x080007BE)
            if not debugger.read(4, player + 4) & 0x80000000 or debugger.read(1, state + 15) != 255:
                raise AssertionError('Native queued stop did not stop imported music/reset indicator')
            report.update(queued_stop=True, music_indicator_reset=True, complete=True)
            if lifecycle:
                if not scene_rule or scene_header != header:
                    raise ValueError('Lifecycle probe requires the same imported song on title and communication')
                # The current return sentinel is breakpoint 7. Further IDs are
                # read from mGBA rather than assuming its allocation policy.
                return_breakpoint = 7

                def breakpoint(address):
                    response = debugger.command(f'break/t {address:#x}')
                    match = re.search(r'Added breakpoint #(\d+)', response)
                    if not match:
                        raise RuntimeError('Cannot identify debugger breakpoint: ' + response)
                    return int(match[1])

                def advance(frames, observe_voices=False):
                    nonlocal registers, return_breakpoint
                    debugger.command(f'delete {return_breakpoint}')
                    for register in range(15):
                        debugger.command(f'w/r r{register} {registers[register]:#x}')
                    debugger.command('w/r pc 0x080007BE')
                    observed = 0
                    for _ in range(frames):
                        debugger.command('frame')
                        if observe_voices:
                            observed = max(observed, voices())
                    entry_breakpoint = breakpoint(0x080007BE)
                    registers = debugger.hit(0x080007BE)
                    if registers[10] != toolkit or registers[13] != stack:
                        raise AssertionError('Queue context changed during lifecycle probe')
                    debugger.command(f'delete {entry_breakpoint}')
                    return_breakpoint = breakpoint(0x0800940A)
                    return observed

                def start_scene():
                    saved_pointer = debugger.read(4, 0x020348BC)
                    saved_scratch = debugger.read(4, 0x02001000)
                    try:
                        debugger.command('w/4 0x020348BC 0x02001000')
                        debugger.command('w/1 0x02001002 21')
                        debugger.command('w/r r5 0x02034880')
                        call(0x080093F4, 8)
                        call(0x080007BE)
                    finally:
                        debugger.command(f'w/4 0x020348BC {saved_pointer:#x}')
                        debugger.command(f'w/4 0x02001000 {saved_scratch:#x}')
                    if (debugger.read(4, player) != header or debugger.read(4, player + 12) != 0
                            or debugger.read(1, state + 15) != 254):
                        raise AssertionError('Communication start did not reset imported song clock')

                transitions = []
                report['lifecycle'] = {'complete': False, 'controlled_helper_calls': True,
                                       'actual_results_screen_tested': False,
                                       'actual_overworld_transition_tested': False,
                                       'cycles': transitions}
                middle_id = 3 if any(r['trigger_id'] == 21 for r in manifest['hook']['rules']) else 21
                for cycle, native_id in enumerate((2, middle_id, 2), 1):
                    start_scene()
                    advance(120)
                    before = debugger.read(4, player + 12)
                    if before <= 0 or not voices():
                        raise AssertionError('Imported song failed to advance before stop')
                    call(0x08000784)
                    call(0x080007BE)
                    if (not debugger.read(4, player + 4) & 0x80000000
                            or debugger.read(1, state + 15) != 255 or voices()):
                        raise AssertionError('Queued stop left live imported voices or music indicator')
                    advance(2)
                    if voices():
                        raise AssertionError('Imported voices returned after stop')
                    call(0x080005D4, native_id)
                    call(0x080007BE)
                    expected = struct.unpack_from('<I', data, table + native_id * 8)[0]
                    native_voices = advance(60, observe_voices=True)
                    if (debugger.read(4, player) != expected or debugger.read(4, player + 12) <= 0
                            or debugger.read(1, state + 15) != native_id or not native_voices):
                        raise AssertionError('Native numbered music failed after imported stop')
                    start_scene()
                    advance(120)
                    rematch_clock = debugger.read(4, player + 12)
                    start_scene()  # Repeated scene marker must still restart.
                    advance(30)
                    after = debugger.read(4, player + 12)
                    if not 0 < after < rematch_clock or not voices():
                        raise AssertionError('Rematch did not restart and resume imported music')
                    transitions.append({'cycle': cycle, 'clock_before_stop': before,
                                        'stop_clears_imported_voices': True,
                                        'native_request_id': native_id, 'native_playback_resumes': True,
                                        'native_max_observed_pcm_voices': native_voices,
                                        'clock_before_rematch': rematch_clock,
                                        'clock_after_rematch_30_frames': after,
                                        'rematch_resets_clock': True})
                report['lifecycle']['complete'] = True
        except BaseException as error:
            report['complete'] = False
            report['error'] = repr(error)
            raise
        finally:
            debugger.close()
            (directory / 'runtime.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mgba', default='/usr/games/mgba')
    parser.add_argument('--lifecycle', action='store_true',
                        help='Also probe three controlled stop/native-restore/rematch cycles with normal frames between requests')
    args = parser.parse_args()
    manifest = json.loads((args.experiment / 'build.json').read_text())
    data = (args.experiment / 'unified.gba').read_bytes()
    if not valid_manifest_target(manifest) or fingerprint(data) != manifest['output_fingerprint']:
        parser.error('ROM does not match verified target manifest')
    reference = check_reference(args.experiment, args.reference) if args.reference else None
    report = probe_runtime(data, manifest, args.out, args.mgba, args.lifecycle)
    if reference:
        (args.out / 'reference-validation.json').write_text(json.dumps(reference, indent=2) + '\n')
    print(f"Native effects, music continuation and queued stop passed; reference notes: {reference['sequence_note_matches'] if reference else 'not checked'}")


if __name__ == '__main__':
    main()
