#!/usr/bin/env python3
"""Build a separately verified STRM -> Japanese EXE6 capability experiment."""
import argparse
import json
from pathlib import Path
import struct

from build_nds_experiment import SOURCES, SOURCE_ARCHIVES, pack_converted_experiment
from nds_music import SoundArchive, nds_sdat
from nds_stream import convert_stream
from scan_audio import fingerprint

STREAM_NAMES = {'ssr1': ('STRM_BGM01TITLE', 'STRM_BGM35STAFFROLL'),
                'ssr2': ('STRM_TITLE',), 'ssr3': ('STRM_TITLE',)}


def build_stream_experiment(source, base, index=0, events=('1', '21', 'scene:communication'), song_gain_db=3.5):
    key = SOURCES.get(fingerprint(source)['sha256'])
    if key is None:
        raise ValueError('Requires a verified original Japanese Star Force ROM')
    family = key[:4]
    if type(index) is not int or not 0 <= index < len(STREAM_NAMES[family]):
        raise ValueError('Stream index outside pinned archive inventory')
    spec = SOURCE_ARCHIVES[family]
    raw_sdat = nds_sdat(source, spec['file_id'])
    if fingerprint(raw_sdat)['sha256'] != spec['sha256']:
        raise ValueError('Pinned SDAT fingerprint mismatch')
    archive = SoundArchive(raw_sdat)
    file_id, reserved, volume, priority, player, unknown = struct.unpack('<HH4B', archive.info(7, index, 8))
    # STRM contains HEAD then DATA; SoundArchive.file targets SSEQ/SBNK/SWAR DATA layouts.
    fat = archive.blocks['FAT ']
    count = struct.unpack('<I', fat.read(8, 4))[0]
    if file_id >= count:
        raise ValueError('STRM FAT file ID outside archive')
    offset, size = struct.unpack('<II', fat.read(12 + file_id * 16, 8))
    raw = archive.reader.read(offset, size)
    blob, dependency, conversion = convert_stream(raw, volume, song_gain_db)
    conversion['stream_info'] = {'index': index, 'file_id': file_id, 'volume': volume,
                                 'priority': priority, 'player': player}
    result = pack_converted_experiment(source, base, key, raw_sdat, 0,
                                      STREAM_NAMES[family][index], blob, dependency,
                                      conversion, events=events)
    manifest = result[2]
    record = manifest['nds_conversion']
    record.pop('sequence_index'); record.pop('sequence_name')
    record.update(source_kind='STRM', stream_index=index, stream_name=STREAM_NAMES[family][index],
                  strm_fingerprint=fingerprint(raw))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stream-index', type=int, default=0)
    parser.add_argument('--song-gain-db', type=float, default=3.5)
    args = parser.parse_args()
    result = build_stream_experiment(args.source.read_bytes(), args.base.read_bytes(),
                                    args.stream_index, song_gain_db=args.song_gain_db)
    args.output.mkdir(parents=True, exist_ok=False)
    rom, patch, manifest, conversion, dependency, blob, catalog, sdat = result
    for name, data in [('unified.gba',rom), ('unified.bps',patch), ('converted-mplay.bin',blob)]:
        (args.output/name).write_bytes(data)
    for name, data in [('build.json',manifest), ('conversion.json',conversion),
                       ('dependencies.json',dependency), ('catalog.json',catalog)]:
        (args.output/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(manifest['output_fingerprint']))


if __name__ == '__main__':
    main()
