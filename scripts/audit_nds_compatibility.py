#!/usr/bin/env python3
"""Audit all SSEQ slots in pinned Star Force 1/2/3 archives against EXE6.

Converter success, shared ROM packing/BPS reconstruction and existing manual
acceptance are separate evidence levels. No ROMs/projects are written; output
contains reports only. SSAR/STRM are counted but not converted by this audit.
"""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import struct

from analyze_song import Reader
from build_nds_experiment import SOURCES, SOURCE_ARCHIVES, pack_converted_experiment
from nds_music import SoundArchive, convert_song, nds_sdat, trace_sequence
from nds_track_merge import BATTLE_GROUPS, SF2_HOKORA_GROUPS, SF3_KINCHO_GROUPS, SF3_DEMPAJIKEN_GROUPS, SF3_BOSSMAE_GROUPS, SF3_CHANGE_GROUPS, SF3_AJITO_GROUPS, SF3_STUDIO_GROUPS, convert_merged_song
from scan_audio import fingerprint
from target_profiles import validate_target

EVENTS = ('1', '21', 'scene:communication')
STATUS_LABELS = {
    'packed_known_fifteen_track_merge': '已验证十五轨分组打包通过',
    'packed_known_fourteen_track_merge': '已验证十四轨分组打包通过',
    'packed_known_thirteen_track_merge': '已验证十三轨分组打包通过',
    'packed_known_twelve_track_merge': '已验证十二轨分组打包通过',
    'packed_known_eleven_track_merge': '已验证十一轨分组打包通过',
    'packed_known_ten_track_merge': '已验证十轨分组打包通过',
    'packed_known_nine_track_merge': '已验证九轨分组打包通过',
    'empty_slot': '空槽', 'silent_sequence': '无执行音符', 'analysis_blocked': '执行分析受阻',
    'packed_standard': '常规路径打包通过', 'packed_lfo_approximation': '颤音近似打包通过',
    'packed_finite_standard': '非循环常规路径打包通过',
    'packed_finite_release_snapshots': '非循环收音快照路径打包通过',
    'packed_mixed_standard': '一次性与循环轨道混合打包通过',
    'packed_mixed_delayed_lfo_approximation': '混合轨道＋延迟颤音近似打包通过',
    'packed_mixed_live_depth_minimum_lfo_approximation': '混合轨道＋实时深度＋弱颤音量化打包通过',
    'packed_mixed_envelope_live_depth_minimum_lfo_approximation': '混合轨道＋包络＋实时深度＋弱颤音量化打包通过',
    'packed_mixed_min_depth_lfo_approximation': '混合轨道＋弱颤音量化打包通过',
    'packed_envelope_approximation': '包络近似打包通过',
    'packed_envelope_lfo_approximation': '包络＋颤音近似打包通过',
    'packed_delayed_lfo_approximation': '固定延迟颤音近似打包通过',
    'packed_envelope_delayed_lfo_approximation': '包络＋固定延迟颤音近似打包通过',
    'packed_variable_late_fitted_lfo_approximation': '变速＋后期启用＋包络颤音打包通过',
    'packed_variable_tempo_lfo_approximation': '变速＋固定颤音补偿打包通过',
    'packed_late_live_depth_lfo_approximation': '后期启用＋实时深度颤音近似打包通过',
    'packed_live_depth_lfo_approximation': '实时深度颤音近似打包通过',
    'packed_envelope_live_depth_lfo_approximation': '包络＋实时深度颤音近似打包通过',
    'packed_live_depth_minimum_lfo_approximation': '实时深度＋弱颤音量化打包通过',
    'packed_envelope_live_depth_minimum_lfo_approximation': '包络＋实时深度＋弱颤音量化打包通过',
    'packed_live_toggle_lfo_approximation': '启闭颤音近似打包通过',
    'packed_envelope_live_toggle_lfo_approximation': '包络＋启闭颤音近似打包通过',
    'capacity_blocked': '超轨数，缺少映射', 'conversion_blocked': '转换受阻',
    'converter_model_blocked': '转换校验待研究', 'packing_blocked': '转换通过，打包受阻',
}


def u32(reader, offset):
    return struct.unpack('<I', reader.read(offset, 4))[0]


def info_count(archive, group):
    block = archive.blocks['INFO']
    offset = u32(block, 8 + group * 4)
    return u32(block, offset) if offset else 0


def sequence_slots(archive):
    """Read INFO presence and SYMB names directly, without ndspy/inventory."""
    block = archive.blocks['INFO']
    table = u32(block, 8)
    if not table:
        return []
    count = u32(block, table)
    entries = struct.unpack('<' + 'I' * count, block.read(table + 4, count * 4))
    names = [None] * count
    offset, size = struct.unpack('<II', archive.reader.read(0x10, 8))
    if offset:
        symbols = Reader(archive.reader.read(offset, size))
        declared = u32(symbols, 4)
        # Nitro directory sizes may omit the trailing SYMB alignment bytes.
        if symbols.read(0, 4) != b'SYMB' or declared not in (size, (size + 3) & ~3):
            raise ValueError('Invalid SDAT symbol block')
        if declared > size:
            if any(archive.reader.read(offset + size, declared - size)):
                raise ValueError('Nonzero SDAT symbol alignment padding')
            symbols = Reader(archive.reader.read(offset, declared))
        symbols_table = u32(symbols, 8)
        if symbols_table:
            if u32(symbols, symbols_table) != count:
                raise ValueError('SSEQ INFO/SYMB slot counts differ')
            pointers = struct.unpack('<' + 'I' * count, symbols.read(symbols_table + 4, count * 4))
            for index, pointer in enumerate(pointers):
                if pointer:
                    symbols.read(pointer, 1)
                    end = symbols.data.find(b'\0', pointer)
                    if end < 0 or end - pointer > 1024:
                        raise ValueError('Invalid SDAT sequence symbol string')
                    names[index] = symbols.read(pointer, end - pointer).decode('ascii')
    return [{'index': i, 'name': names[i], 'present': bool(entry)} for i, entry in enumerate(entries)]


class AuditArchive(SoundArchive):
    """Avoid decoding the same read-only PCM repeatedly during one archive scan."""
    def __init__(self, raw):
        super().__init__(raw)
        self.wave_cache = {}

    def wave(self, archive, index):
        key = archive, index
        if key not in self.wave_cache:
            self.wave_cache[key] = super().wave(archive, index)
        return self.wave_cache[key]


def features(archive, info, tracks):
    notes = [a for t in tracks for a in t['actions'] if a['name'] == 'note']
    controls = [a for t in tracks for a in t['actions'] if a['name'] == 'control']
    depth_changes, depth_toggles = [], []
    for track in tracks:
        previous = 0
        for action in track['actions']:
            if action['opcode'] != 0xCA:
                continue
            depth = action['state_after']['mod_depth']
            if previous > 0 and depth > 0 and previous != depth:
                depth_changes.append({'source_track': track['track'], 'ticks': action['ticks'],
                                      'before': previous, 'after': depth})
            if previous != depth and (previous == 0 or depth == 0):
                depth_toggles.append({'source_track': track['track'], 'ticks': action['ticks'],
                                      'before': previous, 'after': depth})
            previous = depth
    configs = sorted({tuple(a['state_after'][k] for k in
                           ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay'))
                      for a in notes if a['state_after']['mod_depth']})
    result = {'track_count': len(tracks), 'track_ids': [t['track'] for t in tracks],
              'executed_note_events_in_trace': len(notes),
              'termination': sorted({t['termination'] for t in tracks}),
              'loop_periods': sorted({t['loop_ticks'] for t in tracks if t['termination'] == 'loop'}),
              'long_notes': sum(a['duration'] > 223 for a in notes),
              'zero_gate_notes': sum(a['duration'] == 0 for a in notes),
              'executed_controls': sorted({f'0x{a["opcode"]:02X}' for a in controls}),
              'nonzero_mod_depth_executed': any(a['opcode'] == 0xCA and a['value'] for a in controls),
              'positive_mod_depth_changes': depth_changes,
              'mod_depth_toggles': depth_toggles,
              'active_delayed_modulation_executed': any(a.get('state_after', {}).get('mod_depth')
                                                       and a['state_after'].get('mod_delay')
                                                       for t in tracks for a in t['actions']),
              'modulated_note_on_states': sum(bool(a['state_after']['mod_depth']) for a in notes),
              'modulation_configs_at_note_on': [dict(zip(('type', 'speed', 'depth', 'range', 'delay'), values))
                                                for values in configs],
              'nonzero_bend_note_states': sum(bool(a['state_after']['bend']) for a in notes),
              'portamento_note_states': sum(bool(a['state_after']['porta']) for a in notes),
              'envelope_override_controls': sorted({f'0x{a["opcode"]:02X}' for a in controls if 0xD0 <= a['opcode'] <= 0xD3})}
    try:
        bank, archives = archive.bank(info['bank_id'])
        definitions = {archive.note_definition(bank, instrument, key)
                       for t in tracks for instrument, key in t['notes']}
        result['noninstant_attack_definitions'] = sum(d.attack != 127 for d in definitions)
        result['instrument_kinds'] = sorted({d.kind for d in definitions})
        waves = {(archives[d.archive_slot], d.wave_id) for d in definitions
                 if d.kind == 1 and 0 <= d.archive_slot < len(archives) and archives[d.archive_slot] != 65535}
        result['used_wave_count'] = len(waves)
        result['wave_encodings'] = sorted({archive.wave(*wave)[1]['encoding'] for wave in waves})
    except (ValueError, IndexError, struct.error) as error:
        result['resource_inspection_error'] = str(error)
    return result


def error_record(error):
    return {'exception': type(error).__name__, 'message': str(error),
            'model_assertion': isinstance(error, AssertionError)}


def scan_sequence(archive, slot, family, source, base, raw_sdat, profile, capacity,
                  gain_db=3.5, pcm_channels=10, manual_records=()):
    row = {'id': f'{family}:{slot["index"]}', 'family': family, 'index': slot['index'],
           'name': slot['name'], 'attempts': [], 'runtime_tested_by_audit': False,
           'manual_matches_packed_variant': False, 'related_manual_records': []}
    if not slot['present']:
        row['status'] = 'empty_slot'
        return row
    try:
        data, info = archive.sequence(slot['index'])
        row['sequence_info'] = info
        tracks = trace_sequence(data, analysis_only=True)
        row.update(sequence_info=info, features=features(archive, info, tracks))
    except (ValueError, IndexError, struct.error) as error:
        row.update(status='analysis_blocked', analysis_error=error_record(error))
        return row
    if not row['features']['executed_note_events_in_trace']:
        row['status'] = 'silent_sequence'
        return row
    row['related_manual_records'] = [r for r in manual_records if r['family'] == family and r['sequence_index'] == slot['index']]
    groups = [(t['track'],) for t in tracks]
    routes = ['direct', 'singleton_bend_long'] if len(tracks) <= capacity else []
    if len(tracks) <= capacity and row['features']['nonzero_mod_depth_executed']:
        routes.append('native_pitch_lfo_approximation')
    envelope_needed = (row['features'].get('noninstant_attack_definitions', 0)
                       or row['features'].get('envelope_override_controls', []))
    if len(tracks) <= capacity and envelope_needed:
        routes.append('singleton_envelope_approximation')
        if row['features']['nonzero_mod_depth_executed']:
            routes.append('envelope_pitch_lfo_approximation')
    if len(tracks) <= capacity and row['features'].get('active_delayed_modulation_executed'):
        routes.append('fixed_delay_pitch_lfo_approximation')
        if envelope_needed:
            routes.append('envelope_fixed_delay_pitch_lfo_approximation')
    if len(tracks) <= capacity and row['features'].get('positive_mod_depth_changes'):
        routes.append('live_depth_pitch_lfo_approximation')
        if envelope_needed:
            routes.append('envelope_live_depth_pitch_lfo_approximation')
    if len(tracks) <= capacity and row['features']['nonzero_mod_depth_executed']:
        routes.append('live_toggle_pitch_lfo_approximation')
        if envelope_needed:
            routes.append('envelope_live_toggle_pitch_lfo_approximation')
    if (family == 'ssr2' and slot['index'] == 20 and capacity == 8
            and len(tracks) == 9 and {t['track'] for t in tracks} == set(range(9))
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf2_hokora_nine_track_merge')
    if (family == 'ssr3' and slot['index'] == 30 and capacity == 8
            and len(tracks) == 10 and {t['track'] for t in tracks} == set(range(8)) | {14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_kincho_ten_track_merge')
    if (family == 'ssr3' and slot['index'] == 26 and capacity == 8
            and len(tracks) == 11 and {t['track'] for t in tracks} == set(range(9)) | {14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_dempajiken_eleven_track_merge')
    if (family == 'ssr3' and slot['index'] == 27 and capacity == 8
            and len(tracks) == 12 and {t['track'] for t in tracks} == {0,1,2,3,4,5,7,8,9,13,14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_bossmae_twelve_track_merge')
    if (family == 'ssr3' and slot['index'] == 47 and capacity == 8
            and len(tracks) == 13 and {t['track'] for t in tracks} == set(range(10)) | {13,14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_change_thirteen_track_merge')
    if (family == 'ssr3' and slot['index'] == 7 and capacity == 8
            and len(tracks) == 14 and {t['track'] for t in tracks} == set(range(12)) | {14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_ajito_fourteen_track_merge')
    if (family == 'ssr3' and slot['index'] == 4 and capacity == 8
            and len(tracks) == 15 and {t['track'] for t in tracks} == set(range(13)) | {14,15}
            and all(t.get('termination') == 'loop' for t in tracks)
            and not envelope_needed and not row['features']['nonzero_mod_depth_executed']):
        routes.append('known_sf3_studio_fifteen_track_merge')
    if family == 'ssr3' and slot['index'] == 35:
        routes.append('known_sf3_battle_merge')
    if len(tracks) <= capacity and all(t.get('termination') == 'end' for t in tracks):
        routes.append('finite_singleton_long')
    if len(tracks) <= capacity and {t.get('termination') for t in tracks} == {'end', 'loop'}:
        routes.append('mixed_singleton_long')
        if row['features']['nonzero_mod_depth_executed']:
            routes.append('mixed_fixed_delay_pitch_lfo_approximation')
    if not routes:
        row.update(status='capacity_blocked', track_capacity=capacity)
        return row
    pack_errors = False
    for route in routes:
        known_fifteen = route == 'known_sf3_studio_fifteen_track_merge'
        known_fourteen = route == 'known_sf3_ajito_fourteen_track_merge'
        known_thirteen = route == 'known_sf3_change_thirteen_track_merge'
        known_twelve = route == 'known_sf3_bossmae_twelve_track_merge'
        known_eleven = route == 'known_sf3_dempajiken_eleven_track_merge'
        known_ten = route == 'known_sf3_kincho_ten_track_merge'
        known_nine = route == 'known_sf2_hokora_nine_track_merge'
        variable_late_fitted = route == 'variable_late_fitted_pitch_lfo_approximation'
        variable_tempo = variable_late_fitted or route == 'variable_tempo_pitch_lfo_approximation'
        late_depth = route == 'late_live_depth_pitch_lfo_approximation'
        mixed = route.startswith('mixed_')
        mixed_live = route in ('mixed_live_depth_minimum_pitch_lfo_approximation',
                               'mixed_envelope_live_depth_minimum_pitch_lfo_approximation')
        minimum_depth = mixed_live or route in ('mixed_min_depth_pitch_lfo_approximation',
                                  'live_depth_minimum_pitch_lfo_approximation',
                                  'envelope_live_depth_minimum_pitch_lfo_approximation')
        release = route == 'finite_singleton_release'
        finite = release or route == 'finite_singleton_long'
        live_toggle = route in ('live_toggle_pitch_lfo_approximation', 'envelope_live_toggle_pitch_lfo_approximation')
        live_depth = late_depth or mixed_live or route in ('live_depth_pitch_lfo_approximation', 'envelope_live_depth_pitch_lfo_approximation',
                               'live_depth_minimum_pitch_lfo_approximation', 'envelope_live_depth_minimum_pitch_lfo_approximation')
        delayed = live_depth or live_toggle or route in ('fixed_delay_pitch_lfo_approximation', 'envelope_fixed_delay_pitch_lfo_approximation',
                                                       'mixed_fixed_delay_pitch_lfo_approximation', 'mixed_min_depth_pitch_lfo_approximation')
        pitch_lfo = variable_tempo or delayed or route in ('native_pitch_lfo_approximation', 'envelope_pitch_lfo_approximation')
        envelope = variable_late_fitted or route == 'mixed_envelope_live_depth_minimum_pitch_lfo_approximation' or route in ('singleton_envelope_approximation', 'envelope_pitch_lfo_approximation',
                             'envelope_fixed_delay_pitch_lfo_approximation', 'envelope_live_depth_pitch_lfo_approximation',
                             'envelope_live_toggle_pitch_lfo_approximation', 'envelope_live_depth_minimum_pitch_lfo_approximation')
        approximations = {'native_pitch_lfo': pitch_lfo, 'envelope': envelope,
                          'fixed_delay': delayed, 'live_depth': live_depth, 'live_toggle': live_toggle}
        gains = [gain_db]
        for applied_gain in gains:
            attempt = {'route': route, 'gain_db': applied_gain, 'approximations': approximations,
                       'conversion_passed': False, 'packing_passed': False}
            row['attempts'].append(attempt)
            if known_fifteen:
                attempt['known_fifteen_track_groups'] = [list(g) for g in SF3_STUDIO_GROUPS]
            if known_fourteen:
                attempt['known_fourteen_track_groups'] = [list(g) for g in SF3_AJITO_GROUPS]
            if known_thirteen:
                attempt['known_thirteen_track_groups'] = [list(g) for g in SF3_CHANGE_GROUPS]
            if known_twelve:
                attempt['known_twelve_track_groups'] = [list(g) for g in SF3_BOSSMAE_GROUPS]
            if known_eleven:
                attempt['known_eleven_track_groups'] = [list(g) for g in SF3_DEMPAJIKEN_GROUPS]
            if known_ten:
                attempt['known_ten_track_groups'] = [list(g) for g in SF3_KINCHO_GROUPS]
            if known_nine:
                attempt['known_nine_track_groups'] = [list(g) for g in SF2_HOKORA_GROUPS]
            if variable_late_fitted:
                attempt['variable_late_fitted_support'] = True
            if variable_tempo:
                attempt['native_pitch_lfo_variable_tempo'] = True
            if late_depth:
                attempt['native_pitch_lfo_late_depth'] = True
            if finite:
                attempt['finite_support'] = True
            if release:
                attempt['finite_release_support'] = True
            if mixed:
                attempt.update(mixed_loop_support=True, native_pitch_lfo_min_depth=minimum_depth)
            if mixed_live:
                attempt['mixed_live_depth_support'] = True
            elif minimum_depth:
                attempt['native_pitch_lfo_min_depth'] = True
            try:
                if route == 'direct':
                    blob, dependency, conversion = convert_song(archive, slot['index'], capacity,
                                                               song_gain_db=applied_gain, native_effect_headroom=True)
                else:
                    options = {'native_pitch_lfo_live_depth': True} if live_depth else {}
                    if variable_late_fitted:
                        options['variable_late_fitted_support'] = True
                    if variable_tempo:
                        options['native_pitch_lfo_variable_tempo'] = True
                    if late_depth:
                        options['native_pitch_lfo_late_depth'] = True
                    if live_toggle:
                        options['native_pitch_lfo_live_toggle'] = True
                    if finite:
                        options['finite_support'] = True
                    if release:
                        options['finite_release_support'] = True
                    if mixed:
                        options.update(mixed_loop_support=True, native_pitch_lfo_min_depth=minimum_depth)
                    if mixed_live:
                        options['mixed_live_depth_support'] = True
                    elif minimum_depth:
                        options['native_pitch_lfo_min_depth'] = True
                    blob, dependency, conversion = convert_merged_song(
                        archive, slot['index'], BATTLE_GROUPS if route == 'known_sf3_battle_merge' else SF2_HOKORA_GROUPS if known_nine else SF3_KINCHO_GROUPS if known_ten else SF3_DEMPAJIKEN_GROUPS if known_eleven else SF3_BOSSMAE_GROUPS if known_twelve else SF3_CHANGE_GROUPS if known_thirteen else SF3_AJITO_GROUPS if known_fourteen else SF3_STUDIO_GROUPS if known_fifteen else groups,
                        capacity, applied_gain, native_pitch_lfo=pitch_lfo, envelope_support=envelope,
                        native_pitch_lfo_delay=delayed, **options)
                attempt['conversion_passed'] = True
            except (ValueError, AssertionError, IndexError, struct.error) as error:
                attempt['error'] = error_record(error)
                if (route == 'envelope_pitch_lfo_approximation' and type(error) is ValueError
                        and str(error) == 'Native pitch LFO experiment requires a fixed tempo'
                        and envelope_needed and all(t.get('termination') == 'loop' for t in tracks)
                        and 'variable_late_fitted_pitch_lfo_approximation' not in routes):
                    routes.append('variable_late_fitted_pitch_lfo_approximation')
                if (route == 'native_pitch_lfo_approximation' and type(error) is ValueError
                        and str(error) == 'Native pitch LFO experiment requires a fixed tempo'
                        and not envelope_needed and all(t.get('termination') == 'loop' for t in tracks)
                        and 'variable_tempo_pitch_lfo_approximation' not in routes):
                    routes.append('variable_tempo_pitch_lfo_approximation')
                if (route == 'live_depth_pitch_lfo_approximation' and type(error) is ValueError
                        and str(error) == 'Delayed LFO requires activation before or at the first note timestamp'
                        and not envelope_needed and all(t.get('termination') == 'loop' for t in tracks)
                        and 'late_live_depth_pitch_lfo_approximation' not in routes):
                    routes.append('late_live_depth_pitch_lfo_approximation')
                if (route in ('live_depth_pitch_lfo_approximation', 'envelope_live_depth_pitch_lfo_approximation')
                        and type(error) is ValueError
                        and str(error) == 'DS LFO cannot be represented by the bounded native approximation'
                        and all(t.get('termination') == 'loop' for t in tracks)):
                    retry = ('envelope_' if envelope else '') + 'live_depth_minimum_pitch_lfo_approximation'
                    if retry not in routes:
                        routes.append(retry)
                if (route == 'mixed_fixed_delay_pitch_lfo_approximation' and type(error) is ValueError
                        and str(error) == 'Delayed LFO requires fixed per-track modulation after initial activation'
                        and row['features'].get('positive_mod_depth_changes')
                        and {t.get('termination') for t in tracks} == {'end', 'loop'}):
                    for retry in ('mixed_live_depth_minimum_pitch_lfo_approximation',) + (
                            ('mixed_envelope_live_depth_minimum_pitch_lfo_approximation',) if envelope_needed else ()):
                        if retry not in routes:
                            routes.append(retry)
                if (route == 'mixed_fixed_delay_pitch_lfo_approximation' and type(error) is ValueError
                        and str(error) == 'DS LFO cannot be represented by the bounded native approximation'
                        and 'mixed_min_depth_pitch_lfo_approximation' not in routes):
                    routes.append('mixed_min_depth_pitch_lfo_approximation')
                if (route == 'finite_singleton_long' and isinstance(error, ValueError)
                        and str(error) == 'Unsupported merged-conversion effect 0xd3'
                        and 'finite_singleton_release' not in routes):
                    routes.append('finite_singleton_release')
                if applied_gain != 0 and 'headroom' in str(error).lower() and 0 not in gains:
                    gains.append(0.0)
                continue
            try:
                output, patch, manifest, *_ = pack_converted_experiment(
                    source, base, profile, raw_sdat, slot['index'], slot['name'] or f'SSEQ_{slot["index"]}',
                    blob, dependency, conversion, EVENTS, pcm_channels)
            except (ValueError, AssertionError, IndexError, struct.error) as error:
                pack_errors = True
                attempt['packing_error'] = error_record(error)
                continue
            attempt['packing_passed'] = True
            status = ('packed_known_fifteen_track_merge' if known_fifteen else
                      'packed_known_fourteen_track_merge' if known_fourteen else
                      'packed_known_thirteen_track_merge' if known_thirteen else
                      'packed_known_twelve_track_merge' if known_twelve else
                      'packed_known_eleven_track_merge' if known_eleven else
                      'packed_known_ten_track_merge' if known_ten else
                      'packed_known_nine_track_merge' if known_nine else
                      'packed_variable_late_fitted_lfo_approximation' if variable_late_fitted else
                      'packed_variable_tempo_lfo_approximation' if variable_tempo else
                      'packed_late_live_depth_lfo_approximation' if late_depth else
                      'packed_mixed_envelope_live_depth_minimum_lfo_approximation' if mixed_live and envelope else
                      'packed_mixed_live_depth_minimum_lfo_approximation' if mixed_live else
                      'packed_envelope_live_depth_minimum_lfo_approximation' if minimum_depth and live_depth and envelope else
                      'packed_live_depth_minimum_lfo_approximation' if minimum_depth and live_depth else
                      'packed_mixed_min_depth_lfo_approximation' if minimum_depth else
                      'packed_mixed_delayed_lfo_approximation' if mixed and pitch_lfo else
                      'packed_mixed_standard' if mixed else
                      'packed_finite_release_snapshots' if release else
                      'packed_finite_standard' if finite else
                      'packed_envelope_live_toggle_lfo_approximation' if envelope and live_toggle else
                      'packed_live_toggle_lfo_approximation' if live_toggle else
                      'packed_envelope_live_depth_lfo_approximation' if envelope and live_depth else
                      'packed_live_depth_lfo_approximation' if live_depth else
                      'packed_envelope_delayed_lfo_approximation' if envelope and delayed else
                      'packed_delayed_lfo_approximation' if delayed else
                      'packed_envelope_lfo_approximation' if envelope and pitch_lfo else
                      'packed_envelope_approximation' if envelope else
                      'packed_lfo_approximation' if pitch_lfo else 'packed_standard')
            row.update(status=status, approximations=approximations,
                       route=route, gain_db=applied_gain, gain_adjustment_required=applied_gain != gain_db,
                       target_track_count=conversion['track_count'], target_sample_count=len(dependency['samples']),
                       generated_bytes=len(blob), appended_bytes=manifest['appended_bytes'],
                       output_fingerprint=manifest['output_fingerprint'], bps_fingerprint=fingerprint(patch),
                       bps_reconstruction_verified=True,
                       manual_matches_packed_variant=any(r['output_sha256'] == manifest['output_fingerprint']['sha256']
                                                        for r in row['related_manual_records']))
            if known_fifteen:
                row['known_fifteen_track_merge'] = {
                    'source_track_count':15, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_STUDIO_GROUPS],
                    'scope':'Explicit pinned SF3 STUDIO grouping only; existing control and conversion guards; no search',
                    'additional_velocity_ratio_quantization':True,
                    'standalone_native_voice_budget_limit': {
                        'source':'sf3-studio-fifteen-track-exe6-v1',
                        'rom_sha256':'0a45586aee5c22835490442cf4536d3d168f21017bcb923c36583183e2f40489',
                        'pcm_channels':10, 'observed_note_calls':5202, 'observed_rejections':0,
                        'held_or_starting_voice_preemptions':0,
                        'held_preemption_clocks':[],
                        'release_flagged_channel_reuses_with_nonzero_envelope':2863,
                        'scope':'Original standalone two-cycle observation; channel flags are not an audible-error bound',
                        'batch_remeasured':False},
                    'standalone_zero_velocity_limit': {
                        'source_mappings':4, 'observed_native_calls':6,
                        'unpacked_control_source_mappings':4, 'added_by_grouping':0,
                        'events_retained':True, 'batch_remeasured':False}}
            if known_fourteen:
                row['known_fourteen_track_merge'] = {
                    'source_track_count':14, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_AJITO_GROUPS],
                    'scope':'Explicit pinned SF3 AJITO grouping only; existing control and conversion guards; no search',
                    'additional_velocity_ratio_quantization':True,
                    'standalone_native_voice_budget_limit': {
                        'source':'sf3-ajito-fourteen-track-exe6-v1',
                        'rom_sha256':'e7e3331fa5d3c12f75a3719db59a7ae78862439e85a3e091de23966fd09149c1',
                        'pcm_channels':10, 'observed_note_calls':3964, 'observed_rejections':0,
                        'held_or_starting_voice_preemptions':14,
                        'held_preemption_clocks':[1108,1113,5064,5160,5232,5256,6580,6585,10536,10632,10704,10728,12052,12057],
                        'release_flagged_channel_reuses_with_nonzero_envelope':1544,
                        'scope':'Original standalone two-cycle observation; channel flags are not an audible-error bound',
                        'batch_remeasured':False}}
            if known_thirteen:
                row['known_thirteen_track_merge'] = {
                    'source_track_count':13, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_CHANGE_GROUPS],
                    'scope':'Explicit pinned SF3 CHANGE grouping only; existing control and conversion guards; no search',
                    'additional_velocity_ratio_quantization':True,
                    'standalone_native_voice_budget_limit': {
                        'source':'sf3-change-thirteen-track-exe6-v1',
                        'rom_sha256':'34a58369565907c3713ca92bef337cabf7dd14435fe401fb10ff34387aa36575',
                        'pcm_channels':10, 'observed_note_calls':1339, 'observed_rejections':0,
                        'held_or_starting_voice_preemptions':4,
                        'held_preemption_clocks':[352,360,372,376],
                        'release_flagged_channel_reuses_with_nonzero_envelope':183,
                        'scope':'Original standalone two-cycle observation; channel flags are not an audible-error bound',
                        'batch_remeasured':False}}
            if known_twelve:
                row['known_twelve_track_merge'] = {
                    'source_track_count':12, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_BOSSMAE_GROUPS],
                    'scope':'Explicit pinned SF3 BOSSMAE grouping only; existing control and conversion guards; no search',
                    'standalone_native_voice_budget_limit': {
                        'source':'sf3-bossmae-twelve-track-exe6-v1',
                        'rom_sha256':'1ada1a4ed7c64d5279021b69e6ceacc49f14b78a6ee012fe17de1870bdacc935',
                        'pcm_channels':10, 'observed_note_calls':1514, 'observed_rejections':0,
                        'held_or_starting_voice_preemptions':0,
                        'release_flagged_channel_reuses_with_nonzero_envelope':905,
                        'scope':'Original standalone two-cycle observation; channel flags are not an audible-error bound',
                        'batch_remeasured':False}}
            if known_eleven:
                row['known_eleven_track_merge'] = {
                    'source_track_count':11, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_DEMPAJIKEN_GROUPS],
                    'scope':'Explicit pinned SF3 DEMPAJIKEN grouping only; existing control and conversion guards; no search',
                    'standalone_native_allocation_limit': {
                        'source':'sf3-dempajiken-eleven-track-exe6-v1',
                        'pcm_channels':10, 'observed_note_calls':999, 'observed_rejections':3,
                        'rejected_source_track':14, 'rejected_source_key':64,
                        'user_report':'Once-per-cycle accompaniment omission was inaudible on the exact accepted ROM',
                        'batch_remeasured':False}}
            if known_ten:
                row['known_ten_track_merge'] = {'source_track_count':10, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_KINCHO_GROUPS],
                    'scope':'Explicit pinned SF3 KINCHO grouping only; existing control and conversion guards; no search'}
            if known_nine:
                row['known_nine_track_merge'] = {'source_track_count':9, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF2_HOKORA_GROUPS],
                    'scope':'Explicit pinned SF2 HOKORA grouping only; original control compatibility and conversion guards unchanged; no search'}
            row['long_note_loop_carries'] = conversion.get('long_note_loop_carries', [])
            row['note_timing_validation'] = conversion.get('note_timing_validation', [])
            row['voice_context_splits'] = conversion.get('voice_context_splits', [])
            row['finite_song'] = conversion.get('finite_song')
            if mixed:
                row['mixed_loop_song'] = conversion['mixed_loop_song']
            if mixed_live:
                row['mixed_live_depth_extension'] = conversion['mixed_live_depth_extension']
            if release:
                row['finite_release_snapshots'] = conversion['finite_release_snapshots']
            if envelope:
                row['envelope_approximation'] = conversion['envelope_approximation']
            if pitch_lfo:
                row['native_pitch_lfo'] = conversion.get('native_pitch_lfo', {})
            return row
    row['status'] = ('packing_blocked' if pack_errors else 'converter_model_blocked'
                     if any(a.get('error', {}).get('model_assertion') for a in row['attempts']) else 'conversion_blocked')
    return row


ANTIALIAS_LABELS = {
    'packed': '抗混叠打包通过', 'capacity_blocked': '超出独立轨道容量',
    'conversion_blocked': '抗混叠转换受阻', 'converter_model_blocked': '抗混叠模型校验受阻',
    'packing_blocked': '抗混叠打包受阻', 'analysis_blocked': '原曲分析受阻',
    'empty_slot': '空槽', 'silent_sequence': '无执行音符',
}


def scan_antialias_variant(archive, row, source, base, raw_sdat, profile, capacity,
                           gain_db=3.5, pcm_channels=10):
    """Try a separate opt-in variant, never replace the established route.

    Looping non-instant attacks may retry with explicit fitted envelopes,
    retaining the plain failure and each mode's independent gain attempts.
    Finite unsupported D3 may retry the separate pre-note release snapshot mode.
    No inferred listening or runtime acceptance. Exact SHA matches refer to
    an existing verified manual artifact of this family and sequence only.
    """
    result = {'status': row['status'], 'attempts': [], 'runtime_tested_by_audit': False,
              'manual_matches_packed_variant': False}
    if row['status'] in ('empty_slot', 'silent_sequence', 'analysis_blocked'):
        return result
    known_candidate = (capacity == 8
        and (row['family'], row['index'], row['features']['track_count']) in
            (('ssr3',27,12),('ssr3',4,15),('ssr3',7,14),('ssr3',47,13),('ssr2',20,9),('ssr3',30,10),('ssr3',26,11))
        and not row['features'].get('noninstant_attack_definitions', 0)
        and not row['features'].get('nonzero_mod_depth_executed', False))
    if row['features']['track_count'] > capacity and not known_candidate:
        result.update(status='capacity_blocked', track_capacity=capacity)
        return result
    data, _ = archive.sequence(row['index'])
    tracks = trace_sequence(data, analysis_only=True)
    dempajiken = (known_candidate and row['family'] == 'ssr3' and row['index'] == 26
        and len(tracks) == 11 and {t['track'] for t in tracks} == set(range(9)) | {14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    kincho = (known_candidate and row['family'] == 'ssr3' and row['index'] == 30
        and len(tracks) == 10 and {t['track'] for t in tracks} == set(range(8)) | {14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    hokora = (known_candidate and row['family'] == 'ssr2' and row['index'] == 20
        and len(tracks) == 9 and {t['track'] for t in tracks} == set(range(9))
        and all(t.get('termination') == 'loop' for t in tracks))
    change = (known_candidate and row['index'] == 47 and len(tracks) == 13
        and {t['track'] for t in tracks} == set(range(10)) | {13,14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    ajito = (known_candidate and row['index'] == 7 and len(tracks) == 14
        and {t['track'] for t in tracks} == set(range(12)) | {14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    studio = (known_candidate and row['index'] == 4 and len(tracks) == 15
        and {t['track'] for t in tracks} == set(range(13)) | {14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    known_merge = studio or ajito or change or hokora or kincho or dempajiken or (known_candidate and row['index'] == 27 and len(tracks) == 12
        and {t['track'] for t in tracks} == {0,1,2,3,4,5,7,8,9,13,14,15}
        and all(t.get('termination') == 'loop' for t in tracks))
    if row['features']['track_count'] > capacity and not known_merge:
        result.update(status='capacity_blocked', track_capacity=capacity)
        return result
    finite = all(t.get('termination') == 'end' for t in tracks)
    groups = SF3_DEMPAJIKEN_GROUPS if dempajiken else SF3_KINCHO_GROUPS if kincho else SF2_HOKORA_GROUPS if hokora else SF3_CHANGE_GROUPS if change else SF3_AJITO_GROUPS if ajito else SF3_STUDIO_GROUPS if studio else SF3_BOSSMAE_GROUPS if known_merge else [(t['track'],) for t in tracks]
    result['route'] = ('known_sf3_dempajiken_merged_antialias' if dempajiken else
                       'known_sf3_kincho_upward_antialias' if kincho else
                       'known_sf2_hokora_merged_antialias' if hokora else
                       'known_sf3_change_upward_antialias' if change else
                       'known_sf3_ajito_upward_antialias' if ajito else
                       'known_sf3_studio_upward_antialias' if studio else
                       'known_sf3_bossmae_merged_antialias' if known_merge else
                       'finite_singleton_antialias' if finite else 'looping_singleton_antialias')
    modes = [(False, False, result['route'])]
    pack_errors = False
    for envelope, release, route in modes:
        result['route'] = route
        gains = [gain_db]
        for gain in gains:
            attempt = {'gain_db': gain, 'route': route, 'envelope_approximation': envelope,
                       'finite_release_snapshots': release,
                       'conversion_passed': False, 'packing_passed': False}
            result['attempts'].append(attempt)
            try:
                blob, dependency, conversion = convert_merged_song(
                    archive, row['index'], groups, capacity, gain,
                    finite_support=finite, bandlimited_pcm=True, envelope_support=envelope,
                    finite_release_support=release,
                    **({'merged_bandlimited_support': True, 'bandlimited_upward_support': True} if studio or ajito or change or kincho else
                       {'merged_bandlimited_support': True} if known_merge else {}))
                attempt['conversion_passed'] = True
            except (ValueError, AssertionError, IndexError, struct.error) as error:
                attempt['error'] = error_record(error)
                if (not known_merge and not finite and not envelope and isinstance(error, ValueError)
                        and str(error) == 'Non-instant DS attack requires envelope fitting'
                        and not any(mode[0] for mode in modes)):
                    modes.append((True, False, 'looping_singleton_antialias_envelope'))
                if (finite and not release and isinstance(error, ValueError)
                        and str(error) == 'Unsupported merged-conversion effect 0xd3'
                        and not any(mode[1] for mode in modes)):
                    modes.append((False, True, 'finite_singleton_antialias_release'))
                if gain != 0 and 'headroom' in str(error).lower() and 0 not in gains:
                    gains.append(0.0)
                continue
            try:
                output, patch, manifest, *_ = pack_converted_experiment(
                    source, base, profile, raw_sdat, row['index'], row['name'] or f'SSEQ_{row["index"]}',
                    blob, dependency, conversion, EVENTS, pcm_channels)
            except (ValueError, AssertionError, IndexError, struct.error) as error:
                pack_errors = True
                attempt['packing_error'] = error_record(error)
                continue
            attempt['packing_passed'] = True
            result.update(status='packed', gain_db=gain, gain_adjustment_required=gain != gain_db,
                          target_track_count=conversion['track_count'], target_sample_count=len(dependency['samples']),
                          generated_bytes=len(blob), appended_bytes=manifest['appended_bytes'],
                          output_fingerprint=manifest['output_fingerprint'], bps_fingerprint=fingerprint(patch),
                          bps_reconstruction_verified=True,
                          manual_matches_packed_variant=any(r['output_sha256'] == manifest['output_fingerprint']['sha256']
                                                           for r in row['related_manual_records']),
                          bandlimited_pcm=conversion['bandlimited_pcm'],
                          envelope_approximation=conversion.get('envelope_approximation'),
                          finite_release_snapshots=conversion.get('finite_release_snapshots'),
                          finite_song=conversion.get('finite_song'),
                          long_note_loop_carries=conversion.get('long_note_loop_carries', []),
                          note_timing_validation=conversion.get('note_timing_validation', []),
                          voice_context_splits=conversion.get('voice_context_splits', []),
                          prepared_pcm8_bytes=sum(s['pcm8_bytes'] for s in conversion['samples']),
                          pcm8_quantizer_clamped_values=sum(s['resampling']['pcm8_clipped_samples'] for s in conversion['samples']),
                          maximum_source_step=max(s['resampling']['source_pitched_rate_hz'] / 10512 for s in conversion['samples']))
            if known_merge and not (studio or ajito or change or hokora or kincho or dempajiken):
                result['known_merged_antialias'] = {
                    'source_track_count':12, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_BOSSMAE_GROUPS],
                    'scope':'Pinned accepted BOSSMAE grouping and filtering only; existing guards; no group search',
                    'standalone_observations': {
                        'source':'sf3-bossmae-merged-antialias-exe6-v1',
                        'rom_sha256':'dde49b852f1c45e5d988eb45554fe14c029406b9ee976b1a6da1264250813b7c',
                        'observed_note_calls':1514, 'observed_rejections':0,
                        'held_or_starting_preemptions':0,
                        'release_flagged_reuses_with_nonzero_envelope':905,
                        'prepared_pcm8_clamped_values':4763, 'prepared_pcm8_bytes':513763,
                        'scope':'Standalone two-cycle window and prepared storage counts; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if dempajiken:
                result['known_merged_antialias'] = {
                    'source_track_count':11, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_DEMPAJIKEN_GROUPS],
                    'scope':'Pinned accepted DEMPAJIKEN grouping and filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf3-dempajiken-merged-antialias-exe6-v1',
                        'rom_sha256':'5eb54e17c9e4155f975aaab02e8443284f2d49e27336111f42ad7fe39fe03013',
                        'observed_note_calls':999, 'observed_allocations':996, 'observed_rejections':3,
                        'rejected_source_track':14, 'rejected_source_key':64, 'rejected_source_instrument':19,
                        'rejected_note_clocks':[696,2424,4152], 'rejected_identities_match_plain_baseline':True,
                        'held_or_starting_preemptions':3,
                        'held_preemption_clocks':[696,2424,4152],
                        'held_displaced_identities_match_plain_baseline':True,
                        'release_flagged_reuses_with_nonzero_envelope':532,
                        'plain_baseline_release_reuses':522, 'slot_choices_different_from_plain':383,
                        'plain_baseline_observation':'sf3-dempajiken-plain-native-baseline-v1',
                        'prepared_pcm8_clamped_values':5834, 'prepared_pcm8_bytes':680241,
                        'zero_velocity_native_calls':0,
                        'scope':'Standalone two-cycle window and prepared storage; retained original rejection/preemption identities; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if kincho:
                result['known_merged_antialias'] = {
                    'source_track_count':10, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_KINCHO_GROUPS],
                    'scope':'Pinned accepted KINCHO grouping and upward-pitch filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf3-kincho-upward-antialias-exe6-v1',
                        'rom_sha256':'ae6243cff652dc8c028a2ed7d42ebdf38ba001218adec3cbf08231b65260ad01',
                        'observed_note_calls':1194, 'observed_rejections':0,
                        'held_or_starting_preemptions':0,
                        'release_flagged_reuses_with_nonzero_envelope':477,
                        'plain_baseline_release_reuses':476, 'slot_choices_different_from_plain':175,
                        'plain_baseline_observation':'sf3-kincho-plain-native-baseline-v1',
                        'prepared_pcm8_clamped_values':10592, 'prepared_pcm8_bytes':1086559,
                        'zero_velocity_native_calls':0,
                        'scope':'Standalone two-cycle window and prepared storage; fresh plain-ROM native observation; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if hokora:
                result['known_merged_antialias'] = {
                    'source_track_count':9, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF2_HOKORA_GROUPS],
                    'scope':'Pinned accepted SF2 HOKORA grouping and filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf2-hokora-merged-antialias-exe6-v1',
                        'rom_sha256':'923ead50245fcd3fc0eb18d6689abbac0849be57856a1adbab57bc7f3802b022',
                        'observed_note_calls':1555, 'observed_rejections':0,
                        'held_or_starting_preemptions':0,
                        'release_flagged_reuses_with_nonzero_envelope':384,
                        'plain_baseline_release_reuses':385, 'slot_choices_different_from_plain':354,
                        'plain_baseline_observation':'sf2-hokora-plain-native-baseline-v1',
                        'prepared_pcm8_clamped_values':1197, 'prepared_pcm8_bytes':748395,
                        'zero_velocity_native_calls':0,
                        'scope':'Standalone two-cycle window and prepared storage; fresh plain-ROM native observation; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if change:
                result['known_merged_antialias'] = {
                    'source_track_count':13, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_CHANGE_GROUPS],
                    'scope':'Pinned accepted CHANGE grouping and upward-pitch filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf3-change-upward-antialias-exe6-v1',
                        'rom_sha256':'3fe1e8918677ceafe0f5f6b9b4704c6fe8c42dc416e1a7634b666cb3e31b0774',
                        'observed_note_calls':1339, 'observed_rejections':0,
                        'held_or_starting_preemptions':4,
                        'held_preemption_clocks':[352,360,372,376],
                        'held_displaced_identities_match_plain_baseline':True,
                        'release_flagged_reuses_with_nonzero_envelope':188,
                        'plain_baseline_release_reuses':183, 'slot_choices_different_from_plain':159,
                        'prepared_pcm8_clamped_values':1043, 'prepared_pcm8_bytes':646861,
                        'intro_only_source_track':9, 'intro_only_native_note_calls':6,
                        'intro_only_loop_native_note_calls':0, 'zero_velocity_native_calls':0,
                        'scope':'Standalone two-cycle window and prepared storage; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if ajito:
                result['known_merged_antialias'] = {
                    'source_track_count':14, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_AJITO_GROUPS],
                    'scope':'Pinned accepted AJITO grouping and upward-pitch filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf3-ajito-upward-antialias-exe6-v1',
                        'rom_sha256':'1b535b22c63f0da416d55355c63f12c0af3172adab5c68f786119a71312d341c',
                        'observed_note_calls':3964, 'observed_rejections':0,
                        'held_or_starting_preemptions':14,
                        'held_preemption_clocks':[1108,1113,5064,5160,5232,5256,6580,6585,10536,10632,10704,10728,12052,12057],
                        'held_displaced_identities_match_plain_baseline':True,
                        'release_flagged_reuses_with_nonzero_envelope':1551,
                        'plain_baseline_release_reuses':1544, 'slot_choices_different_from_plain':718,
                        'prepared_pcm8_clamped_values':9275, 'prepared_pcm8_bytes':1969559,
                        'zero_velocity_native_calls':0,
                        'scope':'Standalone two-cycle window and prepared storage; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if studio:
                result['known_merged_antialias'] = {
                    'source_track_count':15, 'target_track_count':8,
                    'track_groups':[list(g) for g in SF3_STUDIO_GROUPS],
                    'scope':'Pinned accepted STUDIO grouping and upward-pitch filtering only; existing guards; no search',
                    'standalone_observations': {
                        'source':'sf3-studio-upward-antialias-exe6-v1',
                        'rom_sha256':'02a180120dfd02e4e4e6f16ab6ae1bd38c02c1b72f44a7ed1c607aa8776a82d4',
                        'observed_note_calls':5202, 'observed_rejections':0,
                        'held_or_starting_preemptions':0,
                        'release_flagged_reuses_with_nonzero_envelope':2866,
                        'plain_baseline_release_reuses':2863, 'slot_choices_different_from_plain':115,
                        'prepared_pcm8_clamped_values':1097, 'prepared_pcm8_bytes':903042,
                        'zero_velocity_source_mappings':4, 'unpacked_zero_velocity_source_mappings':4,
                        'zero_velocity_native_calls':6, 'zero_mappings_added_by_filtering':0,
                        'scope':'Standalone two-cycle window and prepared storage; not an audible-error bound',
                        'batch_native_remeasured':False}}
            if studio or ajito or change or kincho:
                result['upward_pitch_preparation'] = {
                    'bound_method':conversion['bandlimited_pcm']['upward_bound_method'],
                    'shift_semitone_counts':dict(Counter(str(s['resampling']['preparation_key']-s['source_key']) for s in conversion['samples'])),
                    'maximum_nominal_cutoff_fraction_of_mixer_nyquist':max(s['resampling']['nominal_cutoff_at_bound_fraction_of_mixer_nyquist'] for s in conversion['samples']),
                    'max_preparation_shift_semitones':12,
                    'scope':'Conversion-derived nominal FIR cutoff with loop/tuning rounding; not a brick-wall or zero-aliasing bound'}
            if row['status'].startswith('packed_'):
                result['appended_bytes_delta_vs_primary'] = result['appended_bytes'] - row['appended_bytes']
            return result
    result['status'] = ('packing_blocked' if pack_errors else 'converter_model_blocked'
                        if any(a.get('error', {}).get('model_assertion') for a in result['attempts']) else 'conversion_blocked')
    return result


def summarize_antialias(rows):
    scanned = [r for r in rows if 'antialias' in r]
    packed = [r for r in scanned if r['antialias']['status'] == 'packed']
    return {'scanned_slots': len(scanned), 'statuses': dict(Counter(r['antialias']['status'] for r in scanned)),
            'packed_variants': len(packed),
            'packed_known_merged_variants': sum(bool(r['antialias'].get('known_merged_antialias')) for r in packed),
            'packed_upward_preparation_variants': sum(bool(r['antialias'].get('upward_pitch_preparation')) for r in packed),
            'packed_by_route': dict(Counter(r['antialias']['route'] for r in packed)),
            'packed_finite_release_variants': sum(bool(r['antialias'].get('finite_release_snapshots')) for r in packed),
            'packed_finite_release_exact_manual_matches': sum(bool(r['antialias'].get('finite_release_snapshots'))
                and r['antialias']['manual_matches_packed_variant'] for r in packed),
            'packed_fitted_envelope_variants': sum(bool(r['antialias'].get('envelope_approximation')) for r in packed),
            'packed_fitted_envelope_exact_manual_matches': sum(bool(r['antialias'].get('envelope_approximation'))
                and r['antialias']['manual_matches_packed_variant'] for r in packed),
            'packed_exact_manual_matches': sum(r['antialias']['manual_matches_packed_variant'] for r in packed),
            'packed_without_exact_manual_match': sum(not r['antialias']['manual_matches_packed_variant'] for r in packed),
            'primary_and_antialias_packed': sum(r['status'].startswith('packed_') for r in packed),
            'antialias_only_packed': sum(not r['status'].startswith('packed_') for r in packed),
            'unique_sequences_any_exact_manual_match': sum(r['manual_matches_packed_variant'] or
                r.get('antialias', {}).get('manual_matches_packed_variant', False) for r in rows),
            'by_family': {family: dict(Counter(r['antialias']['status'] for r in scanned if r['family'] == family))
                          for family in ('ssr1', 'ssr2', 'ssr3')}}


def verified_sources(directory):
    results = []
    for family in ('ssr1', 'ssr2', 'ssr3'):
        spec = SOURCE_ARCHIVES[family]
        variants, representative = [], None
        for key in sorted(k for k in SOURCES.values() if k.startswith(family)):
            path = directory / (key + '.nds')
            if not path.exists():
                continue
            raw = path.read_bytes()
            fp = fingerprint(raw)
            if SOURCES.get(fp['sha256']) != key:
                raise ValueError(f'Unverified source revision or filename mismatch: {path}')
            sdat = nds_sdat(raw, spec['file_id'])
            if fingerprint(sdat)['sha256'] != spec['sha256']:
                raise ValueError(f'SDAT fingerprint mismatch: {path}')
            if representative is None:
                representative = key, path, sdat
            elif sdat != representative[2]:
                raise ValueError(f'Unexpected archive differences within {family}')
            variants.append({'profile': key, 'path': str(path.resolve()), 'rom_fingerprint': fp})
        if representative is None:
            raise ValueError(f'At least one verified {family} original is required')
        results.append({'family': family, 'profile': representative[0], 'path': representative[1],
                        'sdat': representative[2], 'variants': variants})
    return results


def manual_evidence(root):
    records = []
    for path in sorted(root.glob('*/manual-testing.json')):
        value = json.loads(path.read_text())
        if value.get('status') != 'user_reported_pass':
            continue
        manifest = json.loads(path.with_name('build.json').read_text())
        expected = value.get('expected_build_fingerprint', manifest['output_fingerprint'])
        if fingerprint(path.with_name('unified.gba').read_bytes()) != expected:
            raise ValueError(f'Manual evidence artifact differs: {path}')
        if expected != manifest['output_fingerprint']:
            raise ValueError(f'Manual evidence/manifest fingerprints differ: {path}')
        source = manifest['nds_conversion']
        records.append({'family': source['source_profile'][:4], 'sequence_index': source['sequence_index'],
                        'output_sha256': expected['sha256'], 'record': str(path.resolve()),
                        'bandlimited_pcm': bool(source.get('bandlimited_pcm')),
                        'configuration': path.parent.name,
                        'scope': 'user-reported tests for this artifact; separate from batch audit'})
    return records


def summarize(rows):
    blocked = [r for r in rows if r['status'] not in ('empty_slot', 'silent_sequence')
               and not r['status'].startswith('packed_')]
    return {'slots': len(rows), 'statuses': dict(Counter(r['status'] for r in rows)),
            'nonempty_nonsilent_candidates': sum(r['status'] not in ('empty_slot', 'silent_sequence') for r in rows),
            'completed_execution_traces_with_notes': sum(bool(r.get('features', {}).get('executed_note_events_in_trace')) for r in rows),
            'packed': sum(r['status'].startswith('packed_') for r in rows),
            'packed_exact_manual_matches': sum(r['manual_matches_packed_variant'] for r in rows),
            'packed_mixed_variants': sum(bool(r.get('mixed_loop_song')) for r in rows),
            'packed_mixed_exact_manual_matches': sum(bool(r.get('mixed_loop_song')) and r['manual_matches_packed_variant'] for r in rows),
            'packed_minimum_depth_lfo_variants': sum(bool(r.get('native_pitch_lfo', {}).get('minimum_depth_quantization')) for r in rows),
            'blocking_features_nonexclusive': {
                'noninstant_attack_definitions': sum(bool(r.get('features', {}).get('noninstant_attack_definitions')) for r in blocked),
                'envelope_override_controls': sum(bool(r.get('features', {}).get('envelope_override_controls')) for r in blocked),
                'long_gates': sum(bool(r.get('features', {}).get('long_notes')) for r in blocked),
                'nonzero_pitch_modulation_delay': sum(any(c['delay'] for c in r.get('features', {}).get('modulation_configs_at_note_on', [])) for r in blocked)},
            'antialias': summarize_antialias(rows),
            'by_family': {family: dict(Counter(r['status'] for r in rows if r['family'] == family))
                          for family in ('ssr1', 'ssr2', 'ssr3')}}


def write_reports(directory, report):
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    summary = ['# NDS → EXE6 兼容性扫描', '',
               '扫描仅覆盖 SSEQ。通过转换与 ROM 打包不等于人工试听通过；本轮没有执行新曲目的游戏运行测试。', '',
               '| 游戏 | 槽位 | 非空、非无音符候选 | 常规通过 | 颤音近似 | 包络近似 | 包络＋颤音 | 延迟颤音 | 包络＋延迟颤音 | 实时深度颤音 | 包络＋实时深度颤音 | 启闭颤音 | 包络＋启闭颤音 | 非循环常规 | 混合常规 | 混合延迟颤音 | 混合弱颤音量化 | 其余受阻 |',
               '| ' + ' | '.join(['---'] + ['---:'] * 17) + ' |']
    for family in ('ssr1', 'ssr2', 'ssr3'):
        values = report['summary']['by_family'][family]
        slots = sum(values.values())
        candidates = slots - values.get('empty_slot', 0) - values.get('silent_sequence', 0)
        standard = values.get('packed_standard', 0) + values.get('packed_known_nine_track_merge', 0) + values.get('packed_known_ten_track_merge', 0) + values.get('packed_known_eleven_track_merge', 0) + values.get('packed_known_twelve_track_merge', 0) + values.get('packed_known_thirteen_track_merge', 0) + values.get('packed_known_fourteen_track_merge', 0) + values.get('packed_known_fifteen_track_merge', 0)
        lfo = values.get('packed_lfo_approximation', 0) + values.get('packed_variable_tempo_lfo_approximation', 0)
        finite = values.get('packed_finite_standard', 0) + values.get('packed_finite_release_snapshots', 0)
        envelope = values.get('packed_envelope_approximation', 0)
        combined = values.get('packed_envelope_lfo_approximation', 0) + values.get('packed_variable_late_fitted_lfo_approximation', 0)
        delayed = values.get('packed_delayed_lfo_approximation', 0)
        envelope_delayed = values.get('packed_envelope_delayed_lfo_approximation', 0)
        live_depth = sum(values.get(k, 0) for k in ('packed_live_depth_lfo_approximation',
            'packed_live_depth_minimum_lfo_approximation', 'packed_late_live_depth_lfo_approximation'))
        envelope_live_depth = values.get('packed_envelope_live_depth_lfo_approximation', 0) + values.get('packed_envelope_live_depth_minimum_lfo_approximation', 0)
        live_toggle = values.get('packed_live_toggle_lfo_approximation', 0)
        envelope_live_toggle = values.get('packed_envelope_live_toggle_lfo_approximation', 0)
        mixed = values.get('packed_mixed_standard', 0)
        mixed_delay = values.get('packed_mixed_delayed_lfo_approximation', 0)
        mixed_minimum = sum(values.get(k, 0) for k in (
            'packed_mixed_min_depth_lfo_approximation', 'packed_mixed_live_depth_minimum_lfo_approximation',
            'packed_mixed_envelope_live_depth_minimum_lfo_approximation'))
        summary.append(f'| {family} | {slots} | {candidates} | {standard} | {lfo} | {envelope} | {combined} | '
                       f'{delayed} | {envelope_delayed} | {live_depth} | {envelope_live_depth} | {live_toggle} | {envelope_live_toggle} | {finite} | '
                       f'{mixed} | {mixed_delay} | {mixed_minimum} | '
                       f'{candidates - standard - finite - lfo - envelope - combined - delayed - envelope_delayed - live_depth - envelope_live_depth - live_toggle - envelope_live_toggle - mixed - mixed_delay - mixed_minimum} |')
    summary.extend(['', f'与已有人工验收 ROM 字节一致的扫描构建：{report["summary"]["packed_exact_manual_matches"]} 个。', '',
                    '具体曲目、每条转换路径及失败原因见 report.csv、report.json 或 index.html。', '',
                    '向上弯音预滤波仅开放已验收 SF3 STUDIO 十五轨及 AJITO 十四轨固定分组；共享 wave/root/source-key 取各源轨最大正向有效弯音上界，保留音符与控制。标称截止频率不是零混叠或听感误差保证。',
                    '合轨抗混叠开放已验收 SF3 STUDIO 十五轨及 SF3 BOSSMAE 十二轨固定分组，保留既有分组、音高和滤波校验；原生声道复用与采样限幅记录引用独立实验，扫描未新增试听或游戏验证。',
                    '十五轨固定分组仅开放已验收的 SF3 STUDIO，合并源轨 4/5/6/7/8/12/14/15；保持既有校验和固定音量比例量化。独立原生实验 5202 次音符均获分配、无持续／起音抢占，2863 次收音复用；4 个极弱映射在未合轨对照亦为零，扫描未重新观测或试听。常规通过列包含该独立标记子路径。',
                    '十四轨固定分组仅开放已验收的 SF3 AJITO，合并源轨 0/4/6/7/8/11/14；保持控制、长音和转换校验，使用既有固定音量比例量化。独立原生实验记录 14 次持续／起音声道抢占和 1544 次收音声道复用，扫描没有重新观测或试听。常规通过列包含该独立标记子路径。',
                    '十三轨固定分组仅开放已验收的 SF3 CHANGE，合并源轨 4/6/7/9/14/15；保持控制、长音和转换校验，使用既有固定音量比例映射及量化。独立原生实验记录前奏 4 次持续／起音声道抢占及 183 次收音声道复用，扫描没有重新观测或试听。常规通过列包含该独立标记子路径。',
                    '十二轨固定分组仅开放已验收的 SF3 BOSSMAE，合并源轨 0/3/4、5/7 和 13/15；保持控制、声像和转换校验。独立原生实验记录 1514 次音符均获分配、无持续／起音声道被抢占，905 次收音声道复用仍可能缩短尾音；扫描没有重新观测或试听。常规通过列包含该独立标记子路径。',
                    '十一轨固定分组仅开放已验收的 SF3 DEMPAJIKEN，合并源轨 2/4/6 和 5/8；保留控制、声像、长音停音校验。独立原生实验记录十声部预算下每轮一个伴奏音符未获分配，用户报告未听出；扫描没有重新测量分配或执行试听。常规通过列包含该独立标记子路径。',
                    '十轨固定分组仅开放已验收的 SF3 KINCHO，合并源轨 2/4/6；保留既有共享控制和逐音符声像校验，不进行分组搜索，不启用拟合或颤音。常规通过列包含该独立标记子路径。',
                    '九轨固定分组仅开放已验证的 SF2 HOKORA，合并源轨 0/4；仍执行既有共享控制、固定音量、声像和转换校验，不进行自动分组搜索或放宽渐入／颤音限制。常规通过列包含该独立标记子路径。',
                    '常规路径仍使用既有 PCM8、包络和速度量化近似；颤音近似还有共享相位和波形差异。',
                    '包络路径按音符开始时的 ADSR 快照生成乐器；渐入起音拟合有明确误差上限。组合路径同时包含两类近似。',
                    '固定延迟路径接受首次音符之前或同一时刻完成初始化、此后参数固定的延迟颤音；共享相位和延迟会受同轨新音符重置影响。',
                    '实时深度路径仅允许启用后的正深度变化，速度、类型、范围与延迟仍须固定；该基础路径仍拒绝关闭颤音、后期启用与其他参数变化。',
                    '循环独立轨道的实时深度路径明确失败于原生参数表示时，可在其余旧路径之后尝试弱颤音量化，包络拟合仍须单独启用。摘要的实时深度两列包含这些独立标记的子路径，不重复计数；MOD=1 的全相位 10 音分和独立一秒 RMS 5 音分上限只约束弱深度量化。',
                    '混合轨道明确失败于固定颤音参数且有正深度变化时，可另行尝试实时深度与弱深度量化组合；包络拟合单独启用，共同入口最多后移一个完整周期，有限轨道仍只播放一次。混合弱量化列包含这两个独立标记的子路径。',
                    '实时深度路径明确失败于后期首次启用时，可在旧路径之后重试独立的后期启用模式；仅限全部轨道循环、无需包络拟合，仍拒绝弱深度量化、滤波、混合轨道与关闭颤音。恢复非零 LFOS 保留共享相位和计数；摘要的实时深度列包含此独立标记的子路径。',
                    '原生颤音路径明确失败于固定速度要求时，可在旧路径之后重试独立的变速补偿；只接受独立循环轨道、固定零延迟音高颤音且无需包络拟合，主控轨不启用颤音。正 LFOS 更新保留共享相位与计数，音符按当时速度初始化；最多八档速度和 128 次展开后的实际变化。颤音近似列包含此独立标记的子路径。',
                    '包络颤音路径明确失败于固定速度要求且全部轨道循环时，可在旧路径后另行尝试变速、后期首次启用与渐入拟合组合；首次启用前允许零深度音符，启用后正深度和其余参数固定。仍排除启闭、活动延迟、弱深度量化、滤波及混合／有限轨道，拟合和变速上限不放宽。包络＋颤音列包含该独立标记子路径。',
                    '启闭路径允许深度零与单个固定正深度之间切换，其余参数固定。GBA 关闭时清零共享相位，DS 保留各声道相位，仍有近似差异。所有分类互斥，组合路径不重复计数。',
                    '长音跨循环仅接受入口与出口匹配的延续区间，不在跳转处重新起音；独立解码继续追踪窗口末尾音符的停音。扫描未执行原生全循环播放。',
                    '不同原始音高共用同一乐器别名时，使用独立音色表项消除冲突；优先复用兼容音色表，仍限制在 128 个乐器表项内。',
                    '非循环路径仅接受全部轨道自然结束、固定速度的独立轨道；长音先显式停音，再按各轨原定时间结束。D3 失败后可尝试首音之前初始化的收音快照，拒绝音符之后更新、其他 ADSR 覆盖及非瞬时起音。仍拒绝主动颤音、渐强包络拟合及结束后仍未完结的音符。',
                    '原有混合路径在旧路径失败后尝试，要求固定速度、独立轨道、同时含一次性与循环轨道；一次性轨道在原始共享循环入口之前结束且音符门限已关闭。公共周期最多 16384 tick，每轨最多展开 8 倍；该路径不组合滤波、起音拟合或收音覆盖。另行标记的混合实时深度扩展遵循上文的后移入口和显式拟合策略。',
                    '混合固定延迟颤音仅在明确的原生参数表示失败后重试弱深度量化：非零深度映射至 MOD=1，保留源控制，并要求全相位音高差不超过 10 音分、独立一秒 RMS 不超过 5 音分。模型失败与其他错误不会触发此重试。'])
    aa = report['summary'].get('antialias', {})
    if aa.get('scanned_slots'):
        summary.extend(['', '## 独立抗混叠版本', '',
                        '以下是同一曲目的额外版本，不替换主路径，也不重复计为新增曲目。通过打包不代表音质改善或实战通过。', '',
                        '| 游戏 | 扫描槽位 | 抗混叠打包通过 | 精确匹配已验收 ROM | 通过但待试听 | 受阻候选 |',
                        '| --- | ---: | ---: | ---: | ---: | ---: |'])
        for family in ('ssr1', 'ssr2', 'ssr3'):
            values = aa['by_family'][family]
            packed = values.get('packed', 0)
            matches = sum(r.get('antialias', {}).get('manual_matches_packed_variant', False)
                          for r in report['rows'] if r['family'] == family)
            blocked = sum(values.values()) - packed - values.get('empty_slot', 0) - values.get('silent_sequence', 0)
            summary.append(f'| {family} | {sum(values.values())} | {packed} | {matches} | {packed - matches} | {blocked} |')
        summary.extend(['', f'抗混叠版本通过 {aa["packed_variants"]} 个；其中 {aa["packed_exact_manual_matches"]} 个与已验收版本精确匹配。',
                        f'仅抗混叠版本通过、主路径未通过的曲目：{aa["antialias_only_packed"]} 首。',
                        f'其中渐入组合 {aa.get("packed_fitted_envelope_variants", 0)} 个，精确匹配已验收 {aa.get("packed_fitted_envelope_exact_manual_matches", 0)} 个。',
                        f'其中有限收音快照 {aa.get("packed_finite_release_variants", 0)} 个，精确匹配已验收 {aa.get("packed_finite_release_exact_manual_matches", 0)} 个。',
                        '有限短曲明确失败于 D3 时，记录原失败并尝试首音之前初始化的收音快照，不启用起音拟合。',
                        '只接受独立轨道，支持有限短曲和循环曲；循环曲明确需要非瞬时起音拟合时，记录原失败并尝试渐入组合。有限曲目不启用拟合包络，仍拒绝上行弯音、移调、调制、滑音与主动颤音。',
                        '保持 10,512 Hz 混音；离线倍率 1/16–32，单采样最多 1,000,000 点、整曲 PCM 最多 4,000,000 字节。',
                        '音量余量不足时尝试 0 dB，并保留原失败记录；采样削顶计数不等于最终混音削顶。',
                        '人工记录只按同源曲目和同一 ROM 指纹匹配；同曲目的旧未滤波版本通过，不代表新抗混叠版本通过。'])
    (directory / 'summary.md').write_text('\n'.join(summary) + '\n')
    fields = ['id', 'family', 'index', 'name', 'status', 'source_tracks', 'target_tracks', 'samples',
              'route', 'gain_db', 'appended_bytes', 'native_pitch_lfo_approximation',
              'envelope_approximation', 'fixed_delay_approximation', 'live_depth_approximation', 'live_toggle_approximation',
              'source_depth_changes', 'source_depth_toggles', 'modulation_initializations', 'delay_mappings',
              'attack_fits', 'long_note_loop_carries', 'voice_context_splits', 'finite_song', 'finite_track_end_ticks',
              'finite_release_snapshots', 'finite_release_overrides', 'manual_matches_packed_variant', 'errors',
              'mixed_loop_song', 'mixed_finite_track_end_ticks', 'mixed_source_loop_periods',
              'mixed_common_loop_start_ticks', 'mixed_common_loop_ticks', 'minimum_depth_lfo_quantization',
              'minimum_depth_lfo_policy', 'mixed_live_depth_extension', 'late_depth_activation', 'variable_tempo_approximation', 'variable_late_fitted_extension', 'known_nine_track_merge', 'known_ten_track_merge', 'known_eleven_track_merge', 'known_twelve_track_merge', 'known_thirteen_track_merge', 'known_fourteen_track_merge', 'known_fifteen_track_merge',
              'antialias_status', 'antialias_route', 'antialias_gain_db', 'antialias_samples',
              'antialias_pcm8_bytes', 'antialias_appended_bytes_delta', 'antialias_manual_exact_match',
              'antialias_upward_pitch_preparation', 'antialias_known_merged', 'antialias_envelope_approximation', 'antialias_attack_fits', 'antialias_finite_release_snapshots',
              'antialias_finite_release_overrides', 'antialias_errors']
    with (directory / 'report.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in report['rows']:
            errors = [a.get('error') or a.get('packing_error') for a in row['attempts']]
            writer.writerow({'id': row['id'], 'family': row['family'], 'index': row['index'], 'name': row['name'],
                             'status': row['status'], 'source_tracks': row.get('features', {}).get('track_count'),
                             'target_tracks': row.get('target_track_count'), 'samples': row.get('target_sample_count'),
                             'route': row.get('route'), 'gain_db': row.get('gain_db'), 'appended_bytes': row.get('appended_bytes'),
                             'native_pitch_lfo_approximation': row.get('approximations', {}).get('native_pitch_lfo', False),
                             'envelope_approximation': row.get('approximations', {}).get('envelope', False),
                             'fixed_delay_approximation': row.get('approximations', {}).get('fixed_delay', False),
                             'live_depth_approximation': row.get('approximations', {}).get('live_depth', False),
                             'live_toggle_approximation': row.get('approximations', {}).get('live_toggle', False),
                             'source_depth_toggles': json.dumps(row.get('native_pitch_lfo', {}).get('live_toggle_approximation', {}).get('source_depth_toggles', [])),
                             'modulation_initializations': json.dumps(row.get('native_pitch_lfo', {}).get('delay_approximation', {}).get('initializations', [])),
                             'source_depth_changes': json.dumps(row.get('native_pitch_lfo', {}).get('live_depth_approximation', {}).get('source_depth_changes', [])),
                             'delay_mappings': json.dumps([c['delay_mapping'] for c in row.get('native_pitch_lfo', {}).get('configs', [])
                                                          if 'delay_mapping' in c]),
                             'attack_fits': json.dumps(row.get('envelope_approximation', {}).get('attack_fits', [])),
                             'long_note_loop_carries': json.dumps(row.get('long_note_loop_carries', [])),
                             'voice_context_splits': json.dumps(row.get('voice_context_splits', [])),
                             'finite_release_snapshots': bool(row.get('finite_release_snapshots')),
                             'finite_release_overrides': json.dumps((row.get('finite_release_snapshots') or {}).get('source_overrides', [])),
                             'antialias_finite_release_snapshots': bool(row.get('antialias', {}).get('finite_release_snapshots')),
                             'antialias_finite_release_overrides': json.dumps((row.get('antialias', {}).get('finite_release_snapshots') or {}).get('source_overrides', [])),
                             'finite_song': bool(row.get('finite_song')),
                             'finite_track_end_ticks': json.dumps((row.get('finite_song') or {}).get('track_end_ticks', {})),
                             'mixed_loop_song': bool(row.get('mixed_loop_song')),
                             'mixed_finite_track_end_ticks': json.dumps(row.get('mixed_loop_song', {}).get('finite_track_end_ticks', {})),
                             'mixed_source_loop_periods': json.dumps(row.get('mixed_loop_song', {}).get('source_loop_periods', {})),
                             'mixed_common_loop_start_ticks': row.get('mixed_loop_song', {}).get('common_loop_start_ticks'),
                             'mixed_common_loop_ticks': row.get('mixed_loop_song', {}).get('common_loop_ticks'),
                             'minimum_depth_lfo_quantization': bool(row.get('native_pitch_lfo', {}).get('minimum_depth_quantization')),
                             'known_fifteen_track_merge': json.dumps(row.get('known_fifteen_track_merge', {})),
                             'known_fourteen_track_merge': json.dumps(row.get('known_fourteen_track_merge', {})),
                             'known_thirteen_track_merge': json.dumps(row.get('known_thirteen_track_merge', {})),
                             'known_twelve_track_merge': json.dumps(row.get('known_twelve_track_merge', {})),
                             'known_eleven_track_merge': json.dumps(row.get('known_eleven_track_merge', {})),
                             'known_ten_track_merge': json.dumps(row.get('known_ten_track_merge', {})),
                             'known_nine_track_merge': json.dumps(row.get('known_nine_track_merge', {})),
                             'variable_late_fitted_extension': json.dumps(row.get('native_pitch_lfo', {}).get('variable_late_fitted_extension', {})),
                             'variable_tempo_approximation': json.dumps(row.get('native_pitch_lfo', {}).get('variable_tempo_approximation', {})),
                             'late_depth_activation': json.dumps(row.get('native_pitch_lfo', {}).get('late_depth_activation', {})),
                             'mixed_live_depth_extension': json.dumps(row.get('mixed_live_depth_extension', {})),
                             'minimum_depth_lfo_policy': json.dumps(row.get('native_pitch_lfo', {}).get('minimum_depth_quantization', {})),
                             'manual_matches_packed_variant': row['manual_matches_packed_variant'],
                             'errors': json.dumps(row.get('analysis_error') or errors, ensure_ascii=False),
                             'antialias_upward_pitch_preparation': json.dumps(row.get('antialias', {}).get('upward_pitch_preparation', {})),
                             'antialias_known_merged': json.dumps(row.get('antialias', {}).get('known_merged_antialias', {})),
                             'antialias_envelope_approximation': bool(row.get('antialias', {}).get('envelope_approximation')),
                             'antialias_attack_fits': json.dumps((row.get('antialias', {}).get('envelope_approximation') or {}).get('attack_fits', [])),
                             'antialias_status': row.get('antialias', {}).get('status'),
                             'antialias_route': row.get('antialias', {}).get('route'),
                             'antialias_gain_db': row.get('antialias', {}).get('gain_db'),
                             'antialias_samples': row.get('antialias', {}).get('target_sample_count'),
                             'antialias_pcm8_bytes': row.get('antialias', {}).get('prepared_pcm8_bytes'),
                             'antialias_appended_bytes_delta': row.get('antialias', {}).get('appended_bytes_delta_vs_primary'),
                             'antialias_manual_exact_match': row.get('antialias', {}).get('manual_matches_packed_variant', False),
                             'antialias_errors': json.dumps([a.get('error') or a.get('packing_error') for a in
                                                           row.get('antialias', {}).get('attempts', [])], ensure_ascii=False)})
    payload = json.dumps({'report': report, 'labels': STATUS_LABELS, 'antialiasLabels': ANTIALIAS_LABELS}, ensure_ascii=False).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NDS → EXE6 曲目兼容性扫描</title><style>body{font:16px/1.6 system-ui;margin:30px;background:#111923;color:#edf2f7}input,select{font:inherit;padding:6px;margin:5px}table{border-collapse:collapse;width:100%}th,td{padding:8px;border-bottom:1px solid #354458;text-align:left;vertical-align:top}summary{cursor:pointer}pre{white-space:pre-wrap;max-width:65vw;font-size:13px}.ok{color:#89dfa4}.blocked{color:#e8c792}</style>
<h1>NDS → EXE6 曲目兼容性扫描</h1><p>非循环路径接受固定速度、全部轨道自然结束的独立轨道，长音显式停音后按各轨原定时间结束。常规、颤音、包络、固定延迟颤音、实时深度颤音、启闭颤音及其组合路径成功后，均通过共享资源打包和 BPS 回建。常规路径同样使用已有采样和包络近似。详情保留起音拟合误差与延迟映射；固定延迟路径要求首次音符之前或同一时刻完成初始化且此后参数固定。实时深度路径额外允许正深度变化，其余参数固定，MOD 更新保留共享相位和延迟计数，同轨新音符仍会重置相位。启闭路径允许深度零与单个固定正深度之间切换，其余参数固定；GBA 关闭时清零共享相位，而 DS 保留各声道相位。自动通过不等于实际试听或战斗验证通过；空槽、无音符序列不计为可播放曲目。扫描仅覆盖 SSEQ，SSAR 与 STRM 不在转换范围内。</p>
<p>混合路径保留一次性轨道 END，并对循环周期作有限展开；弱颤音量化有独立的音高误差上限；混合实时深度扩展另行明确启用起音拟合，入口最多后移一个完整周期。仍拒绝抗混叠和收音覆盖。详情保留实际周期和近似参数。</p><p>全部轨道循环的实时深度路径也可单独重试弱颤音量化；渐入拟合是明确的附加模式。弱深度误差上限不代表整曲颤音等同 DS。</p><p>抗混叠结果是额外的独立版本，保留原有主路径；主路径通过和人工验收不会自动转移。扫描没有批量试听或游戏验证。</p><p id="counts"></p><label>游戏<select id="game"><option value="">全部</option><option>ssr1</option><option>ssr2</option><option>ssr3</option></select></label><label>结果<select id="status"><option value="">全部</option></select></label><label>结构／颤音<select id="structure"><option value="">全部</option><option value="fifteen">十五轨固定分组</option><option value="fourteen">十四轨固定分组</option><option value="thirteen">十三轨固定分组</option><option value="twelve">十二轨固定分组</option><option value="eleven">十一轨固定分组</option><option value="ten">已验证十轨分组通过</option><option value="nine">已验证九轨分组通过</option><option value="variable_fitted">变速＋渐入组合通过</option><option value="variable">变速颤音补偿通过</option><option value="late">后期启用颤音通过</option><option value="mixed">混合路径通过</option><option value="minimum">弱颤音量化通过</option><option value="accepted">混合路径精确匹配已验收</option></select></label><label>抗混叠<select id="antialias"><option value="">全部</option><option value="packed">打包通过</option><option value="accepted">精确匹配已验收</option><option value="untested">打包通过、待试听</option><option value="blocked">受阻候选</option><option value="upward">向上弯音预滤波通过</option><option value="merged">合轨抗混叠通过</option><option value="envelope">渐入组合通过</option><option value="release">有限收音快照通过</option></select></label><input id="search" placeholder="查找曲名或编号"><span id="shown"></span>
<table><thead><tr><th>曲目</th><th>轨数</th><th>结果</th><th>路径／增益</th><th>主路径人工记录</th><th>抗混叠版本</th><th>抗混叠人工记录</th><th>详情</th></tr></thead><tbody id="rows"></tbody></table>
<script type="application/json" id="data">PAYLOAD</script><script>
const {report,labels,antialiasLabels}=JSON.parse(document.querySelector('#data').textContent);const get=id=>document.getElementById(id);
get('counts').textContent=`${report.summary.slots} 个槽位，${report.summary.packed} 首通过打包，${report.summary.packed_exact_manual_matches} 首与已有人工验收版本字节匹配；混合路径 ${report.summary.packed_mixed_variants??0} 首；弱颤音量化 ${report.summary.packed_minimum_depth_lfo_variants??0} 首。抗混叠另有 ${report.summary.antialias?.packed_variants??0} 个打包通过版本，其中 ${report.summary.antialias?.packed_exact_manual_matches??0} 个精确匹配已验收版本；渐入组合 ${report.summary.antialias?.packed_fitted_envelope_variants??0} 个，有限收音快照 ${report.summary.antialias?.packed_finite_release_variants??0} 个。`;
Object.entries(labels).forEach(([key,label])=>{const o=document.createElement('option');o.value=key;o.textContent=label;get('status').append(o)});
function aaMatch(r){const a=r.antialias,k=get('antialias').value;if(!k)return true;if(!a)return false;if(k==='upward')return a.status==='packed'&&Boolean(a.upward_pitch_preparation);if(k==='merged')return a.status==='packed'&&Boolean(a.known_merged_antialias);if(k==='release')return a.status==='packed'&&Boolean(a.finite_release_snapshots);if(k==='envelope')return a.status==='packed'&&Boolean(a.envelope_approximation);if(k==='accepted')return a.status==='packed'&&a.manual_matches_packed_variant;if(k==='untested')return a.status==='packed'&&!a.manual_matches_packed_variant;if(k==='blocked')return !['packed','empty_slot','silent_sequence'].includes(a.status);return a.status===k}
function structureMatch(r){const k=get('structure').value;if(!k)return true;if(!r.status.startsWith('packed_'))return false;if(k==='fifteen')return Boolean(r.known_fifteen_track_merge);if(k==='fourteen')return Boolean(r.known_fourteen_track_merge);if(k==='thirteen')return Boolean(r.known_thirteen_track_merge);if(k==='twelve')return Boolean(r.known_twelve_track_merge);if(k==='eleven')return Boolean(r.known_eleven_track_merge);if(k==='ten')return Boolean(r.known_ten_track_merge);if(k==='nine')return Boolean(r.known_nine_track_merge);if(k==='variable_fitted')return Boolean(r.native_pitch_lfo?.variable_late_fitted_extension?.enabled);if(k==='variable')return Boolean(r.native_pitch_lfo?.variable_tempo_approximation);if(k==='late')return Boolean(r.native_pitch_lfo?.late_depth_activation?.enabled);if(k==='minimum')return Boolean(r.native_pitch_lfo?.minimum_depth_quantization);if(!r.mixed_loop_song)return false;if(k==='accepted')return r.manual_matches_packed_variant;return k==='mixed'}
function draw(){const chosen=report.rows.filter(r=>aaMatch(r)&&structureMatch(r)&&(!get('game').value||r.family===get('game').value)&&(!get('status').value||r.status===get('status').value)&&(`${r.id} ${r.name||''}`).toLowerCase().includes(get('search').value.toLowerCase()));get('rows').replaceChildren();get('shown').textContent=`显示 ${chosen.length} 项`;
for(const r of chosen){const tr=document.createElement('tr');const cells=[`${r.id} ${r.name||'(无符号名)'}`,`${r.features?.track_count??'—'} → ${r.target_track_count??'—'}`,labels[r.status],r.route?`${r.route} / ${r.gain_db} dB`:'—',r.manual_matches_packed_variant?'与已验收版本一致':r.related_manual_records.length?'同曲目有记录，扫描版本不同':'未匹配人工记录',r.antialias?`${antialiasLabels[r.antialias.status]||r.antialias.status}${r.antialias.status==='packed'?` / ${r.antialias.gain_db} dB / ${r.antialias.target_sample_count} 采样${r.antialias.envelope_approximation?' / 渐入拟合':''}${r.antialias.finite_release_snapshots?' / 有限收音快照':''}`:''}`:'未扫描',r.antialias?.manual_matches_packed_variant?'与已验收版本一致':'未匹配人工记录'];for(const value of cells){const td=document.createElement('td');td.textContent=value;tr.append(td)}tr.children[2].className=r.status.startsWith('packed_')?'ok':'blocked';const td=document.createElement('td'),details=document.createElement('details'),summary=document.createElement('summary'),pre=document.createElement('pre');summary.textContent='执行／资源／尝试记录';pre.textContent=JSON.stringify(r,null,2);details.append(summary,pre);td.append(details);tr.append(td);get('rows').append(tr)}}
['game','status','search','antialias','structure'].forEach(id=>get(id).addEventListener('input',draw));draw();</script></html>'''
    (directory / 'index.html').write_text(page.replace('PAYLOAD', payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--song-gain-db', type=float, default=3.5)
    parser.add_argument('--pcm-channels', type=int, default=10)
    parser.add_argument('--antialias-variants', action='store_true',
                        help='Also try a separate offline-antialias singleton variant for every sequence')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    if not math.isfinite(args.song_gain_db) or not -24 <= args.song_gain_db <= 12:
        parser.error('Song gain must be finite and within -24..12 dB')
    if not 4 <= args.pcm_channels <= 12:
        parser.error('PCM channels must be within 4..12')
    base = args.base.read_bytes()
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        parser.error('Requires original Japanese EXE6 Gregar/Falzar')
    capacity = base[target['layout']['player_table_offset'] + target['layout']['music_player'] * 12 + 8]
    inputs = verified_sources(args.source_dir)
    evidence = manual_evidence(Path(__file__).resolve().parents[1] / 'out/nds-research')
    args.out.mkdir(parents=True)
    report = {'schema_version': 31, 'complete': False, 'scope': 'SSEQ only; no batch runtime or listening checks',
              'known_fifteen_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':4,
                  'source_track_ids':list(range(13))+[14,15],
                  'track_groups':[list(g) for g in SF3_STUDIO_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'existing_fixed_volume_ratio_mapping_with_quantization':True,
                  'long_note_alias_and_release_guards_unchanged':True,
                  'standalone_voice_budget_observations_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_fourteen_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':7,
                  'source_track_ids':list(range(12))+[14,15],
                  'track_groups':[list(g) for g in SF3_AJITO_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'existing_fixed_volume_ratio_mapping_with_quantization':True,
                  'long_note_alias_and_release_guards_unchanged':True,
                  'standalone_voice_budget_observations_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_thirteen_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':47,
                  'source_track_ids':list(range(10))+[13,14,15],
                  'track_groups':[list(g) for g in SF3_CHANGE_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'existing_fixed_volume_ratio_mapping_with_quantization':True,
                  'long_note_alias_and_release_guards_unchanged':True,
                  'standalone_voice_budget_observations_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_twelve_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':27,
                  'source_track_ids':[0,1,2,3,4,5,7,8,9,13,14,15],
                  'track_groups':[list(g) for g in SF3_BOSSMAE_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'standalone_voice_budget_observations_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_eleven_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':26, 'source_track_ids':list(range(9))+[14,15],
                  'track_groups':[list(g) for g in SF3_DEMPAJIKEN_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'long_note_alias_and_release_guards_unchanged':True,
                  'native_voice_budget_limit_retained':True, 'batch_native_runtime_validation':False},
              'known_ten_track_route_policy': {
                  'source_family':'ssr3', 'sequence_index':30, 'source_track_ids':list(range(8))+[14,15],
                  'track_groups':[list(g) for g in SF3_KINCHO_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'batch_native_runtime_validation':False},
              'known_nine_track_route_policy': {
                  'source_family':'ssr2', 'sequence_index':20, 'source_track_ids':list(range(9)),
                  'track_groups':[list(g) for g in SF2_HOKORA_GROUPS], 'target_track_capacity':8,
                  'all_source_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_control_and_conversion_guards':True, 'group_search':False,
                  'batch_native_runtime_validation':False},
              'variable_late_fitted_route_policy': {
                  'retry_after_explicit_envelope_fixed_tempo_failure_only': True,
                  'all_source_tracks_loop': True, 'singleton_tracks_only': True,
                  'initial_zero_depth_notes_before_fixed_positive_enable': True,
                  'fitted_envelopes_explicit': True, 'existing_fit_limits_unchanged': True,
                  'active_delays_live_changes_disable_minimum_filter_finite_mixed': False,
                  'conductor_modulation': False, 'max_source_tempos': 8, 'max_unfolded_tempo_changes': 128,
                  'batch_native_runtime_validation': False},
              'variable_tempo_route_policy': {
                  'retry_after_explicit_fixed_tempo_failure_only': True,
                  'all_source_tracks_loop': True, 'singleton_tracks_only': True,
                  'fixed_zero_delay_pitch_modulation': True, 'conductor_modulation': False,
                  'initial_tempo_at_zero': True, 'max_source_tempos': 8, 'max_unfolded_tempo_changes': 128,
                  'positive_speed_writes_preserve_phase_and_count': True,
                  'fitting_minimum_depth_filter_live_delayed_finite_mixed': False,
                  'batch_native_runtime_validation': False},
              'late_live_depth_route_policy': {
                  'retry_after_explicit_live_activation_failure_only': True,
                  'all_source_tracks_loop': True, 'singleton_tracks_only': True, 'fixed_tempo': True,
                  'positive_depth_changes_route_only': True, 'fixed_type_speed_range_delay': True,
                  'restore_nonzero_lfos_at_enable': True, 'positive_updates_preserve_phase_and_count': True,
                  'fitting_minimum_depth_filter_toggle_finite_mixed': False,
                  'batch_native_runtime_validation': False},
              'live_minimum_depth_route_policy': {
                  'retry_after_explicit_live_depth_representation_failure_only': True,
                  'all_source_tracks_loop': True, 'singleton_tracks_only': True, 'fixed_tempo': True,
                  'fitted_envelope_is_separate_explicit_mode': True,
                  'mixed_finite_filtered_toggle_modes': False, 'existing_activation_and_fixed_parameter_guards': True,
                  'native_minimum_mod': 1, 'all_phase_pitch_difference_bound_cents': 10,
                  'isolated_one_second_rms_limit_cents': 5, 'batch_native_runtime_validation': False},
              'mixed_live_depth_route_policy': {
                  'retry_after_explicit_mixed_fixed_parameter_failure_only': True,
                  'requires_positive_depth_changes_and_mixed_tracks': True,
                  'singleton_tracks_only': True, 'fixed_tempo': True,
                  'max_later_entry_common_cycles': 1, 'finite_gates_closed_by_end': True,
                  'finite_tracks_repeated': False, 'minimum_depth_explicit': True,
                  'fitted_envelope_is_separate_explicit_mode': True,
                  'filtering_release_overrides_live_toggle': False,
                  'batch_native_runtime_validation': False},
              'mixed_route_policy': {'tried_after_existing_routes': True, 'singleton_tracks_only': True,
                  'requires_both_finite_and_looping_tracks': True, 'fixed_tempo': True,
                  'finite_end_not_after_original_shared_loop_entry': True,
                  'finite_gates_closed_by_end': True, 'finite_tracks_repeated': False,
                  'max_common_period_ticks': 16384, 'max_period_expansion': 8,
                  'filtering_fitted_envelopes_release_overrides': False,
                  'fixed_delay_native_lfo': True, 'minimum_depth_retry_after_explicit_representation_failure_only': True,
                  'minimum_depth_native_mod': 1, 'all_phase_pitch_difference_bound_cents': 10,
                  'isolated_one_second_rms_limit_cents': 5, 'batch_native_runtime_validation': False},
              'known_sf3_dempajiken_merged_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':26,
                  'source_track_ids':list(range(9))+[14,15],
                  'track_groups':[list(g) for g in SF3_DEMPAJIKEN_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'upward_preparation':False,
                  'standalone_rejection_preemption_and_clipping_observations_attributed':True,
                  'plain_baseline_observation_is_fresh_read_only_capture':True,
                  'batch_native_runtime_validation':False},
              'known_sf2_hokora_merged_antialias_policy': {
                  'source_family':'ssr2', 'sequence_index':20,
                  'source_track_ids':list(range(9)),
                  'track_groups':[list(g) for g in SF2_HOKORA_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'upward_preparation':False,
                  'standalone_voice_and_clipping_observations_attributed':True,
                  'plain_baseline_observation_is_fresh_read_only_capture':True,
                  'batch_native_runtime_validation':False},
              'known_kincho_upward_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':30,
                  'source_track_ids':list(range(8))+[14,15],
                  'track_groups':[list(g) for g in SF3_KINCHO_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'maximum_shift_semitones':12, 'preparation_key_overflow_rejected':True,
                  'shared_wave_root_source_key_maximum':True,
                  'native_notes_bends_expression_unchanged':True,
                  'standalone_voice_observations_explicitly_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_change_upward_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':47,
                  'source_track_ids':list(range(10))+[13,14,15],
                  'track_groups':[list(g) for g in SF3_CHANGE_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'maximum_shift_semitones':12, 'preparation_key_overflow_rejected':True,
                  'shared_wave_root_source_key_maximum':True,
                  'native_notes_bends_expression_unchanged':True,
                  'standalone_held_preemptions_explicitly_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_ajito_upward_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':7,
                  'source_track_ids':list(range(12))+[14,15],
                  'track_groups':[list(g) for g in SF3_AJITO_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'maximum_shift_semitones':12, 'preparation_key_overflow_rejected':True,
                  'shared_wave_root_source_key_maximum':True,
                  'native_notes_bends_expression_unchanged':True,
                  'standalone_held_preemptions_explicitly_attributed':True,
                  'batch_native_runtime_validation':False},
              'known_upward_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':4,
                  'source_track_ids':list(range(13))+[14,15],
                  'track_groups':[list(g) for g in SF3_STUDIO_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'maximum_shift_semitones':12, 'preparation_key_overflow_rejected':True,
                  'shared_wave_root_source_key_maximum':True,
                  'native_notes_bends_expression_unchanged':True,
                  'batch_native_runtime_validation':False},
              'known_merged_antialias_policy': {
                  'source_family':'ssr3', 'sequence_index':27,
                  'source_track_ids':[0,1,2,3,4,5,7,8,9,13,14,15],
                  'track_groups':[list(g) for g in SF3_BOSSMAE_GROUPS],
                  'all_tracks_loop':True, 'fitting_or_active_modulation':False,
                  'existing_group_and_filter_guards':True, 'group_search':False,
                  'standalone_voice_and_clipping_observations_attributed':True,
                  'batch_native_runtime_validation':False},
              'antialias_variant_policy': {'enabled': args.antialias_variants,
                  'separate_from_primary_route': True, 'singleton_tracks_only': False,
                  'merged_exception':'Pinned SF3 BOSSMAE slot27, STUDIO slot4, AJITO slot7, CHANGE slot47, KINCHO slot30, DEMPAJIKEN slot26 and SF2 HOKORA slot20 only; existing guards and no search',
                  'finite_and_looping_sequences': True, 'source_step_range': [1/16, 32],
                  'pcm_sample_budget': 4_000_000, 'native_mixing_rate_hz': 10512,
                  'upward_bend_transpose_modulation_portamento': False,
                  'native_lfo': False, 'finite_fitted_envelope': False,
                  'looping_fitted_attack_retry': 'Only after explicit non-instant attack fitting requirement',
                  'finite_release_retry': 'Only after explicit unsupported D3 on entirely finite tracks; initialization before first note, instant attacks, no other ADSR overrides',
                  'record_plain_failure_and_fitted_parameters': True, 'neutral_gain_headroom_retry': True,
                  'batch_native_runtime_validation': False, 'exact_variant_sha_required_for_manual_match': True},
              'finite_route_policy': {'singleton_tracks_only': True, 'all_source_tracks_end': True,
                                      'fixed_tempo': True, 'all_gates_close_before_or_at_source_end': True,
                                      'native_lfo_or_fitted_envelope': False,
                                      'release_snapshot_retry': 'Explicit unsupported D3 only, after plain finite route; initialization before first note',
                                      'explicit_eot_before_individual_fine': True,
                                      'tried_after_existing_routes': True,
                                      'neutral_gain_headroom_retry': True,
                                      'batch_native_runtime_validation': False},
              'voice_context_split_policy': {
                  'context_fields': ['source_instrument', 'merged_pan_shift', 'effective_note_on_adsr_if_enabled'],
                  'first_compatible_bank_reused': True,
                  'conflicting_source_key_at_same_alias_creates_bank': True,
                  'source_keys_samples_and_track_local_eots_preserved': True,
                  'max_voice_contexts': 128,
                  'batch_native_runtime_validation': False},
              'long_note_loop_carry_policy': {
                  'matching_entry_exit_intervals_required': True,
                  'overlapping_aliases_supported': False,
                  'boundary_note_retrigger': False,
                  'gate_validation_extends_beyond_note_on_window': True,
                  'batch_native_runtime_validation': False},
              'live_toggle_route_policy': {'singleton_tracks_only': True, 'fixed_tempo': True,
                                           'allowed_depths': 'Zero or one fixed representable positive depth per track',
                                           'fixed_fields': ['mod_type', 'mod_speed', 'mod_range', 'mod_delay'],
                                           'late_activation_and_disabling_supported': True,
                                           'combined_live_depth_changes_supported': False,
                                           'toggle_updates_preserve_delay_count': True,
                                           'target_disable_resets_shared_phase': True,
                                           'source_inactive_voice_phase_is_frozen': True,
                                           'new_notes_reset_shared_phase_and_delay': True},
              'live_depth_route_policy': {'singleton_tracks_only': True, 'fixed_tempo': True,
                                          'activation': 'Before or at first note timestamp, including depth enabled after note at the same tick',
                                          'positive_depth_changes_only': True,
                                          'fixed_fields': ['mod_type', 'mod_speed', 'mod_range', 'mod_delay'],
                                          'disabling_or_late_activation_supported': False,
                                          'depth_update_resets_phase_or_delay_count': False,
                                          'new_notes_reset_shared_phase_and_delay': True,
                                          'requires_representable_nonzero_native_depth': True},
              'fixed_delay_route_policy': {'singleton_tracks_only': True, 'fixed_tempo': True,
                                           'activation': 'Before or at first note timestamp, including depth enabled after note at the same tick',
                                           'live_parameter_changes': False, 'lfodl_max': 255,
                                           'mapping': 'round(DS delay * GBA sequence tick rate / DS timer rate) + 1',
                                           'shared_delay_and_phase': True},
              'envelope_route_policy': {'singleton_tracks_only': True, 'override_range': [0, 127],
                                        'attack_fit_rms_limit': 0.12, 'attack_fit_max_limit': 0.30,
                                        'onset_phase_uncertainty_gba_frames': 1},
              'target': target['key'], 'base_fingerprint': fingerprint(base), 'track_capacity': capacity,
              'song_gain_db': args.song_gain_db, 'neutral_gain_retry_on_headroom_failure': True,
              'pcm_channels': args.pcm_channels, 'events': list(EVENTS), 'archives': [], 'rows': []}
    try:
        for item in inputs:
            source = item['path'].read_bytes()
            if SOURCES.get(fingerprint(source)['sha256']) != item['profile']:
                raise ValueError('Source changed after inspection')
            archive = AuditArchive(item['sdat'])
            slots = sequence_slots(archive)
            report['archives'].append({'family': item['family'], 'representative': item['profile'],
                                       'variants': item['variants'], 'sdat_fingerprint': fingerprint(item['sdat']),
                                       'sequence_slots': len(slots), 'sequence_archive_slots_excluded': info_count(archive, 1),
                                       'stream_slots_excluded': info_count(archive, 7)})
            for number, slot in enumerate(slots, 1):
                row = scan_sequence(archive, slot, item['family'], source, base, item['sdat'], item['profile'],
                                    capacity, args.song_gain_db, args.pcm_channels, evidence)
                if args.antialias_variants:
                    row['antialias'] = scan_antialias_variant(archive, row, source, base, item['sdat'],
                                                            item['profile'], capacity, args.song_gain_db, args.pcm_channels)
                report['rows'].append(row)
                report['summary'] = summarize(report['rows'])
                (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
                print(f'{item["family"]} {number}/{len(slots)} {slot["name"]}: {row["status"]}; antialias={row.get("antialias", {}).get("status", "not_requested")}', flush=True)
            report['summary'] = summarize(report['rows'])
            (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        # Original files must still have their pinned identities after the scan.
        for item in inputs:
            for variant in item['variants']:
                if fingerprint(Path(variant['path']).read_bytes()) != variant['rom_fingerprint']:
                    raise AssertionError('Input source changed during audit')
        if args.base.read_bytes() != base:
            raise AssertionError('Input target changed during audit')
        report.update(complete=True, inputs_unchanged=True, summary=summarize(report['rows']))
        write_reports(args.out, report)
        print(json.dumps(report['summary']), flush=True)
    except BaseException as error:
        report['fatal_error'] = error_record(error)
        report['summary'] = summarize(report['rows'])
        (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
