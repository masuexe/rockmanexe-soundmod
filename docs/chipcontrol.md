# EXE GP ChipControl 1.1.0 and music

Choose **Rockman EXE Battle Chip GP (JP) + ChipControl 1.1.0** under **Game to modify**, then click **Load tracks**. The manager reads the supported original `../roms/exegp.gba` and the Japanese IPS inside `../patches/MegaManBCC-ChipControl-Ver1.1.0.zip`. No manual extraction is needed. A loose `RockmanEXEBCGP-ChipControl-Ver1.1.0-Japanese.ips` in the patches directory is also accepted. The input card accepts that IPS if the local file is unavailable.

Configure **Title screen** and **Communication battles (music #12–14)** as usual, save, and export. The communication group uses IDs shared with some single-player battles. Run `unified.gba` directly, or apply **one** exported `unified.bps` to the **original Japanese EXE GP ROM**. The exporter applies ChipControl first and the music modification second; the final BPS includes both.

```bash
python3 scripts/manage_sound.py --target exegp-chipcontrol
```

Select the ordinary GP target to export music changes without ChipControl. Both GP presets use `project-exegp.json` and the same native track IDs. Saved title/battle pools and weights are retained when switching and loading; names and donor choices remain shared. The loaded project is stamped with the selected target, so exporting an old JSON for another preset still requires loading it through the matching preset or switching and reloading first. Custom uploaded target ROMs and IPS files remain session-local.

The package README states that **both players must use ChipControl for multiplayer**. It also states that ordinary saves are compatible with the original game, while emulator savestates may cause problems. Start a combined-ROM test from a normal boot. These are upstream compatibility statements, not a claim that this project's combination has completed a two-peer gameplay test.

## Checked inputs

| Input | SHA-256 |
| --- | --- |
| Original Japanese EXE GP, 8 MiB | `6c3ac853d06b0fa70d9ac5a0705841ddb4f0e06cd246894e60bcb1cf824ef025` |
| Japanese ChipControl 1.1.0 IPS | `bf8ee7bd208ac97fb559ab8a08388d3926176b84d0609b2c73271217a2124417` |
| GP after ChipControl, 8 MiB | `f0128df1da668aa933bf717756aa1a5998e9d0b93689b9406d2d67368c3bb484` |

The resulting target CRC32 is `A3DD3C4B`. IPS has no embedded source checksum, so this preset checks the original ROM, exact patch bytes, and resulting ROM. The English IPS is rejected for this preset. English BCC remains a donor ROM, not a ChipControl patch target.

The IPS decoder handles literal writes, RLE, zero-filled growth, and the optional final size; truncated records, empty RLE, and trailing garbage are rejected. ZIP loading reads only the named member and does not extract files. Existing PvP BPS workflows retain their format and output.

## Shared implementation and validation

ChipControl uses the existing `exegp-audio-v1` layout, catalog, relocator, start/query hooks, and deterministic timing selector. No separate music engine was added. Pre-patch loading is shared through `scripts/prepatch.py`; `target_profiles.py` supplies the pinned inputs and target identity. Export manifests record the IPS provenance and write ranges under `source_patches.chipcontrol`.

All 189 IPS write ranges are disjoint from the declared music writes. The native song/player table, start/query entry preconditions, and communication music selection branch remain compatible. Every ChipControl record is preserved byte-for-byte in combined exports; new music resources are appended after the 8 MiB target. BPS reconstruction is checked against the original GP ROM.

Automated tests cover IPS decoding, wrong input/patch rejection, ZIP loading, saved GP pool migration, combined exports, and switching back to ordinary GP. The UI fixture checks the IPS input card, preserved GP pools, communication group, and original-ROM BPS instructions. A naturally started combined title produced a nonzero three-second mGBA full-mix recording with `exe1:0`; controlled communication branch probes check all three native choices and both imported headers. Full chip-selection gameplay and a complete two-peer communication battle remain user gameplay tests. Evidence is retained in `out/chipcontrol-validation/`.

The [upstream source](https://github.com/Prof9/MegaManBCC-ChipControl) is available locally in `../references/MegaManBCC-ChipControl`, inspected at commit `aca44b706abf7450691902d8cf54f26a6d34b47c`. The supplied IPS is used directly; this integration does not rebuild or alter upstream ChipControl.
