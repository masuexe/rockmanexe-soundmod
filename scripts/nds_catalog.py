"""Initial manager NDS library, using only registered conversion configurations."""
import copy
from pathlib import Path

from build_nds_experiment import SOURCES, SOURCE_ARCHIVES, build_experiment
from original_catalog import PROFILES
from scan_audio import fingerprint

NDS_DIRECTORY = Path(__file__).resolve().parents[2].parent / 'nds' / 'roms'
NDS_PROFILES = {'nds-' + family: {'label': item['label'] + ' (NDS, JP)',
                                'filename': family + '.nds', 'family': family}
                for family, item in SOURCE_ARCHIVES.items()}
# IDs are permanent; additional configurations append slots, never renumber these.
NDS_SLOT_START = 8954
if max(p['target_slot_start'] + p['entry_count'] for p in PROFILES.values()) > NDS_SLOT_START:
    raise ValueError('GBA donor ranges overlap reserved NDS song slots')
SONGS = (
    ('ssr1', 18, 'sf1-ura-upward-antialias', 'URA', 3.5, False),
    ('ssr1', 26, 'sf1-henkan-antialias', 'HENKAN', 0, True),
    ('ssr2', 30, 'sf2-win-antialias', 'WIN', 3.5, False),
    ('ssr3', 2, 'room-antialias', 'ROOM', 3.5, False),
    ('ssr3', 35, 'sf3-battle-merged-antialias', 'BATTLE', 3.5, False),
    ('ssr1', 4, 'sf1-room-antialias', 'ROOM', 3.5, False),
    ('ssr2', 26, 'sf2-henkan-antialias', 'HENKAN', 3.5, True),
    ('ssr3', 31, 'kando-antialias', 'KANDO', 3.5, False),
)


def identify_nds(data):
    profile = SOURCES.get(fingerprint(data)['sha256'])
    if profile is None:
        raise ValueError('Choose a supported original Japanese Star Force 1/2/3 ROM')
    return 'nds-' + profile[:4]


def discover_nds(directory, uploaded):
    paths = {}
    for key, spec in NDS_PROFILES.items():
        candidates = [uploaded / spec['filename']]
        candidates += [directory / (profile + '.nds') for profile in sorted(SOURCES.values())
                       if profile.startswith(spec['family'])]
        path = next((p for p in candidates if p.is_file()), None)
        if path is not None:
            paths[key] = (path.name, path)
    return paths


def add_nds_catalog(value, reports, sources, originals, base, cache):
    """Extend a GBA catalog with isolated converted banks and stable song IDs."""
    if not originals:
        return
    if value['target_profile'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS music currently requires Japanese EXE6 Gregar or Falzar')
    provenance = {}
    for key, raw in originals.items():
        if key not in NDS_PROFILES or identify_nds(raw) != key:
            raise ValueError('NDS source does not match its selected game')
        provenance[key] = {'rom_fingerprint': fingerprint(raw),
                           'source_profile': SOURCES[fingerprint(raw)['sha256']]}
    conversions = []
    base_sha = fingerprint(base)['sha256']
    for ordinal, (family, index, selector, name, gain, finite) in enumerate(SONGS):
        original_key = 'nds-' + family
        if original_key not in originals:
            continue
        source_sha = provenance[original_key]['rom_fingerprint']['sha256']
        cache_key = (source_sha, base_sha, selector)
        if cache_key not in cache:
            _, _, manifest, conversion, dependency, blob, _, _ = build_experiment(
                originals[original_key], base, song=selector, song_gain_db=gain)
            cache[cache_key] = (blob, dependency, conversion, manifest['nds_conversion'])
        blob, dependency, conversion, origin = cache[cache_key]
        if (origin['sequence_index'] != index or origin['song_gain_db'] != gain
                or bool(conversion.get('finite_song')) != finite):
            raise AssertionError('Registered NDS configuration changed')
        source = f'nds-{family}-{index}'
        song_key = f'{source}:{index}'
        slot = NDS_SLOT_START + ordinal
        label = SOURCE_ARCHIVES[family]['label'] + ' · ' + name
        value['sources'][source] = fingerprint(blob)
        value['source_labels'][source] = label
        value['entries'].append({
            'key': song_key, 'source': source, 'source_label': label, 'source_index': index,
            'target_index': slot, 'track_count': conversion['track_count'],
            'source_player': 0, 'second_field_raw': 0, 'empty': False,
            'playlist_eligible': True, 'availability': 'importable_music',
            'classification': 'converted_nds_music', 'name': name, 'name_status': 'registered_nds_title',
            'finite_song': finite, 'playback_note': 'Ends naturally; does not repeat' if finite else '',
            'nds_selector': selector, 'original_source': original_key})
        reports[song_key] = dependency
        sources[source] = blob
        conversions.append({**copy.deepcopy(origin), 'key': song_key, 'source_key': source,
                            'target_index': slot, 'selector': selector})
    value['table_entry_count'] = max(value['table_entry_count'], NDS_SLOT_START + len(SONGS))
    value['nds_sources'] = provenance
    value['nds_conversions'] = conversions


def annotate_nds_manifest(manifest, value):
    selected = {item['key'] for item in manifest['imports']}
    conversions = [copy.deepcopy(c) for c in value.get('nds_conversions', []) if c['key'] in selected]
    if conversions:
        manifest['nds_manager'] = {'schema_version': 1, 'songs': conversions,
                                   'manual_acceptance_inferred': False,
                                   'library_song_count': len(SONGS),
                                   'scope': 'Registered manager library; converted GBA playback'}
