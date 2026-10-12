#!/usr/bin/env python3
"""Build the pinned agbplay streaming helper; optional Ubuntu deps stay local."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '0b87da48d2502da359e45718eec8566ac40fa9d7'
PACKAGES = ['libfmt-dev','libfmt9','libboost1.83-dev','libzip-dev','libzip4t64']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent / 'references/agbplay')
    parser.add_argument('--fetch-deps', action='store_true', help='Download/extract Ubuntu 24.04 packages locally; no sudo')
    parser.add_argument('--deps', type=Path, default=ROOT / 'out/realtime-deps')
    args = parser.parse_args()
    source, deps = args.source.resolve(), args.deps.resolve()
    if not source.is_dir():
        parser.exit(1, f'Clone https://github.com/ipatix/agbplay.git into {source}, then checkout {COMMIT}\n')
    commit = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'], text=True).strip()
    if commit != COMMIT:
        parser.exit(1, f'Expected agbplay revision {COMMIT}; checkout that revision first\n')
    packages = deps / 'packages'
    if args.fetch_deps:
        packages.mkdir(parents=True, exist_ok=True)
        subprocess.run(['apt-get','download',*PACKAGES], cwd=packages, check=True)
    if packages.is_dir():
        for package in sorted(packages.glob('*.deb')):
            subprocess.run(['dpkg-deb','-x',str(package),str(deps)], check=True)
    output = ROOT / 'out/realtime'
    command = ['cmake','-S',str(ROOT / 'native/realtime'),'-B',str(output),
               '-DCMAKE_BUILD_TYPE=Release',f'-DAGBPLAY_SOURCE={source}']
    if (deps / 'usr/include').is_dir(): command.append(f'-DLOCAL_DEPS={deps}')
    subprocess.run(command, check=True)
    subprocess.run(['cmake','--build',str(output),'-j',str(min(4,os.cpu_count() or 1))], check=True)
    shutil.copyfile(source / 'LICENSE', output / 'AGBPLAY-LICENSE')
    (output / 'engine.json').write_text(json.dumps({'project':'ipatix/agbplay','commit':commit,'source':str(source),
                                                 'license':'LGPL-3.0','transport':'stereo float32 PCM on stdout'},indent=2)+'\n')
    print(f'Realtime helper ready: {output / "exe-realtime"}')


if __name__ == '__main__': main()
