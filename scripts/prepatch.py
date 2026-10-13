"""Strict IPS decoding and local pre-patch discovery (no ZIP extraction)."""
from pathlib import Path
from zipfile import ZipFile, BadZipFile

from scan_audio import apply_bps, fingerprint

MAX_ROM_SIZE = 32 * 1024 * 1024


def apply_ips(base, patch):
    if not patch.startswith(b'PATCH'):
        raise ValueError('Invalid IPS header')
    output = bytearray(base)
    offset, records = 5, []
    while True:
        if len(patch) - offset < 3:
            raise ValueError('Truncated IPS record or missing EOF')
        if patch[offset:offset + 3] == b'EOF':
            offset += 3
            break
        if len(patch) - offset < 5:
            raise ValueError('Truncated IPS record')
        address = int.from_bytes(patch[offset:offset + 3], 'big')
        size = int.from_bytes(patch[offset + 3:offset + 5], 'big')
        offset += 5
        if size:
            if len(patch) - offset < size:
                raise ValueError('Truncated IPS data')
            data = patch[offset:offset + size]
            offset += size
        else:
            if len(patch) - offset < 3:
                raise ValueError('Truncated IPS RLE record')
            count = int.from_bytes(patch[offset:offset + 2], 'big')
            if not count:
                raise ValueError('Empty IPS RLE record')
            data = patch[offset + 2:offset + 3] * count
            offset += 3
        end = address + len(data)
        if end > MAX_ROM_SIZE:
            raise ValueError('IPS output exceeds the GBA ROM size limit')
        if end > len(output):
            output.extend(bytes(end - len(output)))
        output[address:end] = data
        records.append([address, end])
    if len(patch) - offset == 3:
        size = int.from_bytes(patch[offset:], 'big')
        if size > MAX_ROM_SIZE:
            raise ValueError('IPS output exceeds the GBA ROM size limit')
        if size < len(output): del output[size:]
        else: output.extend(bytes(size - len(output)))
    elif len(patch) != offset:
        raise ValueError('Unexpected trailing IPS data')
    return bytes(output), {'format':'ips', 'patch_fingerprint':fingerprint(patch),
                           'source_fingerprint':fingerprint(base),
                           'target_fingerprint':fingerprint(output), 'write_ranges':records}


def apply_prepatch(base, patch, profile):
    """IPS has no source checksum; pinned source/patch/output identities provide it."""
    if fingerprint(base)['sha256'] != profile['base_sha256']:
        raise ValueError('Original ROM does not match the selected pre-patch target')
    expected = profile.get('patch_sha256')
    if expected and fingerprint(patch)['sha256'] != expected:
        raise ValueError('Pre-patch does not match the supported version')
    if profile.get('patch_format', 'bps') == 'ips':
        result, info = apply_ips(base, patch)
    else:
        result, info = apply_bps(base, patch)
    if fingerprint(result) != profile['fingerprint']:
        raise ValueError('Pre-patch does not produce the selected target')
    return result, info


def find_prepatch(profile, directories):
    """Return (filename, bytes), accepting the pinned ZIP member or loose patch."""
    name = profile['patch_filename']
    if not name: return None
    for directory in directories:
        path = Path(directory) / name
        if path.is_file(): return name, path.read_bytes()
        archive = profile.get('patch_archive')
        if archive and (Path(directory) / archive).is_file():
            try:
                with ZipFile(Path(directory) / archive) as z:
                    member = z.getinfo(name)
                    if member.file_size > MAX_ROM_SIZE:
                        raise ValueError('Pre-patch ZIP member is too large')
                    return name, z.read(member)
            except (BadZipFile, KeyError) as exc:
                raise ValueError('Pre-patch archive is invalid or lacks the required patch') from exc
    return None


def prepatch_available(profile, directories):
    return not profile['patch_filename'] or any(
        (Path(d) / profile['patch_filename']).is_file() or
        (profile.get('patch_archive') and (Path(d) / profile['patch_archive']).is_file())
        for d in directories)
