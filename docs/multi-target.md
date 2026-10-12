# Multiple target ROMs

The manager separates the **target game** (the ROM being modified), optional **pre-patch**, and **music sources**. A supported music source is not automatically a supported patch target. The current targets are EXE4.5 JP PvP 0.6.0, BN4.5 English PvP 0.6.0, and the original Japanese EXE Battle Chip GP ROM. EXE1 and BN2 remain music sources; their target adapters are the next expansion.

## Use EXE GP as the target

Choose **Rockman EXE Battle Chip GP (JP)** under **Game to modify**, then click **Load tracks**. Its input defaults to `../roms/exegp.gba`, or use **Choose file** to provide the supported original revision. No PvP patch is required. Select the original games to use as music sources separately.

The GP catalog preserves all 170 native audio IDs. Sixteen entries belong to its music player; these become the default configurable music events. **Title screen** is event 1. Select an event, check its pool tracks, and export. Apply `unified.bps` to the original **EXE GP ROM**, or use the exported `unified.gba` directly. Do not apply it to EXE4.5.

A target can also be chosen at startup:

```bash
python3 scripts/manage_sound.py --target exegp
python3 scripts/manage_sound.py --target bn45-us-pvp
python3 scripts/manage_sound.py --target exe45-pvp
```

`--target` and `--pvp-patch` are mutually exclusive startup overrides. Without either, the manager restores the selected target from `out/manager/target.json`, falling back to Japanese EXE4.5 PvP. The UI remembers target changes. Uploaded input files and custom pre-patches remain session-local.

EXE4.5 JP/English pools continue to use `project.json`; GP pools use `project-exegp.json`. Switching targets stops live audio, invalidates the catalog and preview cache, and clears stale download links. Saved projects are restored separately. Exported projects record their target; importing a project for another target is rejected. Existing EXE4.5 projects without a target field remain usable. Native GP keys use `native-exegp:*`, while legacy/native EXE4.5 keys retain `pvp:*`. Donor keys and fixed slot assignments remain unchanged.

## Shared implementation

`scripts/target_profiles.py` holds ROM fingerprints, required original inputs, pre-patch presets, and verified driver layouts. Both EXE4.5 PvP variants share `exe45-audio-v1`; GP uses `exegp-audio-v1`.

The common code handles catalog construction, conservative sequence/dependency analysis, sparse tone banks, resource allocation and deduplication, pointer relocation, stable donor slots, pool rules, Thumb encoding, native table/prefix preservation, relocation reparsing, and BPS reconstruction. Realtime playback, names, source selection, jobs, and downloads are also shared.

The exporter also adapts verified fixed-step PCM donor waves to the target mixer rate. EXE1 JP drums require this when imported into GP; otherwise they play 1.5 times too fast. Native target audio retains its original resources. See [fixed-step PCM diagnosis and validation](audio-fidelity.md#exe1-opening-drum-correction).

Layouts supply the song/player table locations, native entry count, music player, playback entry/core, table references, SoundMode precondition, selector source, preview event, default events, and preservation probes. The builder checks exact target identity and expected bytes before writing. mGBA capture and runtime validators obtain the same addresses from the target profile. Adding a fingerprint alone does not establish target support.

GP additionally uses a status-query adapter. Its game helper at `0x08003000` normally compares the native header with the active player header. That comparison fails after selecting a foreign song. The adapter recognizes active headers belonging to the requested pool and returns the player's existing status, allowing the original fade helper to work. Unconfigured queries retain native header comparison. No tracking RAM is allocated. Other driver helpers keep their original start/continue/stop semantics; every game path has not been audited.

## GP layout evidence

The original GP ROM has CRC32 `9217FB18` and SHA-256 `6c3ac853d06b0fa70d9ac5a0705841ddb4f0e06cd246894e60bcb1cf824ef025`.

| Field | Verified value |
| --- | --- |
| Start-by-ID entry | `0x0804C3BC` |
| Player initialization core | `0x0804CAF0` |
| Song table | file offset `0x160658`, 170 entries |
| Player table | file offset `0x160604` |
| Music player / capacity | player 0 / 10 tracks |
| Startup SoundMode | `0x0095FA00` at file offset `0x4C3A0`; already ten PCM channels |
| Song table literals | `0x2FFC`, `0x3028`, `0x4C3E4`, `0x4C418`, `0x4C464`, `0x4C4B8`, `0x4C4EC` |
| Game status query | `0x08003000` |
| Title event | 1, reached naturally after startup effects 148, 150, 150, 158 |

The selector reads the existing scheduler tick at `0x030023C0`. The scheduler increments it at `0x08000D44`–`0x08000D48`; natural samples advance from 425 to 435. The hook applies xorshift32 mixing, takes the low byte, then applies the configured shift and modulo pool length. It only reads game state. This is timing-dependent selection, not a claim of uniform or nondeterministic randomness: identical boot/input timing can reproduce a choice. EXE4.5's existing RNG1-byte selection remains byte-identical.

Only declared prefix ranges change: SoundMode, start stub, seven table literals, and the GP status-query stub. Every native table entry and its resources remain intact. Foreign songs are assigned to GP player 0, never to their donor player number. Imported songs are checked against the target's ten-track capacity. GP donor entry 5 therefore becomes eligible for GP export, while remaining over-capacity for the eight-track EXE4.5 target.

## Validation

Evidence is local under `out/multi-target-research/`:

- 67 Python tests cover both EXE4.5 output regressions, GP prefix/native table preservation, write preconditions, selected-only imports, project rejection/isolation, target persistence, and GP BPS reconstruction. Node fixtures cover UI target changes and audio streaming behavior.
- Reference builds for both EXE4.5 PvP variants remain byte-identical to outputs saved before the refactor. Their SHA-256 values are `a33019c572fed9831062197d09bfabf4d72b99f5f9afd4b504fe7b982ab5e212` (JP) and `ac8e91bb9ba07bd34aa7b8b23f30f46781e3585d4e7f350a5139347af9fb0373` (English).
- Eight GP hook/query probes initialize native effects 100, 148, 150, 158 and all three pool entries, including EXE1 entry 0. Controlled tick inputs 0, 8, 16 cover pool positions 0, 2, 1. Selected header/player, status-query return, callee-saved registers, and stack match expectations.
- EXE1 entry 2 starts naturally on GP's title screen and passes 901 frames of sustained execution, complete loop coverage, all five tracks and all five PCM samples. No register/header redirection is used.
- A natural original/transplanted comparison reaches the same title fade request (ID 1, caller `0x0804A03B`). The original song has finished at clock 1805/status 0; the longer foreign song is still active at clock 1527/status 63. This confirms the fade is requested by unchanged game lifecycle code. Evidence: `natural-fade/comparison.json`.
- The actual HTTP workflow loads GP, exports and reconstructs its BPS, streams native GP music through agbplay, records a transplanted EXE1 song, switches to English PvP, then restores GP pools. Its three-second mGBA preview is 44.1 kHz stereo with peak 28907. These are HTTP and fixture checks, not a new real-browser test.

The original game lifecycle remains active. A longer EXE1 title track reaches the GP title fade/transition before complete loop coverage; the strict sustained validator correctly reports that interruption. The status adapter restores fade behavior rather than suppressing scene transitions. Short previews and representative successful songs do not prove that every donor plays to completion in every scene. Multiplayer, hardware, and exhaustive GP gameplay validation remain unperformed.

## Add another target

First verify the exact original ROM and its audio table/player assignments. Identify the playback core, all relevant table references, initialization configuration, and actual scene-to-music-ID calls. Determine a suitable selector source and inspect status/fade/stop helpers that compare native headers. Add a layout or adapter only where behavior differs.

Then validate one foreign song in the new target, preserve native effects and all undeclared bytes, verify pool choices and calling conventions, capture actual emulator output, and perform natural sustained playback. Only expose the target in the manager after these checks. EXE1 and BN2 should follow this process; their donor profiles alone are insufficient.
