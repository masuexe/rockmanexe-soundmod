#!/usr/bin/env python3
"""Record a short full-mix preview from a disposable mGBA SDL process."""
import argparse
from array import array
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time
import wave

from scan_audio import ROM_BASE, fingerprint
from validate_playback import Debugger
from target_profiles import manifest_layout


def capture_preview(rom, manifest, target_id, directory, seconds=12, mgba='/usr/games/mgba'):
    if not 1 <= seconds <= 30:
        raise ValueError('Preview duration must be 1..30 seconds')
    data = Path(rom).read_bytes()
    if fingerprint(data) != manifest['output_fingerprint']:
        raise ValueError('Preview image does not match its build manifest')
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    library = directory / 'capture.so'
    subprocess.run(['cc', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror', '-o', str(library),
                    str(Path(__file__).with_name('capture_audio.c')), '-ldl'], check=True, capture_output=True)
    test_rom = directory / 'test.gba'
    test_rom.write_bytes(data)
    layout = manifest_layout(manifest)
    entry, core = ROM_BASE+layout['entry_offset'], ROM_BASE+layout['core_offset']
    title_trigger = layout['preview_trigger']
    table = manifest['target_table_file_offset']
    header, player_index = struct.unpack_from('<IH', data, table + target_id * 8)
    player = struct.unpack_from('<I', data, layout['player_table_offset'] + player_index * 12)[0]
    title = next((r for r in manifest['hook']['rules'] if r['trigger_id'] == title_trigger), None)
    if not title or title['ids'] != [target_id]:
        raise ValueError(f'Preview build must select exactly this track at title event {title_trigger}')
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_CONFIG_HOME=str(directory / 'config'), LD_PRELOAD=str(library),
               EXE_CAPTURE_DIR=str(directory), EXE_CAPTURE_SECONDS=str(seconds))
    with (directory / 'debugger.txt').open('w') as transcript:
        debugger = Debugger([mgba, '-d', str(test_rom)], env, transcript)
        try:
            debugger.prompt()
            debugger.command(f'break/t 0x{entry:08X}')
            debugger.command(f'break/t 0x{core:08X}')
            incoming = None
            for _ in range(100):
                text = debugger.command('continue')
                regs = {int(n): int(v, 16) for n, v in re.findall(r'\br(\d+):\s*([0-9a-fA-F]{8})', text)}
                if f'at 0x{entry:08X}' in text:
                    incoming = regs[0]
                    continue
                if f'at 0x{core:08X}' not in text:
                    raise RuntimeError('Unexpected preview breakpoint')
                if incoming == title_trigger and regs[0] == player and regs[1] == header:
                    returned = regs[14] & ~1
                    debugger.command(f'break/t 0x{returned:08X}')
                    debugger.hit(returned)
                    break
                incoming = None
            else:
                raise ValueError('Track did not start at the title selection hook')
            for number in (1, 2, 3):
                debugger.command(f'delete {number}')
            (directory / 'enabled').write_text('capture\n')
            os.write(debugger.master, b'continue\n')
            deadline = time.monotonic() + seconds + 20
            while not (directory / 'done').exists():
                if (directory / 'error.txt').exists():
                    raise RuntimeError((directory / 'error.txt').read_text())
                if debugger.process.poll() is not None:
                    raise RuntimeError('mGBA exited before audio capture completed')
                if time.monotonic() > deadline:
                    raise TimeoutError('Audio preview capture timed out')
                time.sleep(0.1)
        finally:
            debugger.close()
    info = json.loads((directory / 'audio-format.json').read_text())
    pcm = (directory / 'audio.pcm').read_bytes()
    samples = array('h')
    samples.frombytes(pcm)
    if os.sys.byteorder != 'little':
        samples.byteswap()
    peak = max((abs(value) for value in samples), default=0)
    if peak == 0:
        raise ValueError('Emulator returned a silent preview')
    wav = directory / 'preview.wav'
    with wave.open(str(wav), 'wb') as stream:
        stream.setnchannels(info['channels'])
        stream.setsampwidth(2)
        stream.setframerate(info['frequency'])
        stream.writeframes(pcm)
    report = {'schema_version': 1, 'rom_fingerprint': fingerprint(data), 'target_id': target_id,
              'seconds': len(pcm) / (info['frequency'] * info['channels'] * 2),
              'audio_format': info, 'peak': peak, 'capture': 'SDL full mix including Direct Sound and PSG',
              'register_injection': False, 'title_trigger': title_trigger,
              'limitations': ['Short clip, not full-track validation', 'Normal game lifecycle remains active; previews limited to 30 seconds']}
    (directory / 'preview.json').write_text(json.dumps(report, indent=2) + '\n')
    return wav, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--seconds', type=int, default=12)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    wav, report = capture_preview(args.rom, json.loads(args.manifest.read_text()), args.id, args.out, args.seconds)
    print(f'{wav}: {report["seconds"]:.1f}s, peak {report["peak"]}, {report["audio_format"]}')


if __name__ == '__main__':
    main()
