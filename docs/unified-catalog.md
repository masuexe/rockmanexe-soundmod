# Unified catalog, combined build, and ROM-resident selection

Status: version-pinned catalog, batch relocation, stable IDs, configurable selection pools, combined BPS export, natural title playback, and representative Soundmod loop playback verified. A local browser manager now provides names, listening previews, pool editing, and export; multiplayer validation remains pending.

## Stable IDs and eligibility

The catalog reserves IDs independently of selection and eligibility:

| Source | Target IDs | Allocation |
|---|---|---|
| PvP | 0–498 | Original table indices, including empty entries, unchanged |
| Soundmod additions | 499–550 | All 52 changed entries, sorted by source index |
| EXEGP | 551–636 | All 86 nonempty entries, sorted by source index |

Stable keys such as `pvp:69`, `soundmod:69`, and `exegp:1` distinguish sources. For example, PvP effect 69 remains 69; Soundmod music 69 becomes 531; EXEGP music 1 becomes 551. The provisional slot 0 from the earlier single-song experiment is no longer used for imports.

The 637-row catalog includes 115 eligible music-player candidates:

- 48 native entries using PvP music player 31.
- All 52 Soundmod additions, using player 31 and no more than eight tracks.
- 15 EXEGP entries using donor music player 0 and no more than eight tracks.

EXEGP has 16 entries on its music player. Entry 5 needs nine tracks, exceeding PvP player 31's eight-track capacity, and remains reserved but unavailable. The 70 other EXEGP entries use other players and are listed as nonmusic candidates; they are not imported by the music builder. Classification is based on player assignment, not verified titles or exhaustive listening.

Unavailable slots remain empty in the expanded table, and cannot be selected in a pool. Their reservations prevent later eligibility changes from renumbering existing keys. Empty/native effect entries cannot be used as playlist triggers or tracks.

```bash
python3 scripts/unified_catalog.py \
  --base ../roms/exe45.gba \
  --pvp-patch references/exe45_pvp_0.6.0.bps \
  --soundmod-patch references/exe45_soundmod.bps \
  --donor ../roms/exegp.gba --out out/unified-catalog
```

`catalog.json` records source hashes, player indices, track counts, eligibility, dependency summaries, and target IDs. `catalog.csv` provides a readable inventory. Names remain unassigned.

## Batch relocation and preservation

The builder independently decodes PvP and Soundmod from the original ROM and checks their known SHA-256 profiles. It imports supported dependencies rather than copying Soundmod's extension over PvP's extension.

Selected tone rows are accumulated into shared sparse banks. Identical pointer-free PCM samples, keymaps, and PSG waves are deduplicated by content. Pointer-bearing headers and sequences use source/offset cache keys and are relocated separately. All 67 imported songs are reparsed after the complete bank updates; notes, timing, termination, and encoded PCM contents match their sources.

The expanded table contains an exact copy of the original 499 PvP entries, followed by imported or reserved entries. All five known table literals are repointed to the expanded table. The original table and existing PvP resources remain present and unchanged.

Changes within the original PvP image are limited to:

- The effective startup SoundMode literal at `0x504`, retaining the previously validated ten-channel budget.
- A 20-byte entry stub at `0xEE344`.
- Table literals at `0xEE36C`, `0xEE3A0`, `0xEE3EC`, `0xEE440`, and `0xEE474`.

The expanded table, imported resources, selection pools, rule records, and handler are appended. Preservation checks reject any other prefix changes.

The reference build imports 67 songs into a 9,585,460-byte ROM (approximately 9.14 MiB), rather than retaining the Soundmod ROM's 24 MiB layout. Its relocation cache records 447 resource hits, and the 1,006,096 appended bytes include resources, banks, the table, and the handler.

## Permanent selection hook

The start-by-ID entry uses a small ARMv4T Thumb far-call stub to reach the appended handler. An indirect call is required because the appended code is beyond the immediate Thumb BL range from the original entry. A local BL/BX trampoline supplies a correctly tagged Thumb return address.

The handler preserves callee-saved registers and the stack, normalizes the incoming ID to 16 bits, looks for a matching rule, and chooses a target ID. It then performs the original table/player lookup and calls the existing player initialization routine. Native IDs without a rule pass through unchanged.

All other table helpers use the expanded table, but retain their own selection logic. Selection currently hooks **start-by-ID only**, matching the entry modified by the original Soundmod. Stop/change/continue behavior for mapped tracks outside the validated title flow needs broader gameplay checks.

The actual title-screen start call uses native ID **55**, observed during an unmodified boot. The default pool redirects it to EXEGP ID 1, stable target ID 551. The introductory ID 68 and subsequent effect IDs 495, 344, and 496 retain their original headers and players.

## Editing pools

`config/playlist.json` is the current management interface. Each rule names a native music trigger and a list of stable track keys:

```json
{
  "schema_version": 1,
  "pools": {
    "55": {
      "tracks": ["exegp:1", "soundmod:0", "soundmod:1"],
      "selector_shift": 0
    }
  }
}
```

Pool length can be 1–255; it does not need to be a power of two. Duplicate keys intentionally give repeated pool entries. `selector_shift` can be 0–7.

The selector is the existing Soundmod byte at `0x02003D58`. Selection computes:

```text
pool_index = (selector_byte >> selector_shift) % pool_length
```

The handler uses BIOS Div (SWI 6) to obtain the remainder; [mGBA's BIOS implementation](https://github.com/mgba-emu/mgba/blob/0.10.2/src/gba/bios.c) and actual emulator probes independently support this behavior. The selector's producer and probability distribution remain unverified. No uniform randomness or new PRNG is claimed; arbitrary pool lengths can introduce modulo bias.

The default configuration retains Soundmod's five selection rules for IDs 64, 65, 89, 98, and 99, including their shifts, repeated entries, and ID 99's eight-entry subset. References to Soundmod 69–80 are converted to their new IDs rather than calling the protected PvP effects. It additionally selects EXEGP 1 for title ID 55.

Rebuild after changing the JSON file. Selecting a different pool does not renumber the catalog. The builder currently packs all 67 eligible foreign songs even when a particular pool does not reference them.

## Build and test

```bash
python3 scripts/build_unified.py \
  --base ../roms/exe45.gba \
  --pvp-patch references/exe45_pvp_0.6.0.bps \
  --soundmod-patch references/exe45_soundmod.bps \
  --donor ../roms/exegp.gba \
  --playlist config/playlist.json --out out/unified-v2

python3 scripts/validate_unified.py out/unified-v2/unified.gba \
  --manifest out/unified-v2/build.json --out out/unified-v2-hook-validation

python3 scripts/validate_song.py out/unified-v2/unified.gba \
  --unified out/unified-v2/build.json --out out/unified-v2-title-validation
```

Use new output directory names when repeating a command. The builder writes `unified.gba`, `unified.bps`, `build.json`, `catalog.json`, and `catalog.csv`. The BPS applies directly to original EXE4.5 CRC32 `A646601B`; source, target, and patch checksums are verified, and decoding reproduces the combined ROM byte-for-byte.

Reference output CRC32: `DF994B26`; SHA-256:

```text
e20a5763e40d3510b200c9fd1a67597eb384d290007e3e38e3b40e5a621b5854
```

The exported BPS is 1,501,838 bytes.

## Verification evidence

The default hook suite passed **31 controlled scenarios**:

- Native ID 68 and each PvP addition 69–80 retain the expected player/header.
- Six configured triggers were tested with selector values 0, 128, and 255.
- After initialization, the active header and tone bank match the selected entry.
- On return to the caller, registers r4–r11 and the stack pointer match their entry values.

A separate three-track title pool passed five scenarios, including selector values 0, 1, 2, and 255. Those select target IDs 551, 499, 500, and 551, validating a non-power-of-two pool and 16-bit IDs beyond the original table.

The default title run passed **1,556 frames**, seven tracks, all nine PCM samples, and normal completion at clock 1804. It used no register injection, no selector override, and no debugger header redirection. The ROM hook itself selected the imported song during normal startup.

A separate configuration selecting `soundmod:0` for title ID 55 passed **2,571 frames**, six tracks, all five PCM samples, and loop coverage through clock 2125. Its state checks crossed the repeated-state boundary and an additional full loop. It also used natural startup without debugger writes.

An exploratory longer `soundmod:3` title run was stopped by the game's attract/demo behavior before full loop coverage: at frame 2586, track 0 became inactive while its cursor/note/tone still matched. That failed run is retained as incomplete evidence, not counted as a successful loop test. A future preview player should isolate song playback from title-screen lifecycle changes.

All **37 automated tests** pass, including preservation, stable IDs, conflict remapping, sparse dependency handling, PCM deduplication, loop-state projection, invalid pool rejection, and BPS reconstruction tests from prior stages. No full gameplay pass for every imported track or PvP multiplayer test has been performed. The dummy audio backend establishes sequence/mixer execution but is not a listening review.

## Listening feedback and local manager

After receiving the reference unified ROM, the user reported that listening tests were completely satisfactory and authorized the manager milestone. This is human feedback on their tested playback, not evidence of an exhaustive audit of every imported song or multiplayer behavior.

The [local manager](manager.md) now uses this JSON catalog and pool contract for file selection, filtering, names, previews, and checked exports. Default manager export reproduces the reference ROM SHA-256 above. Preview builds use a separate single-track title pool and do not change the saved export pools. Selection still occurs on game start calls; finite tracks do not advance automatically.

## Original-ROM manager update

The manager now reads original EXE/BN ROMs directly from `../roms/` and does not require Soundmod BPS. It retains this relocator and hook but uses separate fixed per-ROM slot ranges and packs only selected foreign songs. The Soundmod allocation, default configuration, and reference fingerprints in this document describe the legacy CLI build. See [the original-ROM library record](original-rom-library.md) for current manager profiles and validation.
