#!/usr/bin/env python3
"""Shared music relocation and checked ROM hooks for verified target layouts.

The CLI retains the legacy EXE4.5 Soundmod workflow. The manager builds catalogs
from original ROMs and uses the same relocation/export core for every target.
"""
import argparse
import copy
import json
from pathlib import Path
import struct

from analyze_song import analyze
from scan_audio import ROM_BASE, MAX_ROM_SIZE, apply_bps, fingerprint
from transplant_song import make_bps
from unified_catalog import catalog, write_catalog
from target_profiles import validate_target, LAYOUTS, AUDIO_LAYOUT, check_layout

TABLE_REFERENCES = LAYOUTS[AUDIO_LAYOUT]['table_references']  # Legacy public constant.


class Thumb:
    """Small checked encoder for the handful of ARMv4T instructions in this hook.

No external assembler is required. Disassembly/runtime verification is separate.
"""
    def __init__(self, offset):
        self.offset = offset
        self.data = bytearray()
        self.labels = {}
        self.fixups = []
        self.literals = []

    def emit(self, opcode):
        self.data.extend(struct.pack('<H', opcode))

    def label(self, name):
        self.labels[name] = len(self.data)

    def branch(self, name, condition=None, link=False):
        site = len(self.data)
        self.fixups.append((site, name, condition, link))
        self.emit(0)
        if link:
            self.emit(0)

    def load(self, register, value):
        site = len(self.data)
        self.literals.append((site, register, value))
        self.emit(0)

    def finish(self):
        while (self.offset + len(self.data)) % 4:
            self.emit(0x46C0)  # nop
        for site, register, value in self.literals:
            literal = self.offset + len(self.data)
            pc = (self.offset + site + 4) & ~3
            delta = literal - pc
            if delta < 0 or delta % 4 or delta > 1020:
                raise ValueError('Thumb literal out of range')
            struct.pack_into('<H', self.data, site, 0x4800 | register << 8 | delta // 4)
            self.data.extend(struct.pack('<I', value))
        for site, name, condition, link in self.fixups:
            delta = self.labels[name] - site - 4
            if delta % 2:
                raise ValueError('Unaligned Thumb branch')
            if link:
                if not -(1 << 22) <= delta < (1 << 22):
                    raise ValueError('Thumb BL out of range')
                struct.pack_into('<HH', self.data, site, 0xF000 | (delta >> 12 & 0x7FF), 0xF800 | (delta >> 1 & 0x7FF))
            else:
                bits = 11 if condition is None else 8
                if not -(1 << bits) <= delta < (1 << bits):
                    raise ValueError('Thumb branch out of range')
                opcode = 0xE000 if condition is None else 0xD000 | condition << 8
                struct.pack_into('<H', self.data, site, opcode | (delta >> 1 & ((1 << bits) - 1)))
        return bytes(self.data)


def entry_stub(hook_address, layout=None, returns_value=False):
    layout = layout or LAYOUTS[AUDIO_LAYOUT]
    code = Thumb(layout['entry_offset'])
    code.emit(0xB500)  # push lr
    code.load(3, hook_address | 1)
    code.branch('far_call', link=True)
    code.emit(0xBC08 if returns_value else 0xBC01)  # pop return address into r3/r0
    code.emit(0x4718 if returns_value else 0x4700)  # bx r3/r0
    code.label('far_call')
    code.emit(0x4718)  # bx r3; BL supplied a Thumb return address
    return code.finish()


def selector_hook(offset, rule_address, table_address, layout=None):
    layout = layout or LAYOUTS[AUDIO_LAYOUT]
    code = Thumb(offset)
    code.emit(0xB5F0)  # push r4-r7,lr
    code.emit(0x1C04)  # mov r4,r0
    code.emit(0x0424)  # lsl r4,#16
    code.emit(0x0C24)  # lsr r4,#16
    code.load(5, rule_address)
    code.label('rule')
    code.emit(0x8828)  # ldrh r0,[r5]
    code.load(1, 0xFFFF)
    code.emit(0x4288)  # cmp r0,r1
    code.branch('dispatch', condition=0)
    code.emit(0x42A0)  # cmp r0,r4
    code.branch('found', condition=0)
    code.emit(0x3508)  # add r5,#8
    code.branch('rule')
    code.label('found')
    code.emit(0x78AA)  # ldrb r2,[r5,#2] : shift
    code.emit(0x78E9)  # ldrb r1,[r5,#3] : count
    code.load(0, layout['selector_address'])
    if layout.get('selector_mode') == 'clock-xorshift32':
        code.emit(0x6800)  # ldr r0,[r0] : existing scheduler tick, read only
        code.emit(0x0343)  # lsl r3,r0,#13
        code.emit(0x4058)  # eor r0,r3
        code.emit(0x0C43)  # lsr r3,r0,#17
        code.emit(0x4058)
        code.emit(0x0143)  # lsl r3,r0,#5
        code.emit(0x4058)
        code.emit(0x0600)  # retain low byte, matching pool selector semantics
        code.emit(0x0E00)
    else:
        code.emit(0x7800)  # ldrb r0,[r0] : existing game RNG selector
    code.emit(0x40D0)  # lsr r0,r2
    code.emit(0xDF06)  # BIOS Div; r1 = remainder (pool length is nonzero)
    code.emit(0x686A)  # ldr r2,[r5,#4] : pool pointer
    code.emit(0x0049)  # lsl r1,#1
    code.emit(0x5A54)  # ldrh r4,[r2,r1] : selected 16-bit audio ID
    code.label('dispatch')
    code.load(1, table_address)
    code.emit(0x00E0)  # lsl r0,r4,#3
    code.emit(0x1840)  # add r0,r0,r1
    code.emit(0x8883)  # ldrh r3,[r0,#4]
    code.emit(0x0059)  # lsl r1,r3,#1
    code.emit(0x18C9)  # add r1,r1,r3
    code.emit(0x0089)  # lsl r1,#2
    code.load(2, ROM_BASE + layout['player_table_offset'])
    code.emit(0x1889)  # add r1,r1,r2
    code.emit(0x680A)  # ldr r2,[r1]
    code.emit(0x6801)  # ldr r1,[r0]
    code.emit(0x1C10)  # mov r0,r2
    code.load(3, (ROM_BASE + layout['core_offset']) | 1)
    code.branch('far_call', link=True)
    code.label('core_return')
    code.emit(0xBDF0)  # pop r4-r7,pc
    code.label('far_call')
    code.emit(0x4718)
    raw = code.finish()
    return raw, {name: ROM_BASE + offset + value for name, value in code.labels.items()}


def status_query_hook(offset, rule_address, table_address, layout):
    """EXE GP query: recognize any currently active header in the requested pool.

No per-song RAM is allocated. Unconfigured native queries retain header equality.
The game fade helper uses this query before fading the original music player.
"""
    code = Thumb(offset)
    code.emit(0xB5F0)
    code.emit(0x0404)  # lsl r4,r0,#16
    code.emit(0x0C24)
    code.load(5,rule_address)
    code.label('rule')
    code.emit(0x8828)
    code.load(1,0xFFFF)
    code.emit(0x4288)
    code.branch('native',condition=0)
    code.emit(0x42A0)
    code.branch('pool',condition=0)
    code.emit(0x3508)
    code.branch('rule')
    code.label('pool')
    code.emit(0x78EE)  # ldrb r6,[r5,#3]
    code.emit(0x686D)  # ldr r5,[r5,#4]
    code.load(7,ROM_BASE+layout['player_table_offset']+layout['music_player']*12)
    code.emit(0x683F)  # ldr r7,[r7]
    code.emit(0x683A)  # ldr r2,[r7] : active header
    code.load(1,table_address)
    code.label('member')
    code.emit(0x8828)
    code.emit(0x00C0)  # lsl r0,#3
    code.emit(0x1840)
    code.emit(0x6800)
    code.emit(0x4290)  # cmp r0,r2
    code.branch('status',condition=0)
    code.emit(0x3502)
    code.emit(0x3E01)
    code.branch('member',condition=1)
    code.branch('empty')
    code.label('native')
    code.load(1,table_address)
    code.emit(0x00E0)
    code.emit(0x1840)
    code.emit(0x8883)
    code.emit(0x0059)
    code.emit(0x18C9)
    code.emit(0x0089)
    code.load(2,ROM_BASE+layout['player_table_offset'])
    code.emit(0x1889)
    code.emit(0x680F)  # ldr r7,[r1]
    code.emit(0x683A)
    code.emit(0x6800)
    code.emit(0x4290)
    code.branch('empty',condition=1)
    code.label('status')
    code.emit(0x88B8)  # ldrh r0,[r7,#4]
    code.branch('return')
    code.label('empty')
    code.emit(0x2000)
    code.label('return')
    code.emit(0xBDF0)
    return code.finish()


class Relocator:
    def __init__(self, target_rom, reports):
        self.output = bytearray(target_rom)
        self.tables, self.cache = {}, {}
        self.mapping_reports = []
        self.stats = {'resource_allocations': 0, 'resource_cache_hits': 0, 'pointer_writes': 0}
        requirements = {}
        for source, report in reports:
            for offset, base, index in self.placements(report):
                requirements[source, base] = max(requirements.get((source, base), 128), index + 1)
        for (source, base), count in sorted(requirements.items()):
            self.tables[source, base] = self.allocate(bytes(count * 12))

    @staticmethod
    def placements(report):
        bank = report['header']['tone_bank']['file_offset']
        result = {(bank + voice * 12, bank, voice) for voice, _ in report['voice_key_pairs']}
        for tone in report['tones']:
            if 'children_base' in tone:
                base = tone['children_base']['file_offset']
                result.update((base + index * 12, base, index) for index in tone['child_indices_used'])
        return sorted(result)

    def allocate(self, raw):
        self.output.extend(bytes((-len(self.output)) % 4))
        offset = len(self.output)
        if offset + len(raw) > MAX_ROM_SIZE:
            raise ValueError('Combined resources exceed 32 MiB ROM limit')
        self.output.extend(raw)
        return offset

    def import_song(self, source, data, report):
        local = []
        placements = {}
        for old, base, index in self.placements(report):
            placements.setdefault(old, []).append(self.tables[source, base] + index * 12)
        for resource in report['resources']:
            old, size, kind = resource['file_offset'], resource['size_bytes'], resource['kind']
            raw = data[old:old + size]
            if kind == 'tone_record':
                targets = placements[old]
                for target in targets:
                    self.output[target:target + size] = raw
            else:
                # PCM/keymap/PSG waves have no embedded ROM pointers: deduplicate
                # exact contents across songs/sources. Sequence/header cache keys
                # include the source offset so pointer-bearing bytes aren't merged.
                key = (kind, size, resource['sha256']) if kind in ('pcm_wave', 'keymap', 'psg_wave') else (source, kind, old, size)
                if key in self.cache:
                    target = self.cache[key]
                    self.stats['resource_cache_hits'] += 1
                else:
                    target = self.allocate(raw)
                    self.cache[key] = target
                    self.stats['resource_allocations'] += 1
                targets = [target]
            local.append({'kind': kind, 'source_offset': old, 'size_bytes': size, 'target_offsets': targets})

        def sites(old):
            found = [target + old - r['source_offset'] for r in local if r['source_offset'] <= old < r['source_offset'] + r['size_bytes'] for target in r['target_offsets']]
            if not found:
                raise ValueError(f'Unmapped {source} pointer site/target {old:#x}')
            return sorted(set(found))

        fields = []
        for field in report['pointer_fields']:
            old = field['target']['file_offset']
            if field['kind'] in ('tone_bank', 'tone_children'):
                target = self.tables[source, old]
            else:
                targets = sites(old)
                if len(targets) != 1:
                    raise ValueError('Ambiguous dependency target')
                target = targets[0]
            for site in sites(field['site']['file_offset']):
                struct.pack_into('<I', self.output, site, ROM_BASE + target)
                fields.append({'source_site': field['site']['file_offset'], 'target_site': site, 'target_offset': target, 'kind': field['kind']})
                self.stats['pointer_writes'] += 1
        new_header = sites(report['header']['file_offset'])[0]
        self.mapping_reports.append({'key': f"{source}:{report['index']}", 'header_offset': new_header, 'resources': local, 'pointers': fields})
        return new_header


def resolve_pools(config, value):
    if config.get('schema_version') != 1 or not isinstance(config.get('pools'), dict) or not config['pools']:
        raise ValueError('Playlist requires schema_version 1 and nonempty pools')
    if config.get('target_profile',value.get('target_profile')) != value.get('target_profile'):
        raise ValueError('Playlist belongs to a different target ROM')
    entries = {row['key']: row for row in value['entries']}
    native = {row['source_index']: row for row in value['entries'] if row['source'] == value.get('native_source','pvp')}
    rules = []
    for trigger, pool in config['pools'].items():
        trigger = int(trigger)
        if trigger not in native or not native[trigger]['playlist_eligible']:
            raise ValueError(f'Trigger {trigger} is not native target music; effects cannot be remapped')
        if not isinstance(pool, dict) or not isinstance(pool.get('tracks'), list):
            raise ValueError('Each pool requires a tracks list')
        keys, shift = pool['tracks'], pool.get('selector_shift', 0)
        if not isinstance(keys, list) or not 1 <= len(keys) <= 255 or type(shift) is not int or not 0 <= shift <= 7:
            raise ValueError('Pool requires 1..255 tracks and selector_shift 0..7')
        if any(not isinstance(key, str) or key not in entries or not entries[key]['playlist_eligible'] for key in keys):
            raise ValueError(f'Pool {trigger} contains an unknown, unavailable, or nonmusic track')
        rules.append({'trigger_id': trigger, 'keys': keys, 'ids': [entries[key]['target_index'] for key in keys], 'selector_shift': shift})
    if len({rule['trigger_id'] for rule in rules}) != len(rules):
        raise ValueError('Duplicate normalized trigger ID')
    return sorted(rules, key=lambda r: r['trigger_id'])


def build(base, pvp, sound, gp, playlist, pcm_channels=10):
    value, reports = catalog(base, pvp, sound, gp)
    return build_catalog(base, pvp, value, reports, {'soundmod': sound, 'exegp': gp}, playlist, pcm_channels)


def build_catalog(base, target_rom, value, reports, sources, playlist, pcm_channels=10, selected_only=False):
    """Reuse the checked target relocator/hooks with an independently prepared catalog."""
    target = validate_target(base, target_rom)
    layout = target['layout']
    check_layout(target_rom, layout)
    if value.get('target_profile') != target['key']:
        raise ValueError('Catalog belongs to a different target ROM')
    value = copy.deepcopy(value)
    rules = resolve_pools(playlist, value)
    if selected_only:
        selected = {key for rule in rules for key in rule['keys']}
        reports = {key: report for key, report in reports.items() if key in selected}
    if not 4 <= pcm_channels <= 12:
        raise ValueError('PCM channel budget must be 4..12')
    selected_reports = [(key.split(':')[0], report) for key, report in reports.items()]
    relocator = Relocator(target_rom, selected_reports)
    native_count, native_table = layout['entry_count'], layout['table_offset']
    table = bytearray(target_rom[native_table:native_table + native_count * 8])
    empty = next((table[i*8:(i+1)*8] for i in range(native_count) if table[i*8:i*8+4] == b'\0'*4),None)
    # Some tables use a non-null empty header; select it from the native catalog.
    if empty is None:
        index = next((r['source_index'] for r in value['entries'] if r['source']==value.get('native_source','pvp') and r['empty']),None)
        if index is None: raise ValueError('Target has no verified empty audio entry')
        empty = table[index*8:(index+1)*8]
    if value['table_entry_count'] < native_count or value['table_entry_count'] > 65535:
        raise ValueError('Invalid expanded audio table size')
    table.extend(empty * (value['table_entry_count'] - native_count))
    for row in value['entries']:
        key = row['key']
        if key not in reports:
            continue
        header = relocator.import_song(row['source'], sources[row['source']], reports[key])
        struct.pack_into('<IHH', table, row['target_index'] * 8, ROM_BASE + header, layout['music_player'], layout['music_player'])
        row.update(availability='imported_music', target_header_address=f'0x{ROM_BASE + header:08X}')
    table_offset = relocator.allocate(table)
    output = relocator.output
    pool_offsets = []
    for rule in rules:
        pool_offsets.append(relocator.allocate(struct.pack('<' + 'H' * len(rule['ids']), *rule['ids'])))
    rule_bytes = bytearray()
    for rule, pool_offset in zip(rules, pool_offsets):
        rule_bytes.extend(struct.pack('<HBBI', rule['trigger_id'], rule['selector_shift'], len(rule['ids']), ROM_BASE + pool_offset))
    rule_bytes.extend(struct.pack('<HBBI', 0xFFFF, 0, 0, 0))
    rule_offset = relocator.allocate(rule_bytes)
    hook_offset = (len(output) + 3) & ~3
    code, labels = selector_hook(hook_offset, ROM_BASE + rule_offset, ROM_BASE + table_offset, layout)
    actual_hook = relocator.allocate(code)
    assert actual_hook == hook_offset
    stub = entry_stub(ROM_BASE + hook_offset, layout)
    if len(stub) > layout['stub_capacity']:
        raise ValueError('Entry stub overlaps original literals')
    for offset in layout['table_references']:
        struct.pack_into('<I', output, offset, ROM_BASE + table_offset)
    mode_offset, entry_offset = layout['sound_mode_offset'], layout['entry_offset']
    original_mode = layout['sound_mode']
    mode = (original_mode & ~0xF00) | pcm_channels << 8
    struct.pack_into('<I', output, mode_offset, mode)
    output[entry_offset:entry_offset + len(stub)] = stub
    allowed = [(mode_offset, mode_offset + 4), (entry_offset, entry_offset + len(stub))] + [(offset, offset + 4) for offset in layout['table_references']]
    auxiliary_hooks = {}
    if 'query_entry_offset' in layout:
        query_offset = (len(output)+3)&~3
        query_code = status_query_hook(query_offset, ROM_BASE+rule_offset, ROM_BASE+table_offset,layout)
        assert relocator.allocate(query_code) == query_offset
        query_entry = layout['query_entry_offset']
        query_stub = entry_stub(ROM_BASE+query_offset, {**layout,'entry_offset':query_entry}, returns_value=True)
        if len(query_stub) > layout['query_stub_capacity']:
            raise ValueError('Status query stub exceeds target capacity')
        output[query_entry:query_entry+len(query_stub)] = query_stub
        allowed.append((query_entry,query_entry+len(query_stub)))
        auxiliary_hooks['status_query'] = {'entry_address':f'0x{ROM_BASE+query_entry:08X}',
                                           'handler_address':f'0x{ROM_BASE+query_offset:08X}', 'handler_size':len(query_code)}
    expected = bytearray(target_rom)
    for a, b in allowed:
        expected[a:b] = output[a:b]
    if output[:len(target_rom)] != expected or output[table_offset:table_offset + native_count * 8] != target_rom[native_table:native_table + native_count * 8]:
        raise AssertionError('Target preservation check failed')
    result = bytes(output)
    # Reparse every imported song, including shared banks after all row updates.
    for row in value['entries']:
        if row['key'] not in reports:
            continue
        original = reports[row['key']]
        relocated = analyze(result, table_offset, row['target_index'])
        for old, new in zip(original['tracks'], relocated['tracks']):
            if old['notes'] != new['notes'] or old['ticks_before_repeat'] != new['ticks_before_repeat'] or old['termination'] != new['termination']:
                raise AssertionError(f"Relocated sequence differs: {row['key']}")
        donor = sources[row['source']]
        old_samples = {donor[s['file_offset']:s['file_offset'] + s['size_bytes']] for s in original['samples']}
        new_samples = {result[s['file_offset']:s['file_offset'] + s['size_bytes']] for s in relocated['samples']}
        if old_samples != new_samples:
            raise AssertionError(f"Relocated PCM differs: {row['key']}")
    manifest = {'schema_version': 1, 'target_profile': target['key'], 'target_label':target['label'], 'audio_layout':target['audio_layout'], 'target_base_fingerprint': fingerprint(target_rom),
                'output_fingerprint': fingerprint(result), 'original_fingerprint': fingerprint(base),
                'sources': value['sources'], 'target_table_file_offset': table_offset, 'table_entry_count': value['table_entry_count'],
                'native_source':value.get('native_source','pvp'), 'native_entry_count':native_count,
                'appended_bytes': len(result) - len(target_rom), 'declared_prefix_ranges': allowed,
                'sound_mode_change': {'file_offset': mode_offset, 'before': f'0x{original_mode:08X}', 'after': f'0x{mode:08X}', 'pcm_channels': pcm_channels},
                'hook': {'entry_address': f'0x{ROM_BASE + entry_offset:08X}', 'handler_address': f'0x{ROM_BASE + hook_offset:08X}',
                         'handler_size': len(code), 'entry_stub_size': len(stub), 'labels': labels,
                         'selector_address': f"0x{layout['selector_address']:08X}", 'rules_address': f'0x{ROM_BASE + rule_offset:08X}',
                         'selector_mode':layout.get('selector_mode','byte'), 'selector_description':layout['selector_description'],
                         'rules': rules, 'scope': 'Start-by-ID only; other helpers retain their selection semantics'},
                'auxiliary_hooks':auxiliary_hooks, 'resource_statistics': relocator.stats, 'imports': relocator.mapping_reports,
                'limitations': ['Player-based music candidates; track names not assigned',
                                'Selector distribution is not guaranteed uniform; identical game timing can repeat selections',
                                'Global PCM budget affects mixer work; multiplayer not tested',
                                'Foreign effects and over-capacity music reserved but not imported'],
                'import_policy': 'selected tracks only' if selected_only else 'all eligible foreign tracks'}
    return result, value, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--pvp-patch', type=Path, required=True)
    parser.add_argument('--soundmod-patch', type=Path, required=True)
    parser.add_argument('--donor', type=Path, required=True)
    parser.add_argument('--playlist', type=Path, default=Path('config/playlist.json'))
    parser.add_argument('--pcm-channels', type=int, default=10)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    try:
        base = args.base.read_bytes()
        pvp, pvp_info = apply_bps(base, args.pvp_patch.read_bytes())
        sound, sound_info = apply_bps(base, args.soundmod_patch.read_bytes())
        result, value, manifest = build(base, pvp, sound, args.donor.read_bytes(), json.loads(args.playlist.read_text()), args.pcm_channels)
        patch = make_bps(base, result)
        reconstructed, info = apply_bps(base, patch)
        if reconstructed != result:
            raise AssertionError('BPS reconstruction differs')
        manifest.update(bps=info, source_patches={'pvp': pvp_info, 'soundmod': sound_info}, playlist_path=str(args.playlist))
        args.out.mkdir(parents=True)
        (args.out / 'unified.gba').write_bytes(result)
        (args.out / 'unified.bps').write_bytes(patch)
        (args.out / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
        write_catalog(args.out, value)
        print(f"{len(manifest['imports'])} imported songs; {value['table_entry_count']} stable slots; "
              f"{len(result)} ROM bytes; BPS reconstruction verified")
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'build_unified: {exc}\n')


if __name__ == '__main__':
    main()
