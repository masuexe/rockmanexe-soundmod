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
import struct

from nds_music import SoundArchive
from render_preview import runtime_sound_config, start_preview_song
from scan_audio import ROM_BASE, fingerprint
from target_profiles import manifest_layout, valid_manifest_target
from validate_playback import Debugger
from validate_song import memory


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
    control_matches = 0
    if (reference / 'controls.csv').is_file():
        with (reference / 'controls.csv').open() as stream:
            controls = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        for track in conversion['tracks']:
            for opcode in (0xC0, 0xC4, 0xD5):
                actual = [(a['tick'], a['value']) for a in controls
                          if a['track'] == track['track'] and a['opcode'] == opcode]
                if not actual:
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
                control_matches += len(actual)
    return {'capture': 'software DS reference, not hardware/emulator recording',
            'reference_metadata': json.loads((reference / 'reference.json').read_text()),
            'sequence_note_matches': len(notes), 'per_track_note_matches': counts,
            'decoded_sample_comparisons': sample_checks, 'pan_bend_expression_matches': control_matches,
            'complete': True}


def probe_runtime(data, manifest, directory, mgba):
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
                call(0x080005D4, 21)
                call(0x080007BE)
                native_header = struct.unpack_from('<I', data, table + 21 * 8)[0]
                if debugger.read(4, player) != native_header or debugger.read(1, state + 15) != 21:
                    raise AssertionError('Ordinary music request did not restore native song 21')
                report['native_music_restored'] = True
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
        except BaseException as error:
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
    args = parser.parse_args()
    manifest = json.loads((args.experiment / 'build.json').read_text())
    data = (args.experiment / 'unified.gba').read_bytes()
    if not valid_manifest_target(manifest) or fingerprint(data) != manifest['output_fingerprint']:
        parser.error('ROM does not match verified target manifest')
    reference = check_reference(args.experiment, args.reference) if args.reference else None
    report = probe_runtime(data, manifest, args.out, args.mgba)
    if reference:
        (args.out / 'reference-validation.json').write_text(json.dumps(reference, indent=2) + '\n')
    print(f"Native effects, music continuation and queued stop passed; reference notes: {reference['sequence_note_matches'] if reference else 'not checked'}")


if __name__ == '__main__':
    main()
