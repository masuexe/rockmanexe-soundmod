#!/usr/bin/env python3
"""Trace a supported M4A-style sequence and catalog reachable tone/sample data.

Fails on unsupported commands/types; does not assume adjacent songs or samples
belong to the selected song. Produces analysis, never modifies a ROM.
"""
import argparse
import json
from pathlib import Path
import struct

from scan_audio import ROM_BASE, address, fingerprint, song_header

DURATIONS = list(range(25)) + [28, 30, 32, 36, 40, 42, 44, 48, 52, 54, 56, 60, 64, 66, 68, 72, 76, 78, 80, 84, 88, 90, 92, 96]
ONE_BYTE = {0xBA: 'PRIO', 0xBB: 'TEMPO', 0xBC: 'KEYSH', 0xBD: 'VOICE',
            0xBE: 'VOL', 0xBF: 'PAN', 0xC0: 'BEND', 0xC1: 'BENDR',
            0xC2: 'LFOS', 0xC3: 'LFODL', 0xC4: 'MOD', 0xC5: 'MODT', 0xC8: 'TUNE'}


class Reader:
    def __init__(self, data):
        self.data = data

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise ValueError(f'Read outside ROM: {offset:#x}+{size:#x}')
        return self.data[offset:offset + size]

    def pointer(self, offset):
        pointer = struct.unpack('<I', self.read(offset, 4))[0]
        target = pointer - ROM_BASE
        self.read(target, 1)
        return target


def merge_ranges(ranges):
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def trace_track(data, start, max_events=100000):
    reader = Reader(data)
    pc, status, voice, key, velocity, key_shift, repeat = start, None, None, 0, 0, 0, 0
    stack, seen, consumed, events, pointers = [], {}, [], [], {}
    ticks = 0
    notes = set()
    while len(events) < max_events:
        state = (pc, status, voice, key, velocity, key_shift, repeat, tuple(stack))
        if state in seen:
            first = seen[state]
            if ticks == events[first]['ticks']:
                raise ValueError('Zero-time sequence cycle cannot establish safe playback')
            return {**address(start), 'termination': 'repeated_state', 'loop_start_event': first,
                    'loop_start_ticks': events[first]['ticks'], 'ticks_before_repeat': ticks,
                    'loop_ticks': ticks - events[first]['ticks'],
                    'events': events, 'notes': sorted(notes),
                    'consumed_ranges': merge_ranges(consumed), 'pointer_fields': list(pointers.values())}
        seen[state] = len(events)
        begin = pc
        byte = reader.read(pc, 1)[0]
        if byte >= 0x80:
            pc += 1
            command = byte
            if byte >= 0xBD:
                status = byte
        else:
            if status is None:
                raise ValueError(f'Running data without status at {pc:#x}')
            command = status
        event = {**address(begin), 'ticks': ticks, 'command': f'0x{command:02X}', 'running': byte < 0x80}

        def take(size=1):
            nonlocal pc
            result = reader.read(pc, size)
            pc += size
            return result

        def branch():
            site = pc
            target = reader.pointer(site)
            take(4)
            pointers[site] = {"site": address(site), "target": address(target), "kind": "sequence_branch"}
            return target

        next_pc = None
        if 0x80 <= command <= 0xB0:
            wait = DURATIONS[command - 0x80]
            event.update(name='WAIT', duration_ticks=wait)
            ticks += wait
        elif command == 0xB1:
            event['name'] = 'FINE'
        elif command in (0xB2, 0xB3):
            target = branch()
            event.update(name='GOTO' if command == 0xB2 else 'PATT', target=address(target))
            if command == 0xB3:
                if len(stack) >= 3:
                    raise ValueError('Pattern nesting exceeds three frames')
                stack.append(pc)
            next_pc = target
        elif command == 0xB4:
            event['name'] = 'PEND'
            if stack:
                next_pc = stack.pop()
        elif command == 0xB5:
            count = take()[0]
            target = branch()
            repeat = (repeat + 1) & 255 if count else repeat
            event.update(name='REPT', count=count, target=address(target))
            if count == 0 or repeat < count:
                next_pc = target
            else:
                repeat = 0
        elif command in ONE_BYTE:
            value = take()[0]
            event.update(name=ONE_BYTE[command], value=value)
            if command == 0xBD:
                if value > 127:
                    raise ValueError('VOICE index exceeds supported 128-entry bank')
                voice = value
            elif command == 0xBC:
                key_shift = value - 256 if value >= 128 else value
                if key_shift:
                    raise ValueError('Nonzero KEYSH requires additional note-selection validation')
        elif command == 0xCD:
            extension, value = take(2)
            if extension not in (8, 9):
                raise ValueError(f'Unsupported tone-modifying XCMD {extension:#x}')
            event.update(name='XCMD', extension=extension, value=value)
        elif command == 0xCE:
            event['name'] = 'EOT'
            if reader.read(pc, 1)[0] < 128:
                key = take()[0]
                event['key'] = key
        elif 0xCF <= command <= 0xFF:
            if voice is None:
                raise ValueError('Note before VOICE initialization is unsupported')
            args = []
            for _ in range(3):
                if reader.read(pc, 1)[0] >= 128:
                    break
                args.append(take()[0])
            if args:
                key = args[0]
            if len(args) >= 2:
                velocity = args[1]
            event.update(name='TIE' if command == 0xCF else 'NOTE', voice=voice, key=key,
                         velocity=velocity, explicit_arguments=args)
            if command != 0xCF:
                event['duration_ticks'] = DURATIONS[command - 0xCF] + (args[2] if len(args) == 3 else 0)
            notes.add((voice, key))
        else:
            raise ValueError(f'Unsupported command {command:#x} at {begin:#x}')
        consumed.append((begin, pc))
        event['end_file_offset'] = pc
        event['next_file_offset'] = pc if next_pc is None else next_pc
        event['running_status_after'] = status
        event['pattern_depth_after'] = len(stack)
        events.append(event)
        if command == 0xB1:
            return {**address(start), 'termination': 'fine', 'ticks_before_repeat': ticks,
                    'events': events, 'notes': sorted(notes),
                    'consumed_ranges': merge_ranges(consumed), 'pointer_fields': list(pointers.values())}
        pc = pc if next_pc is None else next_pc
    raise ValueError(f'Sequence trace exceeded {max_events} events; no closure established')


def analyze(data, table, index):
    reader = Reader(data)
    table_entry = table + index * 8
    header_offset = reader.pointer(table_entry)
    header = song_header(data, ROM_BASE + header_offset)
    if header is None or header['empty']:
        raise ValueError('Selected entry is empty or unsupported')
    bank = header['tone_bank']['file_offset']
    tracks = [trace_track(data, track['file_offset']) for track in header['tracks']]
    resources, pointer_fields = {}, {}

    def resource(kind, offset, size):
        raw = reader.read(offset, size)
        item = {"kind": kind, **address(offset), "size_bytes": size, "sha256": fingerprint(raw)['sha256']}
        existing = resources.get((kind, offset))
        if existing and existing != item:
            raise ValueError('Conflicting resource boundaries')
        resources[kind, offset] = item

    def pointer(site, target, kind):
        pointer_fields[site] = {"site": address(site), "target": address(target), "kind": kind}

    resource('song_header', header_offset, 8 + 4 * header['track_count'])
    pointer(header_offset + 4, bank, 'tone_bank')
    for i, track in enumerate(tracks):
        pointer(header_offset + 8 + i * 4, track['file_offset'], 'track_start')
        for a, b in track['consumed_ranges']:
            resource('sequence', a, b - a)
        for field in track['pointer_fields']:
            pointer_fields[field['site']['file_offset']] = field

    samples = {}
    tones = {}

    def tone(offset, key, depth=0):
        if depth > 2:
            raise ValueError('Nested tone depth exceeds supported model')
        raw = reader.read(offset, 12)
        kind = raw[0]
        resource('tone_record', offset, 12)
        item = tones.setdefault(offset, {**address(offset), 'type_raw': kind, 'keys_used': [], 'raw_hex': raw.hex()})
        if key not in item['keys_used']:
            item['keys_used'].append(key)
        if kind & 0xC0:
            if depth:
                raise ValueError('Nested composite tones are rejected by the reference note handler')
            if kind not in (0x40, 0x80):
                raise ValueError(f'Unsupported composite tone type {kind:#x}')
            children = reader.pointer(offset + 4)
            pointer(offset + 4, children, 'tone_children')
            if kind == 0x40:
                keymap = reader.pointer(offset + 8)
                resource('keymap', keymap, 128)
                pointer(offset + 8, keymap, 'keymap')
                child_index = reader.read(keymap + key, 1)[0]
            else:
                child_index = key
            child = children + child_index * 12
            item['children_base'] = address(children)
            item.setdefault('child_indices_used', [])
            if child_index not in item['child_indices_used']:
                item['child_indices_used'].append(child_index)
            tone(child, key, depth + 1)
        elif kind in (0, 8):
            wave = reader.pointer(offset + 4)
            pointer(offset + 4, wave, 'pcm_wave')
            wave_type, flags, frequency, loop_start, size = struct.unpack('<HHIII', reader.read(wave, 16))
            if wave_type != 0 or size == 0 or (flags & 0x4000 and loop_start >= size):
                raise ValueError(f'Unsupported or malformed PCM wave at {wave:#x}')
            resource('pcm_wave', wave, 16 + size)
            samples[wave] = {**address(wave), 'type': wave_type, 'flags': flags,
                             'frequency_raw': frequency, 'loop_start': loop_start,
                             'sample_count': size, 'size_bytes': 16 + size}
        elif kind & 7 in (1, 2, 3, 4) and kind & ~15 == 0:
            # PSG channels 1/2/4 use register parameters, not ROM sample pointers.
            if kind & 7 == 3:
                wave = reader.pointer(offset + 4)
                resource('psg_wave', wave, 16)
                pointer(offset + 4, wave, 'psg_wave')
        else:
            raise ValueError(f'Unsupported tone type {kind:#x} at {offset:#x}')

    pairs = sorted({tuple(pair) for track in tracks for pair in track['notes']})
    for voice, key in pairs:
        tone(bank + voice * 12, key)
    # Bank/child bases can point before the first used record. Preserve base-index
    # relationships in the report; these are not independent movable 12-byte blobs.
    for item in tones.values():
        item['keys_used'].sort()
        if 'child_indices_used' in item:
            item['child_indices_used'].sort()
    resource_list = sorted(resources.values(), key=lambda r: (r['file_offset'], r['kind']))
    coverage = merge_ranges((r['file_offset'], r['file_offset'] + r['size_bytes']) for r in resource_list)
    return {'schema_version': 1, 'rom_fingerprint': fingerprint(data), 'table': address(table),
            'index': index, 'entry': address(table_entry), 'header': header,
            'status': 'supported_sequence_dependency_closure_not_relocation_validation',
            'tracks': tracks, 'voice_key_pairs': pairs,
            'tones': sorted(tones.values(), key=lambda t: t['file_offset']),
            'samples': sorted(samples.values(), key=lambda s: s['file_offset']),
            'resources': resource_list,
            'pointer_fields': sorted(pointer_fields.values(), key=lambda p: p['site']['file_offset']),
            'covered_bytes': sum(b - a for a, b in coverage), 'covered_ranges': coverage,
            'limitations': ['Supported command paths only; nonzero KEYSH and unsupported commands fail',
                            'Tone-bank and nested-table index relationships must survive relocation',
                            'Sequence state closure is not proof of sustained audible playback',
                            'No exporter or ROM changes performed']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--table', type=lambda value: int(value, 0), required=True, help='Table file offset')
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True, help='New analysis directory')
    args = parser.parse_args()
    if args.id < 0 or args.table < 0 or args.out.exists():
        parser.error('Table and ID must be nonnegative; output directory must be new')
    try:
        report = analyze(args.rom.read_bytes(), args.table, args.id)
        report['rom_path'] = str(args.rom)
        args.out.mkdir(parents=True)
        (args.out / 'dependencies.json').write_text(json.dumps(report, indent=2) + '\n')
        lines = ['# Song dependency analysis', '', f"ROM CRC32: `{report['rom_fingerprint']['crc32']}`; table: `0x{args.table:X}`; ID: {args.id}.", '',
                 f"{len(report['tracks'])} tracks; {len({voice for voice, key in report['voice_key_pairs']})} voices; "
                 f"{len(report['tones'])} tone records; {len(report['samples'])} PCM samples; {report['covered_bytes']} covered source bytes.", '',
                 '| Track | Start | Events | Termination | Loop ticks |', '|---|---|---:|---|---:|']
        for i, track in enumerate(report['tracks']):
            lines.append(f"| {i} | {track['rom_address']} | {len(track['events'])} | {track['termination']} | {track.get('loop_ticks', '—')} |")
        lines += ['', 'Supported sequence closure only; relocation and audible playback remain separate checks.']
        (args.out / 'summary.md').write_text('\n'.join(lines) + '\n')
        print('\n'.join(lines))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'analyze_song: {exc}\n')


if __name__ == '__main__':
    main()
