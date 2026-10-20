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
from nds_resample import MIX_RATE, resample_wave
from nds_lfo import compare_config, map_pitch_lfo, note_lfo_commands

BATTLE_GROUPS = ((0, 9), (1,), (2, 15), (3,), (4, 14), (5,), (6,), (7,))


def validate_finite_notes(track, base, end_tick):
    """Compare all finite note gates, explicit EOTs and the final FINE."""
    if track['termination'] != 'fine' or track['ticks_before_repeat'] != end_tick:
        raise AssertionError('Compiled finite track end differs from source')
    actual, ties = [], {}
    for event in track['events']:
        if event['name'] in ('NOTE', 'TIE'):
            row = [event['ticks'], event['voice'], event['key'], event['velocity'], event.get('duration_ticks')]
            actual.append(row)
            if event['name'] == 'TIE':
                if event['key'] in ties:
                    raise AssertionError('Converted long notes share a live alias')
                ties[event['key']] = row
        elif event['name'] == 'EOT':
            if event['key'] not in ties:
                raise AssertionError('EOT has no matching tied note')
            row = ties.pop(event['key'])
            row[4] = event['ticks'] - row[0]
    if ties:
        raise AssertionError('Unclosed tied notes before finite track end')
    if actual != base:
        raise AssertionError('Finite note/gate/timing model differs')
    return {'checked_until_ticks': end_tick, 'complete_finite_track': True,
            'note_events_compared': len(actual), 'explicit_eot_before_fine': True}


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
    expected = base + [[a[0] + period, *a[1:]] for a in base if a[0] >= loop_start]
    # Notes beginning in the last checked cycle may end after its jump.
    # Decode far enough to observe their EOT without counting later note-ons.
    gate_horizon = max([horizon] + [a[0] + a[4] for a in expected])
    events = track['events']
    body = events[track['loop_start_event']:]
    if not body or track['loop_start_ticks'] > loop_start + period:
        raise AssertionError('Compiled loop does not cover the source window')

    def unfolded():
        yield from events
        turn = 1
        while body[0]['ticks'] + turn * period <= gate_horizon:
            for event in body:
                yield {**event, 'ticks': event['ticks'] + turn * period}
            turn += 1

    actual, live_ties = [], {}
    for event in unfolded():
        tick = event['ticks']
        if tick > gate_horizon:
            break
        if event['name'] in ('NOTE', 'TIE') and tick < gate_horizon:
            row = [tick, event['voice'], event['key'], event['velocity'], event.get('duration_ticks')]
            if tick < horizon:
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
    if any(row[0] < horizon for row in live_ties.values()):
        raise AssertionError('Unclosed tied notes in compiled loop')
    if actual != expected:
        raise AssertionError('Merged note/gate/timing model differs')
    return {'checked_until_ticks': horizon, 'complete_loop_cycles': 2,
            'gate_checked_until_ticks': gate_horizon,
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


def assess_groups(tracks, groups, finite_support=False, mixed_loop_support=False, mixed_later_entry=False):
    if mixed_later_entry and not mixed_loop_support:
        raise ValueError('Later entry requires the explicit mixed score mode')
    if finite_support and mixed_loop_support:
        raise ValueError('Finite-only and mixed score modes are separate experiments')
    ids = {t['track'] for t in tracks}
    flat = [n for group in groups for n in group]
    if len(set(flat)) != len(flat) or set(flat) != ids:
        raise ValueError('Track groups must include each source track exactly once')
    if finite_support:
        if any(len(group) != 1 for group in groups) or any(t['termination'] != 'end' for t in tracks):
            raise ValueError('Finite experiment requires singleton, entirely finite source tracks')
        for track in tracks:
            notes = [a for a in track['actions'] if a['name'] == 'note']
            if not notes or any(a['ticks'] + a['duration'] > track['end_ticks'] for a in notes):
                raise ValueError('Finite notes must finish their gates before or at source END')
        return None, None, {t['track']: [dict(a) for a in t['actions']] for t in tracks}, [
            {'source_tracks': list(group), 'shared_expression': True, 'shared_pitch': True} for group in groups]
    looping = [t for t in tracks if t['termination'] == 'loop']
    finite = [t for t in tracks if t['termination'] == 'end']
    if mixed_loop_support:
        if finite_support or not looping or not finite or len(looping) + len(finite) != len(tracks):
            raise ValueError('Mixed experiment requires both finite and looping source tracks')
        if any(len(group) != 1 for group in groups):
            raise ValueError('Mixed experiment requires singleton source tracks')
        for track in finite:
            notes = [a for a in track['actions'] if a['name'] == 'note']
            if not notes or any(a['ticks'] + a['duration'] > track['end_ticks'] for a in notes):
                raise ValueError('Mixed finite notes must close their gates by source END')
    elif len(looping) != len(tracks):
        raise ValueError('Merged experiment requires looping source tracks')
    periods = {t['loop_ticks'] for t in looping}
    if mixed_loop_support:
        if any(p <= 0 for p in periods):
            raise ValueError('Mixed loop periods must be positive')
        period = math.lcm(*periods)
        if period > 16384 or any(period // p > 8 for p in periods):
            raise ValueError('Mixed common period exceeds bounded expansion budget')
    else:
        if len(periods) != 1:
            raise ValueError('Merged experiment requires a common loop period')
        period = next(iter(periods))
    loop_start = max(t['loop_start_ticks'] for t in looping)
    if mixed_loop_support and any(t['end_ticks'] > loop_start for t in finite):
        if not mixed_later_entry:
            raise ValueError('Mixed finite tracks must finish before the shared loop entry')
        advance = (max(t['end_ticks'] for t in finite) - loop_start + period - 1) // period
        if advance > 1:
            raise ValueError('Later mixed entry exceeds one additional common period')
        loop_start += advance * period
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
                        native_pitch_lfo_live_depth=False, native_pitch_lfo_live_toggle=False,
                        finite_support=False, bandlimited_pcm=False, finite_release_support=False,
                        mixed_loop_support=False, native_pitch_lfo_min_depth=False,
                        mixed_live_depth_support=False, native_pitch_lfo_late_depth=False):
    if type(song_gain_db) not in (int, float) or not math.isfinite(song_gain_db) or not -24 <= song_gain_db <= 12:
        raise ValueError('Song gain must be finite and within -24..12 dB')
    if len(groups) > track_capacity:
        raise ValueError('Merged NDS sequence exceeds target track capacity')
    if native_pitch_lfo_late_depth and not (
            native_pitch_lfo and native_pitch_lfo_delay and native_pitch_lfo_live_depth
            and not (mixed_loop_support or finite_support or finite_release_support or
                     bandlimited_pcm or native_pitch_lfo_live_toggle or envelope_support or native_pitch_lfo_min_depth)):
        raise ValueError('Late positive-depth activation requires looping singleton delayed live-depth mode without mixed, finite, filter, toggle, fitting or minimum-depth modes')
    if mixed_live_depth_support and not (
            mixed_loop_support and native_pitch_lfo and native_pitch_lfo_delay and native_pitch_lfo_live_depth
            and not (finite_support or finite_release_support or bandlimited_pcm or native_pitch_lfo_live_toggle)):
        raise ValueError('Mixed live-depth extension requires mixed singleton delayed positive-depth mode without finite-only, filter or toggle modes')
    if native_pitch_lfo_min_depth and not (native_pitch_lfo and (mixed_loop_support or native_pitch_lfo_live_depth)):
        raise ValueError('Minimum-depth LFO requires the explicit mixed or looping live-depth native-LFO experiment')
    if native_pitch_lfo_min_depth and native_pitch_lfo_live_depth and (
            (mixed_loop_support and not mixed_live_depth_support) or finite_support or finite_release_support or
            bandlimited_pcm or native_pitch_lfo_live_toggle):
        raise ValueError('Minimum-depth live LFO requires looping singleton tracks without mixed, finite, filter or toggle modes')
    if mixed_loop_support and (finite_support or finite_release_support or
                               (envelope_support and not mixed_live_depth_support) or bandlimited_pcm):
        raise ValueError('Mixed experiment excludes finite-only, envelope-fitting and filtered modes')
    if bandlimited_pcm and any(len(group) != 1 for group in groups):
        raise ValueError('Bandlimited PCM requires singleton target tracks')
    if bandlimited_pcm and native_pitch_lfo:
        raise ValueError('Bandlimited PCM excludes native LFO modes')
    data, info = archive.sequence(index)
    tracks = trace_sequence(data, analysis_only=True)
    if bandlimited_pcm and any(a.get('state_after', {}).get('bend', 0) > 0 or
                               any(a.get('state_after', {}).get(k, 0) for k in
                                   ('transpose', 'mod_depth', 'porta', 'sweep_pitch'))
                               for t in tracks for a in t['actions']):
        raise ValueError('Bandlimited PCM excludes upward bend, transpose, modulation and portamento')
    if finite_release_support and (not finite_support or envelope_support or native_pitch_lfo):
        raise ValueError('Finite release snapshots require finite mode without LFO or fitted attacks')
    envelope_snapshots = envelope_support or finite_release_support
    if finite_support and (native_pitch_lfo or envelope_support):
        raise ValueError('Finite experiment currently excludes native LFO and fitted-envelope modes')
    if finite_support and len({a['value'] for t in tracks for a in t['actions'] if a['opcode'] == 0xE1}) != 1:
        raise ValueError('Finite experiment currently requires a fixed source tempo')
    if finite_release_support:
        for track in tracks:
            seen_note = False
            for action in track['actions']:
                if action['name'] == 'note':
                    seen_note = True
                if action['opcode'] == 0xD3 and seen_note:
                    raise ValueError('Finite release override must precede the first note on its track')
    if native_pitch_lfo_delay and not native_pitch_lfo:
        raise ValueError('Delay approximation requires native pitch LFO mode')
    if native_pitch_lfo_live_depth and not (native_pitch_lfo and native_pitch_lfo_delay):
        raise ValueError('Live depth approximation requires native pitch LFO delay mode')
    if native_pitch_lfo_live_toggle and not (native_pitch_lfo and native_pitch_lfo_delay):
        raise ValueError('Live toggle approximation requires native pitch LFO delay mode')
    if native_pitch_lfo_live_toggle and native_pitch_lfo_live_depth:
        raise ValueError('Live toggle and positive depth-change modes are separate experiments')
    depth_changes, initializations, toggles = [], [], []
    if native_pitch_lfo_delay:
        fields = ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay')
        for track in tracks:
            notes = [a for a in track['actions'] if a['name'] == 'note']
            active = [i for i, a in enumerate(track['actions'])
                      if a.get('state_after', {}).get('mod_depth') and
                      (a['state_after']['mod_delay'] or native_pitch_lfo_live_depth or native_pitch_lfo_live_toggle)]
            if not active:
                continue
            activation = active[0]
            baseline = tuple(track['actions'][activation]['state_after'][k] for k in fields)
            if not notes or (not (native_pitch_lfo_live_toggle or native_pitch_lfo_late_depth) and track['actions'][activation]['ticks'] > notes[0]['ticks']):
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
                initial_off = (i < activation and (native_pitch_lfo_live_toggle or native_pitch_lfo_late_depth or a['ticks'] == notes[0]['ticks'])
                               and current[2] == 0)
                toggled_off = native_pitch_lfo_live_toggle and current[2] == 0
                live_depth = (native_pitch_lfo_live_depth and current[2] > 0 and
                              current[:2] + current[3:] == baseline[:2] + baseline[3:])
                if current != baseline and not live_depth and not ((initial_off or toggled_off) and current[:2] + current[3:] == baseline[:2] + baseline[3:]):
                    raise ValueError('Delayed LFO requires fixed per-track modulation after initial activation')
            previous_depth = baseline[2]
            if native_pitch_lfo_live_toggle:
                previous = 0
                for a in track['actions']:
                    if a['opcode'] == 0xCA:
                        depth = a['state_after']['mod_depth']
                        if depth != previous:
                            toggles.append({'source_track': track['track'], 'ticks': a['ticks'],
                                            'before': previous, 'after': depth})
                        previous = depth
            for a in track['actions'][activation + 1:]:
                if a['opcode'] not in (0xCA, 0xCB, 0xCC, 0xCD, 0xE0):
                    continue
                current = tuple(a['state_after'][k] for k in fields)
                if current == baseline and not native_pitch_lfo_live_depth:
                    continue
                accepted_depth = ((native_pitch_lfo_live_depth and current[2] > 0) or
                                  (native_pitch_lfo_live_toggle and current[2] in (0, baseline[2])))
                if not (accepted_depth and
                        current[:2] + current[3:] == baseline[:2] + baseline[3:]):
                    raise ValueError('Live delayed-LFO parameter changes are outside this experiment')
                if native_pitch_lfo_live_depth and current[2] != previous_depth:
                    depth_changes.append({'source_track': track['track'], 'ticks': a['ticks'],
                                          'before': previous_depth, 'after': current[2]})
                previous_depth = current[2]
    if envelope_snapshots and any(len(group) != 1 for group in groups):
        raise ValueError('Envelope experiment requires singleton target tracks')
    # Audit mode records effects broadly; this compiler accepts only the
    # specifically implemented controls, never silently drops active effects.
    permitted = {0xFE, 0xC0, 0xC1, 0xC4, 0xC5, 0xC6, 0xC7,
                 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xD4, 0xD5, 0xE0, 0xE1}
    if envelope_support:
        permitted.update((0xD0, 0xD1, 0xD2, 0xD3))
    if finite_release_support:
        permitted.add(0xD3)
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
    loop_start, period, expanded, decisions = assess_groups(
        tracks, groups, finite_support, mixed_loop_support, mixed_live_depth_support)
    selected_entry_before_lfo = loop_start
    if mixed_loop_support and len({a['value'] for t in tracks for a in t['actions'] if a['opcode'] == 0xE1}) != 1:
        raise ValueError('Mixed experiment requires a fixed source tempo')
    finite_ids = {t['track'] for t in tracks if t['termination'] == 'end'}
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
                    map_pitch_lfo(state, lfo_tempo, native_pitch_lfo_delay, native_pitch_lfo_min_depth)
                    if state['mod_depth']:
                        key = tuple(state[k] for k in ('mod_type', 'mod_speed', 'mod_depth', 'mod_range', 'mod_delay'))
                        lfo_configs[key] = compare_config(state, lfo_tempo, native_pitch_lfo_delay, native_pitch_lfo_min_depth)
                        if (lfo_configs[key].get('minimum_depth_quantized') and
                                lfo_configs[key]['single_voice_one_second_rms_pitch_error_cents'] > 5):
                            raise ValueError('Minimum-depth LFO exceeds five-cent isolated RMS pitch error')
    end_tick = max(t['end_ticks'] for t in tracks) + 1 if finite_support else loop_start + period
    bank, archives = archive.bank(info['bank_id'])
    source_map = {n: i for i, group in enumerate(groups) for n in group}
    gain = 10 ** (song_gain_db / 20)
    group_volume = {}
    for i, group in enumerate(groups):
        # A note-free conductor still carries tempo/controls and its loop.
        # DS starts at volume 127; explicit controls below remain authoritative.
        group_volume[i] = max((a['state_after']['volume'] for n in group
                               for a in expanded[n] if a['name'] == 'note'), default=127)
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
    aliases, loop_carries = {}, []
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
            entry = [(start - loop_start, end - loop_start) for start, end in intervals
                     if not finite_support and start < loop_start < end]
            exit = [(start - end_tick, end - end_tick) for start, end in intervals
                    if not finite_support and start < end_tick < end]
            if entry != exit:
                raise ValueError('Long notes require matching carry across merged loop boundary')
            # The warmup's EOT inside the body also closes the previous
            # iteration's TIE after GOTO. Never split/retrigger the note.
            for start, end in entry:
                loop_carries.append({'target_track': i, 'source_track': context[0],
                                     'source_key': context[1], 'gba_key': alias,
                                     'note_start_relative_ticks': start,
                                     'eot_relative_ticks': end})
    voice_contexts, voice_definitions, voice_keys = {}, [], []
    voice_splits, mappings = [], []
    for note in source_notes:
        group = note['target_track']
        pan_shift = note['state_after']['pan'] - 64 if len(groups[group]) > 1 else 0
        context = (note['instrument'], pan_shift)
        if envelope_snapshots:
            definition = archive.note_definition(bank, note['instrument'], note['key'])
            envelope = {field: note['state_after'][field] if note['state_after'][field] is not None
                        else getattr(definition, field) for field in ('attack', 'decay', 'sustain', 'release')}
            note['source_envelope'] = envelope
            context += tuple(envelope.values())
        played_key = aliases.get((group, note['source_track'], note['key']), note['key']) if note['duration'] > 223 else note['key']
        # Rhythm-bank slots are shared by every track selecting this voice.
        # Track-local aliases can name different source keys on other tracks.
        # Reuse the first compatible bank, splitting only a conflicting slot.
        candidates = voice_contexts.setdefault(context, [])
        voice = next((v for v in candidates
                      if voice_keys[v].get(played_key, note['key']) == note['key']), None)
        if voice is None:
            voice = len(voice_definitions)
            if candidates:
                voice_splits.append({'gba_voice': voice, 'existing_voices': list(candidates),
                                     'source_track': note['source_track'], 'tick': note['ticks'],
                                     'source_instrument': note['instrument'],
                                     'gba_key': played_key, 'source_key': note['key'],
                                     'conflicting_source_keys': [voice_keys[v][played_key] for v in candidates]})
            candidates.append(voice)
            voice_definitions.append(context)
            voice_keys.append({})
        voice_keys[voice][played_key] = note['key']
        ratio = level(note['state_after']['volume']) / level(group_volume[group]) if len(groups[group]) > 1 else 1.0
        velocity = round(127 * level(note['velocity']) * ratio)
        note.update(gba_voice=voice, gba_key=played_key,
                    gba_velocity=velocity, pan_shift=pan_shift,
                    gba_priority=priority_map[note['state_after']['priority']])
        mappings.append({'tick': note['ticks'], 'source_track': note['source_track'],
                         'source_instrument': note['instrument'], 'source_key': note['key'],
                         'source_velocity': note['velocity'], 'duration': note['duration'],
                         'target_track': group, 'gba_voice': note['gba_voice'],
                         'gba_key': played_key, 'gba_velocity': velocity,
                         'long_note': note['duration'] > 223})
        if envelope_snapshots:
            mappings[-1]['source_envelope'] = note['source_envelope']
    if len(voice_definitions) > 128:
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
        if envelope_snapshots:
            definition = replace(definition, **note['source_envelope'])
        if definition.kind != 1 or not 0 <= definition.archive_slot < len(archives):
            raise ValueError('Merged experiment requires valid PCM instruments')
        source_wave = (archives[definition.archive_slot], definition.wave_id)
        cache_key = (*source_wave, definition.root_key, note['key']) if bandlimited_pcm else (*source_wave, definition.root_key)
        if cache_key not in wave_cache:
            pcm, metadata = archive.wave(*source_wave)
            frequency = round(metadata['effective_rate_hz'] * 2 ** ((60 - definition.root_key) / 12) * 1024)
            if not 0 < frequency < 2 ** 32:
                raise ValueError('Converted wave frequency out of range')
            pcm8 = bytes(max(-128, min(127, round(x / 256))) & 255 for x in pcm)
            target_loop = metadata['loop_start_samples']
            resampling = None
            if bandlimited_pcm:
                pcm8, frequency, target_loop, resampling = resample_wave(
                    pcm, metadata['effective_rate_hz'], note['key'], definition.root_key,
                    metadata['looped'], metadata['loop_start_samples'])
                if sum(s['pcm8_bytes'] for s in sample_reports) + len(pcm8) > 4_000_000:
                    raise ValueError('Bandlimited song exceeds PCM sample budget')
            raw = struct.pack('<HHIII', 0, 0x4000 if metadata['looped'] else 0,
                              frequency, target_loop, len(pcm8)) + pcm8
            wave_cache[cache_key] = allocate(raw)
            sample_reports.append({**metadata, 'root_key': definition.root_key,
                                   'gba_frequency_raw': frequency, 'gba_wave_offset': wave_cache[cache_key],
                                   'pcm8_bytes': len(pcm8)})
            if bandlimited_pcm:
                sample_reports[-1].update(source_key=note['key'], resampling=resampling)
        pan = max(0, min(127, definition.pan + note['pan_shift']))
        raw = struct.pack('<BBBBI4B', 0, note['key'], 0, 128 + pan,
                          ROM_BASE + wave_cache[cache_key], *convert_envelope(definition, envelope_support))
        site = (note['gba_voice'], note['gba_key'])
        if site in tone_map and tone_map[site] != raw:
            raise ValueError('Conflicting per-note alias/instrument definition')
        tone_map[site] = raw
    instrument_reports = []
    for voice, context in enumerate(voice_definitions):
        children = allocate(bytes(128 * 12))
        keys = sorted(key for v, key in tone_map if v == voice)
        for key in keys:
            output[children + key * 12:children + (key + 1) * 12] = tone_map[voice, key]
        struct.pack_into('<BBBBI4B', output, bank_offset + voice * 12,
                         0x80, 0, 0, 0, ROM_BASE + children, 0, 0, 0, 0)
        instrument_reports.append({'instrument_id': voice, 'source_instrument': context[0],
                                   'pan_shift': context[1], 'keys': keys, 'gba_children_offset': children})
        if envelope_snapshots:
            instrument_reports[-1]['source_envelope'] = dict(zip(('attack', 'decay', 'sustain', 'release'), context[2:]))
            instrument_reports[-1]['gba_envelope'] = list(tone_map[voice, keys[0]][8:12])
    track_offsets, schedules, tempo_reports = [], [], []

    def volume(value, expression):
        result = round(127 * level(info['volume']) * level(value) * level(expression) * gain)
        if result > 127:
            raise ValueError('Song gain exceeds MPlay VOL headroom')
        return result

    long_starts = {(n['target_track'], n['source_track'], n['key'], n['ticks'], n['duration'])
                   for n in source_notes if n['duration'] > 223}
    for group_index, group in enumerate(groups):
        events = []
        primary = group[0]
        track_finite = finite_support or (mixed_loop_support and primary in finite_ids)
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
                value = map_pitch_lfo(state, lfo_tempo, native_pitch_lfo_delay, native_pitch_lfo_min_depth)
                command = (bytes([0xC4, value['mod']]) if native_pitch_lfo_live_depth and not native_pitch_lfo_late_depth and op == 0xCA
                           else bytes([0xC4, value['mod'], 0xC2, value['lfos']]))
            if command:
                order = 1 + action['event_order'] if native_pitch_lfo else 1
                events.append((action['ticks'], order, primary, command, None))
        for note in (a for a in source_notes if a['target_track'] == group_index):
            command = bytes([0xBA, note['gba_priority'], 0xBD, note['gba_voice']])
            if native_pitch_lfo:
                command += note_lfo_commands(note['state_after'], lfo_tempo, native_pitch_lfo_delay, native_pitch_lfo_min_depth)
            if note['duration'] <= 223:
                command += note_bytes(note['gba_key'], note['gba_velocity'], note['duration'])
            else:
                command += bytes([0xCF, note['gba_key'], note['gba_velocity']])
                gate_end = note['ticks'] + note['duration']
                repeats = (group_index, note['source_track'], note['key'],
                           note['ticks'] + period, note['duration']) in long_starts if mixed_loop_support else True
                # An intro-only TIE closing exactly at entry belongs before
                # the loop label. Periodic closures must remain inside it.
                order = -2 if mixed_loop_support and gate_end == loop_start and not repeats else 0
                events.append((gate_end, order, note['source_track'],
                               bytes([0xCE, note['gba_key']]), None))
            order = 1 + note['event_order'] if native_pitch_lfo else 2
            events.append((note['ticks'], order, note['source_track'], command, note))
        if not track_finite:
            events.append((loop_start, -1, 0, b'', None))
        events.sort(key=lambda event: event[:3])
        code = bytearray([0xBD, 0, 0xBE, volume(group_volume[group_index], 127), 0xBF, 64])
        code.extend(pitch_commands(0))
        tick, loop_position = 0, None
        stop_tick = next(t['end_ticks'] for t in tracks if t['track'] == primary) if track_finite else end_tick
        for when, category, _, command, note in events:
            if when > stop_tick or (not track_finite and when == stop_tick):
                continue
            code.extend(wait_bytes(when - tick))
            tick = when
            if category == -1:
                loop_position = len(code)
            code.extend(command)
        code.extend(wait_bytes(stop_tick - tick))
        if track_finite:
            offset = allocate(code + b'\xB1')
        else:
            offset = allocate(code + b'\xB2' + bytes(4))
            struct.pack_into('<I', output, offset + len(code) + 1, ROM_BASE + offset + loop_position)
        track_offsets.append(offset)
        schedules.append({'source_tracks': list(group), 'target_track': group_index,
                          **({'termination': 'end', 'end_ticks': stop_tick} if track_finite else
                             {'loop_start_ticks': loop_start, 'loop_ticks': period})})
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
            note_validation.append(validate_finite_notes(track, base, schedules[group_index]['end_ticks'])
                                   if schedules[group_index].get('termination') == 'end' else validate_loop_notes(track, base, loop_start, period))
        except AssertionError as error:
            raise AssertionError(f'{error} on track {group_index}') from error
    report = {'schema_version': 1, 'sequence_index': index, 'sequence_info': info,
              'source_track_count': len(tracks), 'track_count': len(groups), 'tracks': tracks,
              'track_groups': [list(group) for group in groups], 'merge_assessment': decisions,
              'merged_loop_start_ticks': loop_start, 'merged_loop_ticks': period,
              'note_mapping': mappings, 'target_schedules': schedules,
              'samples': sample_reports, 'instruments': instrument_reports,
              'voice_context_splits': voice_splits,
              'tempo_mapping': tempo_reports, 'song_gain_db': song_gain_db, 'song_gain_linear': gain,
              'song_gain_scope': 'Imported sequence VOL commands only',
              'priority_mapping': {str(k): v for k, v in priority_map.items()}, 'song_priority': 20,
              'generated_bytes': len(blob), 'note_timing_check': True,
              'note_timing_validation': note_validation,
              'long_note_loop_carries': loop_carries,
              'long_note_aliases': [{'target_track': group, 'source_track': source,
                                     'source_key': key, 'gba_key': alias}
                                    for (group, source, key), alias in aliases.items()],
              'limitations': ['DS envelopes and PCM/volume resolution retain the earlier GBA approximations.',
                              'Merged pan changes are applied at note-on; release-tail pan follows GBA behavior.',
                              'Fixed track-volume ratios quantize into note velocity.',
                              'Relative music priorities mapped below native effect priorities.',
                              'Target PCM voice allocation is separate from sequence track merging.',
                              'Independent source execution and actual GBA playback must still be validated.']}
    if mixed_loop_support:
        report['mixed_loop_song'] = {
            'policy': 'Explicit singleton mixed score; finite tracks END once before common loop entry',
            'finite_track_end_ticks': {str(t['track']): t['end_ticks'] for t in tracks if t['track'] in finite_ids},
            'source_loop_periods': {str(t['track']): t['loop_ticks'] for t in tracks if t['track'] not in finite_ids},
            'common_loop_start_ticks': loop_start, 'common_loop_ticks': period,
            'max_common_period_ticks': 16384, 'max_period_expansion': 8,
            'finite_tracks_repeated': False, 'fixed_tempo': True}
    if mixed_live_depth_support:
        original_entry = max(t['loop_start_ticks'] for t in tracks if t['termination'] == 'loop')
        report['mixed_live_depth_extension'] = {
            'original_shared_loop_start_ticks': original_entry,
            'selected_entry_before_lfo_warmup': selected_entry_before_lfo,
            'later_entry_common_cycles': (selected_entry_before_lfo - original_entry) // period,
            'max_later_entry_common_cycles': 1, 'finite_tracks_repeated': False,
            'live_positive_depth': True, 'fitted_envelope_explicit': bool(envelope_support)}
    if bandlimited_pcm:
        report['bandlimited_pcm'] = {'mixing_rate_hz': MIX_RATE,
                                     'policy': ('Opt-in finite singleton, per-key cached PCM8; downward bends retained, no upward bend/modulation; periodic loop guard and compensated tuning'
                                                if finite_support else
                                                'Opt-in looping singleton, per-key cached PCM8; downward bends retained, no upward bend/modulation; periodic loop guard and compensated tuning'),
                                     'runtime_mixer_changed': False, 'offline_dependency': 'Python stdlib',
                                     'sample_budget': 4_000_000}
    if bandlimited_pcm and envelope_support:
        report['bandlimited_pcm']['fitted_attack_envelopes'] = True
    if finite_support:
        report['finite_song'] = {'policy': 'Singleton finite tracks; all gates close before or at source END',
                                 'track_end_ticks': {str(t['track']): t['end_ticks'] for t in tracks},
                                 'explicit_long_note_eot': True, 'native_lfo_or_fitted_envelope': False}
    if finite_release_support:
        report['finite_release_snapshots'] = {
            'policy': 'D3 initialized before the first note on each finite track; instant attacks only',
            'overrides_affect_existing_voices': False,
            'attack_fitting': False,
            'source_overrides': [{'source_track': t['track'], 'tick': a['ticks'], 'release': a['value']}
                                 for t in tracks for a in t['actions'] if a['opcode'] == 0xD3],
            'limitations': ['Decay, sustain and release retain existing GBA quantization and frame-rate approximation.']}
    if native_pitch_lfo:
        report['native_pitch_lfo'] = {'approximation': True, 'configs': list(lfo_configs.values()),
                                    'method': 'MPlay triangle pitch LFO; reset on every note with one-tick onset delay',
                                    'limitations': ['DS sine replaced by coarsely quantized triangle.',
                                                    'Track phase is shared; new notes reset older overlapping voices.',
                                                    'Release tails follow shared GBA phase rather than independent DS phase.']}
    if native_pitch_lfo_min_depth:
        report['native_pitch_lfo']['minimum_depth_quantization'] = {
            'policy': 'Explicit opt-in: nonzero source depth below MOD resolution uses MOD=1',
            'all_phase_pitch_difference_bound_cents': 10, 'isolated_one_second_rms_limit_cents': 5,
            'source_controls_preserved': True, 'scope': ('mixed singleton live-depth experiment only'
                                                        if mixed_live_depth_support else 'looping singleton live-depth experiment only'
                                                        if native_pitch_lfo_live_depth else 'mixed singleton experiment only')}
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
    if native_pitch_lfo_live_toggle:
        report['native_pitch_lfo']['live_toggle_approximation'] = {
            'policy': 'Depth zero or one fixed positive depth per track; fixed pitch type, speed, range and delay',
            'method': 'MOD/LFOS toggles preserve the preloaded delay count; inactive target phase is reset to zero',
            'source_depth_toggles': toggles,
            'limitations': ['DS inactive voice phase/count freeze; target disabling resets shared phase/value.',
                            'Re-enabling older voices approximates independent frozen phases with shared zero phase.',
                            'New notes reset shared phase/delay for overlapping voices and release tails.',
                            'Changing active depth or other modulation parameters remains rejected.']}
        report['native_pitch_lfo']['delay_approximation']['policy'] = report['native_pitch_lfo']['live_toggle_approximation']['policy']
        report['native_pitch_lfo']['method'] = 'MPlay triangle pitch LFO; fixed delay with live on/off approximation'
    if native_pitch_lfo_late_depth:
        report['native_pitch_lfo']['late_depth_activation'] = {
            'enabled': True, 'initial_off_notes_allowed': True,
            'initializations': initializations,
            'disabling_after_activation': False,
            'positive_depth_updates_preserve_phase_and_count': True,
            'enable_emits_nonzero_speed': True,
            'scope': 'Explicit looping singleton delayed positive-depth experiment'}
        live = report['native_pitch_lfo']['live_depth_approximation']
        live['policy'] = 'Initial inactive notes and later first activation; positive depths thereafter; fixed pitch type, speed, range and delay'
        live['method'] = 'Ordered MOD and nonzero LFOS updates preserve shared phase/count; inactive notes preload LFODL and stop LFOS'
        report['native_pitch_lfo']['method'] = 'MPlay triangle pitch LFO; explicit late activation and live positive-depth updates'
        live['limitations'] = [
            'Native shared phase/count and same-track note resets approximate independent DS voice state.',
            'Disabling after activation and other live parameter changes remain rejected.']
        report['native_pitch_lfo']['delay_approximation']['policy'] = live['policy']
    return blob, dependency, report
