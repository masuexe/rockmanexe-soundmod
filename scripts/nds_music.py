"""Bounded Nitro sequence/PCM conversion research; no manager integration.

SDAT/SBNK/SWAR layouts and DS synthesis semantics are checked against
kode54/SSEQPlayer. Unsupported executed instructions fail explicitly.
"""
from dataclasses import dataclass
import math
import struct

from analyze_song import DURATIONS, Reader, analyze
from scan_audio import ROM_BASE

ARM7_CLOCK = 33513982
DS_CLOCK_HZ = ARM7_CLOCK / (64 * 2728)
GBA_FPS = 16777216 / 280896
IMA_STEPS = (7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31,
             34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130,
             143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449,
             494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166, 1282, 1411,
             1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660,
             4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493,
             10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385,
             24623, 27086, 29794, 32767)
IMA_INDEX = (-1, -1, -1, -1, 2, 4, 6, 8)
# Cnv_Sust, FeOS Sound System / SSEQPlayer: attenuation in 0.1 dB units.
SUSTAIN_DB = (-32768, -722, -721, -651, -601, -562, -530, -503,
              -480, -460, -442, -425, -410, -396, -383, -371,
              -360, -349, -339, -330, -321, -313, -305, -297,
              -289, -282, -276, -269, -263, -257, -251, -245,
              -239, -234, -229, -224, -219, -214, -210, -205,
              -201, -196, -192, -188, -184, -180, -176, -173,
              -169, -165, -162, -158, -155, -152, -149, -145,
              -142, -139, -136, -133, -130, -127, -125, -122,
              -119, -116, -114, -111, -109, -106, -103, -101,
              -99, -96, -94, -91, -89, -87, -85, -82,
              -80, -78, -76, -74, -72, -70, -68, -66,
              -64, -62, -60, -58, -56, -54, -52, -50,
              -49, -47, -45, -43, -42, -40, -38, -36,
              -35, -33, -31, -30, -28, -27, -25, -23,
              -22, -20, -19, -17, -16, -14, -13, -11,
              -10, -8, -7, -6, -4, -3, -1, 0)


def level(value):
    if not 0 <= value <= 127:
        raise ValueError('DS volume/envelope value outside 0..127')
    return 0.0 if value == 0 else 10 ** (SUSTAIN_DB[value] / 200)


def decode_adpcm(data):
    """DS IMA: signed predictor, low nibble first, no output header sample."""
    if len(data) < 4 or len(data) % 4:
        raise ValueError('Invalid DS ADPCM length')
    predictor, index_word = struct.unpack_from('<hH', data)
    index = index_word & 0x7F
    if index_word != index or index > 88:
        raise ValueError('Invalid DS ADPCM initial step index')
    result = []
    for byte in data[4:]:
        for nibble in (byte & 15, byte >> 4):
            step = IMA_STEPS[index]
            delta = (step >> 3) + (step if nibble & 4 else 0)
            delta += (step >> 1) if nibble & 2 else 0
            delta += (step >> 2) if nibble & 1 else 0
            predictor = max(-32768, min(32767, predictor + (-delta if nibble & 8 else delta)))
            index = max(0, min(88, index + IMA_INDEX[nibble & 7]))
            result.append(predictor)
    return result


@dataclass(frozen=True)
class NoteDefinition:
    wave_id: int
    archive_slot: int
    root_key: int
    attack: int
    decay: int
    sustain: int
    release: int
    pan: int
    kind: int = 1


class SoundArchive:
    """Checked raw SDAT access for the research subset; all reads bounded."""
    def __init__(self, data):
        self.data = bytes(data)
        self.reader = Reader(self.data)
        if self.reader.read(0, 8) != b'SDAT\xff\xfe\x00\x01':
            raise ValueError('Unsupported SDAT header')
        if self.u32(8) != len(data):
            raise ValueError('SDAT declared length mismatch')
        self.blocks = {}
        for name, site in [('INFO', 0x18), ('FAT ', 0x20)]:
            offset, size = struct.unpack('<II', self.reader.read(site, 8))
            raw = self.reader.read(offset, size)
            if raw[:4] != name.encode() or struct.unpack_from('<I', raw, 4)[0] != size:
                raise ValueError(f'Invalid SDAT {name} block')
            self.blocks[name] = Reader(raw)

    def u32(self, offset):
        return struct.unpack('<I', self.reader.read(offset, 4))[0]

    def info(self, group, index, size):
        block = self.blocks['INFO']
        offset = struct.unpack('<I', block.read(8 + group * 4, 4))[0]
        if not offset:
            raise ValueError('Missing SDAT record group')
        count = struct.unpack('<I', block.read(offset, 4))[0]
        if not 0 <= index < count:
            raise ValueError('SDAT record index out of range')
        site = struct.unpack('<I', block.read(offset + 4 + index * 4, 4))[0]
        if not site:
            raise ValueError('Empty SDAT record')
        return block.read(site, size)

    def file(self, file_id, magic):
        fat = self.blocks['FAT ']
        count = struct.unpack('<I', fat.read(8, 4))[0]
        if not 0 <= file_id < count:
            raise ValueError('SDAT file ID out of range')
        offset, size = struct.unpack('<II', fat.read(12 + file_id * 16, 8))
        raw = self.reader.read(offset, size)
        if raw[:8] != magic + b'\xff\xfe\x00\x01':
            raise ValueError('Unexpected Nitro file format/version')
        length = struct.unpack('<I', raw[8:12])[0]
        reader = Reader(raw[:length])
        if length > len(raw) or reader.read(0x10, 4) != b'DATA':
            raise ValueError('Invalid Nitro file length/DATA')
        return reader

    def sequence(self, index):
        file_id, reserved, bank, volume, channel, poly, player = struct.unpack('<3H4B', self.info(0, index, 10))
        file = self.file(file_id, b'SSEQ')
        offset = struct.unpack('<I', file.read(0x18, 4))[0]
        if offset < 0x1C:
            raise ValueError('Invalid SSEQ data offset')
        return file.read(offset, len(file.data) - offset), {
            'file_id': file_id, 'bank_id': bank, 'volume': volume, 'player_id': player,
            'channel_pressure': channel, 'polyphonic_pressure': poly}

    def bank(self, index):
        file_id, _, *archives = struct.unpack('<6H', self.info(2, index, 12))
        return self.file(file_id, b'SBNK'), archives

    def note_definition(self, bank, instrument, key):
        count = struct.unpack('<I', bank.read(0x38, 4))[0]
        if not 0 <= instrument < count or not 0 <= key <= 127:
            raise ValueError('Invalid instrument/key')
        entry = bank.read(0x3C + instrument * 4, 4)
        kind, offset = entry[0], int.from_bytes(entry[1:], 'little')
        if kind in (1, 2, 3):
            values = struct.unpack('<HH6B', bank.read(offset, 10))
            return NoteDefinition(*values, kind)
        if kind == 16:
            low, high = bank.read(offset, 2)
            if not low <= key <= high:
                raise ValueError('Note outside DS range instrument')
            offset += 2 + (key - low) * 12
        elif kind == 17:
            cutoffs = bank.read(offset, 8)
            last = -1
            for index, cutoff in enumerate(cutoffs):
                if cutoff <= last:
                    raise ValueError('Invalid DS regional instrument')
                if key <= cutoff:
                    offset += 8 + index * 12
                    break
                last = cutoff
            else:
                raise ValueError('Note outside DS regional instrument')
        else:
            raise ValueError(f'Unsupported DS instrument type {kind}')
        values = struct.unpack('<3H6B', bank.read(offset, 12))
        return NoteDefinition(*values[1:], values[0])

    def wave(self, archive, index):
        file_id = struct.unpack('<H', self.info(3, archive, 2))[0]
        file = self.file(file_id, b'SWAR')
        count = struct.unpack('<I', file.read(0x38, 4))[0]
        if not 0 <= index < count:
            raise ValueError('Invalid SWAV index')
        offset = struct.unpack('<I', file.read(0x3C + index * 4, 4))[0]
        kind, loop, rate, timer, start, tail = struct.unpack('<BBHHHI', file.read(offset, 12))
        raw = file.read(offset + 12, (start + tail) * 4)
        if loop not in (0, 1) or timer == 0:
            raise ValueError('Invalid SWAV loop/timer')
        if kind == 2:
            samples = decode_adpcm(raw)
            loop_start = (start - 1) * 8 if start else 0
        elif kind == 1:
            samples = list(struct.unpack('<' + 'h' * (len(raw) // 2), raw))
            loop_start = start * 2
        elif kind == 0:
            samples = [(x - 256 if x >= 128 else x) * 256 for x in raw]
            loop_start = start * 4
        else:
            raise ValueError(f'Unsupported SWAV encoding {kind}')
        if not samples or (loop and not 0 <= loop_start < len(samples)):
            raise ValueError('Invalid decoded SWAV length/loop')
        return samples, {'archive_id': archive, 'wave_id': index, 'encoding': kind,
                         'sample_rate_header': rate, 'timer': timer,
                         'effective_rate_hz': ARM7_CLOCK / (2 * timer),
                         'looped': bool(loop), 'loop_start_samples': loop_start,
                         'sample_count': len(samples), 'encoded_bytes': len(raw)}


def nds_sdat(rom, file_id):
    reader = Reader(rom)
    fat, size = struct.unpack('<II', reader.read(0x48, 8))
    if size % 8 or not 0 <= file_id < size // 8:
        raise ValueError('NDS FAT file ID outside table')
    start, end = struct.unpack('<II', Reader(reader.read(fat, size)).read(file_id * 8, 8))
    return reader.read(start, end - start)


def read_event(data, offset):
    reader = Reader(data)
    pc = offset

    def take(size=1):
        nonlocal pc
        raw = reader.read(pc, size)
        pc += size
        return int.from_bytes(raw, 'little')

    def variable():
        value = 0
        for _ in range(4):
            byte = take()
            value = value * 128 + (byte & 127)
            if byte < 128:
                return value
        raise ValueError('SSEQ variable integer exceeds four bytes')

    op = take()
    event = {'offset': offset, 'opcode': op}
    if op < 0x80:
        velocity, duration = take(), variable()
        if velocity > 127:
            raise ValueError('Invalid SSEQ velocity (possible instruction misalignment)')
        event.update(name='note', key=op, velocity=velocity, duration=duration)
    elif op in (0x80, 0x81):
        event.update(name='rest' if op == 0x80 else 'instrument', value=variable())
    elif op == 0x93:
        event.update(name='open_track', track=take(), target=take(3))
    elif op in (0x94, 0x95):
        event.update(name='jump' if op == 0x94 else 'call', target=take(3))
    elif 0xC0 <= op <= 0xD5:
        event.update(name='control', value=take())
    elif op in (0xE0, 0xE1, 0xE3, 0xFE):
        # MODDELAY (E0) is 16-bit, unlike the ndspy 4.2.0 event definition.
        event.update(name='control', value=take(2))
    elif op in (0xFC, 0xFD, 0xFF):
        event['name'] = {0xFC: 'loop_end', 0xFD: 'return', 0xFF: 'end'}[op]
    else:
        raise ValueError(f'Unsupported executed SSEQ opcode {op:#x} at {offset:#x}')
    event['next'] = pc
    return event


def trace_sequence(data, max_events=100000):
    """Execute each track until a timed state repeats or it ends; unroll calls."""
    pending, done = [(0, 0)], {}
    while pending:
        number, pc = pending.pop(0)
        if number in done or not 0 <= number < 16:
            raise ValueError('Duplicate/invalid opened SSEQ track')
        initial = pc
        state = {'instrument': 0, 'volume': 127, 'expression': 127, 'pan': 64,
                 'priority': 64, 'note_wait': 1, 'tempo': 120, 'mod_depth': 0,
                 'mod_speed': 16, 'mod_type': 0, 'mod_range': 1, 'mod_delay': 0,
                 'bend': 0, 'bend_range': 2, 'transpose': 0, 'porta': 0}
        stack, actions, seen, notes = [], [], {}, set()
        ticks = 0
        for _ in range(max_events):
            signature = (pc, tuple(stack), tuple(sorted(state.items())))
            if signature in seen:
                first, start_tick = seen[signature]
                if ticks == start_tick:
                    raise ValueError('Zero-time SSEQ cycle')
                done[number] = {'track': number, 'start': initial, 'actions': actions,
                                'termination': 'loop', 'loop_action': first,
                                'loop_start_ticks': start_tick, 'end_ticks': ticks,
                                'loop_ticks': ticks - start_tick, 'notes': sorted(notes)}
                break
            seen[signature] = (len(actions), ticks)
            event = read_event(data, pc)
            action = {**event, 'ticks': ticks}
            pc = event['next']
            op, name = event['opcode'], event['name']
            if name == 'note':
                if state['mod_depth'] or state['bend'] or state['transpose'] or state['porta']:
                    raise ValueError('Active pitch/modulation effects require additional conversion')
                if not 1 <= event['duration'] <= 223:
                    raise ValueError('Unsupported zero or >223 tick SSEQ note length')
                action['instrument'] = state['instrument']
                notes.add((state['instrument'], event['key']))
                if state['note_wait']:
                    ticks += event['duration']
            elif name == 'rest':
                ticks += event['value']
            elif name == 'instrument':
                if event['value'] > 127:
                    raise ValueError('Dynamic banks/instrument IDs >127 unsupported')
                state['instrument'] = event['value']
            elif name == 'open_track':
                if number != 0 or ticks != 0:
                    raise ValueError('Only tick-zero track openings from track 0 supported')
                pending.append((event['track'], event['target']))
            elif name == 'call':
                if len(stack) >= 3:
                    raise ValueError('SSEQ call nesting exceeds three')
                stack.append(('call', pc, 0))
                pc = event['target']
            elif name == 'return':
                if not stack or stack[-1][0] != 'call':
                    raise ValueError('SSEQ return without call')
                _, pc, _ = stack.pop()
            elif name == 'jump':
                pc = event['target']
            elif name == 'loop_end':
                if not stack or stack[-1][0] != 'loop':
                    raise ValueError('SSEQ loop end without start')
                _, start, count = stack[-1]
                if count == 0:
                    pc = start
                elif count > 1:
                    stack[-1] = ('loop', start, count - 1)
                    pc = start
                else:
                    stack.pop()
            elif name == 'control':
                value = event['value']
                fields = {0xC0: 'pan', 0xC1: 'volume', 0xC3: 'transpose', 0xC4: 'bend',
                          0xC5: 'bend_range', 0xC6: 'priority', 0xC7: 'note_wait',
                          0xCA: 'mod_depth', 0xCB: 'mod_speed', 0xCC: 'mod_type',
                          0xCD: 'mod_range', 0xCE: 'porta', 0xD5: 'expression',
                          0xE0: 'mod_delay', 0xE1: 'tempo'}
                if op in fields:
                    field = fields[op]
                    if field in ('pan', 'volume', 'expression'):
                        level(value)
                    if field in ('note_wait', 'porta') and value not in (0, 1):
                        raise ValueError('Invalid SSEQ boolean control')
                    if field in ('mod_depth', 'bend', 'transpose', 'porta') and value:
                        raise ValueError('Active pitch/modulation effects require additional conversion')
                    state[field] = value
                elif op == 0xD4:
                    if len(stack) >= 3:
                        raise ValueError('SSEQ loop/call stack exceeds three')
                    stack.append(('loop', pc, value))
                elif op == 0xFE and number == 0 and ticks == 0:
                    action['track_mask'] = value
                else:
                    raise ValueError(f'Unsupported executed SSEQ control {op:#x}')
            elif name == 'end':
                actions.append(action)
                done[number] = {'track': number, 'start': initial, 'actions': actions,
                                'termination': 'end', 'end_ticks': ticks, 'notes': sorted(notes)}
                break
            action['state_after'] = state.copy()
            action['end_ticks'] = ticks
            actions.append(action)
        else:
            raise ValueError('SSEQ execution limit exceeded')
    declared = next((a['track_mask'] for a in done[0]['actions'] if 'track_mask' in a), 1)
    if any(not declared & (1 << n) for n in done):
        raise ValueError('Opened SSEQ track absent from declared mask')
    return [done[n] for n in sorted(done)]


def fall_rate(value):
    if not 0 <= value <= 127:
        raise ValueError('Invalid DS fall parameter')
    if value == 127:
        return 65535
    if value == 126:
        return 15360
    return 2 * value + 1 if value < 50 else 7680 // (126 - value)


def convert_envelope(note):
    # Initial experiment requires the instant attack used by BGM_ROOM.
    if note.attack != 127:
        raise ValueError('Non-instant DS attack requires envelope fitting')
    multiplier = lambda v: min(255, round(256 * 10 ** (-fall_rate(v) * DS_CLOCK_HZ / (128 * 200 * GBA_FPS))))
    return (255, multiplier(note.decay), round(255 * level(note.sustain)), multiplier(note.release))


def wait_bytes(ticks):
    if ticks < 0:
        raise ValueError('Negative sequence wait')
    output = bytearray()
    while ticks:
        value = max(d for d in DURATIONS if d <= ticks)
        output.append(0x80 + DURATIONS.index(value))
        ticks -= value
    return bytes(output)


def note_bytes(key, velocity, duration):
    if not 0 <= key <= 127 or not 0 <= velocity <= 127 or not 1 <= duration <= 223:
        raise ValueError('Unsupported MPlay note arguments')
    base = max(d for d in DURATIONS[1:] if d <= duration)
    result = bytes([0xCF + DURATIONS.index(base), key, velocity])
    return result + (bytes([duration - base]) if duration != base else b'')


def convert_song(archive, index, track_capacity=8, tempo_correction=True, song_gain_db=0.0):
    if type(song_gain_db) not in (int, float) or not math.isfinite(song_gain_db) or not -24 <= song_gain_db <= 12:
        raise ValueError('Song gain must be finite and within -24..12 dB')
    song_gain = 10 ** (song_gain_db / 20)

    def volume_parameter(song_volume, track_volume=127, expression=127):
        value = round(127 * level(song_volume) * level(track_volume) * level(expression) * song_gain)
        if value > 127:
            raise ValueError('Song gain exceeds MPlay VOL headroom; choose a lower gain')
        return value

    data, info = archive.sequence(index)
    tracks = trace_sequence(data)
    if len(tracks) > track_capacity:
        raise ValueError('NDS sequence exceeds target track capacity')
    tempos = [(t['track'], a) for t in tracks for a in t['actions'] if a['opcode'] == 0xE1]
    if not tempos or any(number != 0 for number, _ in tempos):
        raise ValueError('Research conversion requires tempo commands in track 0')
    bank, archives = archive.bank(info['bank_id'])
    output = bytearray((index + 1) * 8)

    def allocate(raw):
        output.extend(bytes(-len(output) % 4))
        offset = len(output)
        output.extend(raw)
        return offset

    bank_offset = allocate(bytes(128 * 12))
    pairs = sorted({tuple(pair) for t in tracks for pair in t['notes']})
    tones, wave_cache, sample_reports = {}, {}, []
    for instrument, key in pairs:
        note = archive.note_definition(bank, instrument, key)
        if note.kind != 1 or not 0 <= note.root_key <= 127 or not 0 <= note.pan <= 127:
            raise ValueError('Research conversion supports valid PCM definitions only')
        if not 0 <= note.archive_slot < len(archives) or archives[note.archive_slot] == 65535:
            raise ValueError('Invalid note wave-archive slot')
        source_wave = (archives[note.archive_slot], note.wave_id)
        cache_key = (*source_wave, note.root_key)
        if cache_key not in wave_cache:
            pcm, wave_info = archive.wave(*source_wave)
            frequency = round(wave_info['effective_rate_hz'] * 2 ** ((60 - note.root_key) / 12) * 1024)
            if not 0 < frequency < 2 ** 32:
                raise ValueError('Converted PCM frequency outside u32')
            pcm8 = bytes(max(-128, min(127, round(x / 256))) & 255 for x in pcm)
            wave_raw = struct.pack('<HHIII', 0, 0x4000 if wave_info['looped'] else 0,
                                   frequency, wave_info['loop_start_samples'], len(pcm8)) + pcm8
            wave_offset = allocate(wave_raw)
            wave_cache[cache_key] = wave_offset
            sample_reports.append({**wave_info, 'root_key': note.root_key,
                                   'gba_frequency_raw': frequency, 'gba_wave_offset': wave_offset,
                                   'pcm8_bytes': len(pcm8)})
        wave_offset = wave_cache[cache_key]
        envelope = convert_envelope(note)
        tones[instrument, key] = struct.pack('<BBBBI4B', 0, key, 0, 128 + note.pan,
                                            ROM_BASE + wave_offset, *envelope)
    instrument_reports = []
    for instrument in sorted({i for i, _ in pairs}):
        keys = [key for i, key in pairs if i == instrument]
        # Rhythm bank with original key as child pitch preserves note tuning,
        # per-key definitions and instrument pan without using fixed-step PCM.
        children = allocate(bytes(128 * 12))
        for key in keys:
            output[children + key * 12:children + (key + 1) * 12] = tones[instrument, key]
        struct.pack_into('<BBBBI4B', output, bank_offset + instrument * 12,
                         0x80, 0, 0, 0, ROM_BASE + children, 0, 0, 0, 0)
        instrument_reports.append({'instrument_id': instrument, 'keys': keys,
                                   'gba_children_offset': children,
                                   'envelopes': {str(k): list(tones[instrument, k][8:12]) for k in keys}})
    track_offsets, tempo_reports = [], []
    for track in tracks:
        code = bytearray([0xBD, 0, 0xBE, volume_parameter(info['volume']), 0xBF, 64])
        action_offsets = []
        for action in track['actions']:
            action_offsets.append(len(code))
            op, name = action['opcode'], action['name']
            if name == 'note':
                velocity = round(127 * level(action['velocity']))
                code.extend(note_bytes(action['key'], velocity, action['duration']))
            elif name == 'instrument':
                code.extend([0xBD, action['value']])
            elif name == 'control':
                state = action['state_after']
                if op == 0xC0:
                    code.extend([0xBF, action['value']])
                elif op in (0xC1, 0xD5):
                    volume = volume_parameter(info['volume'], state['volume'], state['expression'])
                    code.extend([0xBE, volume])
                elif op == 0xC6:
                    code.extend([0xBA, action['value']])
                elif op == 0xE1:
                    tempo = action['value']
                    corrected = round(tempo * DS_CLOCK_HZ * 75 / (240 * GBA_FPS)) if tempo_correction else tempo
                    if not 1 <= corrected <= 127:
                        raise ValueError('Tempo outside conservative MPlay encoding range')
                    code.extend([0xBB, corrected])
                    tempo_reports.append({'nds_tempo': tempo, 'gba_parameter': corrected,
                                          'nds_ticks_per_second': DS_CLOCK_HZ * tempo / 240,
                                          'gba_ticks_per_second': GBA_FPS * corrected / 75})
            elif name == 'end':
                code.append(0xB1)
            code.extend(wait_bytes(action.get('end_ticks', action['ticks']) - action['ticks']))
        offset = allocate(code + (bytes(5) if track['termination'] == 'loop' else b''))
        if track['termination'] == 'loop':
            target = offset + action_offsets[track['loop_action']]
            output[offset + len(code):offset + len(code) + 5] = b'\xB2' + struct.pack('<I', ROM_BASE + target)
        track_offsets.append(offset)
    header_offset = allocate(struct.pack('<BBBBI', len(tracks), 0, 0, 128, ROM_BASE + bank_offset)
                             + struct.pack('<' + 'I' * len(tracks), *(ROM_BASE + o for o in track_offsets)))
    struct.pack_into('<IHH', output, index * 8, ROM_BASE + header_offset, 0, 0)
    blob = bytes(output)
    dependency = analyze(blob, 0, index)
    # Check note keys, velocities, gates and timing against the independent
    # GBA decoder; resource relocation checks happen in build_catalog later.
    for source_track, gba_track in zip(tracks, dependency['tracks']):
        source_notes = [(a['ticks'], a['instrument'], a['key'], round(127 * level(a['velocity'])), a['duration'])
                        for a in source_track['actions'] if a['name'] == 'note']
        target_notes = [(a['ticks'], a['voice'], a['key'], a['velocity'], a['duration_ticks'])
                        for a in gba_track['events'] if a['name'] == 'NOTE']
        # GBA closure includes running key/velocity, so it can legitimately
        # include one extra source cycle before that complete state repeats.
        expected = source_notes[:]
        if source_track['termination'] == 'loop':
            body = [n for n in source_notes if n[0] >= source_track['loop_start_ticks']]
            while len(expected) < len(target_notes):
                shift = source_track['loop_ticks'] * (1 + (len(expected) - len(source_notes)) // max(1, len(body)))
                expected.extend((n[0] + shift, *n[1:]) for n in body)
        if target_notes != expected[:len(target_notes)]:
            raise AssertionError('Converted MPlay note/timing model differs from SSEQ execution')
        if source_track['termination'] == 'loop' and gba_track.get('loop_ticks') != source_track['loop_ticks']:
            raise AssertionError('Converted loop period differs')
    report = {'schema_version': 1, 'sequence_index': index, 'sequence_info': info,
              'track_count': len(tracks), 'tracks': tracks, 'samples': sample_reports,
              'instruments': instrument_reports, 'tempo_mapping': tempo_reports,
              'song_gain_db': song_gain_db, 'song_gain_linear': song_gain,
              'song_gain_scope': 'Imported sequence VOL commands only; samples, velocities and target mixer unchanged',
              'generated_bytes': len(blob), 'note_timing_check': True,
              'limitations': ['DS attenuation mapped to quantized GBA volume/velocity.',
                              'DS exponential envelopes approximated at the GBA frame rate.',
                              'Original-rate signed 8-bit PCM; target mixer rate remains native.',
                              'Inactive modulation controls omitted; active effects rejected.',
                              'No DS hardware or subjective fidelity claim.']}
    return blob, dependency, report
