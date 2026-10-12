# Audio playback entry points and runtime validation

Status: entry-point disassembly, table lookup, player selection, and player header/tone-bank initialization verified on the local ROM versions. Track instruction execution, audible output, complete dependencies, and BGM/SFX names remain unverified.

## Baselines

The validator accepts only the CRC32 and full SHA-256 profiles below. It refuses other revisions rather than applying these addresses to an unknown ROM.

| Profile | CRC32 | SHA-256 |
|---|---|---|
| Original EXE4.5 | `A646601B` | `588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8` |
| EXE4.5 PvP 0.6.0 | `D1240E4B` | `2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278` |
| EXE4.5 Soundmod | `D0020C1F` | `60a6ac7f0846a8aa4b890ca4dd4cc1294e6d3d540171e06929e5e3f4dd39ee2e` |
| EXEGP | `9217FB18` | `6c3ac853d06b0fa70d9ac5a0705841ddb4f0e06cd246894e60bcb1cf824ef025` |

## Entry points and table fields

mGBA's Thumb disassembler confirms these addresses:

| Function/data | EXE4.5 | EXEGP |
|---|---|---|
| Start audio by ID | `0x080EE344` | `0x0804C3BC` |
| Table lookup, before reading first halfword | `0x080EE350` | `0x0804C3C8` |
| Call player initialization | `0x080EE360` | `0x0804C3D8` |
| Return from player initialization | `0x080EE364` | `0x0804C3DC` |
| Player initialization target | `0x080EEA78` | `0x0804CAF0` |
| Audio table | `0x08135214` | `0x08160658` |
| Player descriptor table | `0x08135094` | `0x08160604` |

Original EXE4.5 and EXEGP use the same lookup sequence apart from addresses. The shift pair `lsl r0,#16; lsr r0,#13` computes `(input_id & 0xFFFF) * 8`. The entry's pointer at `+0` supplies the audio header. The halfword at `+4` indexes a 12-byte player descriptor; its pointer at `+0` supplies player state. The initialization function receives the player pointer in `r0` and the header pointer in `r1`.

Thus `field_a_raw` has a verified player-index role for this entry point. The halfword at entry `+6` is not read by this routine; its role remains unverified. A player index is not a track count. For example, PvP entry 69 selects player 12 but has a one-track header and a two-track player capacity.

The player header pointer at `+0` and tone-bank pointer at `+48` match their expected ROM values after the call. Capacity is observed at player offset `+8`. The core disassembly checks the initialization marker at `+52`, handles priority, stores the header, and reads its tone bank. These observations do not establish all fields of the player structure.

The lookup routine itself has no visible table-length check. Scanner-derived table lengths and explicit range checks must be retained in tools that accept user-selected IDs.

## Runtime procedure

`scripts/validate_playback.py` uses ordinary mGBA 0.10.2 with its built-in BIOS and dummy SDL video/audio drivers. Each scenario boots a disposable ROM copy with no personal save. BPS targets are decoded and checksum-verified before a test copy is written. The input files are untouched.

Each run first reaches the start-by-ID routine naturally. Its first argument is 68 for the three EXE4.5 versions, and 148 for EXEGP. The default scenario preserves that argument. Requested `--id` cases replace only `r0` at this naturally reached entry, rather than replacing executable ROM code. An optional `--selector` writes Soundmod's selector byte for a controlled mapping test. mGBA installs its own software breakpoints.

Breakpoints then check the selected table address, player pointer, and header argument. After initialization returns, the active header and tone bank are read from player RAM. Each sample has a debugger transcript and JSON record, including whether register or selector injection occurred. Each scenario starts a fresh emulator process; previous tracks and priorities do not contaminate the next scenario.

## Representative results

The initial runs completed 11 scenarios:

| Profile | Requested IDs | Selected IDs | Header track counts |
|---|---|---|---|
| Original EXE4.5 | natural 68, injected 9, 90 | 68, 9, 90 | 3, 7, 6 |
| PvP | natural 68, injected 69 | 68, 69 | 3, 1 |
| Soundmod | natural 68, injected 0, 69 | 68, 0, 69 | 3, 6, 8 |
| EXEGP | natural 148, injected 1, 100 | 148, 1, 100 | 1, 7, 3 |

All selected headers, players, active headers, and tone banks matched. EXEGP entry 1 selects player 0 with a capacity of 10 tracks; entry 100 selects player 1 with a capacity of three. These differences help choose future music and effect probes, but do not by themselves label every entry as BGM or SFX.

## Soundmod's existing selection hook

Soundmod replaces the instructions at `0x080EE346–0x080EE349` with a call to `0x08475A00`. The hook remaps certain input IDs once, then performs the displaced shift and loads the original player table. The main lookup still uses `0x08135214`, not the additional scanner candidate at `0x09135214`.

The hook reads a byte at RAM address `0x02003D58`. Its producer and statistical behavior have not been investigated; it is called a selector byte here, not proven to be a uniform random source.

| Input ID | Pool ROM address | Pool index |
|---|---|---|
| 89 or 98 | `0x08475A58` | `selector >> 3` (0–31) |
| 99 | `0x08475A58` | `selector >> 5` (0–7) |
| 64 | `0x08475A88` | `selector >> 5` (0–7) |
| 65 | `0x08475A90` | `selector >> 5` (0–7) |

Other inputs retain their IDs. Remapping is not recursive: pool entries such as 89, 98, or 64 are used directly for the subsequent audio-table lookup.

The pool bytes, expressed as decimal audio IDs, are:

```text
0x08475A58:
  5, 18, 98, 69, 79, 88, 33, 89,
  6, 19, 99, 70, 80, 23, 34, 72,
  5, 18, 98, 69, 79, 88, 33, 89,
  6, 19, 82, 70, 80, 23, 34, 11
0x08475A88:
  3, 16, 64, 38, 77, 86, 32, 29
0x08475A90:
  4, 17, 65, 66, 39, 78, 87, 65
```

Six further cold-boot scenarios verified selector zero: natural ID 68 remains 68, and injected IDs 89, 64, 65, 99, 98 select 5, 3, 4, 5, 5 respectively. All initialization checks passed. Five controlled selector-255 probes also passed: input 68 remains 68, and inputs 89, 64, 65, 99 select 11, 29, 65, 89 respectively. These exercise the opposite end of each selection range and are preserved separately under `out/playback-soundmod-selector255/`. In total, all 22 scenarios completed successfully.

The repeated entries and the smaller subset used by ID 99 matter to the future manager. A general list of tracks cannot simply replace every pool: pool lengths, shifts, player selection, and shared IDs must be considered together. This hook also overlaps the PvP additions at IDs 69–80, so both resource relocation and ID remapping are needed for the combined ROM.

## Reproduction

Requires Linux, Python 3.10+, and the mGBA SDL executable with its CLI debugger. Each output directory must be new. Use another directory name when repeating a run.

```bash
python3 scripts/validate_playback.py roms/exe45.gba \
  --id 9 --id 90 --out out/playback-exe45
python3 scripts/validate_playback.py roms/exe45.gba \
  --patch references/exe45_pvp_0.6.0.bps \
  --id 69 --out out/playback-pvp
python3 scripts/validate_playback.py roms/exe45.gba \
  --patch references/exe45_soundmod.bps \
  --id 0 --id 69 --out out/playback-soundmod
python3 scripts/validate_playback.py roms/exegp.gba \
  --id 1 --id 100 --out out/playback-exegp
python3 scripts/validate_playback.py roms/exe45.gba \
  --patch references/exe45_soundmod.bps \
  --id 89 --id 64 --id 65 --id 99 --id 98 \
  --out out/playback-soundmod-remap
python3 scripts/validate_playback.py roms/exe45.gba \
  --patch references/exe45_soundmod.bps --selector 255 \
  --id 89 --id 64 --id 65 --id 99 \
  --out out/playback-soundmod-selector255
```

`validation.json` records profile hashes, source/patch provenance, emulator version, sample state, and whether the run completed. `*-debugger.txt` contains the actual breakpoint and memory-read evidence. `entry-disassembly.txt` contains the entry window; for Soundmod, `hook-disassembly.txt` includes the hook and the beginning of its literal pool, which must not be interpreted as executable instructions.

## Limits and next target

These are initialization checks, not listening tests. The dummy audio backend discards output, and the debugger stops immediately after the initialization call. Neither long-running track execution nor complete sample validity has been verified. Controlled injections are explicitly distinct from natural game behavior; selector tests do not prove its distribution during gameplay.

Next, decode track control flow and tone/sample dependencies for EXEGP entry 1 as a concrete transplantation candidate, and verify its sustained playback before moving it into the PvP ROM. Preserve player-capacity requirements and distinguish sequence/instrument data from code patches during relocation.
