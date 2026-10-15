#!/usr/bin/env python3
"""Check a bounded natural-title window of actual MPlay pitch-LFO execution.

This does not establish complete loops, gameplay, or equality to DS per-voice
synthesis. No RAM/register changes are made to the emulator.
"""
import argparse
import csv
import json
import math
import os
from pathlib import Path
import struct

from analyze_song import analyze
from nds_lfo import gba_lfo_value
from render_preview import start_preview_song
from scan_audio import ROM_BASE, fingerprint
from target_profiles import valid_manifest_target
from validate_playback import Debugger
from validate_song import expected_state, memory


def compare_reference_window(directory, reference):
    """Compare shared target pitch with allocated DS voices by sequence clock.

    Select the latest observed DS timer frame at each clock. This is a
    diagnostic alignment, not waveform alignment or matching voice allocation.
    """
    actual = json.loads((directory / 'validation.json').read_text())
    if not actual['complete']:
        raise ValueError('Requires a passed native LFO window')
    latest = {}
    with (reference / 'modulation.csv').open() as stream:
        for raw in csv.DictReader(stream):
            row = {k: int(v) for k, v in raw.items()}
            tick = row['tick']
            if tick not in latest or row['timer_frame'] > latest[tick][0]:
                latest[tick] = row['timer_frame'], [row]
            elif row['timer_frame'] == latest[tick][0]:
                latest[tick][1].append(row)
    errors = {i: [] for i in (1, 2, 3)}
    for snapshot in actual['snapshots']:
        for row in latest.get(snapshot['clock'], (None, []))[1]:
            i = row['track']
            if i in errors and row['type'] == 0:
                target = snapshot['tracks'][i]['value'] * 4
                errors[i].append((target - row['value']) * 100 / 64)
    if any(not values for values in errors.values()):
        raise ValueError('Reference does not cover all three modulated tracks')
    return {'scope': 'sequence-clock alignment to latest observed DS timer frame, allocated DS voices vs shared target track',
            'sample_aligned': False, 'equal_voice_allocation': False,
            'tracks': {str(i): {'comparisons': len(values),
                               'rms_pitch_difference_cents': math.sqrt(sum(v * v for v in values) / len(values)),
                               'max_pitch_difference_cents': max(map(abs, values))}
                       for i, values in errors.items()}}


class LfoModel:
    def __init__(self, events):
        self.events = events
        self.position = self.clock = 0
        self.speed, self.depth, self.kind = 22, 0, 0
        self.delay = self.count = self.phase = self.value = 0

    def advance(self, clock):
        if clock < self.clock:
            raise ValueError('LFO model does not cover player restarts')
        while self.clock < clock:
            while self.position < len(self.events) and self.events[self.position]['ticks'] == self.clock:
                event = self.events[self.position]
                self.position += 1
                name, value = event['name'], event.get('value')
                if name == 'LFOS':
                    self.speed = value
                    if not value:
                        self.phase = self.value = 0
                elif name == 'LFODL':
                    self.delay = self.count = value
                elif name == 'MOD':
                    self.depth = value
                    if not value:
                        self.phase = self.value = 0
                elif name == 'MODT':
                    self.kind = value
                elif name in ('NOTE', 'TIE'):
                    self.count = self.delay
                    if self.delay:
                        self.phase = self.value = 0
            if self.speed and self.depth:
                if self.count:
                    self.count -= 1
                else:
                    self.phase = (self.phase + self.speed) % 256
                    self.value = gba_lfo_value(self.phase, self.depth)
            self.clock += 1
        return {'value': self.value, 'depth': self.depth, 'kind': self.kind,
                'speed': self.speed, 'phase': self.phase, 'delay': self.delay, 'count': self.count}


def probe(experiment, directory, frames=1500, mgba='/usr/games/mgba'):
    manifest = json.loads((experiment / 'build.json').read_text())
    data = (experiment / 'unified.gba').read_bytes()
    if not valid_manifest_target(manifest) or fingerprint(data) != manifest['output_fingerprint']:
        raise ValueError('ROM does not match verified target manifest')
    if not manifest['nds_conversion'].get('native_pitch_lfo_approximation') or frames < 1:
        raise ValueError('Requires a native pitch-LFO experiment and positive frame count')
    dependency = analyze(data, manifest['target_table_file_offset'], 474)
    directory.mkdir(parents=True, exist_ok=False)
    rom = directory / 'test.gba'
    rom.write_bytes(data)
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory.resolve() / 'config'))
    env.pop('LD_PRELOAD', None)
    models = [LfoModel(t['events']) for t in dependency['tracks']]
    observed = {i: set() for i in range(len(models))}
    report = {'complete': False, 'scope': 'requested natural-title window only',
              'rom_fingerprint': fingerprint(data),
              'register_or_ram_injection': False, 'full_loop_validation': False,
              'ds_synthesis_equivalence': False, 'frames_requested': frames, 'snapshots': []}
    bank = dependency['header']['tone_bank']['file_offset']
    header = struct.unpack_from('<I', data, manifest['target_table_file_offset'] + 474 * 8)[0]
    with (directory / 'debugger.txt').open('w') as transcript:
        d = Debugger([mgba, '-d', str(rom.resolve())], env, transcript)
        try:
            d.prompt()
            player = start_preview_song(d, data, manifest, 474)
            base = d.read(4, player + 44)
            for frame in range(1, frames + 1):
                d.command('frame')
                clock = d.read(4, player + 12)
                if d.read(4, player) != header:
                    raise AssertionError('Game replaced imported music')
                raw = memory(d, base, len(models) * 80)
                rows = []
                for i, (track, model) in enumerate(zip(dependency['tracks'], models)):
                    if clock >= track['ticks_before_repeat']:
                        raise ValueError('Requested window exceeds the nonrepeated decoder prefix')
                    b = raw[i * 80:(i + 1) * 80]
                    actual_track = {'cursor': struct.unpack_from('<I', b, 64)[0], 'wait': b[1],
                                    'pattern_depth': b[2], 'key': b[5], 'velocity': b[6],
                                    'running_status': b[7], 'ended': not bool(b[0] & 0x80),
                                    'tone_hex': b[36:48].hex()}
                    expected_track = expected_state(track, clock, data, bank)
                    if expected_track['tone_hex'] is None:
                        expected_track['tone_hex'] = actual_track['tone_hex']
                    if actual_track != expected_track:
                        raise AssertionError({'frame': frame, 'track': i, 'actual': actual_track,
                                              'expected': expected_track})
                    actual = dict(zip(('value', 'depth', 'kind', 'speed', 'phase', 'delay', 'count'),
                                      (struct.unpack('b', b[22:23])[0], *b[23:29])))
                    expected = model.advance(clock)
                    if actual != expected:
                        raise AssertionError({'frame': frame, 'clock': clock, 'track': i,
                                              'actual_lfo': actual, 'expected_lfo': expected})
                    if actual['depth']:
                        observed[i].add(actual['value'])
                    rows.append(actual)
                report['snapshots'].append({'frame': frame, 'clock': clock, 'tracks': rows})
            active = {i for i, values in observed.items() if len(values) > 2}
            if active != {1, 2, 3}:
                raise AssertionError('Expected three actively modulated source tracks')
            report.update(complete=True, frames_checked=frames, final_clock=clock,
                          active_modulation_tracks=sorted(active),
                          observed_values={str(i): sorted(values) for i, values in observed.items()})
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            d.close()
            (directory / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--frames', type=int, default=1500)
    parser.add_argument('--mgba', default='/usr/games/mgba')
    parser.add_argument('--reference', type=Path, help='Optional per-voice DS modulation reference for diagnostic pitch comparison')
    args = parser.parse_args()
    result = probe(args.experiment, args.out, args.frames, args.mgba)
    if args.reference:
        comparison = compare_reference_window(args.out, args.reference)
        (args.out / 'modulation-comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
    print(f"Checked {result['frames_checked']} natural frames: note states and three native pitch LFOs match the MPlay model")


if __name__ == '__main__':
    main()
