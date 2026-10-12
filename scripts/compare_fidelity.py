#!/usr/bin/env python3
"""Record original and transplanted songs in the same mGBA audio path.

Source selection injects only an audio ID at the first natural music start.
Target playback starts naturally from a single-track title pool. Neither run
suppresses scene transitions. This is diagnostic evidence, not a fidelity score.
"""
import argparse
from array import array
import base64
import html
import json
import math
import os
from pathlib import Path
import shutil
import struct
import wave

from build_unified import build_catalog
from original_catalog import PROFILES, catalog_originals
from render_preview import capture_preview, capture_run
from scan_audio import ROM_BASE, fingerprint
from target_profiles import TARGETS, manifest_layout


def source_driver(data, profile):
    """Require the stock start-by-ID sequence immediately before a table literal."""
    signature = bytes.fromhex('00b50004074a0849400b4018')
    signature_new = bytes.fromhex('00b50004074b0849400b4018')
    needle = struct.pack('<I', ROM_BASE + profile['table_offset'])
    candidates = []
    cursor = 0
    while True:
        literal = data.find(needle, cursor)
        if literal < 0:
            break
        cursor = literal + 1
        entry = literal - 40
        if entry < 0 or entry % 4 or data[entry:entry+12] not in (signature, signature_new):
            continue
        high, low = struct.unpack_from('<HH', data, entry + 28)
        if high & 0xF800 != 0xF000 or low & 0xF800 != 0xF800:
            continue
        delta = ((high & 0x7FF) << 12) | ((low & 0x7FF) << 1)
        if delta & (1 << 22):
            delta -= 1 << 23
        core = entry + 32 + delta
        players = struct.unpack_from('<I', data, literal - 4)[0] - ROM_BASE
        if not 0 <= core < len(data) or not 0 <= players < len(data)-12*(profile['music_player']+1):
            continue
        candidates.append({'entry_offset': entry, 'core_offset': core,
                           'player_table_offset': players})
    if len(candidates) != 1:
        raise ValueError('Source driver is not uniquely recognized; verify its layout first')
    return candidates[0]


def capture_source(data, profile, song, directory, seconds, mgba):
    if fingerprint(data) != profile['fingerprint']:
        raise ValueError('Unsupported source ROM fingerprint')
    driver = source_driver(data, profile)
    return capture_run(data, directory, seconds, mgba,
                       lambda debugger: start_source_song(debugger, data, profile, song),
                       {'source_key': profile['key'], 'source_id': song,
                        'register_injection': True, 'injection': 'audio ID only at natural music call',
                        'driver': driver})


def start_source_song(debugger, data, profile, song):
    driver = source_driver(data, profile)
    entry = ROM_BASE + driver['entry_offset']
    player_index = struct.unpack_from('<H', data, profile['table_offset'] + song*8 + 4)[0]
    if player_index != profile['music_player']:
        raise ValueError('Source entry is not music')
    player = struct.unpack_from('<I', data, driver['player_table_offset'] + player_index*12)[0]
    header = struct.unpack_from('<I', data, profile['table_offset'] + song*8)[0]

    debugger.command(f'break/t 0x{entry:08X}')
    for _ in range(100):
        regs = debugger.hit(entry)
        index = regs[0] & 0xFFFF
        if index >= profile['entry_count']:
            raise ValueError('Source game requested an audio ID outside its table')
        actual_player = struct.unpack_from('<H', data, profile['table_offset'] + index*8 + 4)[0]
        if actual_player == player_index:
            break
    else:
        raise ValueError('Source game did not start music')
    debugger.command(f'w/r r0 0x{song:X}')
    debugger.command(f'break/t 0x{entry+32:08X}')
    debugger.hit(entry+32)
    if debugger.read(4, player) != header:
        raise ValueError('Source music did not initialize the requested header')
    debugger.command('delete 1')
    debugger.command('delete 2')

    return player


def normalize_wav(source, destination):
    """Match whole-clip RMS at -20 dBFS, with peak headroom and no limiter."""
    with wave.open(str(source), 'rb') as stream:
        params = stream.getparams()
        if params.sampwidth != 2:
            raise ValueError('Expected signed 16-bit PCM')
        samples = array('h', stream.readframes(params.nframes))
    if os.sys.byteorder != 'little':
        samples.byteswap()
    peak = max(abs(s) for s in samples)
    rms = math.sqrt(sum(s*s for s in samples)/len(samples))
    if not rms:
        raise ValueError('Cannot normalize silence')
    gain = min(32768*0.1/rms, 32767*0.95/peak)
    normalized = array('h', (round(s*gain) for s in samples))
    if os.sys.byteorder != 'little':
        normalized.byteswap()
    with wave.open(str(destination), 'wb') as stream:
        stream.setparams(params)
        stream.writeframes(normalized.tobytes())
    return {'raw_rms_dbfs': 20*math.log10(rms/32768), 'raw_peak': peak,
            'gain': gain, 'normalized_rms_dbfs': 20*math.log10(rms*gain/32768)}


def mixer_experiment(image, manifest, config, mode):
    """Research-only global startup changes; never used by manager exports."""
    if mode not in ('source-rate-volume', 'source-all'):
        raise ValueError('Unknown mixer experiment')
    freq, vol, channels = (config[k] for k in ('frequency_selector', 'master_volume', 'pcm_channels'))
    if not 1 <= freq <= 12 or not 1 <= vol <= 15 or not 1 <= channels <= 12:
        raise ValueError('Source configuration outside supported mixer limits')
    offset = manifest_layout(manifest)['sound_mode_offset']
    original = struct.unpack_from('<I', image, offset)[0]
    mask = 0xFF000
    fields = freq << 16 | vol << 12
    if mode == 'source-all':
        mask |= 0xF00
        fields |= channels << 8
    changed = (original & ~mask) | fields
    output = bytearray(image)
    # The production builder adapts fixed-step waves for the original target
    # rate. A source-rate experiment must restore their original copies to avoid
    # applying that rate adaptation twice.
    for imported in manifest.get('imports', []):
        adjustments = imported.get('audio_adjustments', [])
        for adjustment in adjustments:
            if adjustment['source_rate'] != config['mixing_rate_raw']:
                raise ValueError('Mixer experiment cannot combine different fixed PCM source rates')
            wave = next(r for r in imported['resources'] if r['kind']=='pcm_wave'
                        and r['source_offset']==adjustment['source_wave_offset'])
            tone = next(r for r in imported['resources'] if r['kind']=='tone_record'
                        and r['source_offset']==adjustment['source_tone_offset'])
            for site in tone['target_offsets']:
                struct.pack_into('<I', output, site+4, ROM_BASE+wave['target_offsets'][0])
                for field in imported['pointers']:
                    if field['target_site'] == site+4:
                        field['target_offset'] = wave['target_offsets'][0]
                        field.pop('audio_adjustment', None)
        if adjustments:
            imported['bypassed_audio_adjustments'] = adjustments
            imported['audio_adjustments'] = []
    struct.pack_into('<I', output, offset, changed)
    manifest['output_fingerprint'] = fingerprint(output)
    manifest['sound_mode_change']['after'] = f'0x{changed:08X}'
    manifest['sound_mode_change']['pcm_channels'] = (changed >> 8) & 15
    manifest['experimental_mixer'] = {'mode': mode, 'source_config': config,
                                      'scope': 'Global startup setting, affects native music and sound effects'}
    return bytes(output)


def listening_page(destination, runs):
    """Create a portable A/B page containing the already normalized WAVs."""
    cases = {}
    labels = {'baseline': 'Current GP mix', 'source-rate-volume': 'Source rate and volume',
              'source-all': 'Source rate, volume and channel budget'}
    for run in runs:
        report = json.loads((run/'comparison.json').read_text())
        for case in report['cases']:
            key = case['track']
            path = run/key.replace(':', '-')
            entries = cases.setdefault(key, [])
            if entries and case['source']['rom_fingerprint'] != entries[0][2]['rom_fingerprint']:
                raise ValueError('Comparison runs use different original ROMs')
            if not entries:
                entries.append(('Original ROM', path/'source-normalized.wav', case['source']))
            mode = case.get('mixer_experiment') or 'baseline'
            label = 'GP with fixed-step PCM rate correction' if case.get('fixed_pcm_rate_correction') else labels.get(mode, mode)
            entries.append((label, path/'target-normalized.wav', case['target']))
    sections = []
    for key, entries in cases.items():
        cards = []
        for label, wav, report in entries:
            encoded = base64.b64encode(wav.read_bytes()).decode('ascii')
            config = report['sound_config']
            cards.append(f'<article><h3>{html.escape(label)}</h3>'
                         f'<p>{config["mixing_rate_raw"]:,} Hz · PCM {config["pcm_channels"]} · '
                         f'Volume {config["master_volume"]} · Reverb {config["reverb"]}</p>'
                         f'<audio controls preload="none" src="data:audio/wav;base64,{encoded}"></audio></article>')
        sections.append(f'<section><h2>{html.escape(key)}</h2><div class="clips">'+''.join(cards)+'</div></section>')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Music fidelity comparison</title>
<style>body{font:16px system-ui;margin:32px auto;max-width:1200px;padding:0 20px;color:#222;background:#f6f7f9}
h1{font-size:28px}h2{margin-top:36px}.clips{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
article{background:white;padding:16px;border:1px solid #ddd;border-radius:8px}h3{font-size:16px;margin:0 0 12px}
p{line-height:1.6}article p{font-size:13px;color:#555}audio{width:100%}</style>
<h1>Original ROM vs transplanted music</h1><p>All clips were recorded through the same mGBA SDL audio path.
Whole-clip RMS is normalized to -20 dBFS, with peak headroom. Starting a clip pauses the others.
Recordings are short, approximately aligned, and retain the normal game lifecycle.</p>
<p>Source-matched mixer variants, when present, are diagnostic experiments with global effects on native music
and sound effects. Fixed-step PCM corrections instead adapt the imported waves to the normal target mixer rate.</p>
''' + ''.join(sections) + '''<script>document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>{
document.querySelectorAll('audio').forEach(b=>{if(b!==a)b.pause()})}));</script></html>''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roms', type=Path, default=Path(__file__).resolve().parents[2]/'roms')
    parser.add_argument('--target', choices=TARGETS, default='exegp')
    parser.add_argument('--target-rom', type=Path, help='Already prepared target ROM (required for PvP)')
    parser.add_argument('--track', action='append', help='Original catalog key, e.g. exe1:2; repeatable')
    parser.add_argument('--seconds', type=int, default=12)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--mgba', default='/usr/games/mgba')
    parser.add_argument('--baseline', type=Path, help='Reuse fingerprint-checked original captures from an earlier run')
    parser.add_argument('--mixer-experiment', choices=['source-rate-volume', 'source-all'],
                        help='Research only: change the target global startup mixer, not manager exports')
    parser.add_argument('--listen-run', type=Path, action='append', help='Combine existing runs into a portable listening page')
    parser.add_argument('--listen-out', type=Path, help='Output HTML for --listen-run (no emulator run)')
    args = parser.parse_args()
    if args.listen_run:
        if not args.listen_out:
            parser.error('--listen-run requires --listen-out')
        listening_page(args.listen_out, args.listen_run)
        print(args.listen_out)
        return
    if not args.out:
        parser.error('Recording requires --out')
    if not 1 <= args.seconds <= 30:
        parser.error('--seconds must be 1..30')
    if args.target != 'exegp' and not args.target_rom:
        parser.error('PvP targets require --target-rom')
    tracks = args.track or ['exe1:2', 'bn2:0', 'exe6:1']
    selections = []
    for key in dict.fromkeys(tracks):
        source, index = key.split(':')
        if source not in PROFILES or not 0 <= int(index) < PROFILES[source]['entry_count']:
            parser.error(f'Unknown source track {key}')
        selections.append((key, source, int(index)))
    args.out.mkdir(parents=True, exist_ok=False)
    base = (args.roms/('exegp.gba' if args.target == 'exegp' else 'exe45.gba')).read_bytes()
    target = args.target_rom.read_bytes() if args.target_rom else base
    donors = {s: (args.roms/PROFILES[s]['filename']).read_bytes() for _, s, _ in selections}
    catalog, dependencies = catalog_originals(base, target, donors)
    native = catalog['native_source']
    trigger = str(catalog['preview_trigger'])
    rows = {r['key']: r for r in catalog['entries']}
    results = []
    for key, source, index in selections:
        if not rows[key]['playlist_eligible']:
            raise ValueError(f'Track cannot be imported: {key}')
        case = args.out/key.replace(':', '-')
        case.mkdir()
        project = {'schema_version': 1, 'target_profile': args.target,
                   'pools': {trigger: {'tracks': [key]}}}
        image, _, manifest = build_catalog(base, target, catalog, dependencies,
                                          {native: target, **donors}, project, selected_only=True)
        if args.baseline:
            reference = args.baseline/key.replace(':', '-')/'source'
            source_report = json.loads((reference/'preview.json').read_text())
            if (source_report['rom_fingerprint'] != fingerprint(donors[source])
                or source_report['source_id'] != index or source_report['source_key'] != source
                or source_report['seconds'] != args.seconds):
                raise ValueError('Baseline capture does not match requested source and duration')
            (case/'source').mkdir()
            source_wav = case/'source/preview.wav'
            shutil.copyfile(reference/'preview.wav', source_wav)
            (case/'source/preview.json').write_text(json.dumps(source_report, indent=2)+'\n')
        else:
            print(f'Recording {key}: original', flush=True)
            source_wav, source_report = capture_source(donors[source], PROFILES[source], index,
                                                       case/'source', args.seconds, args.mgba)
        if args.mixer_experiment:
            image = mixer_experiment(image, manifest, source_report['sound_config'], args.mixer_experiment)
        rom = case/'unified.gba'
        rom.write_bytes(image)
        (case/'build.json').write_text(json.dumps(manifest, indent=2)+'\n')
        print(f'Recording {key}: {args.target}', flush=True)
        target_wav, target_report = capture_preview(rom, manifest, rows[key]['target_index'],
                                                   case/'target', args.seconds, args.mgba)
        metrics = {name: normalize_wav(wav, case/f'{name}-normalized.wav')
                   for name, wav in [('source', source_wav), ('target', target_wav)]}
        result = {'track': key, 'source': source_report, 'target': target_report,
                  'mixer_experiment': args.mixer_experiment,
                  'fixed_pcm_rate_correction': any(i.get('audio_adjustments') for i in manifest['imports']),
                  'normalization': metrics}
        (case/'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
        results.append(result)
        (args.out/'comparison.json').write_text(json.dumps({'target': args.target, 'cases': results}, indent=2)+'\n')
    items = []
    for r in results:
        key = r['track'].replace(':', '-')
        items.append(f'<h2>{html.escape(r["track"])}</h2><p>Original ROM</p>'
                     f'<audio controls src="{key}/source-normalized.wav"></audio><p>Transplanted ROM</p>'
                     f'<audio controls src="{key}/target-normalized.wav"></audio>')
    (args.out/'listen.html').write_text('<!doctype html><meta charset="utf-8"><title>Music fidelity comparison</title>'
                                       '<h1>Same-emulator comparison</h1><p>Whole-clip RMS normalization, peak-capped. '
                                       'Normal game lifecycle remains active. These clips are not sample-aligned.</p>'
                                       + '\n'.join(items))
    print(args.out/'listen.html', flush=True)


if __name__ == '__main__':
    main()
