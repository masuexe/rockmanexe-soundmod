"""Explicit, pinned EXE6 research allocation for sixteen MPlay BGM tracks."""
import struct

from scan_audio import ROM_BASE, fingerprint
from target_profiles import TARGETS

TRACK_BASE = 0x0203FA00
TRACK_END = 0x0203FF00
CLEAR_SITE = 0x71E0
CLEAR_SIGNATURE = bytes.fromhex('50485149091af9f77bfb')


def capacity_plan(rom, target, requested=None):
    """Validate the original image before any relocation or prefix mutation."""
    layout = target['layout']
    entry = layout['player_table_offset'] + layout['music_player'] * 12
    capacity = rom[entry + 8]
    if requested is None:
        return capacity, None
    if type(requested) is not int or requested != 16:
        raise ValueError('Experimental native track capacity must be exactly16')
    key = target['key']
    if key not in ('exe6', 'exe6f') or fingerprint(rom) != TARGETS[key]['fingerprint']:
        raise ValueError('Sixteen tracks require a pinned original Japanese EXE6 ROM')
    if (layout['music_player'] != 31 or capacity != 8
            or struct.unpack_from('<I', rom, entry + 4)[0] != 0x02007EE8
            or rom[CLEAR_SITE:CLEAR_SITE + 10] != CLEAR_SIGNATURE
            or struct.unpack_from('<II', rom, 0x2BC4) != (0x0203E000, 0x02033000)
            or struct.unpack_from('<II', rom, 0x7324) != (0x0203CDA8, 0x02040000)):
        raise ValueError('Sixteen-track player, sprite or battle-clear signature differs')
    return 16, {'entry_offset': entry, 'entry_before': rom[entry:entry + 12]}


def check_import_capacity(reports, capacity):
    """Use parsed header/track records, not an editable catalog row's count."""
    for key, report in reports.items():
        count = report['header']['track_count']
        if not 1 <= count <= capacity or len(report['tracks']) != count:
            raise ValueError(f'Imported song {key} has {count} tracks; native capacity is {capacity}')


def install_capacity(output, plan, allocate):
    """Keep original clear effects on both sides of the reserved track pool."""
    from build_unified import Thumb
    entry = plan['entry_offset']
    if (output[entry:entry + 12] != plan['entry_before']
            or output[CLEAR_SITE:CLEAR_SITE + 10] != CLEAR_SIGNATURE):
        raise ValueError('Sixteen-track hook conflicts with another prefix mutation')
    offset = (len(output) + 3) & ~3
    code = Thumb(offset)
    for start, size in ((0x0203CDA8, TRACK_BASE - 0x0203CDA8), (TRACK_END, 0x100)):
        code.load(0, start)
        code.load(1, size)
        code.load(3, 0x080008E1)
        code.branch('fill', link=True)
    code.load(3, ROM_BASE + CLEAR_SITE + 11)
    code.emit(0x4718)
    code.label('fill')
    code.emit(0x4718)
    stub = code.finish()
    if allocate(stub) != offset:
        raise AssertionError('Sixteen-track stub allocation differs')
    hook = struct.pack('<HHIH', 0x4B00, 0x4718, ROM_BASE + offset + 1, 0x46C0)
    output[CLEAR_SITE:CLEAR_SITE + 10] = hook
    struct.pack_into('<I', output, entry + 4, TRACK_BASE)
    output[entry + 8] = 16
    ranges = [(CLEAR_SITE, CLEAR_SITE + 10), (entry + 4, entry + 9)]
    return ranges, {
        'experimental': True, 'capacity': 16, 'original_capacity': 8,
        'track_memory': {'base': f'0x{TRACK_BASE:08X}', 'end': f'0x{TRACK_END:08X}',
                         'track_bytes': 80, 'size_bytes': TRACK_END - TRACK_BASE},
        'player_entry_offset': entry, 'other_player_entries_changed': False,
        'sprite_limits_changed': False,
        'battle_clear': {'site_offset': CLEAR_SITE, 'before_hex': CLEAR_SIGNATURE.hex(),
                         'after_hex': hook.hex(), 'stub_offset': offset, 'stub_size': len(stub),
                         'resume_address': '0x080071EA',
                         'clear_spans': [['0x0203CDA8', '0x0203FA00'],
                                         ['0x0203FF00', '0x02040000']]},
        'scope': 'Opt-in research allocation only. PCM voice budget is unchanged. '
                 'No manual gameplay, linked-session or all-control-flow RAM acceptance inferred.'}
