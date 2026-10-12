#!/usr/bin/env python3
"""Stable, version-pinned audio IDs for PvP, Soundmod additions, and EXEGP.

Native PvP IDs stay 0..498. Soundmod additions reserve 499..550; all nonempty
EXEGP entries reserve 551..636, including entries not eligible for music export.
Availability never changes allocation, so selection does not renumber a catalog.
"""
import argparse
import csv
import json
from pathlib import Path
import struct

from analyze_song import analyze
from scan_audio import apply_bps, fingerprint, song_header
from validate_playback import PROFILE_SHA256
from target_profiles import validate_target


def catalog(base, pvp, soundmod, gp):
    target = validate_target(base, pvp)
    for label, data in [('exe45-soundmod', soundmod), ('exegp', gp)]:
        if fingerprint(data)['sha256'] != PROFILE_SHA256[label]:
            raise ValueError(f'Unsupported {label} fingerprint')
    rows, reports = [], {}
    sources = {'pvp': (pvp, 0x135214, 499), 'soundmod': (soundmod, 0x135214, 499), 'exegp': (gp, 0x160658, 170)}
    capacity = pvp[0x135094 + 31 * 12 + 8]
    next_id = 499
    for source, (data, table, count) in sources.items():
        for index in range(count):
            pointer, field_a, field_b = struct.unpack_from('<IHH', data, table + index * 8)
            header = song_header(data, pointer)
            if header is None:
                raise ValueError(f'Invalid verified table entry {source}:{index}')
            if source == 'soundmod' and data[table + index * 8:table + index * 8 + 8] == base[table + index * 8:table + index * 8 + 8]:
                continue
            if source == 'exegp' and header['empty']:
                continue
            target_id = index if source == 'pvp' else next_id
            if source != 'pvp':
                next_id += 1
            music_player = 0 if source == 'exegp' else 31
            candidate = not header['empty'] and field_a == music_player
            key = f'{source}:{index}'
            row = {'key': key, 'source': source, 'source_index': index, 'target_index': target_id,
                   'header_address': header['rom_address'], 'track_count': header['track_count'],
                   'source_player': field_a, 'second_field_raw': field_b, 'empty': header['empty'],
                   'classification': 'music_player_candidate' if candidate else ('empty' if header['empty'] else 'other_audio'),
                   'name': None, 'name_status': 'unassigned', 'playlist_eligible': False}
            if header['empty']:
                row['availability'] = 'empty'
            elif not candidate:
                row['availability'] = 'preserved_native_audio' if source == 'pvp' else 'reserved_nonmusic_entry'
            elif header['track_count'] > capacity:
                row['availability'] = 'exceeds_target_track_capacity'
            elif source == 'pvp':
                row.update(availability='native_music', playlist_eligible=True)
            else:
                try:
                    report = analyze(data, table, index)
                except ValueError as exc:
                    row.update(availability='unsupported_dependencies', reason=str(exc))
                else:
                    row.update(availability='importable_music', playlist_eligible=True,
                               dependency_summary={'tone_records': len(report['tones']), 'pcm_samples': len(report['samples']),
                                                   'covered_bytes': report['covered_bytes'],
                                                   'terminations': sorted({track['termination'] for track in report['tracks']})})
                    reports[key] = report
            rows.append(row)
    return {'schema_version': 1, 'target_profile':target['key'], 'target_label':target['label'], 'sources': {name: fingerprint(data) for name, (data, _, _) in sources.items()},
            'target_player': 31, 'target_track_capacity': capacity, 'table_entry_count': next_id,
            'allocation_policy': 'Native IDs preserved; sorted Soundmod additions then sorted nonempty EXEGP IDs; unavailable slots remain reserved',
            'classification_basis': 'Player index, not a verified music title or exhaustive BGM/SFX classification',
            'entries': rows}, reports


def write_catalog(directory, value):
    (directory / 'catalog.json').write_text(json.dumps(value, indent=2) + '\n')
    fields = ['key', 'target_index', 'source_index', 'source_player', 'track_count', 'classification', 'availability', 'playlist_eligible', 'name']
    with (directory / 'catalog.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(value['entries'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--pvp-patch', type=Path, required=True)
    parser.add_argument('--soundmod-patch', type=Path, required=True)
    parser.add_argument('--donor', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    try:
        base = args.base.read_bytes()
        pvp, _ = apply_bps(base, args.pvp_patch.read_bytes())
        sound, _ = apply_bps(base, args.soundmod_patch.read_bytes())
        value, _ = catalog(base, pvp, sound, args.donor.read_bytes())
        args.out.mkdir(parents=True)
        write_catalog(args.out, value)
        print(f"{len(value['entries'])} catalog rows; {value['table_entry_count']} stable table slots; "
              f"{sum(row['playlist_eligible'] for row in value['entries'])} music-player candidates available")
    except (OSError, ValueError) as exc:
        parser.exit(1, f'unified_catalog: {exc}\n')


if __name__ == '__main__':
    main()
