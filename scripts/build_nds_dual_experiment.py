#!/usr/bin/env python3
"""Pack two checked NDS conversions with fixed title/battle/communication routing.

Research exporter only; the existing converter, relocator and hooks are reused.
Original game inputs are read-only. No production manager integration is implied.
"""
import argparse
import copy
import json
from pathlib import Path

from build_nds_experiment import build_experiment, SOURCE_ARCHIVES
from build_unified import build_catalog
from original_catalog import catalog_originals
from scan_audio import apply_bps, fingerprint
from target_profiles import validate_target
from transplant_song import make_bps


def validate_plan(plan):
    if (not isinstance(plan, dict) or plan.get('schema_version') != 1
            or not {'title', 'battle'} <= plan.keys()
            or set(plan) - {'schema_version', 'title', 'battle', 'communication'}):
        raise ValueError('Choose a schema1 title/battle dual NDS plan')
    if plan.get('communication', 'title') not in ('title', 'battle'):
        raise ValueError('Communication must select title or battle')
    for role in ('title', 'battle'):
        spec = plan[role]
        if (not isinstance(spec, dict) or not {'source', 'song'} <= spec.keys()
                or set(spec) - {'source', 'song', 'song_gain_db'}
                or not isinstance(spec['source'], str) or not spec['source']
                or not isinstance(spec['song'], str) or not spec['song']):
            raise ValueError('Each role needs an original source path and registered song selector')


def build_dual_experiment(base, plan, pcm_channels=10):
    validate_plan(plan)
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        raise ValueError('Dual NDS experiment targets original Japanese EXE6 only')
    catalog, reports = catalog_originals(base, base, {})
    native_count = target['layout']['entry_count']
    catalog['table_entry_count'] = native_count + 2
    sources, songs, keys, metadata, original_cache = {}, {}, {}, {}, {}
    for ordinal, role in enumerate(('title', 'battle')):
        spec = plan[role]
        path = Path(spec['source']).resolve()
        if path not in original_cache:
            original_cache[path] = path.read_bytes()
        _, _, single, conversion, dependency, blob, _, sdat = build_experiment(
            original_cache[path], base, events=('1',), pcm_channels=pcm_channels,
            song=spec['song'], song_gain_db=spec.get('song_gain_db', 3.5))
        origin = single['nds_conversion']
        profile, index = origin['source_profile'], origin['sequence_index']
        source_key = 'nds-' + profile + '-' + role
        song_key = source_key + ':' + str(index)
        slot = native_count + ordinal
        label = SOURCE_ARCHIVES[profile[:4]]['label'] + ': ' + origin['sequence_name']
        catalog['sources'][source_key] = fingerprint(blob)
        catalog['source_labels'][source_key] = label + ' (dual research)'
        catalog['entries'].append({
            'key': song_key, 'source': source_key, 'source_index': index,
            'source_label': catalog['source_labels'][source_key], 'target_index': slot,
            'track_count': conversion['track_count'], 'empty': False,
            'playlist_eligible': True, 'classification': 'converted_nds_research_music',
            'availability': 'importable_music', 'name': origin['sequence_name'],
            'name_status': 'original_sdat_symbol', 'source_player': 0, 'second_field_raw': 0})
        reports[song_key], sources[source_key], keys[role] = dependency, blob, song_key
        songs[role] = {'blob': blob, 'dependency': dependency, 'conversion': conversion, 'sdat': sdat}
        metadata[role] = {**copy.deepcopy(origin), 'selector': spec['song'],
                          'source_path': str(path), 'source_key': source_key,
                          'song_key': song_key, 'target_index': slot,
                          'converted_blob': role + '/converted-mplay.bin',
                          'conversion_report': role + '/conversion.json',
                          'dependency_report': role + '/dependencies.json'}
    communication = plan.get('communication', 'title')
    playlist = {'schema_version': 1, 'target_profile': target['key'], 'pools': {
        '1': {'tracks': [keys['title']], 'selector_shift': 0},
        '21': {'tracks': [keys['battle']], 'selector_shift': 0},
        'scene:communication': {'tracks': [keys[communication]], 'selector_shift': 0}}}
    output, catalog, manifest = build_catalog(base, base, catalog, reports, sources,
                                             playlist, pcm_channels, selected_only=True)
    patch = make_bps(base, output)
    rebuilt, patch_info = apply_bps(base, patch)
    if rebuilt != output:
        raise AssertionError('Dual NDS patch reconstruction differs')
    manifest.update(bps=patch_info, nds_dual_conversion={
        'schema_version': 1, 'songs': metadata, 'communication_role': communication,
        'per_song_source_namespace': True, 'simultaneous_music_players': False,
        'conversion_or_native_mixer_changed': False, 'production_manager_support': False,
        'manual_acceptance_inferred_from_standalone_songs': False})
    return output, patch, manifest, catalog, songs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--pcm-channels', type=int, default=10)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Use a fresh output directory')
    output, patch, manifest, catalog, songs = build_dual_experiment(
        args.base.read_bytes(), json.loads(args.plan.read_text()), args.pcm_channels)
    manifest['original_path'] = str(args.base.resolve())
    manifest['plan_path'] = str(args.plan.resolve())
    args.out.mkdir(parents=True)
    (args.out / 'unified.gba').write_bytes(output)
    (args.out / 'unified.bps').write_bytes(patch)
    for name, value in [('build.json', manifest), ('catalog.json', catalog)]:
        (args.out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    for role, data in songs.items():
        folder = args.out / role
        folder.mkdir()
        (folder / 'converted-mplay.bin').write_bytes(data['blob'])
        (folder / 'source.sdat').write_bytes(data['sdat'])
        for name in ('conversion', 'dependency'):
            filename = 'dependencies.json' if name == 'dependency' else 'conversion.json'
            (folder / filename).write_text(json.dumps(data[name], indent=2) + '\n')
    print('Dual NDS title/battle build:', manifest['output_fingerprint'])


if __name__ == '__main__':
    main()
