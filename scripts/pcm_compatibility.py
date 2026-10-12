"""Rate adaptation for verified fixed-step PCM donors.

Type-8 PCM consumes one byte per target mixer output sample, regardless of its
wave header frequency or track pitch. Resample only its private relocated wave;
normal PCM sharing the original wave must retain the original encoded bytes.
"""
import json
from math import gcd
from pathlib import Path
import struct

from scan_audio import MAX_ROM_SIZE

PROFILES = json.loads((Path(__file__).resolve().parents[1]/'config/rom-profiles.json').read_text())['profiles']
FIXED_PCM_RATES = {p['fingerprint']['sha256']: p['fixed_pcm_rate']
                   for p in PROFILES if 'fixed_pcm_rate' in p}


def resample_fixed_pcm(wave, source_rate, target_rate):
    """Adapt signed 8-bit PCM using integer linear interpolation.

The result preserves duration within one target sample. No runtime pitch/tone
    flags change, so fixed-mode notes continue to ignore key, bend and modulation.
    Loops repeat enough source periods to give an exact integer target period.
"""
    if source_rate <= 0 or target_rate <= 0:
        raise ValueError('PCM rates must be positive')
    if source_rate == target_rate:
        return wave
    if len(wave) < 16:
        raise ValueError('Truncated PCM wave')
    kind, flags, frequency, loop_start, count = struct.unpack_from('<HHIII', wave)
    looped = bool(flags & 0x4000)
    if (kind != 0 or flags & ~0x4000 or count == 0 or len(wave) != 16+count
        or looped and loop_start >= count):
        raise ValueError('Fixed PCM rate conversion requires a valid uncompressed wave')
    if looped:
        prefix = (loop_start*target_rate+source_rate-1)//source_rate
        period = count-loop_start
        repeats = source_rate//gcd(source_rate, period*target_rate)
        size = prefix+period*repeats*target_rate//source_rate
    else:
        prefix = 0
        size = (count*target_rate+source_rate-1)//source_rate
    if 16+size > MAX_ROM_SIZE:
        raise ValueError('Resampled PCM exceeds GBA ROM size limit')
    payload = wave[16:]
    output = bytearray(size)
    for i in range(size):
        if looped and i >= prefix:
            index, fraction = divmod((i-prefix)*source_rate, target_rate)
            index = loop_start+index % period
        else:
            index, fraction = divmod(i*source_rate, target_rate)
        a = payload[index]
        a = a-256 if a >= 128 else a
        b = payload[index+1] if index+1 < count else payload[loop_start] if looped else 0
        b = b-256 if b >= 128 else b
        output[i] = ((a*(target_rate-fraction)+b*fraction+target_rate//2)//target_rate) & 255
    return struct.pack('<HHIII', kind, flags, target_rate*1024, prefix if looped else 0, size)+output
