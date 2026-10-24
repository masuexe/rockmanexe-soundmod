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
from nds_track_merge import BATTLE_GROUPS, SF2_HOKORA_GROUPS, SF3_KINCHO_GROUPS, SF3_DEMPAJIKEN_GROUPS, SF3_BOSSMAE_GROUPS, SF3_CHANGE_GROUPS, SF3_AJITO_GROUPS, SF3_STUDIO_GROUPS, convert_merged_song

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
SONG_FAMILIES = {'room': 'ssr3', 'room-antialias': 'ssr3', 'battle': 'ssr3', 'sf3-battle-merged-antialias': 'ssr3', 'kando': 'ssr3', 'kando-antialias': 'ssr3',
                 'sf1-setsunai': 'ssr1', 'sf1-room-antialias': 'ssr1', 'sf1-labo-antialias': 'ssr1', 'sf1-school-antialias': 'ssr1', 'sf1-dempajiken-antialias': 'ssr1', 'sf1-antenna-antialias': 'ssr1', 'sf1-comical-antialias': 'ssr1', 'sf1-jiken-antialias': 'ssr1', 'sf1-kando-antialias': 'ssr1', 'sf1-win-antialias': 'ssr1', 'sf1-bossmae-antialias': 'ssr1', 'sf1-gameover-antialias': 'ssr1', 'sf3-comical-antialias': 'ssr3', 'sf3-gameover-antialias': 'ssr3', 'sf1-setsunai-antialias': 'ssr1', 'sf1-kincho': 'ssr1', 'sf1-kincho-antialias': 'ssr1', 'sf1-battle-lfo': 'ssr1', 'sf1-last': 'ssr1', 'sf1-last-antialias': 'ssr1',
                 'sf1-fmplanet-delay': 'ssr1', 'sf1-hometown-depth': 'ssr1',
                 'sf1-gowaiincho-delay': 'ssr1',
                 'sf1-planetarium-delay': 'ssr1', 'sf1-hokora-mixed-delay': 'ssr1', 'sf1-lose-depth-min': 'ssr1', 'sf1-sabishi-variable-late-envelope': 'ssr1', 'sf3-sabishi-variable-late-envelope': 'ssr3', 'sf3-kincho-ten-track': 'ssr3', 'sf3-kincho-upward-antialias': 'ssr3', 'sf3-studio-fifteen-track': 'ssr3', 'sf3-studio-upward-antialias': 'ssr3', 'sf3-ajito-upward-antialias': 'ssr3', 'sf3-change-upward-antialias': 'ssr3', 'sf3-bossmae-merged-antialias': 'ssr3', 'sf3-ajito-fourteen-track': 'ssr3', 'sf3-change-thirteen-track': 'ssr3', 'sf3-bossmae-twelve-track': 'ssr3', 'sf3-dempajiken-eleven-track': 'ssr3', 'sf3-dempajiken-merged-antialias': 'ssr3',
                 'sf3-lose-depth-min': 'ssr3',
                 'sf2-lose-mixed-depth-min': 'ssr2', 'sf2-vs-late-depth': 'ssr2', 'sf2-mizuumi-variable-tempo': 'ssr2', 'sf2-hokora-nine-track': 'ssr2', 'sf2-hokora-merged-antialias': 'ssr2',
                 'sf1-ura': 'ssr1',
                 'sf1-satellite': 'ssr1', 'sf1-satellite-upward-antialias': 'ssr1',
                 'sf1-henkan-finite': 'ssr1',
                 'sf1-win2-finite': 'ssr1',
                 'sf1-win2-antialias': 'ssr1',
                 'sf1-boss-toggle': 'ssr1',
                 'sf2-win2-release-antialias': 'ssr2', 'sf2-win': 'ssr2', 'sf2-win-antialias': 'ssr2', 'sf2-nessie-envelope': 'ssr2', 'sf2-battle-delay': 'ssr2',
                 'sf2-kaicyou-toggle': 'ssr2',
                 'sf2-dempajiken-envelope': 'ssr2', 'sf2-dempajiken-antialias-envelope': 'ssr2',
                 'sf2-henkan-finite': 'ssr2', 'sf2-henkan-antialias': 'ssr2',
                 'sf3-win2-finite': 'ssr3', 'sf3-win2-antialias': 'ssr3',
                 'sf3-hokora-envelope': 'ssr3', 'sf3-hokora-antialias-envelope': 'ssr3', 'sf3-friend-envelope': 'ssr3'}


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
    elif song == 'sf3-battle-merged-antialias':
        index, name = 35, 'BGM_BATTLE'
        blob, dependency, conversion = convert_merged_song(
            archive, index, BATTLE_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True)
    elif song == 'battle':
        index, name = 35, 'BGM_BATTLE'
        blob, dependency, conversion = convert_merged_song(archive, index, BATTLE_GROUPS, capacity, song_gain_db)
    elif song == 'kando':
        index, name = 31, 'BGM_KANDO'
        blob, dependency, conversion = convert_song(archive, index, capacity,
                                                   song_gain_db=song_gain_db, native_effect_headroom=True)
    elif song == 'sf1-satellite-upward-antialias':
        index, name = 9, 'BGM09SATELLITE'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True, bandlimited_upward_support=True,
            bandlimited_upward_future_support=True)
    elif song == 'sf2-henkan-antialias':
        index, name = 26, 'BGM_HENKAN'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True, finite_support=True)
    elif song == 'sf3-gameover-antialias':
        index, name = 40, 'BGM_GAMEOVER'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True, finite_support=True)
    elif song == 'sf3-comical-antialias':
        index, name = 28, 'BGM_COMICAL'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-gameover-antialias':
        index, name = 33, 'BGM33GAMEOVER'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True, finite_support=True)
    elif song == 'sf1-bossmae-antialias':
        index, name = 34, 'BGM34BOSSMAE'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-win-antialias':
        index, name = 30, 'BGM30WIN'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-kando-antialias':
        index, name = 24, 'BGM24KANDO'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-jiken-antialias':
        index, name = 22, 'BGM22JIKEN'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-comical-antialias':
        index, name = 21, 'BGM21COMICAL'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-antenna-antialias':
        index, name = 16, 'BGM16ANTENNA'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-dempajiken-antialias':
        index, name = 11, 'BGM11DEMPAJIKEN'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-school-antialias':
        index, name = 6, 'BGM06SCHOOL'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-labo-antialias':
        index, name = 5, 'BGM05LABO'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song == 'sf1-room-antialias':
        index, name = 4, 'BGM04ROOM'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=True)
    elif song in ('sf1-kincho', 'sf1-setsunai'):
        index, name = {'sf1-kincho': (23, 'BGM23KINCHO'), 'sf1-setsunai': (25, 'BGM25SETSUNAI')}[song]
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
    elif song in ('sf1-henkan-finite', 'sf2-henkan-finite', 'sf1-win2-finite', 'sf1-win2-antialias',
                  'sf3-win2-finite', 'sf3-win2-antialias', 'sf2-win2-release-antialias'):
        index, name = {'sf1-henkan-finite': (26, 'BGM26HENKAN'),
                       'sf2-henkan-finite': (26, 'BGM_HENKAN'),
                       'sf1-win2-finite': (31, 'BGM31WIN2'),
                       'sf1-win2-antialias': (31, 'BGM31WIN2'),
                       'sf2-win2-release-antialias': (31, 'BGM_WIN2'),
                       'sf3-win2-finite': (39, 'BGM_WIN2'),
                       'sf3-win2-antialias': (39, 'BGM_WIN2')}[song]
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db, finite_support=True,
            bandlimited_pcm=song in ('sf1-win2-antialias', 'sf3-win2-antialias', 'sf2-win2-release-antialias'),
            finite_release_support=song == 'sf2-win2-release-antialias')
    elif song in ('sf1-last', 'sf1-last-antialias', 'sf1-ura', 'sf1-satellite', 'room-antialias', 'sf2-win-antialias', 'sf1-kincho-antialias', 'kando-antialias', 'sf1-setsunai-antialias'):
        index, name = {'sf1-last': (17, 'BGM17LAST'), 'sf1-last-antialias': (17, 'BGM17LAST'), 'sf1-ura': (18, 'BGM18URA'),
                       'sf1-satellite': (9, 'BGM09SATELLITE'), 'room-antialias': (2, 'BGM_ROOM'), 'sf2-win-antialias': (30, 'BGM_WIN'),
                       'sf1-kincho-antialias': (23, 'BGM23KINCHO'), 'kando-antialias': (31, 'BGM_KANDO'),
                       'sf1-setsunai-antialias': (25, 'BGM25SETSUNAI')}[song]
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            bandlimited_pcm=song in ('room-antialias', 'sf1-last-antialias', 'sf2-win-antialias', 'sf1-kincho-antialias', 'kando-antialias', 'sf1-setsunai-antialias'))
    elif song in ('sf1-fmplanet-delay', 'sf1-hometown-depth', 'sf1-gowaiincho-delay', 'sf1-boss-toggle', 'sf1-planetarium-delay'):
        index, name = {'sf1-fmplanet-delay': (2, 'BGM02FMPLANET'),
                       'sf1-hometown-depth': (3, 'BGM03HOMETOWN'),
                       'sf1-gowaiincho-delay': (7, 'BGM07GOWAIINCHO'),
                       'sf1-planetarium-delay': (13, 'BGM13PLANETARIUM'),
                       'sf1-boss-toggle': (28, 'BGM28BOSS')}[song]
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True,
            native_pitch_lfo_live_depth=song == 'sf1-hometown-depth',
            native_pitch_lfo_live_toggle=song == 'sf1-boss-toggle',
            envelope_support=song == 'sf1-hometown-depth')
    elif song == 'sf3-bossmae-merged-antialias':
        index, name = 27, 'BGM_BOSSMAE'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_BOSSMAE_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True)
    elif song == 'sf3-change-upward-antialias':
        index, name = 47, 'BGM_CHANGE'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_CHANGE_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True, bandlimited_upward_support=True)
    elif song == 'sf3-ajito-upward-antialias':
        index, name = 7, 'BGM_AJITO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_AJITO_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True, bandlimited_upward_support=True)
    elif song == 'sf3-studio-upward-antialias':
        index, name = 4, 'BGM_STUDIO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_STUDIO_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True, bandlimited_upward_support=True)
    elif song == 'sf3-studio-fifteen-track':
        index, name = 4, 'BGM_STUDIO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_STUDIO_GROUPS, capacity, song_gain_db)
    elif song == 'sf3-ajito-fourteen-track':
        index, name = 7, 'BGM_AJITO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_AJITO_GROUPS, capacity, song_gain_db)
    elif song == 'sf3-change-thirteen-track':
        index, name = 47, 'BGM_CHANGE'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_CHANGE_GROUPS, capacity, song_gain_db)
    elif song == 'sf3-bossmae-twelve-track':
        index, name = 27, 'BGM_BOSSMAE'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_BOSSMAE_GROUPS, capacity, song_gain_db)
    elif song == 'sf3-dempajiken-merged-antialias':
        index, name = 26, 'BGM_DEMPAJIKEN'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_DEMPAJIKEN_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True)
    elif song == 'sf3-dempajiken-eleven-track':
        index, name = 26, 'BGM_DEMPAJIKEN'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_DEMPAJIKEN_GROUPS, capacity, song_gain_db)
    elif song == 'sf3-kincho-upward-antialias':
        index, name = 30, 'BGM_KINCHO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_KINCHO_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True,
            bandlimited_upward_support=True)
    elif song == 'sf3-kincho-ten-track':
        index, name = 30, 'BGM_KINCHO'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF3_KINCHO_GROUPS, capacity, song_gain_db)
    elif song == 'sf2-hokora-merged-antialias':
        index, name = 20, 'BGM_HOKORA'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF2_HOKORA_GROUPS, capacity, song_gain_db,
            bandlimited_pcm=True, merged_bandlimited_support=True)
    elif song == 'sf2-hokora-nine-track':
        index, name = 20, 'BGM_HOKORA'
        blob, dependency, conversion = convert_merged_song(
            archive, index, SF2_HOKORA_GROUPS, capacity, song_gain_db)
    elif song in ('sf1-sabishi-variable-late-envelope','sf3-sabishi-variable-late-envelope'):
        index, name = (36, 'BGM36SABISHI') if song.startswith('sf1-') else (33, 'BGM_SABISHI')
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_variable_tempo=True,
            envelope_support=True, variable_late_fitted_support=True)
    elif song == 'sf2-mizuumi-variable-tempo':
        index, name = 6, 'BGM_MIZUUMI'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_variable_tempo=True)
    elif song == 'sf2-vs-late-depth':
        index, name = 37, 'BGM_VS'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True, native_pitch_lfo_live_depth=True,
            native_pitch_lfo_late_depth=True)
    elif song == 'sf2-lose-mixed-depth-min':
        index, name = 32, 'BGM_LOSE'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True, native_pitch_lfo_live_depth=True,
            native_pitch_lfo_min_depth=True, mixed_loop_support=True, mixed_live_depth_support=True,
            envelope_support=True)
    elif song in ('sf1-lose-depth-min', 'sf3-lose-depth-min'):
        index, name = (32, 'BGM32LOSE') if song == 'sf1-lose-depth-min' else (42, 'BGM_LOSE')
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True,
            native_pitch_lfo_live_depth=True, native_pitch_lfo_min_depth=True,
            envelope_support=song == 'sf1-lose-depth-min')
    elif song == 'sf1-hokora-mixed-delay':
        index, name = 20, 'BGM20HOKORA'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True, mixed_loop_support=True,
            native_pitch_lfo_min_depth=True)
    elif song == 'sf2-battle-delay':
        index, name = 27, 'BGM_BATTLE'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, native_pitch_lfo_delay=True)
    elif song in ('sf3-hokora-envelope', 'sf3-hokora-antialias-envelope', 'sf3-friend-envelope'):
        index, name = (10, 'BGM_HOKORA') if song != 'sf3-friend-envelope' else (29, 'BGM_FRIEND')
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=song == 'sf3-friend-envelope', envelope_support=True,
            bandlimited_pcm=song == 'sf3-hokora-antialias-envelope')
    elif song in ('sf2-dempajiken-envelope', 'sf2-dempajiken-antialias-envelope'):
        index, name = 11, 'BGM_DEMPAJIKEN'
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            envelope_support=True, bandlimited_pcm=song == 'sf2-dempajiken-antialias-envelope')
    elif song in ('sf2-nessie-envelope', 'sf2-kaicyou-toggle'):
        index, name = (15, 'BGM_NESSIE') if song == 'sf2-nessie-envelope' else (16, 'BGM_KAICYOU')
        tracks = trace_sequence(archive.sequence(index)[0], analysis_only=True)
        blob, dependency, conversion = convert_merged_song(
            archive, index, [(t['track'],) for t in tracks], capacity, song_gain_db,
            native_pitch_lfo=True, envelope_support=True,
            native_pitch_lfo_delay=song == 'sf2-kaicyou-toggle',
            native_pitch_lfo_live_toggle=song == 'sf2-kaicyou-toggle')
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
        if conversion['native_pitch_lfo'].get('delay_approximation'):
            manifest['nds_conversion']['native_pitch_lfo_delay_approximation'] = True
        if conversion['native_pitch_lfo'].get('live_depth_approximation'):
            manifest['nds_conversion']['native_pitch_lfo_live_depth_approximation'] = True
        if conversion['native_pitch_lfo'].get('live_toggle_approximation'):
            manifest['nds_conversion']['native_pitch_lfo_live_toggle_approximation'] = True
    if conversion.get('bandlimited_pcm'):
        manifest['nds_conversion']['bandlimited_pcm'] = conversion['bandlimited_pcm']
    if conversion.get('native_pitch_lfo', {}).get('minimum_depth_quantization'):
        manifest['nds_conversion']['native_pitch_lfo_minimum_depth_quantization'] = True
    if conversion.get('mixed_loop_song'):
        manifest['nds_conversion']['mixed_loop_song'] = conversion['mixed_loop_song']
    if conversion.get('native_pitch_lfo', {}).get('variable_late_fitted_extension'):
        manifest['nds_conversion']['variable_late_fitted_extension'] = conversion['native_pitch_lfo']['variable_late_fitted_extension']
    if conversion.get('native_pitch_lfo', {}).get('variable_tempo_approximation'):
        manifest['nds_conversion']['native_pitch_lfo_variable_tempo_approximation'] = conversion['native_pitch_lfo']['variable_tempo_approximation']
    if conversion.get('native_pitch_lfo', {}).get('late_depth_activation'):
        manifest['nds_conversion']['native_pitch_lfo_late_depth_activation'] = conversion['native_pitch_lfo']['late_depth_activation']
    if conversion.get('mixed_live_depth_extension'):
        manifest['nds_conversion']['mixed_live_depth_extension'] = conversion['mixed_live_depth_extension']
    if conversion.get('finite_song'):
        manifest['nds_conversion']['finite_song'] = True
    if conversion.get('finite_release_snapshots'):
        manifest['nds_conversion']['finite_release_snapshots'] = True
    if conversion.get('envelope_approximation'):
        manifest['nds_conversion']['envelope_approximation'] = True
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
