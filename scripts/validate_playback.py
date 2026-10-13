#!/usr/bin/env python3
"""Validate audio ID lookup and player initialization in mGBA's CLI debugger.

Runs a disposable ROM copy without personal saves. Optional IDs are injected
into r0 at a naturally reached playback entry. No ROM instructions are patched
by this script; mGBA uses its own software breakpoints. This is a state check,
not an audible playback or full-resource validation.
"""
import argparse
import json
import os
from pathlib import Path
import pty
import re
import select
import struct
import subprocess
import time

from scan_audio import ROM_BASE, apply_bps, fingerprint, song_header
from target_profiles import TARGETS

PROFILES = {
    "A646601B": ("exe45", 0xEE344, 0x135214, 0x135094, 499),
    "C361D756": ("bn45-us-pvp", 0xEE344, 0x135214, 0x135094, 499),
    "D1240E4B": ("exe45-pvp", 0xEE344, 0x135214, 0x135094, 499),
    "D0020C1F": ("exe45-soundmod", 0xEE344, 0x135214, 0x135094, 499),
    "9217FB18": ("exegp", 0x4C3BC, 0x160658, 0x160604, 170),
    "6285918A": ("exe6", 0x15B338, 0x164E0C, 0x164C8C, 474),
    "2DFB603E": ("exe6f", 0x1597FC, 0x1632D0, 0x163150, 474),
}
PROFILE_SHA256 = {
    "exe45": "588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8",
    "bn45-us-pvp": TARGETS["bn45-us-pvp"]["fingerprint"]["sha256"],
    "exe45-pvp": "2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278",
    "exe45-soundmod": "60a6ac7f0846a8aa4b890ca4dd4cc1294e6d3d540171e06929e5e3f4dd39ee2e",
    "exegp": "6c3ac853d06b0fa70d9ac5a0705841ddb4f0e06cd246894e60bcb1cf824ef025",
    "exe6": TARGETS['exe6']['fingerprint']['sha256'],
    "exe6f": TARGETS['exe6f']['fingerprint']['sha256'],
}


class Debugger:
    """PTY prompt handling follows the validated rockmanexe-reverse workflow."""
    def __init__(self, command, env, transcript):
        self.master, slave = pty.openpty()
        try:
            self.process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave, env=env)
        except BaseException:
            os.close(self.master)
            raise
        finally:
            os.close(slave)
        self.transcript = transcript

    def prompt(self):
        output = b""
        deadline = time.monotonic() + 20
        while not output.endswith(b"> "):
            if time.monotonic() > deadline:
                raise TimeoutError("Debugger prompt timeout: " + output.decode(errors="replace")[-1500:])
            if select.select([self.master], [], [], 0.2)[0]:
                chunk = os.read(self.master, 65536)
                if not chunk:
                    raise RuntimeError("Debugger closed")
                output += chunk
        text = output.decode(errors="replace").replace("\r", "")
        self.transcript.write(text)
        self.transcript.flush()
        return text

    def command(self, command):
        os.write(self.master, (command + "\n").encode())
        return self.prompt()

    def read(self, size, address):
        text = self.command(f"r/{size} 0x{address:08X}")
        match = re.search(r"\n\s*0x([0-9a-fA-F]+)\s*\n", text)
        if not match:
            raise ValueError(text)
        return int(match[1], 16)

    def hit(self, address):
        text = self.command("continue")
        if f"at 0x{address:08X}" not in text:
            raise RuntimeError("Unexpected breakpoint: " + text)
        return {int(n): int(value, 16) for n, value in re.findall(r"\br(\d+):\s*([0-9a-fA-F]{8})", text)}

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        os.close(self.master)


def validate_sample(rom, data, profile, requested_id, work, mgba, selector_override=None):
    name, offset, table, players, count = profile
    entry = ROM_BASE + offset
    lookup = entry + 12
    call = entry + 28
    returned = entry + 32
    label = "natural" if requested_id is None else f"id-{requested_id}"
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
               XDG_CONFIG_HOME=str(work / "config"))
    # No inherited SDL input injector: these tests use a cold boot without input.
    env.pop("LD_PRELOAD", None)
    with (work / f"{label}-debugger.txt").open("w") as transcript:
        debugger = Debugger([mgba, "-d", str(rom)], env, transcript)
        try:
            debugger.prompt()
            listing = debugger.command(f"disassemble/t 0x{entry:08X} 17")
            (work / "entry-disassembly.txt").write_text(listing)
            if name == "exe45-soundmod":
                (work / "hook-disassembly.txt").write_text(debugger.command("disassemble/t 0x08475A00 42"))
            for target in (entry, lookup, call, returned):
                debugger.command(f"break/t 0x{target:08X}")
            at_entry = debugger.hit(entry)
            natural_id = at_entry[0]
            effective_input = natural_id if requested_id is None else requested_id
            if selector_override is not None:
                debugger.command(f"w/1 0x02003D58 0x{selector_override:X}")
            selector = debugger.read(1, 0x02003D58) if name == "exe45-soundmod" else None
            if requested_id is not None:
                debugger.command(f"w/r r0 0x{requested_id:X}")
            at_lookup = debugger.hit(lookup)
            table_address = at_lookup[0]
            index = (table_address - ROM_BASE - table) // 8
            if not 0 <= index < count or table_address != ROM_BASE + table + index * 8:
                raise AssertionError(f"Lookup outside verified table: {table_address:#x}")
            expected_index = effective_input & 0xFFFF
            remap = {98: (0x475A58, 3), 89: (0x475A58, 3), 99: (0x475A58, 5),
                     65: (0x475A90, 5), 64: (0x475A88, 5)}
            if name == "exe45-soundmod" and effective_input in remap:
                pool, shift = remap[effective_input]
                expected_index = data[pool + (selector >> shift)]
            if index != expected_index:
                raise AssertionError(f"Selected index {index} differs from expected {expected_index}")
            header_pointer, field_a, field_b = struct.unpack_from("<IHH", data, table + index * 8)
            header = song_header(data, header_pointer)
            if header is None or header["empty"]:
                raise AssertionError(f"Selected entry {index} is empty or unsupported")
            at_call = debugger.hit(call)
            player_pointer = struct.unpack_from("<I", data, players + field_a * 12)[0]
            if at_call[0] != player_pointer or at_call[1] != header_pointer:
                raise AssertionError("Runtime player/header differs from ROM lookup")
            capacity = debugger.read(1, player_pointer + 8)
            debugger.hit(returned)
            active_header = debugger.read(4, player_pointer)
            tone_pointer = debugger.read(4, player_pointer + 48)
            expected_tone = ROM_BASE + header["tone_bank"]["file_offset"]
            if active_header != header_pointer or tone_pointer != expected_tone:
                raise AssertionError("Player did not accept expected header and tone bank")
            return {"scenario": label, "natural_input_id": natural_id,
                    "requested_id": natural_id if requested_id is None else requested_id,
                    "register_injection": requested_id is not None, "selector_override": selector_override,
                    "selected_index": index, "selector_byte": selector, "expected_index": expected_index, "entry_address": f"0x{table_address:08X}",
                    "header_address": f"0x{header_pointer:08X}",
                    "player_index": field_a, "second_field_raw": field_b,
                    "player_address": f"0x{player_pointer:08X}",
                    "player_track_capacity": capacity, "header_track_count": header["track_count"],
                    "active_header": f"0x{active_header:08X}", "tone_bank": f"0x{tone_pointer:08X}",
                    "checks_passed": ["id_selection", "table_lookup", "player_lookup", "header_argument", "active_header", "tone_bank"]}
        finally:
            debugger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--id", type=lambda v: int(v, 0), action="append", default=[])
    parser.add_argument("--selector", type=lambda v: int(v, 0), help="Controlled Soundmod selector-byte override (0..255)")
    parser.add_argument("--out", type=Path, required=True, help="New disposable directory")
    parser.add_argument("--mgba", default="/usr/games/mgba")
    args = parser.parse_args()
    data = args.rom.read_bytes()
    origin = {"rom_path": str(args.rom), "source_fingerprint": fingerprint(data)}
    if args.patch:
        patch = args.patch.read_bytes()
        data, info = apply_bps(data, patch)
        origin.update(patch_path=str(args.patch), patch_fingerprint=fingerprint(patch), bps=info)
    image = fingerprint(data)
    profile = PROFILES.get(image["crc32"])
    if profile is None or image["sha256"] != PROFILE_SHA256[profile[0]]:
        parser.error("Playback addresses have not been verified for this ROM fingerprint")
    if args.selector is not None and (profile[0] != "exe45-soundmod" or not 0 <= args.selector <= 255):
        parser.error("--selector requires Soundmod and a byte in 0..255")
    if any(not 0 <= n < profile[4] for n in args.id) or len(set(args.id)) != len(args.id):
        parser.error("IDs must be unique and within the verified table")
    for n in args.id:
        pointer = struct.unpack_from("<I", data, profile[2] + n * 8)[0]
        header = song_header(data, pointer)
        if header is None or header["empty"]:
            parser.error(f"ID {n} is empty or structurally unsupported")
    args.out.mkdir(parents=True, exist_ok=False)
    work = args.out.resolve()
    rom = work / "test.gba"
    rom.write_bytes(data)
    samples = []
    version = subprocess.run([args.mgba, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    report = {"schema_version": 1, "profile": profile[0], "fingerprint": image,
              "provenance": origin, "emulator": version, "bios": "mGBA built-in",
              "limitations": ["register or selector injected cases are controlled probes, not unmodified game calls",
                              "no audible output or sustained playback checked",
                              "no resource dependency decoding or relocation performed"],
              "samples": samples, "complete": False}
    try:
        for requested in [None] + args.id:
            sample = validate_sample(rom, data, profile, requested, work, args.mgba, args.selector)
            samples.append(sample)
            print(f"{profile[0]} {sample['scenario']}: input {sample['requested_id']} -> entry {sample['selected_index']}, "
                  f"header {sample['header_address']}, {sample['header_track_count']} tracks; checks passed", flush=True)
        report["complete"] = True
    finally:
        (work / "validation.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
