"""Fingerprint-pinned targets and verified M4A playback layouts.

ROM identity, audio-driver layout, and optional input patches are independent.
Addresses are file offsets unless explicitly named address.
"""
import copy
import json
import struct
from pathlib import Path
from scan_audio import fingerprint, ROM_BASE

BASE_SHA256 = '588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8'
AUDIO_LAYOUT = 'exe45-audio-v1'  # Compatibility for existing callers/manifests.
LAYOUTS = {
    AUDIO_LAYOUT: {
        'table_offset':0x135214, 'entry_count':499, 'player_table_offset':0x135094,
        'music_player':31, 'entry_offset':0xEE344, 'core_offset':0xEEA78,
        'table_references':[0xEE36C,0xEE3A0,0xEE3EC,0xEE440,0xEE474],
        'entry_signature':'00b50004', 'stub_capacity':0x24,
        'sound_mode_offset':0x504, 'sound_mode':0x0093040D,
        'selector_address':0x02003D58, 'selector_description':'Existing game RNG1 low byte; read only',
        'preview_trigger':55, 'event_labels':{'55':'Title screen'},
        'default_events':[55,64,65,89,98,99], 'preservation_probes':[68,*range(69,81)],
        'native_source':'pvp',
    },
    'exegp-audio-v1': {
        'table_offset':0x160658, 'entry_count':170, 'player_table_offset':0x160604,
        'music_player':0, 'entry_offset':0x4C3BC, 'core_offset':0x4CAF0,
        'table_references':[0x2FFC,0x3028,0x4C3E4,0x4C418,0x4C464,0x4C4B8,0x4C4EC],
        'entry_signature':'00b50004', 'stub_capacity':0x24,
        'sound_mode_offset':0x4C3A0, 'sound_mode':0x0095FA00,
        'selector_address':0x030023C0, 'selector_mode':'clock-xorshift32',
        'selector_description':'Read-only scheduler tick mixed with xorshift32; timing based, deterministic',
        'preview_trigger':1, 'event_labels':{'1':'Title screen'},
        'default_events':None, 'preservation_probes':[148,100,150,158],
        'native_source':'native-exegp',
        'query_entry_offset':0x3000, 'query_entry_signature':'0004084a', 'query_stub_capacity':0x24,
    },
}
TARGETS = {
    'exe45-pvp': {
        'label':'EXE4.5 PvP 0.6.0 (Japanese)', 'native_label':'EXE4.5 (JP PvP base)',
        'fingerprint':{'size_bytes':8579364,'crc32':'D1240E4B','sha256':'2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278'},
        'audio_layout':AUDIO_LAYOUT, 'base_sha256':BASE_SHA256,
        'filename':'exe45.gba', 'patch_filename':'exe45_pvp_0.6.0.bps',
    },
    'bn45-us-pvp': {
        'label':'Battle Network 4.5 PvP 0.6.0 (English)', 'native_label':'BN4.5 (English PvP base)',
        'fingerprint':{'size_bytes':8583022,'crc32':'C361D756','sha256':'89e92cd0545128612cdb318f3fbffb8c604206a69e78a1745bb290451692ac48'},
        'audio_layout':AUDIO_LAYOUT, 'base_sha256':BASE_SHA256,
        'filename':'exe45.gba', 'patch_filename':'bn45_us_pvp_0.6.0.bps',
    },
}
_originals = json.loads((Path(__file__).resolve().parents[1] / 'config/rom-profiles.json').read_text())
_gp = next(p for p in _originals['profiles'] if p['key']=='exegp')
TARGETS['exegp'] = {'label':_gp['label'], 'native_label':_gp['label']+' (target)',
                      'fingerprint':_gp['fingerprint'], 'audio_layout':'exegp-audio-v1',
                      'base_sha256':_gp['fingerprint']['sha256'], 'filename':_gp['filename'], 'patch_filename':None}


def target_profile(key):
    profile = TARGETS[key]
    return {'key':key, **copy.deepcopy(profile), 'layout':copy.deepcopy(LAYOUTS[profile['audio_layout']])}


def identify_target(data):
    value = fingerprint(data)
    for key, profile in TARGETS.items():
        if value == profile['fingerprint']:
            return target_profile(key)
    raise ValueError('Unsupported target ROM fingerprint; choose a verified target and revision')


def validate_target(base, target_rom):
    target = identify_target(target_rom)
    if fingerprint(base)['sha256'] != target['base_sha256']:
        raise ValueError('Original ROM does not match this target profile')
    return target


def valid_manifest_target(manifest):
    profile = TARGETS.get(manifest.get('target_profile'))
    return bool(profile and manifest.get('target_base_fingerprint') == profile['fingerprint']
                and manifest.get('audio_layout',profile['audio_layout'])==profile['audio_layout'])


def manifest_layout(manifest):
    if not valid_manifest_target(manifest):
        raise ValueError('Manifest does not identify a verified target')
    return target_profile(manifest['target_profile'])['layout']


def check_layout(data, layout):
    """Check write preconditions independently of ROM identity."""
    entry = layout['entry_offset']
    signature = bytes.fromhex(layout['entry_signature'])
    if data[entry:entry+len(signature)] != signature:
        raise ValueError('Unexpected target audio entry code')
    for offset in layout['table_references']:
        if struct.unpack_from('<I',data,offset)[0] != ROM_BASE+layout['table_offset']:
            raise ValueError('Unexpected target table reference')
    if struct.unpack_from('<I',data,layout['sound_mode_offset'])[0] != layout['sound_mode']:
        raise ValueError('Unexpected target SoundMode configuration')
    if 'query_entry_offset' in layout:
        offset = layout['query_entry_offset']
        signature = bytes.fromhex(layout['query_entry_signature'])
        if data[offset:offset+len(signature)] != signature:
            raise ValueError('Unexpected target audio status query code')
    if layout['selector_address'] is None:
        raise ValueError('Target selector source has not been verified')


def selector_value(layout, raw):
    if layout.get('selector_mode') == 'clock-xorshift32':
        raw ^= (raw << 13) & 0xFFFFFFFF
        raw ^= raw >> 17
        raw ^= (raw << 5) & 0xFFFFFFFF
    return raw & 255
