# Original-ROM music library

The local manager now reads music from original ROMs in `../roms/`, replacing Soundmod BPS as its music source. The legacy Soundmod-based CLI remains available for reproducing previous experiments. The shared directory has 23 supported donor profiles, including original EXE4.5 as both a pre-patch input and an independent music source.

## Discovery and profiles

`scan_audio.scan_tables` found one structural M4A-style table in each supplied ROM. The exact source fingerprints, table offsets/counts, profile music-player index, game label, and fixed target-slot ranges are recorded in `config/rom-profiles.json`. Profile identity uses the ROM SHA-256 rather than its uploaded filename. Other revisions are rejected.

The profiles use player 31 for the EXE/BN RPG entries and player 0 for Battle Chip GP/Challenge candidates. These assignments are based on the table grouping and track structure, with representative transplanted runtime checks; they are not an exhaustive donor entry-point audit or verified song-name inventory.

| Source | Table offset | Entries | Eligible music-player candidates |
|---|---:|---:|---:|
| Mega Man Battle Network 1 (EN) (`bn1`) | `0xA111C` | 238 | 20 |
| Mega Man Battle Network 2 (EN) (`bn2`) | `0xF3898` | 304 | 35 |
| Mega Man Battle Network 3 White (EN) (`bn3`) | `0x148B6C` | 330 | 34 |
| Mega Man Battle Network 3 Blue (EN) (`bn3b`) | `0x148C6C` | 330 | 34 |
| Mega Man Battle Network 4 Red Sun (EN) (`bn4`) | `0x155FF8` | 457 | 34 |
| Mega Man Battle Network 4 Blue Moon (EN) (`bn4b`) | `0x15600C` | 457 | 34 |
| Mega Man Battle Network 5 Team ProtoMan (EN) (`bn5`) | `0x155B0C` | 372 | 35 |
| Mega Man Battle Network 5 Team Colonel (EN) (`bn5k`) | `0x155BF4` | 372 | 35 |
| Mega Man Battle Network 6 Gregar (EN) (`bn6`) | `0x159F48` | 474 | 35 |
| Mega Man Battle Network 6 Falzar (EN) (`bn6f`) | `0x1583F8` | 474 | 35 |
| Mega Man Battle Chip Challenge (EN) (`bnbcc`) | `0x106DD0` | 170 | 15 |
| Rockman EXE 1 (JP) (`exe1`) | `0xA0EFC` | 238 | 20 |
| Rockman EXE 2 (JP) (`exe2`) | `0xF3774` | 304 | 35 |
| Rockman EXE 3 (JP) (`exe3`) | `0x149408` | 330 | 34 |
| Rockman EXE 3 Black (JP) (`exe3b`) | `0x149518` | 330 | 34 |
| Rockman EXE 4 Red Sun (JP) (`exe4`) | `0x155E64` | 457 | 34 |
| Rockman EXE 4 Blue Moon (JP) (`exe4b`) | `0x155E78` | 457 | 34 |
| Rockman EXE 4.5 Real Operation (JP) (`exe45`) | `0x135214` | 499 | 47 |
| Rockman EXE 5 Team Blues (JP) (`exe5`) | `0x155674` | 372 | 35 |
| Rockman EXE 5 Team Colonel (JP) (`exe5k`) | `0x15575C` | 372 | 35 |
| Rockman EXE 6 Gregar (JP) (`exe6`) | `0x164E0C` | 474 | 35 |
| Rockman EXE 6 Falzar (JP) (`exe6f`) | `0x1632D0` | 474 | 35 |
| Rockman EXE Battle Chip GP (JP) (`exegp`) | `0x160658` | 170 | 15 |

With every source selected for EXE4.5, the full library has **8,954 entries**, of which **787 are playlist-eligible**: 48 native PvP entries and 739 original-ROM donor entries. English/Japanese and version variants remain separate sources, so these counts include duplicate compositions.

Foreign candidates must fit the target eight-track capacity and pass conservative sequence/tone/PCM dependency analysis. Over-capacity entries, notes before explicit VOICE initialization, and unsupported commands remain visible but unavailable.

## Packing and preservation

Native PvP IDs 0–498 remain unchanged. Every donor profile has a fixed reserved range covering all of its table entries, including effects and empty entries. IDs stay stable when other ROMs are absent or added. Keys such as `exe1:0` and `exe6:1` are the project-facing identifiers. Numeric target IDs differ from the older Soundmod-based allocation.

Original EXE4.5 uses keys such as `exe45:55` and an appended slot range 8,455–8,953. The table keeps its existing 8,455-slot span when this source is not selected, preserving previous outputs. Selecting EXE4.5 extends it to 8,954 slots. The original file is recognized by its SHA-256 even if uploaded under another filename. PvP/translated/exported ROMs are not accepted as original music sources.

When EXE4.5 is the target, `pvp:*` continues to identify native target playback and `exe45:*` identifies the original donor; compositions can overlap. With GP as the target, selecting `exe45.gba` provides 47 importable original EXE4.5 candidates. Its verified 10,512 Hz fixed-PCM rate is adapted through the shared exporter. Original/title and GP-transplanted three-second mGBA clips, live agbplay PCM and source-role upload/export checks are recorded under `out/exe45-source-check/`.

The manager packs only foreign entries referenced by the export pools. It uses the same checked sparse-bank relocation, PCM deduplication, start-by-ID hook, and ten-channel mixer setting as the previous unified builder. Original PvP table entries and resources are preserved. Unselected foreign table slots remain empty. Every imported song is reparsed after packing, comparing notes, timing, termination, and sample contents.

## Runtime and browser evidence

A Chromium browser against the real local HTTP server completed the following workflow without JavaScript exceptions: load all 22 donors, display 740 available rows, filter EXE1 and EXE6, record and fetch their three-second WAV previews, add entries from both games to the title pool, export, and download BPS/ROM/project/catalog files.

EXE1 entry 0 and EXE6 entry 1 played through the normal title-start hook with no debugger register injection. Each captured WAV was 529,244 bytes: 44.1 kHz, stereo signed 16-bit, exactly three seconds of nonzero full SDL audio. These are representative playback checks, not sustained whole-track validation or listening approval for the entire catalog.

The mixed browser export was 8,751,444 bytes; its BPS was 667,821 bytes. The backend decoded the BPS and compared it with the generated ROM byte-for-byte. Browser evidence is retained under `out/original-browser-validation/`; structural inventories are under `out/original-rom-inventory/`.

A separate batch check relocated and reparsed **all 692 eligible original-ROM donor entries** into a 12,337,752-byte test image. Note/timing/termination/sample comparisons and native PvP preservation checks passed. The report is retained in `out/original-library-relocation-check/build.json`. This verifies packing across the entire eligible library, not full-track runtime playback.

The Python suite passes 45 tests, including selected-only imports, fingerprint-based donor identity, stable profile IDs, legacy builder preservation, input rejection, names/projects, and BPS reconstruction. The lightweight DOM/API workflow check also passes.

## Limits

Track labels show the original game plus table index until manually named. Classification is by music-player assignment; some short cues may be included and other players may contain music-like audio. Unsupported sequences are excluded. Short title-screen previews retain the normal game lifecycle and are capped at 30 seconds. The existing selector byte has no verified uniform distribution; pools support 1–255 entries, and finite songs do not advance automatically. Hardware timing and PvP multiplayer remain untested.

See [manager usage](manager.md) for the interface and [the previous unified build](unified-catalog.md) for the underlying hook and preservation evidence.
