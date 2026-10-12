# English PvP 0.6.0 target

The manager and unified builder support both `exe45_pvp_0.6.0.bps` and `bn45_us_pvp_0.6.0.bps`. Both supplied patches apply directly to the same original Japanese EXE4.5 ROM. A separately translated input ROM is not required.

## Use the English target

Start the manager from the project root:

```bash
python3 scripts/manage_sound.py \
  --pvp-patch ../patches/bn45_us_pvp_0.6.0.bps
```

Alternatively, use **Choose file** for the PvP BPS input in an already restarted manager server. Select that BPS, keep `../roms/exe45.gba` as the base, and click **Load tracks**. The catalog reports the English target and labels native entries as `BN4.5 (English PvP base)`. Source checkboxes, realtime preview, saved pool keys, and export work the same way as for the Japanese target.

Communication battle music remains **Music event #98**. Its pool accepts the same stable keys. Every scene requesting that ID is affected by the rule. Use the exported ROM directly, or apply its BPS to the original EXE4.5 ROM. The generated BPS includes the English translation, PvP changes, and configured music changes together.

`--pvp-patch` is a startup option. Uploaded patch selection is held for the current server session; restarting without that option uses the default Japanese patch. Source-checkbox preferences and saved pools remain in the selected manager data directory.

The default Japanese patch is discovered in `../patches/exe45_pvp_0.6.0.bps`, falling back to the older `references/` copy when the shared file is absent. Target identity is determined by the decoded ROM fingerprint, not the patch filename. Other revisions remain rejected.

The legacy Soundmod-based builder also accepts the English target:

```bash
python3 scripts/build_unified.py \
  --base ../roms/exe45.gba \
  --pvp-patch ../patches/bn45_us_pvp_0.6.0.bps \
  --soundmod-patch ../patches/exe45_soundmod.bps \
  --donor ../roms/exegp.gba \
  --playlist config/playlist.json --out out/english-legacy-soundmod
```

Use a new output directory. This retains the legacy Soundmod/GP catalog allocation and its default title pool, rather than the manager's selected-only original-ROM packing.

## Pinned fingerprints

| Image | Bytes | CRC32 | SHA-256 |
|---|---:|---|---|
| Original EXE4.5 | 8,388,608 | `A646601B` | `588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8` |
| Japanese PvP 0.6.0 | 8,579,364 | `D1240E4B` | `2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278` |
| English PvP 0.6.0 | 8,583,022 | `C361D756` | `89e92cd0545128612cdb318f3fbffb8c604206a69e78a1745bb290451692ac48` |

The English BPS is 752,115 bytes, SHA-256 `1fa1f74e3ec00e73c9b8fad41d57958f793b108be79ff892c4ab4ec8ef7bdb7a`. BPS source, target, and patch checksum checks pass. Profiles are centralized in `scripts/target_profiles.py`; manifests name the precise target and use the shared `exe45-audio-v1` layout.

## Layout and preservation evidence

Binary comparisons establish the same startup SoundMode literal at `0x504`, audio start/lookup code from `0xEE344` through `0xEEA80`, player table at `0x135094`, 499-entry song table at `0x135214`, and five table-reference locations. All 48 native music table entries are identical between the supplied JP and English targets.

The 12 PvP effect entries at IDs 69–80 have different header pointers in the English output. They are preserved from the selected English ROM, not reconstructed from Japanese pointers. The builder copies the complete selected target image and verifies that only the declared audio literal, entry stub, and table references change within its prefix. This also preserves the English translation and target-specific PvP resources.

The communication descriptor-99 lookup and its music byte `0x62` (98), plus the battle-start selection branch at `0x08007954`, are unchanged between targets. The communication setup's extra PvP trampoline pointer differs; that pointer is retained with the rest of the selected target's code. See [communication music tracing](communication-battle-music.md).

## Validation

The Python suite passes **60 tests**, including exact target identification, modified-ROM rejection, manifest/profile consistency, JP regression checks, English prefix/native-effect preservation, original source compatibility, manager export/BPS reconstruction, and legacy Soundmod packing for English PvP. Frontend and AudioWorklet tests also pass.

A sample English manager build uses GP entry 1 on the title screen and a communication pool containing EXE1 entry 0, EXE6 entry 1, and GP entry 1. It is retained under `out/us-manager-validation/`. The resulting ROM is 8,864,884 bytes, CRC32 `912996E1`, SHA-256 `46bd7d42c8c0b9424c4f5584100ec5d15d414c44649c48a03201d93337e2f2de`.

The English target passed:

- 31 controlled mGBA initialization/ABI cases: native ID 68, all PvP effects 69–80, and six configured events with selector values 0, 128, and 255.
- Three additional cases covering communication event 98 with selector values 1 and 2, plus native ID 68. All three entries of the non-power-of-two pool were selected across the runs.
- Natural title playback for 1,556 frames, seven tracks, all nine PCM samples, reaching completion at clock 1804 with no register injection.
- Actual three-second mGBA audio capture with nonzero stereo 44.1 kHz output.
- Realtime agbplay playback of native English-target music ID 98.

Reports are under `out/us-hook-validation/`, `out/us-link-pool-selector-validation/`, `out/us-title-sustained/`, and `out/us-title-preview/`. These establish audio compatibility and target preservation, not an exhaustive English gameplay or two-peer PvP validation. Existing source-preview versus target-playback limitations still apply.
