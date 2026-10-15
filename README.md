# rockmanexe-soundmod

A local sound manager and ROM audio analysis tools for Rockman EXE. Modify a verified target ROM using music read directly from original EXE/BN ROMs, preview tracks in realtime, edit names and playback pools, and export a checked BPS patch. Targets include EXE4.5 JP/English PvP, EXE Battle Chip GP with or without ChipControl, and both Japanese EXE6 variants.

The tools provide **read-only audio table scanning, verified BPS decoding, patch comparison, and supported-song dependency analysis**. The manager reads 23 original-ROM profiles from the shared `../roms/` directory, including original `exe45.gba` as a music source. With all sources selected, the EXE4.5 target has 787 eligible entries (48 native PvP and 739 foreign music-player candidates); availability depends on the target player capacity. Export packs only selected foreign songs with stable IDs and configurable ROM-resident selection. The earlier Soundmod-based command-line builder remains available for reproducing the validated legacy build. Input ROMs are never modified. Background music and sound effects are not yet classified; nonempty audio entries are not a count of music tracks.

## Open the local manager

```bash
python3 scripts/manage_sound.py
```

Open `http://127.0.0.1:8765/` if the browser does not open automatically. Choose **Game to modify** before loading. The previous target choice is restored; on first use, the base ROM and default Japanese PvP patch are preloaded. The English PvP 0.6.0 patch is also supported; start with `--pvp-patch ../patches/bn45_us_pvp_0.6.0.bps` or choose it in the PvP input. Both patches require the same original `exe45.gba`; see [English target setup and validation](docs/english-pvp.md). Original music ROMs in `../roms/` appear as checkboxes; select the games you need and click **Load tracks**. Only checked ROMs are read and analyzed, and the selection is remembered. You can also add files in the interface. After loading the catalog, select a track and click **Play now** for realtime preview, edit its name, choose a playback event, check its tracks, then build and download the patch. The BPS applies to the **original selected target ROM**. EXE4.5 exports include PvP; GP exports apply directly to original `exegp.gba` without a pre-patch. GP also offers **Communication battles (music #12–14)** to edit its three native battle choices together; these music IDs are shared with some single-player battles. See [communication battle pools](docs/communication-battle-music.md). See [target selection, shared architecture, and GP validation](docs/multi-target.md). For EXE6, choose **Rockman EXE 6 Gregar (JP)** or **Rockman EXE 6 Falzar (JP)**; title event 1, numbered music pools, and **Communication battles only** are independently configurable. See [EXE6 setup and validation](docs/exe6.md). To combine GP music with ChipControl, choose **Rockman EXE Battle Chip GP (JP) + ChipControl 1.1.0**; the manager reads the Japanese IPS from the supplied ZIP and exports one BPS for original GP. See [ChipControl setup and validation](docs/chipcontrol.md).

Catalog editing and export require only Python 3.10+. Realtime preview uses a locally built agbplay core: run `python3 scripts/build_realtime.py --fetch-deps` once in the tested Ubuntu environment. See [realtime setup](docs/realtime-preview.md). The optional mGBA verification capture additionally requires Linux, the mGBA SDL executable (tested with 0.10.2), `cc`, and SDL2 development headers. See [manager usage and preview details](docs/manager.md) for supported versions, saved projects, and limitations.

For differences between original and transplanted music, see [same-emulator fidelity comparisons](docs/audio-fidelity.md). The diagnostic tools record original/target pairs, generate normalized listening pages, and probe sequence and mixer state without changing manager export defaults.

EXE1 JP and EXE4 Red Sun JP fixed-step PCM drums are automatically adapted to the target mixer rate during export. This corrects accelerated percussion in GP imports, including `exe1:0` and `exe4:0`; see the [drum correction evidence](docs/audio-fidelity.md).

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

The first [NDS music conversion experiment](docs/nds-import-research.md) imports Star Force 3 `BGM_ROOM` into Japanese EXE6 through a separate checked CLI. Six tracks and 15 original samples pass independent DS execution/decoding comparisons and sustained natural GBA playback through two loops. The experiment includes measured song-volume compensation after title-screen listening feedback. NDS import and preview are not yet supported by the manager; voice allocation and envelope fidelity remain research work.

The second [BGM_BATTLE experiment](docs/nds-battle-research.md) maps all eleven source tracks into eight EXE6 tracks and checks the source notes, controls, decoded samples and controlled scene lifecycle. The user reports successful three-minute communication playback alongside chips and Buster effects, plus virus-battle playback, victory/map music restoration and restarting on the next encounter. This establishes the tested single-song gameplay baseline; communication rematches remain an unreported gameplay check.

The next [BGM_KANDO experiment](docs/nds-kando-research.md) retains seven original tracks and fourteen samples. Independent source comparisons, one natural GBA loop and controlled lifecycle checks pass. The user also reports successful sustained listening, chips/Buster effects, victory/map restoration and next-encounter playback, establishing a second tested gameplay baseline. Its separate ROM replaces title, ordinary music 21 and communication battles.

The first [Star Force 1 experiment](docs/nds-sf1-research.md) converts `BGM23KINCHO` with eight original tracks and fifteen samples. All three pinned Japanese source variants share the verified archive. Independent source comparisons, one natural GBA loop and controlled lifecycle checks pass. The user also confirms sustained listening, chips/Buster effects, victory/map restoration and next-encounter playback, establishing the first accepted Star Force 1 gameplay baseline.

The first [Star Force 2 experiment](docs/nds-sf2-research.md) converts `BGM_WIN` with seven original tracks and fifteen samples. Both pinned Japanese originals export identical music. Independent source comparisons, two natural GBA periods and controlled lifecycle probes pass. The user confirms sustained listening, chips/Buster effects, victory/map restoration and next-encounter playback. All three games now have a user-accepted candidate within the supported subset; active modulation, wider song coverage and manager NDS integration remain research work.

The [native pitch-LFO experiment](docs/nds-lfo-research.md) converts Star Force 1 `BGM27BATTLE` with seven tracks and twenty-two samples. It explicitly approximates DS per-voice sine modulation using shared GBA triangle modulation. Source comparisons, a bounded actual native-LFO window and controlled lifecycle probes pass. The user reports no issues with the requested long listening/loop, effects coexistence, map restoration and next-encounter tests. This accepts the approximation for that configuration; measured pitch differences remain. Delayed/volume/pan modulation remain unsupported in this mode.

The [batch compatibility audit](docs/nds-compatibility-audit.md) covers all 132 SSEQ slots across the three archives. Of 122 nonempty/nonsilent candidates, 28 pass conversion, shared EXE6 packing and BPS reconstruction (24 standard paths, four native-LFO approximations); five outputs matched existing user-accepted ROMs when that scan ran. Other new batch candidates still need runtime/listening validation. The eight earlier note/repeat/tie assertions are resolved by checking complete decoded loops, with regression tests and independent DS source comparisons.

The [Star Force 1 LAST experiment](docs/nds-last-research.md) provides a separate eight-track test ROM for the recovered tied-note boundary case. Bounded natural playback and controlled effects/lifecycle checks pass. The user reports no issues with the requested sustained loop listening, chips/Buster effects, map restoration and next-encounter tests, accepting this build. Instrumented full GBA loops and communication rematches remain separate uncompleted checks.

The [envelope experiments](docs/nds-envelope-research.md) add opt-in note-on ADSR snapshots and bounded gradual-attack fitting. Star Force 3 HOKORA tests non-instant attack; FRIEND tests release overrides alongside the existing pitch-LFO approximation. Independent DS envelope traces and bounded native GBA envelope checks pass. The user reports both builds passed the requested listening/gameplay tests, accepting these approximations for their tested configurations. The default audit policy remains unchanged.

See [audio baseline research](docs/audio-baseline.md) for the initial findings, evidence, and limitations. The inventories can be consumed by `rockmanexe-reverse` without maintaining a second parser. Research distinguishes original behavior from patch additions.

Playback entry points and representative header/tone-bank initialization have now been verified in mGBA; see [playback validation](docs/audio-playback.md) for results and commands. Soundmod's existing ID-selection hook has also been identified. The user has confirmed that the unified ROM sounds correct during their listening test; sustained donor and transplanted execution are covered in the transplantation research.

EXEGP song 1 has now been decoded, relocated, and validated through sustained playback in a PvP-based experiment. See [song transplantation](docs/song-transplant.md) for build commands, the startup mixer adjustment, BPS output, and limitations. That earlier experiment used a provisional slot and debugger selection; the unified build now assigns stable IDs and selects the title song during normal startup.

The unified catalog and permanent start-by-ID selection hook are now implemented; see [unified build and pool configuration](docs/unified-catalog.md). The default build plays EXEGP song 1 on the title screen and preserves the original Soundmod selection pools using remapped IDs.

The local manager now provides track previews, names, pool selection, project persistence, and export directly from original ROMs. It shares the checked relocator with the legacy builder, while using a separate original-ROM catalog and fixed slot ranges. EXE4.5 selection reads its existing RNG1 byte; GP reads and mixes a verified scheduler tick. Uniform randomness is not established. Finite tracks do not automatically advance to another song.

ROMs, saves, BPS files, and generated reports remain local and are excluded from version control.
