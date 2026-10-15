#!/usr/bin/env python3
"""Build checked Star Force 3 room/battle music -> Japanese EXE6 research ROM/BPS.

This bounded experiment uses the existing GBA export core, not the manager's
production source catalog. Original ROMs are read only. Python 3.10+, stdlib.
"""
import argparse
import json
from pathlib import Path

from build_unified import build_catalog
from nds_music import SoundArchive, convert_song, nds_sdat
from original_catalog import catalog_originals
from scan_audio import apply_bps, fingerprint
from target_profiles import validate_target
from transplant_song import make_bps
from nds_track_merge import BATTLE_GROUPS, convert_merged_song

SOURCES = {
    '64ff3011d41dbcb56990f355254fe765c5088daf2915f695e31420114356743a': 'ssr3b',
    'eaa53a29170a6740ac2f9476321149ccf95f0bc54835fdb51ca66cf5165aca1b': 'ssr3r',
}
SDAT_SHA256 = 'bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220'


def build_experiment(source, base, events=('1',), pcm_channels=10, song_gain_db=3.5, song='room'):
    source_fingerprint = fingerprint(source)
    key = SOURCES.get(source_fingerprint['sha256'])
    if key is None:
        raise ValueError('Requires one of the verified Japanese Star Force 3 original ROMs')
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS experiment currently targets original Japanese EXE6 only')
    raw_sdat = nds_sdat(source, 187)
    if fingerprint(raw_sdat)['sha256'] != SDAT_SHA256:
        raise ValueError('Star Force 3 SDAT fingerprint mismatch')
    archive = SoundArchive(raw_sdat)
    capacity = base[target['layout']['player_table_offset'] + target['layout']['music_player'] * 12 + 8]
    if song == 'room':
        index, name = 2, 'BGM_ROOM'
        blob, dependency, conversion = convert_song(archive, index, capacity, song_gain_db=song_gain_db)
    elif song == 'battle':
        index, name = 35, 'BGM_BATTLE'
        blob, dependency, conversion = convert_merged_song(archive, index, BATTLE_GROUPS, capacity, song_gain_db)
    else:
        raise ValueError('Unknown NDS experiment song')
    catalog, reports = catalog_originals(base, base, {})
    source_key = 'nds-' + key
    song_key = source_key + ':' + str(index)
    slot = target['layout']['entry_count']
    catalog['table_entry_count'] = slot + 1
    catalog['sources'][source_key] = fingerprint(blob)
    catalog['source_labels'][source_key] = f'Star Force 3: converted {name} (research)'
    catalog['entries'].append({'key': song_key, 'source': source_key, 'source_index': index,
                               'source_label': catalog['source_labels'][source_key],
                               'target_index': slot, 'track_count': conversion['track_count'],
                               'empty': False, 'playlist_eligible': True,
                               'classification': 'converted_nds_research_music',
                               'availability': 'importable_music', 'name': name,
                               'name_status': 'original_sdat_symbol', 'source_player': 0,
                               'second_field_raw': 0})
    reports[song_key] = dependency
    if not events or len(set(events)) != len(events):
        raise ValueError('Choose distinct nonempty target events')
    playlist = {'schema_version': 1, 'target_profile': target['key'],
                'pools': {str(event): {'tracks': [song_key], 'selector_shift': 0} for event in events}}
    output, catalog, manifest = build_catalog(base, base, catalog, reports,
                                               {source_key: blob}, playlist, pcm_channels,
                                               selected_only=True)
    patch = make_bps(base, output)
    reconstructed, patch_info = apply_bps(base, patch)
    if reconstructed != output:
        raise AssertionError('NDS experiment BPS reconstruction differs')
    manifest.update(bps=patch_info, nds_conversion={
        'source_profile': key, 'source_rom_fingerprint': source_fingerprint,
        'sdat_fingerprint': fingerprint(raw_sdat), 'nds_file_id': 187,
        'sequence_index': index, 'sequence_name': name,
        'generated_mplay_fingerprint': fingerprint(blob),
        'note_timing_check': conversion['note_timing_check'],
        'song_gain_db': conversion['song_gain_db'],
        'song_gain_scope': conversion['song_gain_scope'],
        'conversion_report': 'conversion.json', 'production_manager_support': False})
    return output, patch, manifest, conversion, dependency, blob, catalog, raw_sdat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--song', choices=['room', 'battle'], default='room')
    parser.add_argument('--event', action='append', help='Native music ID or scene:communication; repeatable; default 1')
    parser.add_argument('--pcm-channels', type=int, default=10)
    parser.add_argument('--song-gain-db', type=float, default=3.5,
                        help='Imported song compensation in dB; default +3.5; source-specific calibration remains experimental')
    parser.add_argument('--out', type=Path, required=True, help='New output directory')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    try:
        source, base = args.source.read_bytes(), args.base.read_bytes()
        output, patch, manifest, conversion, dependency, blob, catalog, sdat = build_experiment(
            source, base, args.event or ['1'], args.pcm_channels, args.song_gain_db, args.song)
        manifest['nds_conversion']['source_path'] = str(args.source.resolve())
        manifest['original_path'] = str(args.base.resolve())
        args.out.mkdir(parents=True)
        for name, raw in [('unified.gba', output), ('unified.bps', patch),
                          ('converted-mplay.bin', blob), ('source.sdat', sdat)]:
            (args.out / name).write_bytes(raw)
        for name, value in [('build.json', manifest), ('conversion.json', conversion),
                            ('dependencies.json', dependency), ('catalog.json', catalog)]:
            (args.out / name).write_text(json.dumps(value, indent=2) + '\n')
        if args.source.read_bytes() != source or args.base.read_bytes() != base:
            raise AssertionError('Input ROM changed during build')
        print(f"{manifest['target_profile']}: {manifest['nds_conversion']['sequence_name']} -> slot {manifest['native_entry_count']}; "
              f"{conversion['track_count']} tracks, {len(dependency['samples'])} PCM samples, "
              f"{manifest['appended_bytes']} appended bytes, song gain {conversion['song_gain_db']:+g} dB; BPS reconstruction verified")
    except (OSError, ValueError) as error:
        parser.exit(1, f'build_nds_experiment: {error}\n')


if __name__ == '__main__':
    main()
