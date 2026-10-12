#!/usr/bin/env python3
"""Probe original/target track and PCM-channel state at specified music clocks.

This complements the same-emulator WAV comparison. Original selection uses a
controlled audio-ID injection; target selection uses its natural title hook.
No mixer registers, sample buffers, or later song starts are redirected.
"""
import argparse
import json
import os
from pathlib import Path
import struct

from analyze_song import analyze
from compare_fidelity import start_source_song
from original_catalog import PROFILES
from render_preview import start_preview_song, runtime_sound_config
from scan_audio import ROM_BASE, fingerprint
from target_profiles import manifest_layout, valid_manifest_target
from validate_playback import Debugger
from validate_song import memory, expected_state


def probe(data, table, song, start, directory, clocks, mgba):
    directory.mkdir(parents=True, exist_ok=False)
    rom = directory/'test.gba'
    rom.write_bytes(data)
    dep = analyze(data, table, song)
    count = dep['header']['track_count']
    bank = dep['header']['tone_bank']['file_offset']
    samples = {ROM_BASE+s['file_offset']: s for s in dep['samples']}
    header = struct.unpack_from('<I', data, table+song*8)[0]
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory.resolve()/'config'))
    env.pop('LD_PRELOAD', None)
    report = {'rom_fingerprint': fingerprint(data), 'song': song, 'snapshots': [],
              'sequence_model_matches': 0, 'requested_clocks': clocks}
    seen_waves = set()
    maximum_channels = 0
    with (directory/'debugger.txt').open('w') as transcript:
        debugger = Debugger([mgba, '-d', str(rom)], env, transcript)
        try:
            debugger.prompt()
            player = start(debugger)
            tracks = debugger.read(4, player+44)
            config = runtime_sound_config(debugger)
            report['sound_config'] = config
            report['sound_registers_initial_hex'] = memory(debugger, 0x04000080, 16).hex()
            sound = int(config['sound_info'], 16)
            pending = list(clocks)
            previous_clock = 0
            for frame in range(1, 2001):
                debugger.command('frame')
                player_raw = memory(debugger, player, 64)
                actual_header, status = struct.unpack_from('<II', player_raw)
                clock = struct.unpack_from('<I', player_raw, 12)[0]
                if actual_header != header or clock < previous_clock:
                    raise ValueError('Game interrupted the selected song during probe')
                previous_clock = clock
                raw_tracks = memory(debugger, tracks, count*80)
                track_states = []
                for i, track in enumerate(dep['tracks']):
                    raw = raw_tracks[i*80:(i+1)*80]
                    actual = {'cursor': struct.unpack_from('<I', raw, 64)[0], 'wait': raw[1],
                              'pattern_depth': raw[2], 'key': raw[5], 'velocity': raw[6],
                              'running_status': raw[7], 'ended': not bool(raw[0] & 0x80),
                              'tone_hex': raw[36:48].hex()}
                    expected = expected_state(track, clock, data, bank)
                    if expected['tone_hex'] is None:
                        expected['tone_hex'] = actual['tone_hex']
                    if expected != actual:
                        raise ValueError(f'Sequence mismatch at frame {frame}, clock {clock}, track {i}: {actual} != {expected}')
                    report['sequence_model_matches'] += 1
                    track_states.append({'track': i, 'state_bytes_0_31': raw[:32].hex(),
                                         'key': raw[5], 'velocity': raw[6], 'wait': raw[1],
                                         'tone_type': raw[36], 'tone_key': raw[37],
                                         'tone_envelope_hex': raw[44:48].hex()})
                channels = []
                channel_bytes = memory(debugger, sound+80, 12*64)
                for offset in range(0, len(channel_bytes), 64):
                    raw = channel_bytes[offset:offset+64]
                    wave, current, owner = struct.unpack_from('<III', raw, 36)
                    if raw[0] & 0xC7 and tracks <= owner < tracks+count*80:
                        seen_waves.add(wave)
                        if wave not in samples:
                            raise ValueError('Mixer used a sample outside the dependency closure')
                        sample = samples[wave]
                        wave_offset, wave_size = sample['file_offset'], sample['size_bytes']
                        channels.append({'track': (owner-tracks)//80, 'status': raw[0],
                                         'type_raw': raw[1], 'sample_position': current-wave-16,
                                         'key': raw[8], 'envelope': raw[9],
                                         'right_volume': raw[2], 'left_volume': raw[3],
                                         'frequency_raw': struct.unpack_from('<I', raw, 32)[0],
                                         'wave_sha256': fingerprint(data[wave_offset:wave_offset+wave_size])['sha256']})
                maximum_channels = max(maximum_channels, len(channels))
                if pending and clock >= pending[0]:
                    report['snapshots'].append({'requested_clock': pending.pop(0), 'clock': clock,
                                                'frame': frame, 'player_status': status,
                                                'tracks': track_states, 'pcm_channels': channels,
                                                'sound_registers_hex': memory(debugger, 0x04000060, 48).hex()})
                if not pending:
                    report.update(frames=frame, final_clock=clock, complete=True,
                                  distinct_pcm_samples=len(seen_waves), max_active_pcm_channels=maximum_channels)
                    break
            else:
                raise ValueError('Frame limit reached before requested clocks')
        except BaseException as error:
            report.update(complete=False, error=str(error))
            raise
        finally:
            debugger.close()
            (directory/'probe.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--key', required=True, help='Original source track key, e.g. exe1:2')
    parser.add_argument('--target-rom', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--clock', type=int, action='append')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mgba', default='/usr/games/mgba')
    args = parser.parse_args()
    try:
        source, index = args.key.split(':')
        index = int(index)
        profile = PROFILES[source]
    except (ValueError, KeyError):
        parser.error('Choose a cataloged original track key, e.g. exe1:2')
    if not 0 <= index < profile['entry_count']:
        parser.error('Source song is outside its verified table')
    original, target = args.source.read_bytes(), args.target_rom.read_bytes()
    manifest = json.loads(args.manifest.read_text())
    if fingerprint(original) != profile['fingerprint']:
        parser.error('Unsupported source fingerprint')
    if not valid_manifest_target(manifest) or fingerprint(target) != manifest['output_fingerprint']:
        parser.error('Unsupported target or mismatched build manifest')
    clocks = sorted(set(args.clock or [64, 128, 256]))
    if not clocks or clocks[0] < 1:
        parser.error('Clocks must be positive')
    layout = manifest_layout(manifest)
    rule = next((r for r in manifest['hook']['rules'] if r['trigger_id']==layout['preview_trigger']), None)
    if rule is None or rule['keys'] != [args.key]:
        parser.error('Target title pool must contain exactly the requested source track')
    song = rule['ids'][0]
    args.out.mkdir(parents=True, exist_ok=False)
    results = {}
    results['source'] = probe(original, profile['table_offset'], index,
                              lambda d: start_source_song(d, original, profile, index),
                              args.out/'source', clocks, args.mgba)
    results['target'] = probe(target, manifest['target_table_file_offset'], song,
                              lambda d: start_preview_song(d, target, manifest, song),
                              args.out/'target', clocks, args.mgba)
    (args.out/'comparison.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps({name: {k: r[k] for k in ['complete', 'frames', 'final_clock', 'sequence_model_matches',
                                             'distinct_pcm_samples', 'max_active_pcm_channels']}
                      for name, r in results.items()}, indent=2))


if __name__ == '__main__':
    main()
