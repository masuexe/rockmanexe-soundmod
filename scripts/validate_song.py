#!/usr/bin/env python3
"""Compare sustained donor or transplanted song execution with the sequence model.

Uses dummy SDL output, not an audible listening test. A controlled ID injection
selects the song at the first natural start call, then normal game/emulator code
runs frame by frame. Optional --keep-song redirects later header arguments in
the debugger, without adding a permanent game hook. Reports sequence and mixer evidence.
"""
import argparse
import json
import os
from pathlib import Path
import re
import struct

from analyze_song import analyze
from scan_audio import ROM_BASE, fingerprint
from validate_playback import Debugger, PROFILE_SHA256


def memory(debugger, address, size):
    text = debugger.command(f'x/1 0x{address:08X} {size}')
    output = bytearray()
    for line in text.splitlines():
        if re.match(r'^0x[0-9A-Fa-f]+:', line):
            output.extend(int(value, 16) for value in line.split(':', 1)[1].split())
    if len(output) != size:
        raise ValueError(f'Expected {size} bytes, got {len(output)}: {text}')
    return bytes(output)


def expected_state(track, clock, data, bank):
    if track['termination'] == 'repeated_state' and clock > track['ticks_before_repeat']:
        start, duration = track['loop_start_ticks'], track['loop_ticks']
        clock = start + (clock - start - 1) % duration + 1
    result = {'cursor': ROM_BASE + track['file_offset'], 'wait': 0, 'pattern_depth': 0,
              'key': 0, 'velocity': 0, 'running_status': 0, 'ended': False, 'tone_hex': None}
    for event in track['events']:
        if event['ticks'] >= clock:
            break
        result['cursor'] = ROM_BASE + event['next_file_offset']
        result['running_status'] = event['running_status_after'] or 0
        result['pattern_depth'] = event['pattern_depth_after']
        result['wait'] = max(0, event['duration_ticks'] - (clock - event['ticks'])) if event['name'] == 'WAIT' else 0
        if event['name'] in ('NOTE', 'TIE'):
            result['key'] = event['key']
            result['velocity'] = event['velocity']
        elif event['name'] == 'EOT' and 'key' in event:
            result['key'] = event['key']
        elif event['name'] == 'VOICE':
            offset = bank + event['value'] * 12
            result['tone_hex'] = data[offset:offset + 12].hex()
        elif event['name'] == 'FINE':
            result['ended'] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--id', type=int)
    parser.add_argument('--unified', type=Path, help='Unified build manifest; starts the selected title song naturally')
    parser.add_argument('--transplant', type=Path, help='Manifest authorizing the verified experimental PvP image')
    parser.add_argument('--keep-song', action='store_true', help='Redirect later starts on the selected player to this header in debugger RAM')
    parser.add_argument('--frames', type=int, default=3000, help='Maximum frames; must reach sequence completion')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mgba', default='/usr/games/mgba')
    args = parser.parse_args()
    data = args.rom.read_bytes()
    profile, table, player_table, entry, core, count = 'exegp', 0x160658, 0x160604, 0x0804C3BC, 0x0804CAF0, 170
    manifest = None
    if args.unified:
        if args.transplant or args.keep_song:
            parser.error('--unified validates natural playback; incompatible with transplant/keep-song probes')
        manifest = json.loads(args.unified.read_text())
        if (manifest.get('target_profile') != 'exe45-pvp'
            or manifest['target_base_fingerprint']['sha256'] != PROFILE_SHA256['exe45-pvp']
            or manifest['output_fingerprint'] != fingerprint(data)):
            parser.error('Unified image does not match its version-pinned manifest')
        profile, table, player_table, entry, core, count = 'exe45-pvp-unified', manifest['target_table_file_offset'], 0x135094, 0x080EE344, 0x080EEA78, manifest['table_entry_count']
        if args.id is None:
            title = next((rule for rule in manifest['hook']['rules'] if rule['trigger_id'] == 55), None)
            if title is None or len(title['ids']) != 1:
                parser.error('Choose --id explicitly unless title pool contains one track')
            args.id = title['ids'][0]
    elif args.transplant:
        manifest = json.loads(args.transplant.read_text())
        if (manifest.get('target_profile') != 'exe45-pvp'
            or manifest['target_base_fingerprint']['sha256'] != PROFILE_SHA256['exe45-pvp']
            or manifest['output_fingerprint'] != fingerprint(data)
            or manifest['target_table_file_offset'] != 0x135214):
            parser.error('Experimental ROM/manifest does not match the verified PvP profile')
        profile, table, player_table, entry, core, count = 'exe45-pvp-transplant', 0x135214, 0x135094, 0x080EE344, 0x080EEA78, 499
        args.id = manifest['target_id'] if args.id is None else args.id
    elif fingerprint(data)['sha256'] != PROFILE_SHA256['exegp']:
        parser.error('Requires the verified EXEGP baseline or an explicit transplant manifest')
    if args.id is None:
        args.id = 1
    if args.id < 0 or args.id >= count or args.frames < 1:
        parser.error('Invalid ID or frame limit')
    dependency = analyze(data, table, args.id)
    validation_clock = max(track['ticks_before_repeat'] + (track['loop_ticks'] if track['termination'] == 'repeated_state' else 0) + 1 for track in dependency['tracks'])
    args.out.mkdir(parents=True, exist_ok=False)
    work = args.out.resolve()
    rom = work / 'test.gba'
    rom.write_bytes(data)
    (work / 'dependencies.json').write_text(json.dumps(dependency, indent=2) + '\n')
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', XDG_CONFIG_HOME=str(work / 'config'))
    env.pop('LD_PRELOAD', None)
    snapshots, seen_waves, pcm_hashes = [], set(), set()
    report = {'schema_version': 1, 'rom_fingerprint': fingerprint(data), 'rom_path': str(args.rom),
              'id': args.id, 'register_injection': not bool(args.unified), 'audio_output': 'SDL dummy',
              'complete': False, 'clock_restarts': 0, 'snapshots': snapshots,
              'profile': profile, 'transplant_manifest': str(args.transplant) if args.transplant else None,
              'keep_song': args.keep_song, 'core_header_redirects': [],
              'unified_manifest': str(args.unified) if args.unified else None, 'startup_calls': []}
    bank = dependency['header']['tone_bank']['file_offset']
    track_count = len(dependency['tracks'])
    field_a = struct.unpack_from('<H', data, table + args.id * 8 + 4)[0]
    player = struct.unpack_from('<I', data, player_table + field_a * 12)[0]
    header = ROM_BASE + dependency['header']['file_offset']
    allowed_waves = {ROM_BASE + sample['file_offset'] for sample in dependency['samples']}
    previous_clock = 0
    with (work / 'debugger.txt').open('w') as transcript:
        debugger = Debugger([args.mgba, '-d', str(rom)], env, transcript)
        try:
            debugger.prompt()
            debugger.command(f'break/t 0x{entry:08X}')
            if args.unified:
                debugger.command(f'break/t 0x{core:08X}')
                incoming = None
                for _ in range(100):
                    text = debugger.command('continue')
                    regs = {int(n): int(value, 16) for n, value in re.findall(r'\br(\d+):\s*([0-9a-fA-F]{8})', text)}
                    if f'at 0x{entry:08X}' in text:
                        incoming = regs[0]
                        continue
                    if f'at 0x{core:08X}' not in text:
                        raise RuntimeError('Unexpected startup breakpoint')
                    report['startup_calls'].append({'incoming_id': incoming, 'player': f'0x{regs[0]:08X}', 'header': f'0x{regs[1]:08X}'})
                    incoming = None
                    if regs[0] == player and regs[1] == header:
                        returned = regs[14] & ~1
                        debugger.command(f'break/t 0x{returned:08X}')
                        debugger.hit(returned)
                        break
                else:
                    raise AssertionError('Selected song was not reached naturally')
                for number in (1, 2, 3):
                    debugger.command(f'delete {number}')
            else:
                debugger.hit(entry)
                debugger.command(f'w/r r0 {args.id}')
                debugger.command(f'break/t 0x{entry + 32:08X}')
                debugger.hit(entry + 32)
                debugger.command('delete 1')
                debugger.command('delete 2')
            if args.keep_song:
                debugger.command(f'break/t 0x{core:08X}')
            track_base = debugger.read(4, player + 44)
            capacity = debugger.read(1, player + 8)
            if capacity < track_count or debugger.read(4, player) != header:
                raise AssertionError('Header/player capacity mismatch')
            sound = debugger.read(4, 0x03007FF0)
            config = memory(debugger, sound, 80)
            report['sound_config'] = {'pcm_channels': config[6], 'frequency_selector': config[8],
                                      'samples_per_vblank': struct.unpack_from('<I', config, 16)[0],
                                      'mixing_rate_raw': struct.unpack_from('<I', config, 20)[0]}
            for frame in range(1, args.frames + 1):
                text = debugger.command('frame')
                while 'Hit breakpoint' in text:
                    if not args.keep_song or f'at 0x{core:08X}' not in text:
                        raise RuntimeError('An unexpected breakpoint remains enabled')
                    regs = {int(n): int(value, 16) for n, value in re.findall(r'\br(\d+):\s*([0-9a-fA-F]{8})', text)}
                    if regs[0] == player and regs[1] != header:
                        report['core_header_redirects'].append({'frame': frame, 'original_header': f'0x{regs[1]:08X}', 'replacement_header': f'0x{header:08X}'})
                        debugger.command(f'w/r r1 0x{header:08X}')
                    text = debugger.command('frame')
                player_bytes = memory(debugger, player, 64)
                actual_header, status = struct.unpack_from('<II', player_bytes)
                clock = struct.unpack_from('<I', player_bytes, 12)[0]
                if actual_header != header:
                    raise AssertionError(f'Game replaced selected song at frame {frame}')
                if clock < previous_clock:
                    report['clock_restarts'] += 1
                previous_clock = clock
                track_bytes = memory(debugger, track_base, track_count * 80)
                records = []
                for i, track in enumerate(dependency['tracks']):
                    raw = track_bytes[i * 80:(i + 1) * 80]
                    actual = {'cursor': struct.unpack_from('<I', raw, 64)[0], 'wait': raw[1],
                              'pattern_depth': raw[2], 'key': raw[5], 'velocity': raw[6],
                              'running_status': raw[7], 'ended': not bool(raw[0] & 0x80),
                              'tone_hex': raw[36:48].hex()}
                    expected = expected_state(track, clock, data, bank)
                    # Before the first sequence tick, the VOICE has not executed.
                    if expected['tone_hex'] is None:
                        expected['tone_hex'] = actual['tone_hex']
                    if actual != expected:
                        report['mismatch'] = {'frame': frame, 'clock': clock, 'track': i,
                                              'actual': actual, 'expected': expected}
                        raise AssertionError(report['mismatch'])
                    records.append(actual)
                snapshot = {'frame': frame, 'clock': clock, 'status': status, 'tracks': records}
                # Inspect PCM channel wave pointers every frame, restricted to this
                # player's tracks so other game effects are not counted as dependencies.
                channels = memory(debugger, sound + 80, 12 * 64)
                for offset in range(0, len(channels), 64):
                    raw = channels[offset:offset + 64]
                    wave, current, owner = struct.unpack_from('<III', raw, 36)
                    if raw[0] & 0xC7 and track_base <= owner < track_base + track_count * 80:
                        if wave not in allowed_waves:
                            raise AssertionError(f'Undecoded sample {wave:#x} at frame {frame}')
                        seen_waves.add(wave)
                if frame % 60 == 0:
                    pcm = memory(debugger, sound + 0x350, 2 * 1584)
                    if any(pcm):
                        pcm_hashes.add(fingerprint(pcm)['sha256'])
                snapshots.append(snapshot)
                if frame % 120 == 0:
                    print(f'frame {frame}: clock {clock}, {len(seen_waves)} observed samples, {len(pcm_hashes)} nonzero PCM snapshots', flush=True)
                if clock >= validation_clock:
                    break
            else:
                raise AssertionError('Frame limit reached before finite completion or loop coverage')
            report.update(frames=len(snapshots), final_clock=clock,
                          player_address=f'0x{player:08X}', track_base=f'0x{track_base:08X}',
                          sound_info=f'0x{sound:08X}', observed_samples=[f'0x{wave:08X}' for wave in sorted(seen_waves)],
                          nonzero_pcm_hashes=sorted(pcm_hashes))
            if seen_waves != allowed_waves or len(pcm_hashes) < 2:
                raise AssertionError('Sample coverage or changing PCM evidence incomplete')
            report['complete'] = True
            report['validation_clock_target'] = validation_clock
            report['terminations'] = sorted({track['termination'] for track in dependency['tracks']})
            print(f"Passed {len(snapshots)} frames, {track_count} tracks, all {len(seen_waves)} samples; final clock {clock}", flush=True)
        except BaseException as exc:
            report['error'] = repr(exc)
            raise
        finally:
            debugger.close()
            (work / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
