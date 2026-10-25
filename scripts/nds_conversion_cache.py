"""Content-addressed, checked JSON/PCM cache; dependency reports are reparsed."""
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import sys
import tempfile
import threading

from analyze_song import analyze
from build_nds_experiment import SOURCES, SOURCE_ARCHIVES, SONG_FAMILIES, build_experiment
from nds_music import nds_sdat
from scan_audio import fingerprint
from target_profiles import validate_target

ROOT = Path(__file__).resolve().parents[1]
MAX_CACHE_BYTES = 64 * 1024 * 1024


def canonical(value):
    # Normalize tuple/list and integer/string JSON keys before sorting. Otherwise
    # numeric keys such as2/10 hash differently after a disk round trip.
    value = json.loads(json.dumps(value, ensure_ascii=True, allow_nan=False))
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def toolchain_fingerprint():
    files = sorted((ROOT / 'scripts').glob('*.py')) + sorted((ROOT / 'config').glob('*.json'))
    return digest({'files': {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
                   'python': sys.version, 'implementation': platform.python_implementation(),
                   'system': platform.system(), 'machine': platform.machine(), 'libc': platform.libc_ver()})


# Snapshot the loaded release. Editing files while an old server is still running
# must not label results from its old Python modules with the new release's key.
TOOLCHAIN = toolchain_fingerprint()


def conversion_identity(source, base, spec, track_count):
    family, index, selector, _, gain, finite = spec
    src = fingerprint(source)
    profile = SOURCES.get(src['sha256'])
    if profile is None or profile[:4] != family or SONG_FAMILIES.get(selector) != family:
        raise ValueError('NDS conversion source/configuration does not match a verified original')
    target = validate_target(base, base)
    if target['key'] not in ('exe6', 'exe6f'):
        raise ValueError('NDS conversion requires Japanese EXE6')
    sdat = fingerprint(nds_sdat(source, SOURCE_ARCHIVES[family]['file_id']))
    if sdat['sha256'] != SOURCE_ARCHIVES[family]['sha256']:
        raise ValueError('NDS SDAT fingerprint differs')
    return {'schema_version': 1, 'toolchain': TOOLCHAIN, 'source': src, 'sdat': sdat,
            'source_profile': profile, 'target': fingerprint(base), 'target_profile': target['key'],
            'selector': selector, 'sequence_index': index, 'gain_db': gain,
            'finite': finite, 'track_count': track_count, 'pcm_channels': 10}


def validate_result(blob, conversion, origin, identity):
    if (origin['source_profile'] != identity['source_profile']
            or origin['source_rom_fingerprint'] != identity['source']
            or origin['sdat_fingerprint'] != identity['sdat']
            or origin['sequence_index'] != identity['sequence_index']
            or origin['song_gain_db'] != identity['gain_db']
            or conversion['song_gain_db'] != identity['gain_db']
            or conversion['track_count'] != identity['track_count']
            or bool(conversion.get('finite_song')) != identity['finite']
            or fingerprint(blob) != origin['generated_mplay_fingerprint']):
        raise ValueError('Cached NDS conversion differs from the requested configuration')
    # Reparse native dependency types, including note tuples changed by JSON.
    dependency = analyze(blob, 0, identity['sequence_index'])
    if len(dependency['tracks']) != identity['track_count']:
        raise ValueError('Cached NDS track count differs')
    return blob, dependency, conversion, origin


class NdsConversionCache:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.memory = {}
        self.lock = threading.RLock()
        self.stats = {'memory_hits': 0, 'disk_hits': 0, 'conversions': 0, 'invalid_entries': 0}

    def _read(self, path, identity):
        if path.stat().st_size > MAX_CACHE_BYTES:
            raise ValueError('Oversized NDS cache entry')
        record = json.loads(path.read_bytes())
        if record['identity'] != identity or record['payload_digest'] != digest(record['payload']):
            raise ValueError('NDS cache identity/checksum differs')
        payload = record['payload']
        blob = base64.b64decode(payload['blob'], validate=True)
        return validate_result(blob, payload['conversion'], payload['origin'], identity)

    def _write(self, path, identity, result):
        blob, _, conversion, origin = result
        payload = {'blob': base64.b64encode(blob).decode('ascii'), 'conversion': conversion, 'origin': origin}
        raw = canonical({'identity': identity, 'payload_digest': digest(payload), 'payload': payload})
        if len(raw) > MAX_CACHE_BYTES:
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=self.directory, prefix='entry-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def get(self, source, base, spec, track_count):
        # Validate current original inputs before consulting either cache layer.
        identity = conversion_identity(source, base, spec, track_count)
        key = digest(identity)
        with self.lock:
            if key in self.memory:
                self.stats['memory_hits'] += 1
                return self.memory[key]
            path = self.directory / (key + '.json')
            try:
                result = self._read(path, identity)
            except FileNotFoundError:
                result = None
            except (OSError, ValueError, KeyError, TypeError, AssertionError, struct.error, OverflowError, RecursionError):
                self.stats['invalid_entries'] += 1
                result = None
            if result is not None:
                self.stats['disk_hits'] += 1
            else:
                # Converter failures propagate; a cache never bypasses its guards.
                _, _, manifest, conversion, _, blob, _, _ = build_experiment(
                    source, base, song=spec[2], song_gain_db=spec[4])
                result = validate_result(blob, conversion, manifest['nds_conversion'], identity)
                self.stats['conversions'] += 1
                try:
                    self._write(path, identity, result)
                except (OSError, ValueError, TypeError, OverflowError):
                    pass  # A read-only/full cache must not block a valid export.
            self.memory[key] = result
            return result
