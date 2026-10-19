#!/usr/bin/env python3
"""Check actual allocated PCM envelope parameters and steps in a title window.

Natural title start, dummy SDL output, no register/RAM edits. This checks native
GBA envelope behavior, not DS waveform equality, complete loops or gameplay.
"""
import argparse
import json
import os
from pathlib import Path
import struct

from analyze_song import analyze
from render_preview import start_preview_song
from scan_audio import ROM_BASE, fingerprint
from target_profiles import valid_manifest_target
from validate_playback import Debugger
from validate_song import memory


def envelope_step(flags, level, adsr):
    """One ordinary PCM mixer envelope update, excluding START/pseudo echo."""
    attack, decay, sustain, release = adsr
    if flags & 0x80 or flags & 4:
        raise ValueError('Start/pseudo-echo outside this step model')
    if flags & 0x40:
        value = level * release >> 8
        return (flags, value) if value else (0, 0)
    if flags & 3 == 3:
        value = min(255, level + attack)
        return (flags - int(value == 255), value)
    if flags & 3 == 2:
        value = level * decay >> 8
        if value <= sustain:
            return (flags - 1, sustain) if sustain else (0, 0)
        return flags, value
    return flags, level


def note_started_between(track, key, start, end):
    """Find note-ons in [start, end), including unfolded command cycles."""
    def matches(event):
        return event['name'] in ('NOTE', 'TIE') and event['key'] == key

    if any(matches(e) and start <= e['ticks'] < end for e in track['events']):
        return True
    if track['termination'] == 'repeated_state':
        period = track['loop_ticks']
        for event in track['events'][track['loop_start_event']:]:
            if matches(event):
                turn = max(1, (start - event['ticks'] + period - 1) // period)
                if event['ticks'] + turn * period < end:
                    return True
    return False


def probe(experiment, directory, frames=1800, mgba='/usr/games/mgba'):
    manifest = json.loads((experiment / 'build.json').read_text())
    data = (experiment / 'unified.gba').read_bytes()
    if (not valid_manifest_target(manifest) or fingerprint(data) != manifest['output_fingerprint']
            or not (manifest.get('nds_conversion', {}).get('envelope_approximation')
                    or manifest.get('nds_conversion', {}).get('finite_release_snapshots'))):
        raise ValueError('Requires a matching envelope experiment ROM/manifest')
    conversion = json.loads((experiment / 'conversion.json').read_text())
    song = next(r['ids'][0] for r in manifest['hook']['rules'] if r['trigger_id'] == 1)
    dependency = analyze(data, manifest['target_table_file_offset'], song)
    bank = dependency['header']['tone_bank']['file_offset']
    allowed = set()
    for n in conversion['note_mapping']:
        children = struct.unpack_from('<I', data, bank + n['gba_voice'] * 12 + 4)[0] - ROM_BASE
        tone = data[children + n['gba_key'] * 12:children + (n['gba_key'] + 1) * 12]
        allowed.add((n['target_track'], struct.unpack_from('<I', tone, 4)[0], n['gba_key'], tuple(tone[8:12])))
    directory.mkdir(parents=True, exist_ok=False)
    rom = directory / 'test.gba'
    rom.write_bytes(data)
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory.resolve() / 'config'))
    env.pop('LD_PRELOAD', None)
    report = {'complete': False, 'rom_fingerprint': fingerprint(data), 'scope': 'bounded natural title window',
              'register_injection': False, 'full_loop_coverage': False,
              'sampling_point': 'Root MPlayMain entry before sequence/mixer updates, once per SoundMain call',
              'requested_frames': frames, 'snapshots': []}
    with (directory / 'debugger.txt').open('w') as transcript:
        debugger = Debugger([mgba, '-d', str(rom.resolve())], env, transcript)
        try:
            debugger.prompt()
            player = start_preview_song(debugger, data, manifest, song)
            header = debugger.read(4, player)
            track_base = debugger.read(4, player + 44)
            sound = debugger.read(4, 0x03007FF0)
            callback = debugger.read(4, sound + 32) & ~1
            root_player = debugger.read(4, sound + 36)
            debugger.command(f'break/t {callback:#x}')
            previous, previous_clock = {}, 0
            comparisons = observed = slow = releases = 0
            for frame in range(1, frames + 1):
                for _ in range(64):
                    registers = debugger.hit(callback)
                    if registers[0] == root_player:
                        break
                else:
                    raise AssertionError('Root sound callback not reached')
                clock = debugger.read(4, player + 12)
                if debugger.read(4, player) != header or clock < previous_clock:
                    raise AssertionError('Game replaced or restarted envelope song')
                raw = memory(debugger, sound + 80, 12 * 64)
                current, rows = {}, []
                for slot in range(12):
                    channel = raw[slot * 64:(slot + 1) * 64]
                    flags = channel[0]
                    wave, _, owner = struct.unpack_from('<III', channel, 36)
                    if not flags & 0xC7 or not track_base <= owner < track_base + len(dependency['tracks']) * 80:
                        continue
                    track = (owner - track_base) // 80
                    adsr, key, level = tuple(channel[4:8]), channel[17], channel[9]
                    identity = (track, wave, key, adsr)
                    if identity not in allowed:
                        raise AssertionError(f'Allocated channel envelope differs from mapped tone: {identity}')
                    observed += 1
                    slow += int(adsr[0] != 255 and flags & 3 == 3 and not flags & 0xC0)
                    releases += int(bool(flags & 0x40))
                    current[slot] = (identity, flags, level)
                    before = previous.get(slot)
                    # A slot can be stolen/retriggered between video snapshots.
                    new_note = note_started_between(dependency['tracks'][track], key, previous_clock, clock)
                    if (before and before[0] == identity and not new_note
                            and not before[1] & 0x84 and not flags & 0x84
                            and bool(before[1] & 0x40) == bool(flags & 0x40)
                            and channel[12] == 0):
                        expected = envelope_step(before[1], before[2], adsr)
                        if expected != (flags, level):
                            raise AssertionError(f'Native envelope step differs at frame {frame}, slot {slot}: '
                                                 f'{expected} != {(flags, level)}')
                        comparisons += 1
                    rows.append({'slot': slot, 'track': track, 'key': key, 'adsr': adsr,
                                 'flags': flags, 'amplitude': level})
                report['snapshots'].append({'frame': frame, 'clock': clock, 'channels': rows})
                previous, previous_clock = current, clock
            # Some songs first use the fitted attack after the title window.
            # Require it only when a corresponding source note was reached,
            # and report the remaining coverage explicitly.
            slow_notes = [n for n in conversion['note_mapping']
                          if n['source_envelope']['attack'] != 127]
            expects_slow = any(n['tick'] < clock for n in slow_notes)
            if not comparisons or not observed or (expects_slow and not slow):
                raise AssertionError('Insufficient live envelope/attack observations')
            report.update(complete=True, final_clock=clock, mapped_channel_observations=observed,
                          exact_native_step_comparisons=comparisons, slow_attack_observations=slow,
                          slow_attack_source_note_in_window=expects_slow,
                          full_song_slow_attack_covered=not slow_notes or bool(slow),
                          release_observations=releases)
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            debugger.close()
            (directory / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--frames', type=int, default=1800)
    args = parser.parse_args()
    if not 2 <= args.frames <= 2400:
        parser.error('Choose 2..2400 frames for a bounded title window')
    r = probe(args.experiment, args.out, args.frames)
    print(f"Passed {r['exact_native_step_comparisons']} native envelope steps; "
          f"{r['slow_attack_observations']} slow-attack, {r['release_observations']} release observations")


if __name__ == '__main__':
    main()
