"""Bounded offline PCM16 -> per-key PCM8 bandlimiting, using only stdlib.

A Blackman-windowed sinc filters before downsampling. Looped waves use an
integer output period and a short prefix guard so convolution sees the same
periodic history on both sides of the stored loop. Tuning compensates the
rounded period. This does not change the native mixer or its voice budget.
"""
import math

MIX_RATE = 10512
PHASES = 256


def resample_wave(pcm, source_rate, key, root_key, looped=False, loop_start=0,
                  mixing_rate=MIX_RATE):
    if (not pcm or any(type(v) is not int or not -32768 <= v <= 32767 for v in pcm)
            or not isinstance(source_rate, (int, float)) or not math.isfinite(source_rate)
            or source_rate <= 0 or type(key) is not int or not 0 <= key <= 127
            or type(root_key) is not int or not 0 <= root_key <= 127
            or type(mixing_rate) is not int or not 8000 <= mixing_rate <= 48000
            or type(looped) is not bool or type(loop_start) is not int
            or not 0 <= loop_start < len(pcm)):
        raise ValueError('Invalid offline resampling input')
    pitched_rate = source_rate * 2 ** ((key - root_key) / 12)
    step = pitched_rate / mixing_rate
    if not 1 / 16 <= step <= 32:
        raise ValueError('Offline resampling ratio exceeds bounded range')
    period = len(pcm) - loop_start
    output_period = round(period / step) if looped else None
    if looped:
        if output_period < 16:
            raise ValueError('Resampled loop is too short')
        step = period / output_period
    # Normalized to input Nyquist; leave a transition band below output Nyquist.
    cutoff = .90 * min(1.0, 1 / step)
    radius = math.ceil(32 / cutoff)
    guard = math.ceil(radius / step) + 1
    prefix = round(loop_start / step) if looped else 0
    phase = loop_start - prefix * step if looped else 0.0
    target_loop = prefix + guard if looped else 0
    count = target_loop + output_period if looped else math.ceil(len(pcm) / step) + guard
    if count > 1_000_000:
        raise ValueError('Offline wave exceeds sample budget')
    kernels = {}

    def kernel(phase_index):
        if phase_index not in kernels:
            fraction = phase_index / PHASES
            weights = []
            for k in range(-radius, radius + 1):
                x = k - fraction
                if abs(x) >= radius:
                    w = 0.0
                else:
                    window = .42 + .5 * math.cos(math.pi * x / radius) + .08 * math.cos(2 * math.pi * x / radius)
                    w = (cutoff if x == 0 else math.sin(math.pi * cutoff * x) / (math.pi * x)) * window
                weights.append(w)
            total = sum(weights)
            kernels[phase_index] = [w / total for w in weights]
        return kernels[phase_index]

    result = bytearray()
    clipped = 0
    for i in range(count):
        position = phase + i * step
        origin = math.floor(position)
        weights = kernel(round((position - origin) * PHASES))
        value = 0.0
        for j, w in enumerate(weights, origin - radius):
            if j >= len(pcm) and looped:
                j = loop_start + (j - loop_start) % period
            if 0 <= j < len(pcm):
                value += pcm[j] * w
        quantized = round(value / 256)
        clipped += int(not -128 <= quantized <= 127)
        result.append(max(-128, min(127, quantized)) & 255)
    native_rate = pitched_rate / step
    frequency = round(native_rate * 1024 * 2 ** ((60 - key) / 12))
    if not 0 < frequency < 2 ** 32:
        raise ValueError('Offline converted frequency outside native range')
    actual_rate = frequency / 1024 * 2 ** ((key - 60) / 12)
    report = {'method': 'Blackman-windowed sinc, 32 lobes, 256 fractional phases, unity DC',
              'mixing_rate_hz': mixing_rate, 'source_pitched_rate_hz': pitched_rate,
              'source_samples': len(pcm), 'source_loop_start': loop_start,
              'output_samples': len(result), 'output_loop_start': target_loop,
              'output_loop_period': output_period, 'source_samples_per_output': step,
              'filter_cutoff_input_nyquist_fraction': cutoff,
              'filter_radius_source_samples': radius, 'prefix_guard_output_samples': guard,
              'initial_source_phase_samples': phase, 'native_playback_rate_hz': actual_rate,
              'pitch_error_cents': 1200 * math.log2(actual_rate * step / pitched_rate),
              'pcm8_clipped_samples': clipped,
              'loop_history': 'Original prefix followed by periodic extension; loop starts after filter guard' if looped else 'Zero extension; filter tail retained'}
    return bytes(result), frequency, target_loop, report
