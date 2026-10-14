#!/usr/bin/env python3
"""Probe ROM-resident playlist selection and preservation of native PvP effects.

Controlled arguments/selector bytes are explicit. The hook executes real Thumb
code and BIOS Div in mGBA; checks arguments, initialized state, stack and ABI.
Sustained natural playback is tested separately by validate_song.py --unified.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import struct

from scan_audio import ROM_BASE, fingerprint
from validate_playback import Debugger
from target_profiles import valid_manifest_target, manifest_layout, selector_value


def probe(rom, data, manifest, trigger, selector, work, mgba):
    layout = manifest_layout(manifest)
    entry, core = ROM_BASE+layout['entry_offset'], ROM_BASE+layout['core_offset']
    selector_address = layout['selector_address']
    selector_width = 4 if layout.get('selector_mode')=='clock-xorshift32' else 1
    label = f'id-{trigger}-selector-{selector if selector is not None else "native"}'
    directory = work / label
    directory.mkdir()
    sample_rom = directory / 'test.gba'
    # Link only the disposable test image, giving every process its own save/config path.
    os.link(rom, sample_rom)
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', XDG_CONFIG_HOME=str(directory / 'config'))
    env.pop('LD_PRELOAD', None)
    with (directory / 'debugger.txt').open('w') as transcript:
        debugger = Debugger([mgba, '-d', str(sample_rom)], env, transcript)
        try:
            debugger.prompt()
            if trigger == layout['preservation_probes'][0]:
                handler = int(manifest['hook']['handler_address'], 16)
                size = manifest['hook']['handler_size']
                listing = debugger.command(f'disassemble/t 0x{handler:08X} {(size - 24) // 2}')
                (directory / 'handler-disassembly.txt').write_text(listing)
                (directory / 'stub-disassembly.txt').write_text(debugger.command(f'disassemble/t 0x{entry:08X} 7'))
            debugger.command(f'break/t 0x{entry:08X}')
            before = debugger.hit(entry)
            debugger.command(f'w/r r0 {trigger}')
            if selector is not None:
                debugger.command(f'w/{selector_width} 0x{selector_address:08X} {selector}')
            selector_raw = debugger.read(selector_width, selector_address)
            scene = layout.get('scene_selector')
            scene_raw = debugger.read(4,scene['address']) if scene and trigger == scene['trigger_id'] else 0
            observed_selector = selector_value(layout,selector_raw,trigger,scene_raw)
            expected_id = trigger
            rule = next((r for r in manifest['hook']['rules'] if r['trigger_id'] == trigger), None)
            if rule:
                expected_id = rule['ids'][(observed_selector >> rule['selector_shift']) % len(rule['ids'])]
            table = manifest['target_table_file_offset']
            header, player_index = struct.unpack_from('<IH', data, table + expected_id * 8)
            player = struct.unpack_from('<I', data, layout['player_table_offset'] + player_index * 12)[0]
            debugger.command(f'break/t 0x{core:08X}')
            at_core = debugger.hit(core)
            if at_core[0] != player or at_core[1] != header or at_core[4] != expected_id:
                raise AssertionError('Hook selection/player/header mismatch')
            returned = at_core[14] & ~1
            debugger.command(f'break/t 0x{returned:08X}')
            debugger.hit(returned)
            active_header = debugger.read(4, player)
            tone_bank = debugger.read(4, player + 48)
            expected_tone = struct.unpack_from('<I', data, header - ROM_BASE + 4)[0]
            if active_header != header or tone_bank != expected_tone:
                raise AssertionError('Player did not initialize selected header/tone')
            caller = before[14] & ~1
            debugger.command(f'break/t 0x{caller:08X}')
            after = debugger.hit(caller)
            if scene and trigger == scene['trigger_id'] and debugger.read(4,scene['address']) != scene_raw:
                raise AssertionError('Hook changed local RNG1 state')
            if any(before[r] != after[r] for r in list(range(4, 12)) + [13]):
                raise AssertionError('Hook changed callee-saved registers or stack')
            query_checked = False
            if 'query_entry_offset' in layout:
                expected_status = debugger.read(2,player+4)
                query = ROM_BASE+layout['query_entry_offset']
                debugger.command(f'w/r r0 {trigger}')
                debugger.command(f'w/r r14 {caller|1}')
                debugger.command(f'w/r r15 {query}')
                queried = debugger.hit(caller)
                if queried[0] != expected_status:
                    raise AssertionError('Status query did not recognize the selected pool header')
                if any(after[r] != queried[r] for r in list(range(4,12))+[13]):
                    raise AssertionError('Status query changed callee-saved registers or stack')
                query_checked = True
            return {'status_query_checked':query_checked, 'trigger_id': trigger, 'selector_override': selector, 'selector_byte': observed_selector, 'selector_raw':selector_raw, 'scene_rng_raw':scene_raw,
                    'selected_id': expected_id, 'player_index': player_index, 'header': f'0x{header:08X}',
                    'tone_bank': f'0x{tone_bank:08X}', 'register_injection': True,
                    'abi_preserved': True, 'player_initialized': True}
        finally:
            debugger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--trigger', type=int, action='append', help='Probe specified triggers instead of the full preservation suite')
    parser.add_argument('--selector', type=int, action='append', help='Override the default probe values 0,128,255')
    parser.add_argument('--mgba', default='/usr/games/mgba')
    args = parser.parse_args()
    data = args.rom.read_bytes()
    manifest = json.loads(args.manifest.read_text())
    if (manifest['output_fingerprint'] != fingerprint(data)
        or not valid_manifest_target(manifest)):
        parser.error('ROM does not match the pinned unified manifest')
    if not 1 <= args.jobs <= 4:
        parser.error('--jobs must be 1..4')
    args.out.mkdir(parents=True, exist_ok=False)
    work = args.out.resolve()
    rom = work / 'test.gba'
    rom.write_bytes(data)
    selectors = args.selector if args.selector is not None else [0, 128, 255]
    if any(not 0 <= value <= 255 for value in selectors):
        parser.error('Selector values must be 0..255')
    layout = manifest_layout(manifest)
    native_cases = [(i,None) for i in layout['preservation_probes']]
    if args.trigger:
        if any(not 0 <= value < manifest['table_entry_count'] for value in args.trigger):
            parser.error('Trigger outside unified table')
        cases = native_cases[:1] + [(trigger, selector) for trigger in args.trigger for selector in selectors]
    else:
        cases = native_cases
        cases += [(rule['trigger_id'], selector) for rule in manifest['hook']['rules'] for selector in selectors]
    cases = list(dict.fromkeys(cases))
    samples, errors = [], []
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {executor.submit(probe, rom, data, manifest, trigger, selector, work, args.mgba): (trigger, selector) for trigger, selector in cases}
            for future in as_completed(futures):
                case = futures[future]
                try:
                    sample = future.result()
                except Exception as exc:
                    errors.append({'case': case, 'error': repr(exc)})
                    print(f'{case}: FAILED {exc}', flush=True)
                else:
                    samples.append(sample)
                    print(f'{case}: selected {sample["selected_id"]}; player/ABI checks passed', flush=True)
    finally:
        report = {'schema_version': 1, 'rom_fingerprint': fingerprint(data), 'manifest_path': str(args.manifest),
                  'cases': len(cases), 'complete': not errors and len(samples) == len(cases),
                  'samples': sorted(samples, key=lambda s: (s['trigger_id'], s['selector_byte'])), 'errors': errors,
                  'limitations': ['Controlled arguments/selector overrides', 'Initialization/ABI checks, not full playback for every pool track']}
        (work / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    if errors:
        parser.exit(1, f'{len(errors)} hook probes failed\n')
    print(f'All {len(samples)} hook probes passed', flush=True)


if __name__ == '__main__':
    main()
