#!/usr/bin/env python3
"""Observe a carried TIE on native GBA PCM in a disposable synthetic song.

Reuses the first carried note's real bank, alias and gate. Shortens the cycle
to reach repeated jumps within the title window. This is a focused engine
probe, not execution of the original song's complete loops or gameplay.
"""
import argparse
import json
import os
from pathlib import Path
import struct

from analyze_song import trace_track
from nds_music import wait_bytes
from nds_track_merge import validate_loop_notes
from render_preview import start_preview_song
from scan_audio import ROM_BASE, fingerprint
from target_profiles import valid_manifest_target
from validate_playback import Debugger
from validate_song import memory


def probe(experiment, directory, mgba='/usr/games/mgba'):
    manifest = json.loads((experiment / 'build.json').read_text())
    original = (experiment / 'unified.gba').read_bytes()
    if not valid_manifest_target(manifest) or fingerprint(original) != manifest['output_fingerprint']:
        raise ValueError('Requires a matching verified experiment ROM')
    conversion = json.loads((experiment / 'conversion.json').read_text())
    carry = conversion['long_note_loop_carries'][0]
    note = next(n for n in conversion['note_mapping'] if n['target_track'] == carry['target_track']
                and n['gba_key'] == carry['gba_key'] and n['long_note'])
    cut, duration = -carry['note_start_relative_ticks'], note['duration']
    if not 0 < cut < duration:
        raise ValueError('Unsupported synthetic carry geometry')
    period = duration + 116
    tempo = conversion['tempo_mapping'][0]['gba_parameter']
    data = bytearray(original)
    table = manifest['target_table_file_offset']
    header = struct.unpack_from('<I', data, table + 474 * 8)[0] - ROM_BASE
    bank = struct.unpack_from('<I', data, header + 4)[0]
    code_offset = len(data) + (-len(data) % 4)
    tie = bytes([0xCF, note['gba_key'], note['gba_velocity']])
    prefix = bytes([0xBB, tempo, 0xBD, note['gba_voice'], 0xBE, 100, 0xBF, 64]) + tie + wait_bytes(cut)
    body = (wait_bytes(duration - cut) + bytes([0xCE, note['gba_key']])
            + wait_bytes(period - duration) + tie + wait_bytes(cut))
    code = prefix + body + b'\xB2' + struct.pack('<I', ROM_BASE + code_offset + len(prefix))
    decoded = trace_track(bytes(code_offset) + code, code_offset)
    model = validate_loop_notes(decoded, [[0, note['gba_voice'], note['gba_key'], note['gba_velocity'], duration],
                                        [period, note['gba_voice'], note['gba_key'], note['gba_velocity'], duration]], cut, period)
    data.extend(bytes(code_offset - len(data)) + code)
    data.extend(bytes(-len(data) % 4))
    new_header = len(data)
    data.extend(struct.pack('<BBBBII', 1, 0, 20, 128, bank, ROM_BASE + code_offset))
    struct.pack_into('<I', data, table + 474 * 8, ROM_BASE + new_header)
    directory.mkdir(parents=True, exist_ok=False)
    rom = directory / 'synthetic.gba'
    rom.write_bytes(data)
    report = {'complete': False, 'synthetic_sequence': True, 'register_or_ram_injection': False,
              'scope': 'Short single-voice TIE/EOT cycle with original converted bank; not original full-song execution',
              'original_rom_fingerprint': fingerprint(original), 'probe_rom_fingerprint': fingerprint(data),
              'period_ticks': period, 'loop_start_ticks': cut, 'gate_ticks': duration,
              'note_model': model, 'snapshots': [], 'joins': []}
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory.resolve() / 'config'))
    env.pop('LD_PRELOAD', None)
    with (directory / 'debugger.txt').open('w') as transcript:
        d = Debugger([mgba, '-d', str(rom.resolve())], env, transcript)
        try:
            d.prompt()
            player = start_preview_song(d, data, manifest, 474)
            owner = d.read(4, player + 44)
            sound = d.read(4, 0x03007FF0)
            callback = d.read(4, sound + 32) & ~1
            root = d.read(4, sound + 36)
            d.command(f'break/t {callback:#x}')
            previous = None
            stopped = set()
            for frame in range(1600):
                for _ in range(64):
                    if d.hit(callback)[0] == root:
                        break
                else:
                    raise AssertionError('Root callback not reached')
                clock = d.read(4, player + 12)
                if d.read(4, player) != ROM_BASE + new_header:
                    raise AssertionError('Game replaced synthetic song')
                raw = memory(d, sound + 80, 12 * 64)
                channels = []
                for slot in range(12):
                    ch = raw[slot * 64:(slot + 1) * 64]
                    if ch[0] & 0xC7 and struct.unpack_from('<I', ch, 44)[0] == owner:
                        channels.append({'slot': slot, 'flags': ch[0], 'key': ch[17],
                                         'wave': struct.unpack_from('<I', ch, 36)[0]})
                # clock is the next sequence tick, before this frame's update.
                held = clock > 0 and (clock - 1) % period < duration
                active = [ch for ch in channels if not ch['flags'] & 0x40]
                if held and (len(active) != 1 or active[0]['key'] != note['gba_key']):
                    raise AssertionError(f'Carried note lost or duplicated at {clock}: {channels}')
                if not held and active:
                    raise AssertionError(f'EOT did not stop note at {clock}')
                if clock > duration + 1 and not held:
                    stopped.add((clock - 1) // period)
                if previous and clock > previous['clock']:
                    for turn in range(1, 4):
                        join = cut + turn * period
                        if previous['clock'] <= join < clock:
                            before = [ch for ch in previous['channels'] if not ch['flags'] & 0x40]
                            if before != active or active[0]['flags'] & 0x80:
                                raise AssertionError('GOTO replaced/retriggered carried channel')
                            report['joins'].append({'tick': join, 'channel': active[0]})
                previous = {'clock': clock, 'channels': channels}
                report['snapshots'].append(previous)
                if clock > cut + 3 * period + duration:
                    break
            if len(report['joins']) != 3 or len(stopped) < 3:
                raise AssertionError('Insufficient native jump/EOT coverage')
            if (experiment / 'unified.gba').read_bytes() != original:
                raise AssertionError('Original experiment ROM changed')
            report.update(complete=True, final_clock=clock, observed_eot_cycles=len(stopped))
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            d.close()
            (directory / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = probe(args.experiment, args.out)
    print(f"Checked {len(result['joins'])} native carried-channel jumps and {result['observed_eot_cycles']} EOT cycles")
