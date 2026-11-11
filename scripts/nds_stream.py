"""Bounded STRM ADPCM decoding and experimental stereo PCM8 conversion.

This module does not register streams in the production manager. The decoder
uses independent vgmstream PCM/loop comparisons recorded in the source research.
"""
from array import array
import math
import struct

from analyze_song import analyze
from nds_music import IMA_INDEX, IMA_STEPS
from nds_resample import resample_wave
from scan_audio import ROM_BASE


def decode_stream(raw):
    """Decode checked, block-interleaved stereo NDS ADPCM to two PCM16 arrays."""
    raw = bytes(raw)
    if not 0x68 <= len(raw) <= 16_000_000:
        raise ValueError('STRM file size outside research bound')
    magic, bom, version, declared, header, sections = struct.unpack_from('<4sHHIHH', raw)
    if ((magic, bom, version, header, sections) != (b'STRM', 0xFEFF, 0x100, 16, 2)
            or not 104 <= declared <= len(raw) or len(raw) - declared > 4
            or any(raw[declared:])):
        raise ValueError('Unsupported STRM standard header')
    source_bytes = len(raw)
    raw = raw[:declared]
    if struct.unpack_from('<4sI', raw, 16) != (b'HEAD', 80):
        raise ValueError('Unsupported STRM HEAD layout')
    fields = struct.unpack_from('<4B2H16I', raw, 24)
    codec, looped, channels, _, rate, timer = fields[:6]
    start, count, offset, blocks, size, samples, last_size, last_samples, padded, *unknown = fields[6:]
    if codec != 2 or channels != 2 or looped != 1:
        raise ValueError('Research STRM requires looped stereo NDS ADPCM')
    if not 8000 <= rate <= 48000 or not 0 <= start < count <= 5_000_000:
        raise ValueError('STRM rate, sample count or loop outside research bound')
    if (offset != 104 or blocks < 1 or size != 512 or samples != 1016
            or not 4 < last_size <= size or not 1 <= last_samples <= (last_size - 4) * 2
            or (last_size - 4) * 2 - last_samples > 1 or padded != 0
            or count != (blocks - 1) * samples + last_samples):
        raise ValueError('Inconsistent STRM block sizes or sample counts')
    if struct.unpack_from('<4sI', raw, 96) != (b'DATA', len(raw) - 96):
        raise ValueError('Inconsistent STRM DATA size')
    end = offset + (blocks - 1) * size * channels + last_size * channels
    aligned = (end + 3) & ~3
    if aligned > len(raw) or len(raw) - aligned > 4 or any(raw[end:]):
        raise ValueError('STRM payload size or trailing padding mismatch')
    output = [array('h') for _ in range(channels)]
    pos = offset
    for block in range(blocks):
        length = last_size if block == blocks - 1 else size
        emit = last_samples if block == blocks - 1 else samples
        for channel in output:
            predictor, index = struct.unpack_from('<hH', raw, pos)
            if index > 88:
                raise ValueError('STRM ADPCM initial index outside 0..88')
            for i in range(emit):
                byte = raw[pos + 4 + i // 2]
                nibble = (byte >> (4 * (i % 2))) & 15
                step = IMA_STEPS[index]
                delta = ((step >> 3) + (step if nibble & 4 else 0)
                         + ((step >> 1) if nibble & 2 else 0)
                         + ((step >> 2) if nibble & 1 else 0))
                predictor = max(-32767, min(32767, predictor + (-delta if nibble & 8 else delta)))
                index = max(0, min(88, index + IMA_INDEX[nibble & 7]))
                channel.append(predictor)
            pos += length
        pos = (pos + 3) & ~3
    return output, {'encoding': 'NDS ADPCM', 'channels': channels, 'sample_rate_hz': rate,
                    'timer_raw': timer, 'source_sample_count': count, 'source_loop_start': start,
                    'blocks': blocks, 'source_bytes': source_bytes, 'declared_bytes': declared}


def convert_stream(raw, source_volume, song_gain_db=3.5):
    """Experimental two-TIE export; sample loops run independently of MPlay ticks.

    Source volume uses an explicit linear policy for this experiment. DS runtime
    master/player gain, fades and effects are not reproduced or claimed exact.
    The existing resampler's one-million-sample bound remains in effect.
    """
    if type(source_volume) is not int or not 0 <= source_volume <= 127:
        raise ValueError('STRM source volume outside 0..127')
    if type(song_gain_db) not in (int, float) or not math.isfinite(song_gain_db) or not -24 <= song_gain_db <= 12:
        raise ValueError('STRM gain must be finite and within -24..12 dB')
    volume = round(source_volume * 10 ** (song_gain_db / 20))
    if volume > 127:
        raise ValueError('STRM gain exceeds native volume headroom')
    channels, info = decode_stream(raw)
    output = bytearray(8)
    def allocate(data):
        output.extend(bytes(-len(output) % 4))
        site = len(output)
        output.extend(data)
        return site
    bank = allocate(bytes(128 * 12))
    reports = []
    for i, channel in enumerate(channels):
        pcm, frequency, loop, report = resample_wave(channel, info['sample_rate_hz'], 60, 60,
                                                    True, info['source_loop_start'])
        wave = allocate(struct.pack('<HHIII', 0, 0x4000, frequency, loop, len(pcm)) + pcm)
        struct.pack_into('<BBBBI4B', output, bank + 12 * i, 0, 60, 0, 0,
                         ROM_BASE + wave, 255, 0, 255, 0)
        reports.append({**report, 'channel': i, 'wave_file_offset': wave,
                        'gba_frequency_raw': frequency})
    tracks = []
    for i, pan in enumerate((0, 127)):
        code = bytes([0xBB, 75, 0xBD, i, 0xBE, volume, 0xBF, pan, 0xCF, 60, 127, 0xB0])
        track = allocate(code + b'\xB2' + bytes(4))
        struct.pack_into('<I', output, track + len(code) + 1, ROM_BASE + track + len(code) - 1)
        tracks.append(track)
    header = allocate(struct.pack('<BBBBIII', 2, 0, 20, 128, ROM_BASE + bank,
                                  *(ROM_BASE + t for t in tracks)))
    struct.pack_into('<IHH', output, 0, ROM_BASE + header, 0, 0)
    blob = bytes(output)
    dependency = analyze(blob, 0, 0)
    for track in dependency['tracks']:
        assert sum(e['name'] == 'TIE' for e in track['events']) == 1
        assert not any(e['name'] in ('NOTE', 'EOT', 'FINE') for e in track['events'])
    conversion = {**info, 'track_count': 2, 'native_track_volume': volume,
                  'source_volume_raw': source_volume, 'song_gain_db': song_gain_db,
                  'song_gain_scope': 'Linear STRM metadata volume times requested dB gain; DS runtime fades/master effects not modeled',
                  'note_timing_check': 'Two simultaneous TIEs at tick0; no sequence NOTE retrigger, loops reside in PCM headers',
                  'channel_resampling': reports, 'experimental_strm': True}
    return blob, dependency, conversion
