"""Bounded pitch-only DS sine -> native MPlay triangle LFO approximation.

DS phases belong to voices; MPlay phases belong to tracks. Resetting at each
note approximates a fresh voice and also resets older overlapping voices.
This is deliberately not an exact synthesis claim.
"""
import math

from nds_music import DS_CLOCK_HZ, GBA_FPS

SINE_QUARTER = (0, 6, 12, 19, 25, 31, 37, 43, 49, 54, 60, 65, 71, 76, 81,
                85, 90, 94, 98, 102, 106, 109, 112, 115, 117, 120, 122, 123,
                125, 126, 126, 127, 127)


def ds_sine(index):
    if not 0 <= index < 128:
        raise ValueError('DS LFO sine index outside 0..127')
    if index < 32:
        return SINE_QUARTER[index]
    if index < 64:
        return SINE_QUARTER[64 - index]
    if index < 96:
        return -SINE_QUARTER[index - 64]
    return -SINE_QUARTER[128 - index]


def ds_pitch_units(phase, depth, span=1):
    if not 0 <= phase < 32768:
        raise ValueError('DS LFO phase outside 0..32767')
    return (ds_sine(phase >> 8) * span * depth) >> 8


def gba_lfo_value(phase, depth):
    if not 0 <= phase <= 255 or not 0 <= depth <= 127:
        raise ValueError('MPlay LFO parameter outside encoding range')
    point = 128 - phase if 64 <= phase < 192 else phase if phase < 128 else phase - 256
    return (point * depth) >> 6


def map_pitch_lfo(state, gba_tempo):
    depth, speed, span = (state[k] for k in ('mod_depth', 'mod_speed', 'mod_range'))
    if not all(type(v) is int and 0 <= v <= 127 for v in (depth, speed, span)):
        raise ValueError('Invalid DS LFO parameter')
    if not depth:
        return {'lfos': 0, 'mod': 0}
    if state['mod_type'] != 0 or state['mod_delay'] != 0 or not speed or not span:
        raise ValueError('Native LFO experiment supports active pitch modulation with zero DS delay and nonzero speed/range only')
    if not 1 <= gba_tempo <= 255:
        raise ValueError('Invalid MPlay tempo')
    tick_rate = GBA_FPS * gba_tempo / 75
    lfos = round(DS_CLOCK_HZ * speed / (2 * tick_rate))
    mod = round(127 * span * depth / 1024)
    if not 1 <= lfos <= 255 or not 1 <= mod <= 127:
        raise ValueError('DS LFO cannot be represented by the bounded native approximation')
    return {'lfos': lfos, 'mod': mod}


def note_lfo_commands(state, gba_tempo):
    value = map_pitch_lfo(state, gba_tempo)
    # LFOS=0 resets phase/value; a one-tick LFODL keeps onset at zero.
    return bytes([0xC2, 0, 0xC5, 0, 0xC3, 1, 0xC4, value['mod'], 0xC2, value['lfos']])


def compare_config(state, gba_tempo):
    value = map_pitch_lfo(state, gba_tempo)
    tick_rate = GBA_FPS * gba_tempo / 75
    errors = []
    for millisecond in range(1000):
        t = millisecond / 1000
        source = ds_pitch_units((int(t * DS_CLOCK_HZ) * state['mod_speed'] * 64) % 32768,
                                state['mod_depth'], state['mod_range'])
        target = 4 * gba_lfo_value((int(t * tick_rate) * value['lfos']) % 256, value['mod'])
        errors.append((target - source) * 100 / 64)
    return {**{k: state[k] for k in ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay')},
            **value, 'gba_tempo': gba_tempo,
            'source_frequency_hz': DS_CLOCK_HZ * state['mod_speed'] / 512,
            'target_frequency_hz': tick_rate * value['lfos'] / 256,
            'single_voice_one_second_rms_pitch_error_cents': math.sqrt(sum(e * e for e in errors) / len(errors)),
            'single_voice_one_second_max_pitch_error_cents': max(map(abs, errors)),
            'comparison_scope': 'isolated fresh note, 1 ms sampling, no overlapping-note resets or audio-frame quantization'}
