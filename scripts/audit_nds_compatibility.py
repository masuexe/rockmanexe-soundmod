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
from nds_track_merge import BATTLE_GROUPS, convert_merged_song
from scan_audio import fingerprint
from target_profiles import validate_target

EVENTS = ('1', '21', 'scene:communication')
STATUS_LABELS = {
    'empty_slot': '空槽', 'silent_sequence': '无执行音符', 'analysis_blocked': '执行分析受阻',
    'packed_standard': '常规路径打包通过', 'packed_lfo_approximation': '颤音近似打包通过',
    'packed_envelope_approximation': '包络近似打包通过',
    'packed_envelope_lfo_approximation': '包络＋颤音近似打包通过',
    'packed_delayed_lfo_approximation': '固定延迟颤音近似打包通过',
    'packed_envelope_delayed_lfo_approximation': '包络＋固定延迟颤音近似打包通过',
    'packed_live_depth_lfo_approximation': '实时深度颤音近似打包通过',
    'packed_envelope_live_depth_lfo_approximation': '包络＋实时深度颤音近似打包通过',
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
    depth_changes = []
    for track in tracks:
        previous = 0
        for action in track['actions']:
            if action['opcode'] != 0xCA:
                continue
            depth = action['state_after']['mod_depth']
            if previous > 0 and depth > 0 and previous != depth:
                depth_changes.append({'source_track': track['track'], 'ticks': action['ticks'],
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
    if family == 'ssr3' and slot['index'] == 35:
        routes.append('known_sf3_battle_merge')
    if not routes:
        row.update(status='capacity_blocked', track_capacity=capacity)
        return row
    pack_errors = False
    for route in routes:
        live_depth = route in ('live_depth_pitch_lfo_approximation', 'envelope_live_depth_pitch_lfo_approximation')
        delayed = live_depth or route in ('fixed_delay_pitch_lfo_approximation', 'envelope_fixed_delay_pitch_lfo_approximation')
        pitch_lfo = delayed or route in ('native_pitch_lfo_approximation', 'envelope_pitch_lfo_approximation')
        envelope = route in ('singleton_envelope_approximation', 'envelope_pitch_lfo_approximation',
                             'envelope_fixed_delay_pitch_lfo_approximation', 'envelope_live_depth_pitch_lfo_approximation')
        approximations = {'native_pitch_lfo': pitch_lfo, 'envelope': envelope,
                          'fixed_delay': delayed, 'live_depth': live_depth}
        gains = [gain_db]
        for applied_gain in gains:
            attempt = {'route': route, 'gain_db': applied_gain, 'approximations': approximations,
                       'conversion_passed': False, 'packing_passed': False}
            row['attempts'].append(attempt)
            try:
                if route == 'direct':
                    blob, dependency, conversion = convert_song(archive, slot['index'], capacity,
                                                               song_gain_db=applied_gain, native_effect_headroom=True)
                else:
                    options = {'native_pitch_lfo_live_depth': True} if live_depth else {}
                    blob, dependency, conversion = convert_merged_song(
                        archive, slot['index'], BATTLE_GROUPS if route == 'known_sf3_battle_merge' else groups,
                        capacity, applied_gain, native_pitch_lfo=pitch_lfo, envelope_support=envelope,
                        native_pitch_lfo_delay=delayed, **options)
                attempt['conversion_passed'] = True
            except (ValueError, AssertionError, IndexError, struct.error) as error:
                attempt['error'] = error_record(error)
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
            status = ('packed_envelope_live_depth_lfo_approximation' if envelope and live_depth else
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
            if envelope:
                row['envelope_approximation'] = conversion['envelope_approximation']
            if pitch_lfo:
                row['native_pitch_lfo'] = conversion.get('native_pitch_lfo', {})
            return row
    row['status'] = ('packing_blocked' if pack_errors else 'converter_model_blocked'
                     if any(a.get('error', {}).get('model_assertion') for a in row['attempts']) else 'conversion_blocked')
    return row


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
        source = manifest['nds_conversion']
        records.append({'family': source['source_profile'][:4], 'sequence_index': source['sequence_index'],
                        'output_sha256': expected['sha256'], 'record': str(path.resolve()),
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
            'blocking_features_nonexclusive': {
                'noninstant_attack_definitions': sum(bool(r.get('features', {}).get('noninstant_attack_definitions')) for r in blocked),
                'envelope_override_controls': sum(bool(r.get('features', {}).get('envelope_override_controls')) for r in blocked),
                'long_gates': sum(bool(r.get('features', {}).get('long_notes')) for r in blocked),
                'nonzero_pitch_modulation_delay': sum(any(c['delay'] for c in r.get('features', {}).get('modulation_configs_at_note_on', [])) for r in blocked)},
            'by_family': {family: dict(Counter(r['status'] for r in rows if r['family'] == family))
                          for family in ('ssr1', 'ssr2', 'ssr3')}}


def write_reports(directory, report):
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    summary = ['# NDS → EXE6 兼容性扫描', '',
               '扫描仅覆盖 SSEQ。通过转换与 ROM 打包不等于人工试听通过；本轮没有执行新曲目的游戏运行测试。', '',
               '| 游戏 | 槽位 | 非空、非无音符候选 | 常规通过 | 颤音近似 | 包络近似 | 包络＋颤音 | 延迟颤音 | 包络＋延迟颤音 | 实时深度颤音 | 包络＋实时深度颤音 | 其余受阻 |',
               '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for family in ('ssr1', 'ssr2', 'ssr3'):
        values = report['summary']['by_family'][family]
        slots = sum(values.values())
        candidates = slots - values.get('empty_slot', 0) - values.get('silent_sequence', 0)
        standard, lfo = values.get('packed_standard', 0), values.get('packed_lfo_approximation', 0)
        envelope = values.get('packed_envelope_approximation', 0)
        combined = values.get('packed_envelope_lfo_approximation', 0)
        delayed = values.get('packed_delayed_lfo_approximation', 0)
        envelope_delayed = values.get('packed_envelope_delayed_lfo_approximation', 0)
        live_depth = values.get('packed_live_depth_lfo_approximation', 0)
        envelope_live_depth = values.get('packed_envelope_live_depth_lfo_approximation', 0)
        summary.append(f'| {family} | {slots} | {candidates} | {standard} | {lfo} | {envelope} | {combined} | '
                       f'{delayed} | {envelope_delayed} | {live_depth} | {envelope_live_depth} | '
                       f'{candidates - standard - lfo - envelope - combined - delayed - envelope_delayed - live_depth - envelope_live_depth} |')
    summary.extend(['', f'与已有人工验收 ROM 字节一致的扫描构建：{report["summary"]["packed_exact_manual_matches"]} 个。', '',
                    '具体曲目、每条转换路径及失败原因见 report.csv、report.json 或 index.html。', '',
                    '常规路径仍使用既有 PCM8、包络和速度量化近似；颤音近似还有共享相位和波形差异。',
                    '包络路径按音符开始时的 ADSR 快照生成乐器；渐入起音拟合有明确误差上限。组合路径同时包含两类近似。',
                    '固定延迟路径接受首次音符之前或同一时刻完成初始化、此后参数固定的延迟颤音；共享相位和延迟会受同轨新音符重置影响。',
                    '实时深度路径仅允许启用后的正深度变化，速度、类型、范围与延迟仍须固定；关闭颤音、后期启用与其他参数变化仍拒绝。分类互斥，组合路径不重复计数。'])
    (directory / 'summary.md').write_text('\n'.join(summary) + '\n')
    fields = ['id', 'family', 'index', 'name', 'status', 'source_tracks', 'target_tracks', 'samples',
              'route', 'gain_db', 'appended_bytes', 'native_pitch_lfo_approximation',
              'envelope_approximation', 'fixed_delay_approximation', 'live_depth_approximation',
              'source_depth_changes', 'delay_mappings',
              'attack_fits', 'manual_matches_packed_variant', 'errors']
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
                             'source_depth_changes': json.dumps(row.get('native_pitch_lfo', {}).get('live_depth_approximation', {}).get('source_depth_changes', [])),
                             'delay_mappings': json.dumps([c['delay_mapping'] for c in row.get('native_pitch_lfo', {}).get('configs', [])
                                                          if 'delay_mapping' in c]),
                             'attack_fits': json.dumps(row.get('envelope_approximation', {}).get('attack_fits', [])),
                             'manual_matches_packed_variant': row['manual_matches_packed_variant'],
                             'errors': json.dumps(row.get('analysis_error') or errors, ensure_ascii=False)})
    payload = json.dumps({'report': report, 'labels': STATUS_LABELS}, ensure_ascii=False).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NDS → EXE6 曲目兼容性扫描</title><style>body{font:16px/1.6 system-ui;margin:30px;background:#111923;color:#edf2f7}input,select{font:inherit;padding:6px;margin:5px}table{border-collapse:collapse;width:100%}th,td{padding:8px;border-bottom:1px solid #354458;text-align:left;vertical-align:top}summary{cursor:pointer}pre{white-space:pre-wrap;max-width:65vw;font-size:13px}.ok{color:#89dfa4}.blocked{color:#e8c792}</style>
<h1>NDS → EXE6 曲目兼容性扫描</h1><p>常规、颤音、包络、固定延迟颤音、实时深度颤音及其组合路径成功后，均通过共享资源打包和 BPS 回建。常规路径同样使用已有采样和包络近似。详情保留起音拟合误差与延迟映射；固定延迟路径要求首次音符之前或同一时刻完成初始化且此后参数固定。实时深度路径额外允许正深度变化，其余参数固定，MOD 更新保留共享相位和延迟计数，同轨新音符仍会重置相位。自动通过不等于实际试听或战斗验证通过；空槽、无音符序列不计为可播放曲目。扫描仅覆盖 SSEQ，SSAR 与 STRM 不在转换范围内。</p>
<p id="counts"></p><label>游戏<select id="game"><option value="">全部</option><option>ssr1</option><option>ssr2</option><option>ssr3</option></select></label><label>结果<select id="status"><option value="">全部</option></select></label><input id="search" placeholder="查找曲名或编号"><span id="shown"></span>
<table><thead><tr><th>曲目</th><th>轨数</th><th>结果</th><th>路径／增益</th><th>现有人工记录</th><th>详情</th></tr></thead><tbody id="rows"></tbody></table>
<script type="application/json" id="data">PAYLOAD</script><script>
const {report,labels}=JSON.parse(document.querySelector('#data').textContent);const get=id=>document.getElementById(id);
get('counts').textContent=`${report.summary.slots} 个槽位，${report.summary.packed} 首通过打包，${report.summary.packed_exact_manual_matches} 首与已有人工验收版本字节匹配。`;
Object.entries(labels).forEach(([key,label])=>{const o=document.createElement('option');o.value=key;o.textContent=label;get('status').append(o)});
function draw(){const chosen=report.rows.filter(r=>(!get('game').value||r.family===get('game').value)&&(!get('status').value||r.status===get('status').value)&&(`${r.id} ${r.name||''}`).toLowerCase().includes(get('search').value.toLowerCase()));get('rows').replaceChildren();get('shown').textContent=`显示 ${chosen.length} 项`;
for(const r of chosen){const tr=document.createElement('tr');const cells=[`${r.id} ${r.name||'(无符号名)'}`,`${r.features?.track_count??'—'} → ${r.target_track_count??'—'}`,labels[r.status],r.route?`${r.route} / ${r.gain_db} dB`:'—',r.manual_matches_packed_variant?'与已验收版本一致':r.related_manual_records.length?'同曲目有记录，扫描版本不同':'未匹配人工记录'];for(const value of cells){const td=document.createElement('td');td.textContent=value;tr.append(td)}tr.children[2].className=r.status.startsWith('packed_')?'ok':'blocked';const td=document.createElement('td'),details=document.createElement('details'),summary=document.createElement('summary'),pre=document.createElement('pre');summary.textContent='执行／资源／尝试记录';pre.textContent=JSON.stringify(r,null,2);details.append(summary,pre);td.append(details);tr.append(td);get('rows').append(tr)}}
['game','status','search'].forEach(id=>get(id).addEventListener('input',draw));draw();</script></html>'''
    (directory / 'index.html').write_text(page.replace('PAYLOAD', payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--song-gain-db', type=float, default=3.5)
    parser.add_argument('--pcm-channels', type=int, default=10)
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
    report = {'schema_version': 4, 'complete': False, 'scope': 'SSEQ only; no batch runtime or listening checks',
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
                report['rows'].append(row)
                print(f'{item["family"]} {number}/{len(slots)} {slot["name"]}: {row["status"]}', flush=True)
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
