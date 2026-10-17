"""Checked track merging for the Star Force 3 battle experiment.

No notes are discarded. Shared expression/pitch must agree at every control
boundary. Different fixed gains and note-on pan are retained per source.
GBA release-tail controls and volume quantization remain fidelity limits.
"""
import math
import struct
from dataclasses import replace

from analyze_song import analyze
from nds_music import (ROM_BASE, DS_CLOCK_HZ, GBA_FPS,
                       convert_envelope, fit_attack_parameter, level, note_bytes, trace_sequence, wait_bytes)
from nds_lfo import compare_config, map_pitch_lfo, note_lfo_commands

BATTLE_GROUPS = ((0, 9), (1,), (2, 15), (3,), (4, 14), (5,), (6,), (7,))


def validate_loop_notes(track, base, loop_start, period):
    """Check an intro and two whole musical loops, including boundary EOTs.

    The independent decoder closes at a repeated command state, which can be
    between commands at the same tick. Its event prefix therefore need not
    contain every event at its final timestamp, or the EOT for its last TIE.
    Unfold the decoded command cycle, preserving event order, before comparing
    complete time windows with the source schedule.
    """
    if track['termination'] != 'repeated_state' or track['loop_ticks'] != period:
        raise AssertionError('Compiled loop period differs from source')
    horizon = loop_start + 2 * period
    events = track['events']
    body = events[track['loop_start_event']:]
    if not body or track['loop_start_ticks'] > loop_start + period:
        raise AssertionError('Compiled loop does not cover the source window')

    def unfolded():
        yield from events
        turn = 1
        while body[0]['ticks'] + turn * period <= horizon:
            for event in body:
                yield {**event, 'ticks': event['ticks'] + turn * period}
            turn += 1

    actual, live_ties = [], {}
    for event in unfolded():
        tick = event['ticks']
        if tick > horizon:
            break
        if event['name'] in ('NOTE', 'TIE') and tick < horizon:
            row = [tick, event['voice'], event['key'], event['velocity'], event.get('duration_ticks')]
            actual.append(row)
            if event['name'] == 'TIE':
                if event['key'] in live_ties:
                    raise AssertionError('Converted long notes share a live alias')
                live_ties[event['key']] = row
        elif event['name'] == 'EOT':
            if event['key'] not in live_ties:
                raise AssertionError('EOT has no matching tied note')
            row = live_ties.pop(event['key'])
            row[4] = tick - row[0]
    if live_ties:
        raise AssertionError('Unclosed tied notes in compiled loop')
    expected = base + [[a[0] + period, *a[1:]] for a in base if a[0] >= loop_start]
    if actual != expected:
        raise AssertionError('Merged note/gate/timing model differs')
    return {'checked_until_ticks': horizon, 'complete_loop_cycles': 2,
            'note_events_compared': len(actual), 'boundary_eot_included': True}


def expand_actions(track, end_tick):
    actions = []
    for action in track['actions']:
        if action['ticks'] < end_tick:
            actions.append(dict(action))
    if track['termination'] != 'loop':
        return actions
    body = track['actions'][track['loop_action']:]
    for turn in range(1, 1 + end_tick // track['loop_ticks']):
        shift = turn * track['loop_ticks']
        for action in body:
            if action['ticks'] + shift >= end_tick:
                continue
            copied = {**action, 'ticks': action['ticks'] + shift}
            if 'end_ticks' in copied:
                copied['end_ticks'] += shift
            actions.append(copied)
    return actions


def state_series(actions, field, default):
    result = [(0, default)]
    for action in actions:
        if 'state_after' not in action:
            continue
        value = action['state_after'][field]
        if value != result[-1][1]:
            if result[-1][0] == action['ticks']:
                result[-1] = (action['ticks'], value)
            else:
                result.append((action['ticks'], value))
    return result


def series_at(series, tick):
    value = series[0][1]
    for start, current in series:
        if start > tick:
            break
        value = current
    return value


def pitch_series(actions):
    result = [(0, 0)]
    for action in actions:
        state = action.get('state_after')
        if state is None:
            continue
        value = (state['bend'] * state['bend_range']) >> 1
        if value != result[-1][1]:
            if result[-1][0] == action['ticks']:
                result[-1] = (action['ticks'], value)
            else:
                result.append((action['ticks'], value))
    return result


def pitch_commands(units):
    """Encode DS's 1/64-semitone bend in MPlay BEND + signed TUNE."""
    bend = max(-64, min(63, round(units / 12)))
    tune = units - bend * 12
    if not -64 <= tune <= 63:
        raise ValueError('Pitch bend exceeds research MPlay range')
    return bytes([0xC1, 12, 0xC0, 64 + bend, 0xC8, 64 + tune])


def assess_groups(tracks, groups):
    ids = {t['track'] for t in tracks}
    flat = [n for group in groups for n in group]
    if len(set(flat)) != len(flat) or set(flat) != ids:
        raise ValueError('Track groups must include each source track exactly once')
    if any(t['termination'] != 'loop' for t in tracks):
        raise ValueError('Merged experiment requires looping source tracks')
    periods = {t['loop_ticks'] for t in tracks}
    if len(periods) != 1:
        raise ValueError('Merged experiment requires a common loop period')
    period = next(iter(periods))
    loop_start = max(t['loop_start_ticks'] for t in tracks)
    end_tick = loop_start + period
    by_id = {t['track']: t for t in tracks}
    expanded = {n: expand_actions(t, end_tick + period) for n, t in by_id.items()}
    decisions = []
    for group in groups:
        members = list(group)
        decision = {'source_tracks': members, 'shared_expression': True, 'shared_pitch': True}
        if len(group) > 1:
            for name, get in [('expression', lambda a: state_series(a, 'expression', 127)),
                              ('pitch', pitch_series)]:
                series = {n: get(expanded[n]) for n in group}
                boundaries = sorted({tick for values in series.values() for tick, _ in values})
                if any(len({series_at(series[n], tick) for n in group}) > 1 for tick in boundaries):
                    raise ValueError(f'Tracks {members} have incompatible {name} controls')
            for n in group:
                actions = expanded[n]
                volumes = state_series(actions, 'volume', 127)
                if len({value for _, value in volumes}) != 1:
                    raise ValueError('Merged track volume must remain fixed')
                pan = state_series(actions, 'pan', 64)
                notes = [a for a in actions if a['name'] == 'note']
                for tick, _ in pan[1:]:
                    if any(a['ticks'] < tick < a['ticks'] + a['duration'] for a in notes):
                        raise ValueError(f'Track {n} changes pan during a held note')
            decision['pan_method'] = 'Per-note instrument pan; changes occur without a held note'
            decision['volume_method'] = 'Fixed source-volume ratio in note velocity; shared expression remains live'
        decisions.append(decision)
    return loop_start, period, expanded, decisions


def convert_merged_song(archive, index, groups, track_capacity=8, song_gain_db=0.0,
                        native_pitch_lfo=False, envelope_support=False, native_pitch_lfo_delay=False,
                        native_pitch_lfo_live_depth=False):
    if type(song_gain_db) not in (int, float) or not math.isfinite(song_gain_db) or not -24 <= song_gain_db <= 12:
        raise ValueError('Song gain must be finite and within -24..12 dB')
    if len(groups) > track_capacity:
        raise ValueError('Merged NDS sequence exceeds target track capacity')
    data, info = archive.sequence(index)
    tracks = trace_sequence(data, analysis_only=True)
    if native_pitch_lfo_delay and not native_pitch_lfo:
        raise ValueError('Delay approximation requires native pitch LFO mode')
    if native_pitch_lfo_live_depth and not (native_pitch_lfo and native_pitch_lfo_delay):
        raise ValueError('Live depth approximation requires native pitch LFO delay mode')
    depth_changes, initializations = [], []
    if native_pitch_lfo_delay:
        fields = ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay')
        for track in tracks:
            notes = [a for a in track['actions'] if a['name'] == 'note']
            active = [i for i, a in enumerate(track['actions'])
                      if a.get('state_after', {}).get('mod_depth') and
                      (a['state_after']['mod_delay'] or native_pitch_lfo_live_depth)]
            if not active:
                continue
            activation = active[0]
            baseline = tuple(track['actions'][activation]['state_after'][k] for k in fields)
            if not notes or track['actions'][activation]['ticks'] > notes[0]['ticks']:
                raise ValueError('Delayed LFO requires activation before or at the first note timestamp')
            initializations.append({'source_track': track['track'],
                                    'activation_tick': track['actions'][activation]['ticks'],
                                    'first_note_tick': notes[0]['ticks'], 'depth': baseline[2]})
            for i, a in enumerate(track['actions']):
                if a['name'] != 'note':
                    continue
                current = tuple(a['state_after'][k] for k in fields)
                # Some originals enable depth just after their first note at
                # the same tick. No DS timer update has elapsed in between.
                initial_off = i < activation and a['ticks'] == notes[0]['ticks'] and current[2] == 0
                live_depth = (native_pitch_lfo_live_depth and current[2] > 0 and
                              current[:2] + current[3:] == baseline[:2] + baseline[3:])
                if current != baseline and not live_depth and not (initial_off and current[:2] + current[3:] == baseline[:2] + baseline[3:]):
                    raise ValueError('Delayed LFO requires fixed per-track modulation after initial activation')
            previous_depth = baseline[2]
            for a in track['actions'][activation + 1:]:
                if a['opcode'] not in (0xCA, 0xCB, 0xCC, 0xCD, 0xE0):
                    continue
                current = tuple(a['state_after'][k] for k in fields)
                if current == baseline and not native_pitch_lfo_live_depth:
                    continue
                if not (native_pitch_lfo_live_depth and current[2] > 0 and
                        current[:2] + current[3:] == baseline[:2] + baseline[3:]):
                    raise ValueError('Live delayed-LFO parameter changes are outside this experiment')
                if current[2] != previous_depth:
                    depth_changes.append({'source_track': track['track'], 'ticks': a['ticks'],
                                          'before': previous_depth, 'after': current[2]})
                previous_depth = current[2]
    if envelope_support and any(len(group) != 1 for group in groups):
        raise ValueError('Envelope experiment requires singleton target tracks')
    # Audit mode records effects broadly; this compiler accepts only the
    # specifically implemented controls, never silently drops active effects.
    permitted = {0xFE, 0xC0, 0xC1, 0xC4, 0xC5, 0xC6, 0xC7,
                 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xD4, 0xD5, 0xE0, 0xE1}
    if envelope_support:
        permitted.update((0xD0, 0xD1, 0xD2, 0xD3))
    for track in tracks:
        for action in track['actions']:
            if action['name'] == 'control':
                op = action['opcode']
                if 0xD0 <= op <= 0xD3 and not 0 <= action['value'] <= 127:
                    raise ValueError('Envelope override outside supported 0..127 range')
                if op not in permitted or (op == 0xCE and action['value']) or (op == 0xCA and action['value'] and not native_pitch_lfo):
                    raise ValueError(f'Unsupported merged-conversion effect {op:#x}')
                if op == 0xE1 and track['track'] != 0:
                    raise ValueError('Merged experiment requires tempo in source track 0')
            if action['name'] == 'note' and not 1 <= action['duration'] <= 65535:
                raise ValueError('Unsupported merged note duration')
    loop_start, period, expanded, decisions = assess_groups(tracks, groups)
    lfo_tempo, lfo_configs = None, {}
    if native_pitch_lfo:
        if any(len(group) != 1 for group in groups):
            raise ValueError('Native pitch LFO experiment requires one source track per target track')
        tempos = {a['value'] for t in tracks for a in t['actions'] if a['opcode'] == 0xE1}
        if len(tempos) != 1:
            raise ValueError('Native pitch LFO experiment requires a fixed tempo')
        lfo_tempo = round(tempos.pop() * DS_CLOCK_HZ * 75 / (240 * GBA_FPS))
        # A common timestamp can fall inside a source's partial-tick loop
        # closure. Compile a complete warmup period before looping this mode.
        loop_start += period
        expanded = {t['track']: expand_actions(t, loop_start + 2 * period) for t in tracks}
        for actions in expanded.values():
            for order, action in enumerate(actions):
                action['event_order'] = order
        for t in tracks:
            for a in t['actions']:
                if a['name'] == 'note' or (a['name'] == 'control' and a['opcode'] == 0xCA and a['value']):
                    state = a['state_after']
                    map_pitch_lfo(state, lfo_tempo, native_pitch_lfo_delay)
                    if state['mod_depth']:
                        key = tuple(state[k] for k in ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay'))
                        lfo_configs[key] = compare_config(state, lfo_tempo, native_pitch_lfo_delay)
    end_tick = loop_start + period
    bank, archives = archive.bank(info['bank_id'])
    source_map = {n: i for i, group in enumerate(groups) for n in group}
    gain = 10 ** (song_gain_db / 20)
    group_volume = {}
    for i, group in enumerate(groups):
        group_volume[i] = max(a['state_after']['volume'] for n in group
                              for a in expanded[n] if a['name'] == 'note')
    source_notes = []
    for n, actions in expanded.items():
        for action in actions:
            if action['name'] == 'note' and action['ticks'] < end_tick:
                source_notes.append({**action, 'source_track': n, 'target_track': source_map[n]})
    source_notes.sort(key=lambda a: (a['ticks'], a['source_track']))
    priorities = sorted({a['state_after']['priority'] for a in source_notes})
    priority_map = {value: i for i, value in enumerate(priorities)}
    if len(priorities) > 32:
        raise ValueError('Too many music priorities for native-effect headroom')
    # Long notes use TIE/EOT. Distinct aliases keep overlapping source/echo
    # notes with the same pitch independently stoppable after track merging.
    aliases = {}
    for i, group in enumerate(groups):
        notes = [a for a in source_notes if a['target_track'] == i]
        used = {a['key'] for a in notes}
        free = [key for key in range(127, -1, -1) if key not in used]
        contexts = sorted({(a['source_track'], a['key']) for a in notes if a['duration'] > 223})
        if len(contexts) > len(free):
            raise ValueError('Not enough note keys for independent long-note aliases')
        for context, alias in zip(contexts, free):
            aliases[i, *context] = alias
            intervals = sorted((a['ticks'], a['ticks'] + a['duration']) for a in notes
                               if (a['source_track'], a['key']) == context and a['duration'] > 223)
            if any(start < end for (_, end), (start, _) in zip(intervals, intervals[1:])):
                raise ValueError('Overlapping long notes require more aliases')
            if any(start < loop_start < end or start < end_tick < end for start, end in intervals):
                raise ValueError('Long note crosses merged loop boundary')
    voice_contexts, mappings = {}, []
    for note in source_notes:
        group = note['target_track']
        pan_shift = note['state_after']['pan'] - 64 if len(groups[group]) > 1 else 0
        context = (note['instrument'], pan_shift)
        if envelope_support:
            definition = archive.note_definition(bank, note['instrument'], note['key'])
            envelope = {field: note['state_after'][field] if note['state_after'][field] is not None
                        else getattr(definition, field) for field in ('attack', 'decay', 'sustain', 'release')}
            note['source_envelope'] = envelope
            context += tuple(envelope.values())
        if context not in voice_contexts:
            voice_contexts[context] = len(voice_contexts)
        played_key = aliases.get((group, note['source_track'], note['key']), note['key']) if note['duration'] > 223 else note['key']
        ratio = level(note['state_after']['volume']) / level(group_volume[group]) if len(groups[group]) > 1 else 1.0
        velocity = round(127 * level(note['velocity']) * ratio)
        note.update(gba_voice=voice_contexts[context], gba_key=played_key,
                    gba_velocity=velocity, pan_shift=pan_shift,
                    gba_priority=priority_map[note['state_after']['priority']])
        mappings.append({'tick': note['ticks'], 'source_track': note['source_track'],
                         'source_instrument': note['instrument'], 'source_key': note['key'],
                         'source_velocity': note['velocity'], 'duration': note['duration'],
                         'target_track': group, 'gba_voice': note['gba_voice'],
                         'gba_key': played_key, 'gba_velocity': velocity,
                         'long_note': note['duration'] > 223})
        if envelope_support:
            mappings[-1]['source_envelope'] = note['source_envelope']
    if len(voice_contexts) > 128:
        raise ValueError('Merged voice contexts exceed GBA bank capacity')
    output = bytearray((index + 1) * 8)

    def allocate(raw):
        output.extend(bytes(-len(output) % 4))
        offset = len(output)
        output.extend(raw)
        return offset

    bank_offset = allocate(bytes(128 * 12))
    tone_map, wave_cache, sample_reports = {}, {}, []
    for note in source_notes:
        definition = archive.note_definition(bank, note['instrument'], note['key'])
        if envelope_support:
            definition = replace(definition, **note['source_envelope'])
        if definition.kind != 1 or not 0 <= definition.archive_slot < len(archives):
            raise ValueError('Merged experiment requires valid PCM instruments')
        source_wave = (archives[definition.archive_slot], definition.wave_id)
        cache_key = (*source_wave, definition.root_key)
        if cache_key not in wave_cache:
            pcm, metadata = archive.wave(*source_wave)
            frequency = round(metadata['effective_rate_hz'] * 2 ** ((60 - definition.root_key) / 12) * 1024)
            if not 0 < frequency < 2 ** 32:
                raise ValueError('Converted wave frequency out of range')
            pcm8 = bytes(max(-128, min(127, round(x / 256))) & 255 for x in pcm)
            raw = struct.pack('<HHIII', 0, 0x4000 if metadata['looped'] else 0,
                              frequency, metadata['loop_start_samples'], len(pcm8)) + pcm8
            wave_cache[cache_key] = allocate(raw)
            sample_reports.append({**metadata, 'root_key': definition.root_key,
                                   'gba_frequency_raw': frequency, 'gba_wave_offset': wave_cache[cache_key],
                                   'pcm8_bytes': len(pcm8)})
        pan = max(0, min(127, definition.pan + note['pan_shift']))
        raw = struct.pack('<BBBBI4B', 0, note['key'], 0, 128 + pan,
                          ROM_BASE + wave_cache[cache_key], *convert_envelope(definition, envelope_support))
        site = (note['gba_voice'], note['gba_key'])
        if site in tone_map and tone_map[site] != raw:
            raise ValueError('Conflicting per-note alias/instrument definition')
        tone_map[site] = raw
    instrument_reports = []
    for context, voice in voice_contexts.items():
        children = allocate(bytes(128 * 12))
        keys = sorted(key for v, key in tone_map if v == voice)
        for key in keys:
            output[children + key * 12:children + (key + 1) * 12] = tone_map[voice, key]
        struct.pack_into('<BBBBI4B', output, bank_offset + voice * 12,
                         0x80, 0, 0, 0, ROM_BASE + children, 0, 0, 0, 0)
        instrument_reports.append({'instrument_id': voice, 'source_instrument': context[0],
                                   'pan_shift': context[1], 'keys': keys, 'gba_children_offset': children})
        if envelope_support:
            instrument_reports[-1]['source_envelope'] = dict(zip(('attack', 'decay', 'sustain', 'release'), context[2:]))
            instrument_reports[-1]['gba_envelope'] = list(tone_map[voice, keys[0]][8:12])
    track_offsets, schedules, tempo_reports = [], [], []

    def volume(value, expression):
        result = round(127 * level(info['volume']) * level(value) * level(expression) * gain)
        if result > 127:
            raise ValueError('Song gain exceeds MPlay VOL headroom')
        return result

    for group_index, group in enumerate(groups):
        events = []
        primary = group[0]
        # Expression and effective bend are proven equal for merged members.
        for action in expanded[primary]:
            if action['ticks'] >= end_tick or action['name'] != 'control':
                continue
            state, op = action['state_after'], action['opcode']
            command = b''
            if op == 0xE1:
                tempo = round(action['value'] * DS_CLOCK_HZ * 75 / (240 * GBA_FPS))
                if not 1 <= tempo <= 255:
                    raise ValueError('Tempo outside MPlay encoding')
                command = bytes([0xBB, tempo])
                tempo_reports.append({'nds_tempo': action['value'], 'gba_parameter': tempo,
                                      'nds_ticks_per_second': DS_CLOCK_HZ * action['value'] / 240,
                                      'gba_ticks_per_second': GBA_FPS * tempo / 75})
            elif op == 0xC0 and len(group) == 1:
                command = bytes([0xBF, action['value']])
            elif op in (0xC1, 0xD5):
                value = group_volume[group_index] if len(group) > 1 else state['volume']
                command = bytes([0xBE, volume(value, state['expression'])])
            elif op in (0xC4, 0xC5):
                command = pitch_commands((state['bend'] * state['bend_range']) >> 1)
            elif native_pitch_lfo and op in (0xCA, 0xCB, 0xCC, 0xCD, 0xE0):
                value = map_pitch_lfo(state, lfo_tempo, native_pitch_lfo_delay)
                command = (bytes([0xC4, value['mod']]) if native_pitch_lfo_live_depth and op == 0xCA
                           else bytes([0xC4, value['mod'], 0xC2, value['lfos']]))
            if command:
                order = 1 + action['event_order'] if native_pitch_lfo else 1
                events.append((action['ticks'], order, primary, command, None))
        for note in (a for a in source_notes if a['target_track'] == group_index):
            command = bytes([0xBA, note['gba_priority'], 0xBD, note['gba_voice']])
            if native_pitch_lfo:
                command += note_lfo_commands(note['state_after'], lfo_tempo, native_pitch_lfo_delay)
            if note['duration'] <= 223:
                command += note_bytes(note['gba_key'], note['gba_velocity'], note['duration'])
            else:
                command += bytes([0xCF, note['gba_key'], note['gba_velocity']])
                events.append((note['ticks'] + note['duration'], 0, note['source_track'],
                               bytes([0xCE, note['gba_key']]), None))
            order = 1 + note['event_order'] if native_pitch_lfo else 2
            events.append((note['ticks'], order, note['source_track'], command, note))
        events.append((loop_start, -1, 0, b'', None))
        events.sort(key=lambda event: event[:3])
        code = bytearray([0xBD, 0, 0xBE, volume(group_volume[group_index], 127), 0xBF, 64])
        code.extend(pitch_commands(0))
        tick, loop_position = 0, None
        for when, category, _, command, note in events:
            if when >= end_tick:
                continue
            code.extend(wait_bytes(when - tick))
            tick = when
            if category == -1:
                loop_position = len(code)
            code.extend(command)
        code.extend(wait_bytes(end_tick - tick))
        offset = allocate(code + b'\xB2' + bytes(4))
        struct.pack_into('<I', output, offset + len(code) + 1, ROM_BASE + offset + loop_position)
        track_offsets.append(offset)
        schedules.append({'source_tracks': list(group), 'target_track': group_index,
                          'loop_start_ticks': loop_start, 'loop_ticks': period})
    header = allocate(struct.pack('<BBBBI', len(groups), 0, 20, 128, ROM_BASE + bank_offset)
                      + struct.pack('<' + 'I' * len(groups), *(ROM_BASE + offset for offset in track_offsets)))
    struct.pack_into('<IHH', output, index * 8, ROM_BASE + header, 0, 0)
    blob = bytes(output)
    dependency = analyze(blob, 0, index)
    # Independent MPlay decoding verifies every note (including tied gates)
    # and alias root pitch against the complete source execution schedule.
    note_validation = []
    for group_index, track in enumerate(dependency['tracks']):
        base = [[a['ticks'], a['gba_voice'], a['gba_key'], a['gba_velocity'], a['duration']]
                for a in source_notes if a['target_track'] == group_index]
        try:
            note_validation.append(validate_loop_notes(track, base, loop_start, period))
        except AssertionError as error:
            raise AssertionError(f'{error} on track {group_index}') from error
    report = {'schema_version': 1, 'sequence_index': index, 'sequence_info': info,
              'source_track_count': len(tracks), 'track_count': len(groups), 'tracks': tracks,
              'track_groups': [list(group) for group in groups], 'merge_assessment': decisions,
              'merged_loop_start_ticks': loop_start, 'merged_loop_ticks': period,
              'note_mapping': mappings, 'target_schedules': schedules,
              'samples': sample_reports, 'instruments': instrument_reports,
              'tempo_mapping': tempo_reports, 'song_gain_db': song_gain_db, 'song_gain_linear': gain,
              'song_gain_scope': 'Imported sequence VOL commands only',
              'priority_mapping': {str(k): v for k, v in priority_map.items()}, 'song_priority': 20,
              'generated_bytes': len(blob), 'note_timing_check': True,
              'note_timing_validation': note_validation,
              'long_note_aliases': [{'target_track': group, 'source_track': source,
                                     'source_key': key, 'gba_key': alias}
                                    for (group, source, key), alias in aliases.items()],
              'limitations': ['DS envelopes and PCM/volume resolution retain the earlier GBA approximations.',
                              'Merged pan changes are applied at note-on; release-tail pan follows GBA behavior.',
                              'Fixed track-volume ratios quantize into note velocity.',
                              'Relative music priorities mapped below native effect priorities.',
                              'Target PCM voice allocation is separate from sequence track merging.',
                              'Independent source execution and actual GBA playback must still be validated.']}
    if native_pitch_lfo:
        report['native_pitch_lfo'] = {'approximation': True, 'configs': list(lfo_configs.values()),
                                    'method': 'MPlay triangle pitch LFO; reset on every note with one-tick onset delay',
                                    'limitations': ['DS sine replaced by coarsely quantized triangle.',
                                                    'Track phase is shared; new notes reset older overlapping voices.',
                                                    'Release tails follow shared GBA phase rather than independent DS phase.']}
    if envelope_support:
        attacks = sorted({n['source_envelope']['attack'] for n in source_notes})
        report['envelope_approximation'] = {
            'method': 'Note-on ADSR snapshots in independent rhythm-bank voice contexts; fitted native GBA attack',
            'overrides_affect_existing_voices': False,
            'attack_fits': [{'ds_attack': a, 'gba_attack': fit_attack_parameter(a)[0],
                             'rms_amplitude_error': fit_attack_parameter(a)[1],
                             'max_amplitude_error': fit_attack_parameter(a)[2],
                             'ds_timer_updates_to_peak': fit_attack_parameter(a)[3]} for a in attacks],
            'limitations': ['Attack-only fitting at zero-aligned model updates; onset phase may differ by one GBA frame.',
                            'GBA linear amplitude attack approximates DS exponential attenuation attack.',
                            'Decay, sustain and release retain the existing GBA quantization and frame-rate approximation.']}
    if native_pitch_lfo_delay:
        report['native_pitch_lfo']['method'] = 'MPlay triangle pitch LFO; shared phase reset per note with quantized fixed-delay LFODL'
        report['native_pitch_lfo']['delay_approximation'] = {
            'policy': 'Fixed per-track delayed modulation initialized before or at the first note timestamp, including depth enabled after that note at the same tick; no live parameter changes',
            'method': 'Round DS timer delay to sequence ticks, plus the existing one-tick zero-phase onset',
            'initializations': initializations,
            'limitations': ['Delay and phase belong to the target track, not independent source voices.',
                            'New notes reset the shared delay/phase for overlapping voices and release tails.',
                            'LFODL is limited to 255 ticks; overflowing delays are rejected.']}
    if native_pitch_lfo_live_depth:
        report['native_pitch_lfo']['live_depth_approximation'] = {
            'policy': 'Positive depth changes only after initial activation; fixed pitch type, speed, range and delay',
            'method': 'Ordered MOD updates without resetting shared phase or delay count; note-on resets remain',
            'source_depth_changes': depth_changes,
            'limitations': ['Positive source depths must map to nonzero native MOD values.',
                            'Disabling modulation, later activation and other live parameter changes remain rejected.',
                            'Depth updates use shared target phase for overlapping voices and release tails.']}
        report['native_pitch_lfo']['delay_approximation']['policy'] = report['native_pitch_lfo']['live_depth_approximation']['policy']
        report['native_pitch_lfo']['method'] = 'MPlay triangle pitch LFO; quantized fixed delay with live positive depth updates'
    return blob, dependency, report
