#!/usr/bin/env python3
"""Read-only GBA audio inventory and verified BPS comparison (stdlib only)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROM_BASE = 0x08000000
MAX_ROM_SIZE = 32 * 1024 * 1024


def fingerprint(data: bytes) -> dict:
    return {"size_bytes": len(data), "crc32": f"{zlib.crc32(data):08X}",
            "sha256": hashlib.sha256(data).hexdigest()}


def apply_bps(source: bytes, patch: bytes) -> tuple[bytes, dict]:
    """Decode BPS, enforcing source, target, patch checksums and copy bounds."""
    if len(patch) < 19 or patch[:4] != b"BPS1":
        raise ValueError("Not a BPS1 patch")
    source_crc, target_crc, patch_crc = struct.unpack_from("<III", patch, len(patch) - 12)
    if zlib.crc32(patch[:-4]) != patch_crc:
        raise ValueError("BPS patch checksum mismatch")
    if zlib.crc32(source) != source_crc:
        raise ValueError("BPS source checksum mismatch")
    end = len(patch) - 12
    cursor = 4

    def number() -> int:
        nonlocal cursor
        result, shift = 0, 1
        for _ in range(10):
            if cursor >= end:
                raise ValueError("Truncated BPS integer")
            value = patch[cursor]
            cursor += 1
            result += (value & 127) * shift
            if value & 128:
                return result
            shift <<= 7
            result += shift
        raise ValueError("Oversized BPS integer")

    source_size, target_size, metadata_size = number(), number(), number()
    if source_size != len(source):
        raise ValueError("BPS source size mismatch")
    if target_size > MAX_ROM_SIZE:
        raise ValueError("BPS target exceeds GBA inventory size limit (32 MiB)")
    if cursor + metadata_size > end:
        raise ValueError("Truncated BPS metadata")
    metadata = patch[cursor:cursor + metadata_size]
    cursor += metadata_size
    output = bytearray()
    source_relative = target_relative = 0
    while cursor < end:
        action = number()
        kind, length = action & 3, (action >> 2) + 1
        if len(output) + length > target_size:
            raise ValueError("BPS action exceeds target size")
        if kind == 0:
            start = len(output)
            if start + length > len(source):
                raise ValueError("BPS SourceRead outside source")
            output.extend(source[start:start + length])
        elif kind == 1:
            if cursor + length > end:
                raise ValueError("Truncated BPS TargetRead")
            output.extend(patch[cursor:cursor + length])
            cursor += length
        else:
            offset = number()
            delta = -(offset >> 1) if offset & 1 else offset >> 1
            if kind == 2:
                source_relative += delta
                if source_relative < 0 or source_relative + length > len(source):
                    raise ValueError("BPS SourceCopy outside source")
                output.extend(source[source_relative:source_relative + length])
                source_relative += length
            else:
                target_relative += delta
                if not 0 <= target_relative < len(output):
                    raise ValueError("BPS TargetCopy outside produced target")
                # BPS permits overlapping copies; slice copying is incorrect here.
                for _ in range(length):
                    output.append(output[target_relative])
                    target_relative += 1
    if len(output) != target_size or zlib.crc32(output) != target_crc:
        raise ValueError("BPS target size/checksum mismatch")
    return bytes(output), {"source_size_bytes": source_size,
                           "target_size_bytes": target_size,
                           "metadata_hex": metadata.hex(),
                           "source_crc32": f"{source_crc:08X}",
                           "target_crc32": f"{target_crc:08X}",
                           "checksums_verified": ["source", "target", "patch"]}


def address(offset: int) -> dict:
    return {"file_offset": offset, "rom_address": f"0x{ROM_BASE + offset:08X}"}


def song_header(data: bytes, pointer: int) -> dict | None:
    offset = pointer - ROM_BASE
    if offset < 0 or offset % 4 or offset + 8 > len(data):
        return None
    count, blocks, priority, reverb = data[offset:offset + 4]
    tone = struct.unpack_from("<I", data, offset + 4)[0]
    if count == 0:
        if data[offset:offset + 4] != bytes(4):
            return None
        return {**address(offset), "empty": True, "track_count": 0,
                "tone_field_raw": f"0x{tone:08X}"}
    if not 1 <= count <= 16 or blocks != 0 or offset + 8 + count * 4 > len(data):
        return None
    if not ROM_BASE <= tone < ROM_BASE + len(data):
        return None
    tracks = struct.unpack_from("<" + "I" * count, data, offset + 8)
    if not all(ROM_BASE <= item < ROM_BASE + len(data) for item in tracks):
        return None
    header = data[offset:offset + 8 + count * 4]
    return {**address(offset), "empty": False, "track_count": count,
            "block_count": blocks, "priority": priority, "reverb_raw": reverb,
            "tone_bank": address(tone - ROM_BASE),
            "tracks": [{**address(item - ROM_BASE),
                        "prefix_hex": data[item - ROM_BASE:item - ROM_BASE + 16].hex()}
                       for item in tracks],
            "header_sha256": hashlib.sha256(header).hexdigest()}


def scan_tables(data: bytes, min_entries: int = 16) -> list[dict]:
    """Heuristic candidates; table IDs and player fields require code verification."""
    cache = {}
    candidates = []
    for phase in (0, 4):
        entries = []
        start = None

        def finish() -> None:
            if len(entries) < min_entries or sum(not e["header"]["empty"] for e in entries) < 4:
                return
            groups = {}
            for entry in entries:
                groups.setdefault(entry["header"]["file_offset"], []).append(entry["index"])
            for entry in entries:
                entry["same_header_indices"] = groups[entry["header"]["file_offset"]]
            table_bytes = data[start:start + len(entries) * 8]
            needle = struct.pack("<I", ROM_BASE + start)
            occurrences = []
            position = 0
            while (position := data.find(needle, position)) >= 0:
                occurrences.append(address(position))
                position += 1
            candidates.append({**address(start),
                               "raw_table_sha256": hashlib.sha256(table_bytes).hexdigest(),
                               "table_pointer_occurrences": occurrences,
                               "pointer_occurrences_status": "raw_literals_not_verified_code_references",
                               "end_file_offset_exclusive": start + len(entries) * 8,
                               "entry_count": len(entries),
                               "nonempty_count": sum(not e["header"]["empty"] for e in entries),
                               "unique_nonempty_headers": len({e["header"]["file_offset"]
                                   for e in entries if not e["header"]["empty"]}),
                               "status": "structural_candidate_not_runtime_verified",
                               "entries": list(entries)})

        for offset in range(phase, len(data) - 7, 8):
            pointer, field_a, field_b = struct.unpack_from("<IHH", data, offset)
            header = None
            if ROM_BASE <= pointer < ROM_BASE + len(data) and field_a <= 31 and field_b <= 31:
                if pointer not in cache:
                    cache[pointer] = song_header(data, pointer)
                header = cache[pointer]
            if header is not None:
                if start is None:
                    start = offset
                entries.append({"index": len(entries), "entry": address(offset),
                                "field_a_raw": field_a, "field_b_raw": field_b,
                                "kind": "empty" if header["empty"] else "unclassified_audio",
                                "header": header})
            else:
                finish()
                entries = []
                start = None
        finish()
    return sorted(candidates, key=lambda table: table["file_offset"])


def ranges_from_mask(mask) -> list[dict]:
    ranges = []
    start = None
    end = 0
    for end, changed in enumerate(mask, 1):
        if changed and start is None:
            start = end - 1
        elif not changed and start is not None:
            ranges.append({"start": start, "end_exclusive": end - 1, "size_bytes": end - 1 - start})
            start = None
    if start is not None:
        ranges.append({"start": start, "end_exclusive": end, "size_bytes": end - start})
    return ranges


def differences(base: bytes, target: bytes) -> dict:
    ranges = ranges_from_mask(a != b for a, b in zip(base, target))
    return {"changed_bytes_within_common_size": sum(r["size_bytes"] for r in ranges),
            "changed_ranges": ranges,
            "appended_size_bytes": max(0, len(target) - len(base)),
            "truncated_size_bytes": max(0, len(base) - len(target))}


def compare_entries(base_tables: list, target_tables: list) -> list:
    target_by_offset = {t["file_offset"]: t for t in target_tables}
    result = []
    for base in base_tables:
        target = target_by_offset.get(base["file_offset"])
        if target is None:
            result.append({"table_file_offset": base["file_offset"], "status": "candidate_not_found_in_target"})
            continue
        changes = []
        for old, new in zip(base["entries"], target["entries"]):
            if (old["header"], old["field_a_raw"], old["field_b_raw"]) != (new["header"], new["field_a_raw"], new["field_b_raw"]):
                changes.append({"index": old["index"], "base": old, "target": new})
        result.append({"table_file_offset": base["file_offset"],
                       "base_entry_count": base["entry_count"], "target_entry_count": target["entry_count"],
                       "changed_entry_count": len(changes), "changed_entries": changes})
    return result


def inventory(name: str, data: bytes, provenance: dict, min_entries: int) -> dict:
    if not 0xC0 <= len(data) <= MAX_ROM_SIZE:
        raise ValueError("ROM size outside supported range")
    return {"schema_version": 1, "name": name, "provenance": provenance,
            "fingerprint": fingerprint(data),
            "gba_header": {"title": data[0xA0:0xAC].decode("ascii", errors="replace"),
                           "game_code": data[0xAC:0xB0].decode("ascii", errors="replace"),
                           "revision": data[0xBC],
                           "checksum_valid": ((-sum(data[0xA0:0xBD]) - 0x19) & 255) == data[0xBD]},
            "detection": {"method": "aligned_m4a_style_table_and_header_structure",
                          "min_entries": min_entries, "max_tracks": 16,
                          "max_table_field": 31, "minimum_nonempty_entries": 4,
                          "bgm_sfx_classification": "not_verified",
                          "resource_boundaries_and_dependencies": "not_decoded"},
            "tables": scan_tables(data, min_entries)}


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="Base ROM (never modified)")
    parser.add_argument("--patch", type=Path, action="append", default=[], help="BPS independently applied to base; repeatable")
    parser.add_argument("--donor", type=Path, action="append", default=[], help="Additional ROM to inventory; repeatable")
    parser.add_argument("--out", type=Path, required=True, help="New output directory (must not exist)")
    parser.add_argument("--min-entries", type=int, default=16)
    args = parser.parse_args()
    if args.min_entries < 4:
        parser.error("--min-entries must be at least 4")
    if args.out.exists():
        parser.error("Output directory already exists; choose a new directory")
    try:
        base = args.rom.read_bytes()
        inputs = [(args.rom.stem, base, {"rom_path": str(args.rom)}, None)]
        for patch_path in args.patch:
            patch = patch_path.read_bytes()
            target, info = apply_bps(base, patch)
            inputs.append((patch_path.stem, target,
                           {"base_rom_path": str(args.rom), "patch_path": str(patch_path),
                            "patch_fingerprint": fingerprint(patch), "bps": info}, True))
        for donor in args.donor:
            inputs.append((donor.stem, donor.read_bytes(), {"rom_path": str(donor)}, None))
        # Use numeric prefixes so different input paths with the same stem cannot collide.
        reports = [inventory(name, data, origin, args.min_entries)
                   for name, data, origin, _ in inputs]
        comparisons = []
        for (_, data, _, patched), report in zip(inputs, reports):
            if patched:
                comparisons.append({"target": report["name"], **differences(base, data),
                                    "table_comparison": compare_entries(reports[0]["tables"], report["tables"])})
        conflicts = []
        patched_inputs = [(name, data) for name, data, _, patched in inputs if patched]
        for i, (name_a, a) in enumerate(patched_inputs):
            for name_b, b in patched_inputs[i + 1:]:
                ranges = ranges_from_mask(x != s and y != s and x != y for s, x, y in zip(base, a, b))
                common_end = min(len(a), len(b))
                extension_ranges = ranges_from_mask(x != y for x, y in zip(a[len(base):], b[len(base):]))
                for r in extension_ranges:
                    r["start"] += len(base)
                    r["end_exclusive"] += len(base)
                conflicts.append({"patch_a": name_a, "patch_b": name_b,
                                  "base_conflicting_bytes": sum(r["size_bytes"] for r in ranges),
                                  "base_conflicting_ranges": ranges,
                                  "extension_overlap": {"start": len(base), "end_exclusive": max(len(base), common_end),
                                                        "size_bytes": max(0, common_end - len(base)),
                                                        "differing_bytes": sum(r["size_bytes"] for r in extension_ranges),
                                                        "differing_ranges": extension_ranges},
                                  "resolution": "not_attempted"})
        args.out.mkdir(parents=True)
        manifest = []
        for i, report in enumerate(reports):
            filename = f"{i:02d}-{report['name']}.json"
            write_json(args.out / filename, report)
            csv_name = f"{i:02d}-{report['name']}.csv"
            with (args.out / csv_name).open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["table_file_offset", "index", "kind", "header_address", "track_count",
                                 "tone_bank_address", "field_a_raw", "field_b_raw", "same_header_indices"])
                for table in report["tables"]:
                    for entry in table["entries"]:
                        header = entry["header"]
                        writer.writerow([f"0x{table['file_offset']:X}", entry["index"], entry["kind"],
                                         header["rom_address"], header["track_count"],
                                         header.get("tone_bank", {}).get("rom_address", ""),
                                         entry["field_a_raw"], entry["field_b_raw"],
                                         ";".join(map(str, entry["same_header_indices"]))])
            manifest.append({"inventory": filename, "catalog_csv": csv_name, "fingerprint": report["fingerprint"],
                             "provenance": report["provenance"]})
        write_json(args.out / "manifest.json", {"schema_version": 1, "inputs": manifest})
        write_json(args.out / "comparisons.json", {"schema_version": 1, "comparisons": comparisons, "patch_conflicts": conflicts})
        lines = ["# Audio inventory", "", "Structural candidates only; no BGM/SFX or runtime confirmation.", "",
                 "| Input | Bytes | Table offset | Entries | Nonempty | Unique nonempty headers |",
                 "|---|---:|---|---:|---:|---:|"]
        for report in reports:
            for table in report["tables"]:
                lines.append(f"| {report['name']} | {report['fingerprint']['size_bytes']} | 0x{table['file_offset']:X} | {table['entry_count']} | {table['nonempty_count']} | {table['unique_nonempty_headers']} |")
            if not report["tables"]:
                lines.append(f"| {report['name']} | {report['fingerprint']['size_bytes']} | none detected | — | — | — |")
        for c in conflicts:
            lines.extend(["", f"{c['patch_a']} vs {c['patch_b']}: {c['base_conflicting_bytes']} conflicting bytes in original ROM; "
                          f"{c['extension_overlap']['size_bytes']} overlapping extension bytes. No merge performed."])
        (args.out / "summary.md").write_text("\n".join(lines) + "\n")
        print("\n".join(lines))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"scan_audio: {exc}\n")


if __name__ == "__main__":
    main()
