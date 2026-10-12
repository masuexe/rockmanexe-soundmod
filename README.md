# rockmanexe-soundmod

ROM audio analysis and transplantation tools for Rockman EXE. The eventual goal is a manager that combines EXE4.5 PvP with Soundmod and music from other games, lets users select tracks for random playback, and exports a patch.

The tools provide **read-only audio table scanning, verified BPS decoding, patch comparison, and supported-song dependency analysis**. The unified builder exports PvP plus all 52 Soundmod additions and 15 eligible EXEGP songs, with stable IDs and configurable ROM-resident selection. Input ROMs are never modified. Background music and sound effects are not yet classified; nonempty audio entries are not a count of music tracks.

## Scan local ROMs

Requires Python 3.10 or newer, with no third-party Python dependencies. Run from the project root:

```bash
python3 scripts/scan_audio.py roms/exe45.gba \
  --patch references/exe45_pvp_0.6.0.bps \
  --patch references/exe45_soundmod.bps \
  --donor roms/exegp.gba \
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

## Build the unified ROM

Edit `config/playlist.json` to choose pools using stable keys from the catalog. For example, `exegp:1` identifies the donor entry regardless of its relocated address. The current interface is JSON/CSV; the graphical manager is not implemented yet.

```bash
python3 scripts/build_unified.py \
  --base roms/exe45.gba \
  --pvp-patch references/exe45_pvp_0.6.0.bps \
  --soundmod-patch references/exe45_soundmod.bps \
  --donor roms/exegp.gba \
  --playlist config/playlist.json --out out/unified-v2
```

Outputs include `unified.gba`, a BPS patch for the original EXE4.5 ROM, `catalog.json`/`catalog.csv`, and a versioned build manifest. Existing PvP entries and resources are preserved; declared changes are the selector stub, table references, and ten-channel mixer setting. EXEGP entry 5 is excluded because it exceeds the target player's track capacity. See the unified research record for gameplay and audio validation limits.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Tests cover BPS decoding/export, overlapping copies, checksums, invalid references, sequence patterns and running commands, PCM boundaries, sparse drum dependencies, preservation of existing PvP data, and relocated sample contents. When local ROMs and patches are available, they also verify discovered tables, target checksums, and the PvP conflict indices. Those integration tests are skipped when their inputs are absent.

## Research and next steps

See [audio baseline research](docs/audio-baseline.md) for the initial findings, evidence, and limitations. The inventories can be consumed by `rockmanexe-reverse` without maintaining a second parser. Research distinguishes original behavior from patch additions.

Playback entry points and representative header/tone-bank initialization have now been verified in mGBA; see [playback validation](docs/audio-playback.md) for results and commands. Soundmod's existing ID-selection hook has also been identified. Audible listening remains unverified; sustained donor and transplanted execution are covered in the transplantation research.

EXEGP song 1 has now been decoded, relocated, and validated through sustained playback in a PvP-based experiment. See [song transplantation](docs/song-transplant.md) for build commands, the startup mixer adjustment, BPS output, and limitations. That earlier experiment used a provisional slot and debugger selection; the unified build now assigns stable IDs and selects the title song during normal startup.

The unified catalog and permanent start-by-ID selection hook are now implemented; see [unified build and pool configuration](docs/unified-catalog.md). The default build plays EXEGP song 1 on the title screen and preserves the original Soundmod selection pools using remapped IDs.

The next milestone is a local manager interface using this catalog/build backend, with track preview, names, pool selection, and export. Selection currently follows Soundmod's existing selector byte; its distribution is not verified. Finite tracks do not automatically advance to another song.

ROMs, saves, BPS files, and generated reports remain local and are excluded from version control.
