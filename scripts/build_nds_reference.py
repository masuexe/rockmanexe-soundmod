#!/usr/bin/env python3
"""Build the optional software DS reference renderer from a supplied public core.

Copies kode54/SSEQPlayer into a new local output directory, adjusts its old
codecvt compatibility guards for modern GCC, and adds note trace hooks.
The supplied upstream source directory is never changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True, help='kode54/SSEQPlayer source directory')
    parser.add_argument('--out', type=Path, required=True, help='New build output directory')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory must be new')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.core.iterdir()
              if p.is_file() and p.suffix in ('.cpp', '.h')}
    required = ('Player.cpp', 'Track.cpp', 'Channel.cpp', 'convert.h', 'SDAT.cpp')
    if any(name not in hashes for name in required):
        parser.error('Expected SSEQPlayer core files not found')
    args.out.mkdir(parents=True)
    copied = args.out / 'core'
    copied.mkdir()
    for name in hashes:
        shutil.copyfile(args.core / name, copied / name)
    if (args.core / 'LICENSE.TXT').is_file():
        shutil.copyfile(args.core / 'LICENSE.TXT', copied / 'LICENSE.TXT')
    for name in ('Player.cpp', 'convert.h'):
        path = copied / name
        text = path.read_text()
        guard = '#if (defined(__GNUC__) || defined(__clang__)) && !defined(_LIBCPP_VERSION)'
        if text.count(guard) != 1:
            raise ValueError('Unknown upstream codecvt guard; inspect source before building')
        path.write_text(text.replace(guard, '#if 0 // modern GCC provides standard codecvt'))
    player = copied / 'Player.cpp'
    text = player.read_text()
    marker = '\t\tthis->tempoCount -= 240;'
    if text.count(marker) != 1:
        raise ValueError('Unknown upstream sequence tick; trace hook not installed')
    text = text.replace(marker, marker + '\n\t\t++researchSequenceClock;')
    timer = 'void Player::Timer()\n{'
    if text.count(timer) != 1:
        raise ValueError('Unknown upstream timer; modulation clock hook not installed')
    player.write_text('extern unsigned researchSequenceClock;\nextern unsigned researchTimerClock;\n' +
                      text.replace(timer, timer + '\n\t++researchTimerClock;'))
    channel = copied / 'Channel.cpp'
    text = channel.read_text()
    marker = '\t\t\tmodParam >>= 8; // tmr/pan: adjust to 7.6'
    if text.count(marker) != 1:
        raise ValueError('Unknown upstream modulation calculation; hook not installed')
    channel.write_text('class Channel;\nextern void researchModulation(const Channel&, int);\n' +
                       text.replace(marker, marker + '\n\t\tresearchModulation(*this, modParam);'))
    track = copied / 'Track.cpp'
    text = track.read_text()
    marker = 'int Track::NoteOn(int key, int vel, int len)\n{'
    if text.count(marker) != 1:
        raise ValueError('Unknown upstream NoteOn; trace hook not installed')
    declaration = '\nextern void researchNote(const Track&, int, int, int);\nextern void researchControl(const Track&, int, int);\n'
    text = text.replace(marker, declaration + marker + '\n\tresearchNote(*this, key, vel, len);')
    for statement, opcode, value in [
        ('this->pan = this->overriding.val(pData, read8) - 64;', 0xC0, 'this->pan + 64'),
        ('this->pitchBend = this->overriding.val(pData, read8);', 0xC4, 'this->pitchBend'),
        ('this->expr = this->overriding.val(pData, read8);', 0xD5, 'this->expr'),
    ]:
        if text.count(statement) != 1:
            raise ValueError('Unknown upstream control statement; trace hook not installed')
        text = text.replace(statement, statement + f'\n\t\t\t\t\tresearchControl(*this, {opcode}, {value});')
    track.write_text(text)
    binary = args.out / 'nds-reference'
    command = ['g++', '-std=c++11', '-O2', '-I', str(copied),
               str(Path(__file__).resolve().parents[1] / 'native/nds_reference.cpp'),
               *(str(p) for p in sorted(copied.glob('*.cpp'))), '-o', str(binary)]
    subprocess.run(command, check=True)
    report = {'core': str(args.core.resolve()), 'upstream_files_sha256': hashes,
              'research_renderer_sha256': hashlib.sha256((Path(__file__).resolve().parents[1] / 'native/nds_reference.cpp').read_bytes()).hexdigest(),
              'renderer': 'kode54/SSEQPlayer', 'compiler_command': command,
              'modifications': ['Use standard codecvt on modern GCC',
                                'Observe sequence/timer clocks, NoteOn, controls and per-voice modulation; no synthesis changes'],
              'limitations': ['Software DS reference, not hardware or DS emulator output']}
    (args.out / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(binary)


if __name__ == '__main__':
    main()
