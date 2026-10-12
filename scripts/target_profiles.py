"""Exact supported PvP outputs sharing the verified EXE4.5 audio layout."""
from scan_audio import fingerprint

BASE_SHA256 = '588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8'
TARGETS = {
    'exe45-pvp': {
        'label':'EXE4.5 PvP 0.6.0 (Japanese)',
        'native_label':'EXE4.5 (JP PvP base)',
        'fingerprint':{'size_bytes':8579364,'crc32':'D1240E4B','sha256':'2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278'},
    },
    'bn45-us-pvp': {
        'label':'Battle Network 4.5 PvP 0.6.0 (English)',
        'native_label':'BN4.5 (English PvP base)',
        'fingerprint':{'size_bytes':8583022,'crc32':'C361D756','sha256':'89e92cd0545128612cdb318f3fbffb8c604206a69e78a1745bb290451692ac48'},
    },
}
AUDIO_LAYOUT = 'exe45-audio-v1'


def identify_target(data):
    value = fingerprint(data)
    for key, profile in TARGETS.items():
        if value == profile['fingerprint']:
            return {'key':key, 'audio_layout':AUDIO_LAYOUT, **profile}
    raise ValueError('Unsupported PvP fingerprint; supported patches are EXE4.5 JP and BN4.5 English PvP 0.6.0')


def validate_target(base, pvp):
    if fingerprint(base)['sha256'] != BASE_SHA256:
        raise ValueError('Unsupported exe45 fingerprint')
    return identify_target(pvp)


def valid_manifest_target(manifest):
    profile = TARGETS.get(manifest.get('target_profile'))
    return bool(profile and manifest.get('target_base_fingerprint') == profile['fingerprint'])
