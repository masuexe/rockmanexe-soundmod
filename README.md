# rockmanexe-soundmod

A local sound manager and ROM audio analysis tools for Rockman EXE. Combine EXE4.5 PvP with music read directly from original EXE/BN ROMs, preview tracks in realtime, edit names and playback pools, and export a checked BPS patch.

The tools provide **read-only audio table scanning, verified BPS decoding, patch comparison, and supported-song dependency analysis**. The manager reads 22 original-ROM profiles from the shared `../roms/` directory, with 740 eligible entries in the current library (48 native PvP and 692 foreign music-player candidates). Export packs only selected foreign songs with stable IDs and configurable ROM-resident selection. The earlier Soundmod-based command-line builder remains available for reproducing the validated legacy build. Input ROMs are never modified. Background music and sound effects are not yet classified; nonempty audio entries are not a count of music tracks.

## Open the local manager

```bash
python3 scripts/manage_sound.py
```

Open `http://127.0.0.1:8765/` if the browser does not open automatically. Original ROMs in `../roms/` and the PvP patch in `references/` are preloaded; you can also choose files in the interface. Load the catalog, select a track and click **Play now** for realtime preview, edit its name, choose a playback event, check its tracks, then build and download the patch. The BPS applies to the **original EXE4.5 ROM**, and already includes PvP.

Catalog editing and export require only Python 3.10+. Realtime preview uses a locally built agbplay core: run `python3 scripts/build_realtime.py --fetch-deps` once in the tested Ubuntu environment. See [realtime setup](docs/realtime-preview.md). The optional mGBA verification capture additionally requires Linux, the mGBA SDL executable (tested with 0.10.2), `cc`, and SDL2 development headers. See [manager usage and preview details](docs/manager.md) for supported versions, saved projects, and limitations.

## Scan local ROMs

Requires Python 3.10 or newer, with no third-party Python dependencies. Run from the project root:

```bash
python3 scripts/scan_audio.py ../roms/exe45.gba \
  --patch references/exe45_pvp_0.6.0.bps \
  --patch references/exe45_soundmod.bps \
  --donor ../roms/exegp.gba \
  --out out/baseline-audio
```

Both `--patch` and `--donor` are repeatable. Each patch is independently applied to the original input ROM in memory. Source, patch, and target CRC32 checks must pass before the patched image is analyzed; the decoder does not bypass the BPS source requirement.

The output directory must not exist. Choose a new directory for another run. Other ROMs can be supplied directly; finding no candidate tables means the current rules did not match, rather than proving that the ROM contains no music.

Outputs:

- `summary.md`: input and candidate table statistics.
- `manifest.json`: ROM and patch fingerprints and input provenance.
- `00-*.json`, etc.: entries, headers, track and tone-bank addresses, raw fields, shared headers, and occurrences of table pointers.
- `00-*.csv`, etc.: readable catalogs, including empty entries. Track names and BGM/SFX labels are not assigned yet.
- `comparisons.json`: changes within the original ROM, overlapping extension space, and changes to audio entries.

Addresses include both file offsets and `0x08000000 + offset` ROM addresses. Table indices start at zero. Their relationship to runtime audio IDs must be verified from playback code for each ROM version.

## Reproduce the legacy Soundmod-based ROM

Edit `config/playlist.json` to choose pools using stable keys from the catalog. For example, `exegp:1` identifies the donor entry regardless of its relocated address. The browser manager uses the same pool format with original-ROM keys such as `exe1:0` and `exe6:1`. Legacy `soundmod:*` keys are specific to this earlier builder and cannot be used in the manager.

```bash
python3 scripts/build_unified.py \
  --base ../roms/exe45.gba \
  --pvp-patch references/exe45_pvp_0.6.0.bps \
  --soundmod-patch references/exe45_soundmod.bps \
  --donor ../roms/exegp.gba \
  --playlist config/playlist.json --out out/unified-v2
```

Outputs include `unified.gba`, a BPS patch for the original EXE4.5 ROM, `catalog.json`/`catalog.csv`, and a versioned build manifest. Existing PvP entries and resources are preserved; declared changes are the selector stub, table references, and ten-channel mixer setting. EXEGP entry 5 is excluded because it exceeds the target player's track capacity. See the unified research record for gameplay and audio validation limits.

## Tests

```bash
python3 -m unittest discover -s tests -v
node tests/test_manager_ui.mjs
node tests/test_audio_worklet.mjs
```

Tests cover BPS decoding/export, overlapping copies, checksums, invalid references, sequence patterns and running commands, PCM boundaries, sparse drum dependencies, preservation of existing PvP data, and relocated sample contents. When local ROMs and patches are available, they also verify discovered tables, target checksums, and the PvP conflict indices. Those integration tests are skipped when their inputs are absent.

## Research and next steps

See [audio baseline research](docs/audio-baseline.md) for the initial findings, evidence, and limitations. The inventories can be consumed by `rockmanexe-reverse` without maintaining a second parser. Research distinguishes original behavior from patch additions.

Playback entry points and representative header/tone-bank initialization have now been verified in mGBA; see [playback validation](docs/audio-playback.md) for results and commands. Soundmod's existing ID-selection hook has also been identified. The user has confirmed that the unified ROM sounds correct during their listening test; sustained donor and transplanted execution are covered in the transplantation research.

EXEGP song 1 has now been decoded, relocated, and validated through sustained playback in a PvP-based experiment. See [song transplantation](docs/song-transplant.md) for build commands, the startup mixer adjustment, BPS output, and limitations. That earlier experiment used a provisional slot and debugger selection; the unified build now assigns stable IDs and selects the title song during normal startup.

The unified catalog and permanent start-by-ID selection hook are now implemented; see [unified build and pool configuration](docs/unified-catalog.md). The default build plays EXEGP song 1 on the title screen and preserves the original Soundmod selection pools using remapped IDs.

The local manager now provides track previews, names, pool selection, project persistence, and export directly from original ROMs. It shares the checked relocator with the legacy builder, while using a separate original-ROM catalog and fixed slot ranges. Selection currently follows Soundmod's existing selector byte; its distribution is not verified. Finite tracks do not automatically advance to another song.

ROMs, saves, BPS files, and generated reports remain local and are excluded from version control.
