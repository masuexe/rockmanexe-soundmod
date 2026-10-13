"""Fingerprint-pinned catalogs from original ROMs, independent of Soundmod BPS."""
import json
from pathlib import Path
import struct

from analyze_song import analyze
from scan_audio import fingerprint, song_header
from target_profiles import validate_target

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DATA = json.loads((ROOT / 'config/rom-profiles.json').read_text())
PROFILES = {p['key']: p for p in PROFILE_DATA['profiles']}


def identify(data):
    digest = fingerprint(data)['sha256']
    for key, profile in PROFILES.items():
        if digest == profile['fingerprint']['sha256']:
            return key
    raise ValueError('Unsupported original music ROM revision; choose an original ROM listed in Original music ROMs')


def catalog_originals(base, target_rom, donors):
    target = validate_target(base, target_rom)
    layout = target['layout']
    native = layout['native_source']
    rows, reports = [], {}
    source_info = {native: fingerprint(target_rom)}
    labels = {native: target['native_label']}
    capacity = target_rom[layout['player_table_offset'] + layout['music_player'] * 12 + 8]
    sources = [(native, target_rom, {**layout, 'target_slot_start':0})]
    for key in sorted(donors):
        profile = PROFILES.get(key)
        if not profile or fingerprint(donors[key]) != profile['fingerprint']:
            raise ValueError(f'Unsupported {key} fingerprint')
        labels[key] = profile['label']
        source_info[key] = profile['fingerprint']
        sources.append((key, donors[key], profile))
    for source, data, profile in sources:
        for index in range(profile['entry_count']):
            pointer, player, second = struct.unpack_from('<IHH', data, profile['table_offset'] + index * 8)
            header = song_header(data, pointer)
            if header is None:
                raise ValueError(f'Invalid original ROM audio entry {source}:{index}')
            candidate = not header['empty'] and player == profile['music_player']
            key = f'{source}:{index}'
            row = {'key':key,'source':source,'source_label':labels[source], 'source_index':index,
                   'target_index':profile['target_slot_start']+index,'header_address':header['rom_address'],
                   'track_count':header['track_count'],'source_player':player,'second_field_raw':second,
                   'empty':header['empty'],'name':None,'name_status':'unassigned','playlist_eligible':False,
                   'classification':'music_player_candidate' if candidate else ('empty' if header['empty'] else 'other_audio')}
            if header['empty']:
                row['availability']='empty'
            elif not candidate:
                row['availability']='preserved_native_audio' if source==native else 'reserved_nonmusic_entry'
            elif header['track_count']>capacity:
                row['availability']='exceeds_target_track_capacity'
            elif source==native:
                row.update(availability='native_music',playlist_eligible=True)
            else:
                try:
                    report=analyze(data,profile['table_offset'],index)
                except ValueError as exc:
                    row.update(availability='unsupported_dependencies',reason=str(exc))
                else:
                    reports[key]=report
                    row.update(availability='importable_music',playlist_eligible=True,
                               dependency_summary={'tone_records':len(report['tones']),'pcm_samples':len(report['samples']),
                                                   'covered_bytes':report['covered_bytes']})
            rows.append(row)
    minimum = PROFILE_DATA.get('minimum_table_entry_count', PROFILE_DATA['table_entry_count'])
    table_count = max(minimum, *(p['target_slot_start']+p['entry_count'] for _, _, p in sources))
    return {'schema_version':1,'target_profile':target['key'],'target_label':target['label'],'sources':source_info,'source_labels':labels,'native_source':native, 'target_player':layout['music_player'], 'event_labels':layout['event_labels'], 'preview_trigger':layout['preview_trigger'],
            'event_groups':layout.get('event_groups',{}),
            'target_track_capacity':capacity,'table_entry_count':table_count,
            'allocation_policy':'Native and existing donor IDs preserved; optional donor ranges extend the reserved table when selected',
            'classification_basis':'Profile music-player candidates, not verified song titles; donor runtime coverage is representative',
            'entries':rows}, reports
