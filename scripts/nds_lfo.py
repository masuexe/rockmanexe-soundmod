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


def map_pitch_delay(state, gba_tempo):
    delay = state['mod_delay']
    if type(delay) is not int or not 0 <= delay <= 65535:
        raise ValueError('Invalid DS LFO delay')
    if not 1 <= gba_tempo <= 255:
        raise ValueError('Invalid MPlay tempo')
    tick_rate = GBA_FPS * gba_tempo / 75
    shift = round(delay * tick_rate / DS_CLOCK_HZ)
    # Retain the one-tick zero-phase onset used by the zero-delay mode.
    if shift + 1 > 255:
        raise ValueError('DS LFO delay exceeds native LFODL capacity')
    return {'lfodl': shift + 1, 'phase_delay_ticks': shift,
            'source_delay_ms': delay * 1000 / DS_CLOCK_HZ,
            'target_phase_delay_ms': shift * 1000 / tick_rate,
            'phase_delay_error_ms': (shift / tick_rate - delay / DS_CLOCK_HZ) * 1000,
            'native_counter_wait_ms': (shift + 1) * 1000 / tick_rate}


def map_pitch_lfo(state, gba_tempo, allow_delay=False, allow_min_depth=False):
    depth, speed, span = (state[k] for k in ('mod_depth', 'mod_speed', 'mod_range'))
    if not all(type(v) is int and 0 <= v <= 127 for v in (depth, speed, span)):
        raise ValueError('Invalid DS LFO parameter')
    if not depth:
        return {'lfos': 0, 'mod': 0}
    if state['mod_type'] != 0 or (state['mod_delay'] != 0 and not allow_delay) or not speed or not span:
        raise ValueError('Native LFO experiment supports active pitch modulation with zero DS delay and nonzero speed/range only')
    if allow_delay:
        map_pitch_delay(state, gba_tempo)
    if not 1 <= gba_tempo <= 255:
        raise ValueError('Invalid MPlay tempo')
    tick_rate = GBA_FPS * gba_tempo / 75
    lfos = round(DS_CLOCK_HZ * speed / (2 * tick_rate))
    mod = round(127 * span * depth / 1024)
    quantized = not mod and allow_min_depth
    if quantized:
        mod = 1
        source = [ds_pitch_units(phase << 8, depth, span) for phase in range(128)]
        target = [4 * gba_lfo_value(phase, mod) for phase in range(256)]
        if max(abs(a-b) for a in source for b in target) * 100 / 64 > 10:
            raise ValueError('Minimum-depth LFO exceeds ten-cent absolute pitch difference bound')
    if not 1 <= lfos <= 255 or not 1 <= mod <= 127:
        raise ValueError('DS LFO cannot be represented by the bounded native approximation')
    result = {'lfos': lfos, 'mod': mod}
    if quantized:
        result['minimum_depth_quantized'] = True
        result['all_phase_pitch_difference_bound_cents'] = max(abs(a-b) for a in source for b in target) * 100 / 64
    return result


def note_lfo_commands(state, gba_tempo, allow_delay=False, allow_min_depth=False):
    value = map_pitch_lfo(state, gba_tempo, allow_delay, allow_min_depth)
    delay = map_pitch_delay(state, gba_tempo)['lfodl'] if allow_delay else 1
    # LFOS=0 resets phase/value; a one-tick LFODL keeps onset at zero.
    return bytes([0xC2, 0, 0xC5, 0, 0xC3, delay, 0xC4, value['mod'], 0xC2, value['lfos']])


def compare_config(state, gba_tempo, allow_delay=False, allow_min_depth=False):
    value = map_pitch_lfo(state, gba_tempo, allow_delay, allow_min_depth)
    delay = map_pitch_delay(state, gba_tempo) if allow_delay else None
    tick_rate = GBA_FPS * gba_tempo / 75
    errors = []
    for millisecond in range(1000):
        t = millisecond / 1000
        source_steps = max(0, int(t * DS_CLOCK_HZ) - (state['mod_delay'] if allow_delay else 0))
        target_steps = max(0, int(t * tick_rate) - (delay['phase_delay_ticks'] if delay else 0))
        source = ds_pitch_units((source_steps * state['mod_speed'] * 64) % 32768,
                                state['mod_depth'], state['mod_range'])
        target = 4 * gba_lfo_value((target_steps * value['lfos']) % 256, value['mod'])
        errors.append((target - source) * 100 / 64)
    result = {**{k: state[k] for k in ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay')},
            **value, 'gba_tempo': gba_tempo,
            'source_frequency_hz': DS_CLOCK_HZ * state['mod_speed'] / 512,
            'target_frequency_hz': tick_rate * value['lfos'] / 256,
            'single_voice_one_second_rms_pitch_error_cents': math.sqrt(sum(e * e for e in errors) / len(errors)),
            'single_voice_one_second_max_pitch_error_cents': max(map(abs, errors)),
            'comparison_scope': 'isolated fresh note, 1 ms sampling, no overlapping-note resets or audio-frame quantization'}
    if delay:
        result['delay_mapping'] = delay
    return result
