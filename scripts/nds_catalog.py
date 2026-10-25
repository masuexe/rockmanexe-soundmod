"""Initial manager NDS library, using only registered conversion configurations."""
import copy
from pathlib import Path

from build_nds_experiment import SOURCES, SOURCE_ARCHIVES
from nds_music import nds_sdat
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
    ('ssr1', 6, 'sf1-school-antialias', 'SCHOOL', 3.5, False),
    ('ssr2', 31, 'sf2-win2-release-antialias', 'WIN2', 3.5, True),
    ('ssr3', 28, 'sf3-comical-antialias', 'COMICAL', 3.5, False),
    ('ssr1', 21, 'sf1-comical-antialias', 'COMICAL', 3.5, False),
    ('ssr1', 24, 'sf1-kando-antialias', 'KANDO', 3.5, False),
    ('ssr2', 11, 'sf2-dempajiken-antialias-envelope', 'DEMPAJIKEN', 3.5, False),
    ('ssr2', 20, 'sf2-hokora-merged-antialias', 'HOKORA', 3.5, False),
    ('ssr3', 39, 'sf3-win2-antialias', 'WIN2', 3.5, True),
    ('ssr3', 40, 'sf3-gameover-antialias', 'GAMEOVER', 3.5, True),
    ('ssr1', 5, 'sf1-labo-antialias', 'LABO', 3.5, False),
    ('ssr1', 22, 'sf1-jiken-antialias', 'JIKEN', 3.5, False),
    ('ssr2', 27, 'sf2-battle-delay', 'BATTLE', 3.5, False),
    ('ssr2', 16, 'sf2-kaicyou-toggle', 'KAICYOU', 3.5, False),
    ('ssr3', 27, 'sf3-bossmae-merged-antialias', 'BOSSMAE', 3.5, False),
    ('ssr3', 30, 'sf3-kincho-upward-antialias', 'KINCHO', 3.5, False),
    ('ssr1', 16, 'sf1-antenna-antialias', 'ANTENNA', 3.5, False),
    ('ssr1', 11, 'sf1-dempajiken-antialias', 'DEMPAJIKEN', 3.5, False),
    ('ssr1', 30, 'sf1-win-antialias', 'WIN', 3.5, False),
    ('ssr1', 33, 'sf1-gameover-antialias', 'GAMEOVER', 3.5, True),
    ('ssr1', 34, 'sf1-bossmae-antialias', 'BOSSMAE', 3.5, False),
    ('ssr3', 26, 'sf3-dempajiken-merged-antialias', 'DEMPAJIKEN', 3.5, False),
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


# Static facts from the registered, independently checked configurations.
TRACK_COUNTS = dict(zip((s[2] for s in SONGS), (8, 4, 7, 6, 8, 6, 4, 7, 7, 6, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 8, 8, 8)))


def add_nds_catalog(value, originals):
    """Validate originals and list registered songs without converting audio."""
    if not originals:
        return
    if value['target_profile'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS music currently requires Japanese EXE6 Gregar or Falzar')
    provenance = {}
    for key, raw in originals.items():
        fp = fingerprint(raw)
        profile = SOURCES.get(fp['sha256'])
        if key not in NDS_PROFILES or profile is None or 'nds-' + profile[:4] != key:
            raise ValueError('NDS source does not match its selected game')
        archive = SOURCE_ARCHIVES[profile[:4]]
        sdat = fingerprint(nds_sdat(raw, archive['file_id']))
        if sdat['sha256'] != archive['sha256']:
            raise ValueError('NDS SDAT fingerprint differs')
        provenance[key] = {'rom_fingerprint': fp, 'source_profile': profile,
                           'sdat_fingerprint': sdat}
    for ordinal, (family, index, selector, name, gain, finite) in enumerate(SONGS):
        original_key = 'nds-' + family
        if original_key not in originals:
            continue
        source = f'nds-{family}-{index}'
        label = SOURCE_ARCHIVES[family]['label'] + ' · ' + name
        value['source_labels'][source] = label
        value['entries'].append({
            'key': f'{source}:{index}', 'source': source, 'source_label': label, 'source_index': index,
            'target_index': NDS_SLOT_START + ordinal, 'track_count': TRACK_COUNTS[selector],
            'source_player': 0, 'second_field_raw': 0, 'empty': False,
            'playlist_eligible': True, 'availability': 'importable_music',
            'classification': 'converted_nds_music', 'name': name, 'name_status': 'registered_nds_title',
            'finite_song': finite, 'playback_note': 'Ends naturally; does not repeat' if finite else '',
            'nds_selector': selector, 'original_source': original_key})
    value['table_entry_count'] = max(value['table_entry_count'], NDS_SLOT_START + len(SONGS))
    value['nds_sources'] = provenance
    value['nds_conversions'] = []


def prepare_nds_catalog(value, reports, sources, originals, base, keys, cache):
    """Prepare only selected songs in a private build snapshot, in registry order."""
    value, reports, sources = copy.deepcopy(value), dict(reports), dict(sources)
    rows = {row['key']: row for row in value['entries']}
    for spec in SONGS:
        family, index, selector, _, _, _ = spec
        source = f'nds-{family}-{index}'
        song_key = f'{source}:{index}'
        if song_key not in keys:
            continue
        row = rows[song_key]
        blob, dependency, conversion, origin = cache.get(
            originals[row['original_source']], base, spec, TRACK_COUNTS[selector])
        value['sources'][source] = fingerprint(blob)
        reports[song_key], sources[source] = dependency, blob
        value['nds_conversions'].append({**copy.deepcopy(origin), 'key': song_key, 'source_key': source,
                                        'target_index': row['target_index'], 'selector': selector})
    return value, reports, sources


def annotate_nds_manifest(manifest, value):
    selected = {item['key'] for item in manifest['imports']}
    conversions = [copy.deepcopy(c) for c in value.get('nds_conversions', []) if c['key'] in selected]
    if conversions:
        manifest['nds_manager'] = {'schema_version': 1, 'songs': conversions,
                                   'manual_acceptance_inferred': False,
                                   'library_song_count': len(SONGS),
                                   'scope': 'Registered manager library; converted GBA playback'}
