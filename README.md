# rockmanexe-soundmod

ROM audio analysis and transplantation tools for Rockman EXE. The eventual goal is a manager that combines EXE4.5 PvP with Soundmod and music from other games, lets users select tracks for random playback, and exports a patch.

The first stage provides **read-only audio table scanning, verified BPS decoding, and patch comparison**. It does not modify input ROMs or produce a merged ROM. Background music and sound effects are not yet classified; nonempty audio entries are not a count of music tracks.

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

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Tests cover all four BPS actions, overlapping copies, backward relative offsets, checksum failures, invalid references, and audio-header rules. When local ROMs and patches are available, they also verify discovered tables, target checksums, and the PvP conflict indices. Those integration tests are skipped when their inputs are absent.

## Research and next steps

See [audio baseline research](docs/audio-baseline.md) for the initial findings, evidence, and limitations. The inventories can be consumed by `rockmanexe-reverse` without maintaining a second parser. Research distinguishes original behavior from patch additions.

Playback entry points and representative header/tone-bank initialization have now been verified in mGBA; see [playback validation](docs/audio-playback.md) for results and commands. Soundmod's existing ID-selection hook has also been identified. Audible output and sustained playback remain unverified.

The next stage decodes track instructions, tone banks, and sample dependencies. A single EXEGP track will be transplanted into a PvP-based ROM before batch transplantation, random playback, or a manager UI is implemented.

ROMs, saves, BPS files, and generated reports remain local and are excluded from version control.
