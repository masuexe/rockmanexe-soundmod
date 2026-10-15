#!/usr/bin/env python3
"""Build checked Star Force 1/2/3 music -> Japanese EXE6 research ROM/BPS.

This bounded experiment uses the existing GBA export core, not the manager's
production source catalog. Original ROMs are read only. Python 3.10+, stdlib.
"""
import argparse
import json
from pathlib import Path

from build_unified import build_catalog
from nds_music import SoundArchive, convert_song, nds_sdat, trace_sequence
from original_catalog import catalog_originals
from scan_audio import apply_bps, fingerprint
from target_profiles import validate_target
from transplant_song import make_bps
from nds_track_merge import BATTLE_GROUPS, convert_merged_song

SOURCES = {
    '9ea3c6e253d4111eec250d611296be5fab0e2ec2b8f6f25ece71dcc8e3492899': 'ssr2d',
    'dfa8780c1f98059d466509e90004793ad89b87a7f9fce48210fca8ddc0ff3745': 'ssr2s',
    'b531571a442d1aadd96ba7fa63637b97a8066b39ee5c54641eb61d4e5808807c': 'ssr1d',
    '5a31dd8472f120dc95808c8d4eeb549909ed75d2fca05af894e949b52de723d8': 'ssr1l',
    'd4ec40d1c0a169925f5ca58952a00e8b6865ac41e1e8300d609688a2c72beb6b': 'ssr1p',
    '64ff3011d41dbcb56990f355254fe765c5088daf2915f695e31420114356743a': 'ssr3b',
    'eaa53a29170a6740ac2f9476321149ccf95f0bc54835fdb51ca66cf5165aca1b': 'ssr3r',
}
SDAT_SHA256 = 'bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220'
SOURCE_ARCHIVES = {
    'ssr1': {'file_id': 667, 'sha256': '2b162eced95dadba3362316e0eb49b95b2990014a7fcb119fb9d21c1b01c1fd7',
             'label': 'Star Force 1'},
    'ssr2': {'file_id': 975, 'sha256': 'eb092e07ab410a3c81db491f0feb905f6259b891fb0b3cedfccaeca78ddc4ab4',
             'label': 'Star Force 2'},
    'ssr3': {'file_id': 187, 'sha256': SDAT_SHA256, 'label': 'Star Force 3'},
}
SONG_FAMILIES = {'room': 'ssr3', 'battle': 'ssr3', 'kando': 'ssr3',
                 'sf1-kincho': 'ssr1', 'sf1-battle-lfo': 'ssr1', 'sf2-win': 'ssr2'}


def build_experiment(source, base, events=('1',), pcm_channels=10, song_gain_db=3.5, song='room'):
    source_fingerprint = fingerprint(source)
    key = SOURCES.get(source_fingerprint['sha256'])
    if key is None:
        raise ValueError('Requires one of the verified Japanese Star Force 1/2/3 original ROMs')
    family = key[:4]
    source_archive = SOURCE_ARCHIVES[family]
    if song not in SONG_FAMILIES:
        raise ValueError('Unknown NDS experiment song')
    if SONG_FAMILIES[song] != family:
        raise ValueError('Song does not belong to the selected source game')
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS experiment currently targets original Japanese EXE6 only')
    raw_sdat = nds_sdat(source, source_archive['file_id'])
    if fingerprint(raw_sdat)['sha256'] != source_archive['sha256']:
        raise ValueError(source_archive['label'] + ' SDAT fingerprint mismatch')
    archive = SoundArchive(raw_sdat)
    capacity = base[target['layout']['player_table_offset'] + target['layout']['music_player'] * 12 + 8]
    if song == 'room':
        index, name = 2, 'BGM_ROOM'
        blob, dependency, conversion = convert_song(archive, index, capacity, song_gain_db=song_gain_db)
    elif song == 'battle':
        index, name = 35, 'BGM_BATTLE'
        blob, dependency, conversion = convert_merged_song(archive, index, BATTLE_GROUPS, capacity, song_gain_db)
    elif song == 'kando':
        index, name = 31, 'BGM_KANDO'
        blob, dependency, conversion = convert_song(archive, index, capacity,
                                                   song_gain_db=song_gain_db, native_effect_headroom=True)
    elif song == 'sf1-kincho':
        index, name = 23, 'BGM23KINCHO'
        blob, dependency, conversion = convert_song(archive, index, capacity,
                                                   song_gain_db=song_gain_db, native_effect_headroom=True)
    elif song == 'sf2-win':
        index, name = 30, 'BGM_WIN'
        blob, dependency, conversion = convert_song(archive, index, capacity,
                                                   song_gain_db=song_gain_db, native_effect_headroom=True)
    elif song == 'sf1-battle-lfo':
        index, name = 27, 'BGM27BATTLE'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db, native_pitch_lfo=True)
    else:
        raise ValueError('Unknown NDS experiment song')
    return pack_converted_experiment(source, base, key, raw_sdat, index, name,
                                     blob, dependency, conversion, events, pcm_channels)


def pack_converted_experiment(source, base, key, raw_sdat, index, name, blob, dependency,
                              conversion, events=('1',), pcm_channels=10):
    """Pack an already-converted research song through the shared exporter.

    Kept separate so a read-only batch audit can check candidate resources
    without registering untested songs in the research CLI or manager.
    """
    source_fingerprint = fingerprint(source)
    if SOURCES.get(source_fingerprint['sha256']) != key:
        raise ValueError('Converted experiment source is not a verified original')
    source_archive = SOURCE_ARCHIVES[key[:4]]
    if fingerprint(raw_sdat)['sha256'] != source_archive['sha256']:
        raise ValueError('Converted experiment SDAT fingerprint mismatch')
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS experiment currently targets original Japanese EXE6 only')
    catalog, reports = catalog_originals(base, base, {})
    source_key = 'nds-' + key
    song_key = source_key + ':' + str(index)
    slot = target['layout']['entry_count']
    catalog['table_entry_count'] = slot + 1
    catalog['sources'][source_key] = fingerprint(blob)
    catalog['source_labels'][source_key] = f'{source_archive["label"]}: converted {name} (research)'
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
        'sdat_fingerprint': fingerprint(raw_sdat), 'nds_file_id': source_archive['file_id'],
        'sequence_index': index, 'sequence_name': name,
        'generated_mplay_fingerprint': fingerprint(blob),
        'note_timing_check': conversion['note_timing_check'],
        'song_gain_db': conversion['song_gain_db'],
        'song_gain_scope': conversion['song_gain_scope'],
        'conversion_report': 'conversion.json', 'production_manager_support': False})
    if conversion.get('native_pitch_lfo'):
        manifest['nds_conversion']['native_pitch_lfo_approximation'] = True
    return output, patch, manifest, conversion, dependency, blob, catalog, raw_sdat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--song', choices=tuple(SONG_FAMILIES), default='room')
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
