#!/usr/bin/env python3
"""Experimental EXEGP song transplantation into verified EXE4.5 PvP.

Preserves existing PvP data outside a declared mixer setting and one empty
entry, then appends relocated resources. Exports an independent test ROM and BPS patch for the original EXE4.5 ROM.
No input is modified. This does not merge the full Soundmod patch.
"""
import argparse
import json
from pathlib import Path
import struct
import zlib

from analyze_song import analyze, Reader
from scan_audio import ROM_BASE, MAX_ROM_SIZE, apply_bps, fingerprint
from validate_playback import PROFILE_SHA256


def encode_number(value):
    output = bytearray()
    while True:
        byte = value & 127
        value >>= 7
        if value == 0:
            output.append(byte | 128)
            return bytes(output)
        output.append(byte)
        value -= 1


def make_bps(source, target):
    patch = bytearray(b'BPS1' + encode_number(len(source)) + encode_number(len(target)) + encode_number(0))
    start = 0
    while start < len(target):
        unchanged = start < len(source) and target[start] == source[start]
        end = start + 1
        while end < len(target) and (end < len(source) and target[end] == source[end]) == unchanged:
            end += 1
        patch.extend(encode_number(((end - start - 1) << 2) | (0 if unchanged else 1)))
        if not unchanged:
            patch.extend(target[start:end])
        start = end
    patch.extend(struct.pack('<II', zlib.crc32(source), zlib.crc32(target)))
    patch.extend(struct.pack('<I', zlib.crc32(patch)))
    return bytes(patch)


def transplant(donor, target, donor_id=1, target_id=0, pcm_channels=10):
    if fingerprint(donor)['sha256'] != PROFILE_SHA256['exegp'] or fingerprint(target)['sha256'] != PROFILE_SHA256['exe45-pvp']:
        raise ValueError('Requires verified EXEGP and EXE4.5 PvP baselines')
    if not 0 <= donor_id < 170 or not 0 <= target_id < 499:
        raise ValueError('ID outside verified table')
    table = 0x135214
    entry = table + target_id * 8
    pointer = struct.unpack_from('<I', target, entry)[0]
    if Reader(target).read(pointer - ROM_BASE, 4) != bytes(4):
        raise ValueError('Target slot is not empty; existing PvP audio must be preserved')
    if not 4 <= pcm_channels <= 12:
        raise ValueError('PCM channel budget must be 4..12')
    mode_offset = 0x504
    old_mode = struct.unpack_from('<I', target, mode_offset)[0]
    if old_mode != 0x0093040D:
        raise ValueError('Unexpected PvP SoundMode configuration')
    new_mode = (old_mode & ~0xF00) | (pcm_channels << 8)
    report = analyze(donor, 0x160658, donor_id)
    # Player 31 is the existing EXE4.5 music player. Descriptor byte +8 is
    # configured track capacity; do not copy the donor player index (0).
    capacity = target[0x135094 + 31 * 12 + 8]
    if report['header']['track_count'] > capacity:
        raise ValueError('Donor track count exceeds target music player capacity')
    output = bytearray(target)
    struct.pack_into('<I', output, mode_offset, new_mode)
    blocks, tables = [], {}

    def allocate(raw):
        output.extend(bytes((-len(output)) % 4))
        offset = len(output)
        output.extend(raw)
        if len(output) > MAX_ROM_SIZE:
            raise ValueError('Transplant exceeds 32 MiB ROM limit')
        return offset

    bank = report['header']['tone_bank']['file_offset']
    placements = {}
    for voice in {voice for voice, key in report['voice_key_pairs']}:
        placements.setdefault(bank + voice * 12, set()).add((bank, voice))
    for tone in report['tones']:
        if 'children_base' in tone:
            base = tone['children_base']['file_offset']
            for index in tone['child_indices_used']:
                placements.setdefault(base + index * 12, set()).add((base, index))
    # Build sparse banks with preserved indices. Unused rows are zero-filled,
    # rather than carrying unrelated donor pointers into the target ROM.
    bases = sorted({base for options in placements.values() for base, index in options})
    for base in bases:
        row_count = max(128, max(index for options in placements.values() for table_base, index in options if table_base == base) + 1)
        tables[base] = allocate(bytes(row_count * 12))
    tone_sites = {}
    for resource in report['resources']:
        old, size = resource['file_offset'], resource['size_bytes']
        raw = donor[old:old + size]
        if resource['kind'] == 'tone_record':
            if old not in placements:
                raise ValueError('Tone has no validated bank/index placement')
            sites = []
            for base, index in sorted(placements[old]):
                new = tables[base] + index * 12
                output[new:new + size] = raw
                sites.append(new)
            tone_sites[old] = sites
        else:
            new = allocate(raw)
            blocks.append({'kind': resource['kind'], 'source_offset': old, 'size_bytes': size, 'target_offset': new})

    def sites(old):
        result = [b['target_offset'] + old - b['source_offset'] for b in blocks
                  if b['source_offset'] <= old < b['source_offset'] + b['size_bytes']]
        for base, targets in tone_sites.items():
            if base <= old < base + 12:
                result += [target + old - base for target in targets]
        if not result:
            raise ValueError(f'Unmapped pointer site {old:#x}')
        return result

    def mapped(old, kind):
        if kind in ('tone_bank', 'tone_children'):
            if old not in tables:
                raise ValueError(f'Unmapped bank base {old:#x}')
            return tables[old]
        candidates = sites(old)
        if len(set(candidates)) != 1:
            raise ValueError('Ambiguous relocation target')
        return candidates[0]

    relocated = []
    for field in report['pointer_fields']:
        old_site, old_target = field['site']['file_offset'], field['target']['file_offset']
        new_target = mapped(old_target, field['kind'])
        for new_site in sites(old_site):
            struct.pack_into('<I', output, new_site, ROM_BASE + new_target)
            relocated.append({'kind': field['kind'], 'source_site': old_site, 'target_site': new_site,
                              'source_target': old_target, 'target_target': new_target})
    new_header = mapped(report['header']['file_offset'], 'header')
    struct.pack_into('<IHH', output, entry, ROM_BASE + new_header, 31, 31)
    # Only the empty entry and explicitly declared SoundMode configuration change.
    expected_prefix = bytearray(target)
    struct.pack_into('<I', expected_prefix, mode_offset, new_mode)
    expected_prefix[entry:entry + 8] = output[entry:entry + 8]
    if output[:len(target)] != expected_prefix:
        raise AssertionError('Existing PvP bytes changed outside declared entry/configuration')
    result = bytes(output)
    relocated_report = analyze(result, table, target_id)
    for old, new in zip(report['tracks'], relocated_report['tracks']):
        if old['notes'] != new['notes'] or old['ticks_before_repeat'] != new['ticks_before_repeat'] or old['termination'] != new['termination']:
            raise AssertionError('Relocated sequence semantics differ')
    original_samples = sorted((sample['size_bytes'], donor[sample['file_offset']:sample['file_offset'] + sample['size_bytes']]) for sample in report['samples'])
    new_samples = sorted((sample['size_bytes'], result[sample['file_offset']:sample['file_offset'] + sample['size_bytes']]) for sample in relocated_report['samples'])
    if original_samples != new_samples:
        raise AssertionError('Relocated sample contents differ')
    manifest = {'schema_version': 1, 'target_profile': 'exe45-pvp',
                'target_base_fingerprint': fingerprint(target), 'donor_fingerprint': fingerprint(donor),
                'output_fingerprint': fingerprint(result), 'donor_id': donor_id, 'target_id': target_id,
                'target_table_file_offset': table, 'target_header_address': f'0x{ROM_BASE + new_header:08X}',
                'appended_bytes': len(result) - len(target), 'changed_existing_entry': [entry, entry + 8],
                'preservation': 'All existing PvP bytes outside selected empty entry and declared SoundMode configuration verified unchanged',
                'sound_mode_change': {'file_offset': mode_offset, 'before': f'0x{old_mode:08X}',
                                      'after': f'0x{new_mode:08X}', 'pcm_channels': pcm_channels,
                                      'scope': 'Game startup SoundMode override; other bits and library defaults preserved'},
                'bank_allocations': [{'source_base': old, 'target_base': new, 'size_bytes': max(128, max(index for options in placements.values() for base, index in options if base == old) + 1) * 12} for old, new in sorted(tables.items())],
                'resource_blocks': blocks, 'relocated_pointer_fields': relocated,
                'limitations': ['Experimental single-song transplant; full Soundmod merge not included',
                                'Unused bank rows are zero-filled; selected dependency closure only',
                                'Playback requires separate runtime validation',
                                'Higher global PCM budget changes mixer load; PvP multiplayer performance not tested']}
    return result, manifest, report, relocated_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True, help='Original EXE4.5 ROM')
    parser.add_argument('--pvp-patch', type=Path, required=True)
    parser.add_argument('--donor', type=Path, required=True)
    parser.add_argument('--donor-id', type=int, default=1)
    parser.add_argument('--target-id', type=int, default=0)
    parser.add_argument('--pcm-channels', type=int, default=10, help='Global mixer budget (4..12), default matches donor budget 10')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    try:
        original = args.base.read_bytes()
        pvp_patch = args.pvp_patch.read_bytes()
        target, pvp_info = apply_bps(original, pvp_patch)
        result, manifest, source_report, target_report = transplant(args.donor.read_bytes(), target, args.donor_id, args.target_id, args.pcm_channels)
        patch = make_bps(original, result)
        reconstructed, info = apply_bps(original, patch)
        if reconstructed != result:
            raise AssertionError('Exported BPS does not reproduce transplant')
        manifest.update(original_fingerprint=fingerprint(original), pvp_patch_fingerprint=fingerprint(pvp_patch),
                        pvp_bps=pvp_info, exported_bps=info,
                        input_paths={'base': str(args.base), 'pvp_patch': str(args.pvp_patch), 'donor': str(args.donor)})
        args.out.mkdir(parents=True)
        (args.out / 'transplanted.gba').write_bytes(result)
        (args.out / 'transplanted.bps').write_bytes(patch)
        for name, value in [('transplant.json', manifest), ('source-dependencies.json', source_report), ('target-dependencies.json', target_report)]:
            (args.out / name).write_text(json.dumps(value, indent=2) + '\n')
        print(f'EXEGP {args.donor_id} -> PvP {args.target_id}; appended {manifest["appended_bytes"]} bytes; '
              f'{len(manifest["relocated_pointer_fields"])} relocated pointer fields; BPS roundtrip verified')
    except (OSError, ValueError) as exc:
        parser.exit(1, f'transplant_song: {exc}\n')


if __name__ == '__main__':
    main()
