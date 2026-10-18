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

The [batch compatibility audit](docs/nds-compatibility-audit.md) covers all 132 SSEQ slots across the three archives. Of 122 nonempty/nonsilent candidates, 54 pass conversion, shared EXE6 packing and BPS reconstruction (26 standard, four finite-standard, four LFO-only, two envelope-only, three envelope/LFO, eight fixed delayed-LFO, four envelope/delayed-LFO, one envelope/live-depth-LFO, one live-toggle-LFO and one envelope/live-toggle-LFO approximation); twenty outputs match existing user-accepted ROMs. V10 adds the finite singleton route for Star Force 1/2 HENKAN and Star Force 1/3 WIN2. Star Force 1 HENKAN uses the recorded 0 dB headroom retry and matches its accepted build. All 50 earlier packed variants retain identical ROM/BPS fingerprints, routes and gain. Star Force 2 HENKAN subsequently passed standalone source/runtime checks and user-reported listening/gameplay tests; other batch candidates still need runtime/listening checks. Archived scans retain their original evidence.

The [Star Force 1 LAST experiment](docs/nds-last-research.md) provides a separate eight-track test ROM for the recovered tied-note boundary case. Bounded natural playback and controlled effects/lifecycle checks pass. The user reports no issues with the requested sustained loop listening, chips/Buster effects, map restoration and next-encounter tests, accepting this build. Instrumented full GBA loops and communication rematches remain separate uncompleted checks.

The [envelope experiments](docs/nds-envelope-research.md) add opt-in note-on ADSR snapshots and bounded gradual-attack fitting. Star Force 3 HOKORA tests non-instant attack; FRIEND tests release overrides alongside the existing pitch-LFO approximation. Independent DS envelope traces and bounded native GBA envelope checks pass. The user reports both builds passed the requested listening/gameplay tests, accepting these approximations for their tested configurations. The batch audit now attempts these bounded envelope paths and reports their approximation categories separately.

The [Star Force 2 NESSIE experiment](docs/nds-nessie-research.md) provides the next combined-envelope/LFO test ROM, adding DS attack 90 alongside the previously tested attack 100. Independent DS references, bounded actual envelope/LFO playback and controlled lifecycle checks pass. The user reports no issues with the requested sustained listening, loop joins, chips/Buster effects, map restoration and next-encounter tests, accepting this configuration. Instrumented full-loop GBA execution remains separate.

The [fixed delayed-LFO experiment](docs/nds-delayed-lfo-research.md) converts Star Force 1 FMPLANET with seven tracks and 16 samples. A fixed ten-update DS delay maps to native LFODL with explicit timing/phase approximations. Independent delay-counter observations, bounded native playback and controlled lifecycle checks pass. The user reports no issues with the requested sustained listening, effects coexistence, map restoration and next-encounter tests, accepting this configuration. The batch audit now tries this bounded fixed-delay policy and reports its additional approximation separately.

The [Star Force 2 BATTLE experiment](docs/nds-sf2-battle-research.md) retains eight tracks and 24 samples while checking the same fixed DS delay at a faster tempo. Independent DS references, bounded native playback and controlled lifecycle probes pass. The user reports no issues with the requested four-minute battle listening, loop joins, effects coexistence, map restoration and next-encounter restart for this exact ROM; the shared-phase approximation remains.

The [Star Force 1 HOMETOWN experiment](docs/nds-live-depth-research.md) adds an explicit mode for positive pitch-LFO depth changes while keeping speed, range, type and delay fixed. Ordered MOD updates preserve shared target phase and delay count. It combines this approximation with fitted attack 90 and retains eight tracks and 19 samples. The user reports no issues with the requested six-minute battle listening, depth changes, later gradual attack, loop joins, effects coexistence, map restoration and next-encounter restart for this exact ROM. The v6 batch audit now includes this bounded policy; the shared-phase approximation remains.

The [Star Force 1 GOWAIINCHO experiment](docs/nds-pre-note-lfo-research.md) corrects a boundary check that rejected modulation setup before a track's first note. It sets depth at tick 24 before track 2 first sounds at tick 688; the default fixed-delay mode still rejects actual mid-note activation. The user reports no issues with the eight-track, 24-sample ROM's requested four-minute battle listening, loop joins, effects coexistence, map restoration and next-encounter restart. All thirteen earlier accepted ROMs and patches rebuild identically; the archived v6 scan remains unchanged.

The [Star Force 1 BOSS experiment](docs/nds-live-toggle-research.md) adds a separate opt-in on/off approximation with fixed positive depth and other modulation parameters. Independent DS references, a bounded native BOSS window, a synthetic held-note enable/disable probe and controlled lifecycle checks pass. The user reports no issues with its seven-track, 21-sample ROM's requested four-minute battle listening, enable/disable repetitions, loop joins, effects coexistence, map restoration and next-encounter restart. Target disabling clears shared phase while DS voices retain theirs; this difference remains explicit. The v7 batch audit now tries this bounded mode and its envelope combination after existing routes.

The [Star Force 2 KAICYOU experiment](docs/nds-kaicyou-research.md) combines fitted attack 100 with delayed modulation activated after track 2 has started and zero-delay modulation configured before track 4 first sounds. Its eight-track, 24-sample ROM matches the v7 packed variant and passed user-reported sustained battle listening and gameplay checks on 2026-10-17. The reference checker follows the source's enable-only controls and does not claim disable coverage.

The [Star Force 1 PLANETARIUM experiment](docs/nds-planetarium-research.md) permits long notes to carry across a loop jump when entry/exit intervals match. Independent decoding checks complete gates beyond two loop periods; a short native probe confirms three jumps preserve the same PCM channel. The user reports no issues with its eight-track, 29-sample ROM after the requested sustained battle listening, loop joins, effects coexistence, map restoration and next-encounter restart checks on 2026-10-17. All sixteen earlier accepted ROMs and patches rebuild identically.

The [Star Force 2 DEMPAJIKEN experiment](docs/nds-dempajiken-research.md) combines fitted attack 100 with a 239-tick carried long note. Its eight-track, 19-sample ROM and patch match v8 exactly. Independent DS references, one complete natural GBA loop with all samples, actual first-jump channel continuity/EOT, a bounded envelope window and controlled lifecycle checks pass. The envelope checker now recognizes note-ons in later command cycles. The user reports no issues with the requested three-minute battle listening, repeated joins, effects coexistence, map restoration and next-encounter restart on 2026-10-17.

The [Star Force 1 URA experiment](docs/nds-ura-research.md) resolves two tracks sharing an instrument and long-note alias for different source keys by allocating a second compatible rhythm bank. Its eight-track, ten-sample ROM passes independent source checks, one complete natural GBA loop, actual distinct-wave/held-channel/independent-EOT observations and controlled lifecycle checks. All eighteen earlier accepted ROMs and patches rebuild identically. The user reports no issues with the requested three-minute battle listening, sustained parts, repeated joins, effects coexistence, map restoration and next-encounter restart on 2026-10-17.

The [Star Force 1 SATELLITE experiment](docs/nds-satellite-research.md) provides an eight-track, 28-sample ROM matching v9 exactly. Independent DS checks, bounded natural playback, actual distinct-wave/independent-EOT observations and controlled lifecycle checks pass. The natural window reaches 25/28 samples; the other three first enter later. Its first loop jump is around 83 seconds, beyond title playback. The user reports no issues with the requested four-minute battle listening, later parts, loop joins, effects coexistence, map restoration and next-encounter restart on 2026-10-17.

The [Star Force 1 HENKAN experiment](docs/nds-henkan-research.md) adds an explicit finite singleton mode with TIE/EOT and individual FINE times. Its four-track, two-sample cue finishes around six seconds, then stays silent. It uses 0 dB because +3.5 dB exceeds native volume headroom. Independent DS references, complete natural playback, more than ten seconds of inactive/empty-channel observation and controlled lifecycle checks pass. All twenty earlier accepted ROMs and patches rebuild identically. The user reports no issues with the requested complete cue, ten-second silence, effects during/after playback, map restoration and repeated encounter starts on 2026-10-17.

The [Star Force 2 HENKAN experiment](docs/nds-sf2-henkan-research.md) validates the finite mode with four tracks sharing one sample and 468-tick gates. Its +3.5 dB ROM and patch match v10 exactly. Independent DS checks, complete natural playback, more than ten seconds of inactive/empty-channel observation and controlled lifecycle checks pass. The user reports no issues with the requested complete five-second cue, ten-second silence, effects during/after playback, map restoration and repeated encounter starts on 2026-10-17.

See [audio baseline research](docs/audio-baseline.md) for the initial findings, evidence, and limitations. The inventories can be consumed by `rockmanexe-reverse` without maintaining a second parser. Research distinguishes original behavior from patch additions.

Playback entry points and representative header/tone-bank initialization have now been verified in mGBA; see [playback validation](docs/audio-playback.md) for results and commands. Soundmod's existing ID-selection hook has also been identified. The user has confirmed that the unified ROM sounds correct during their listening test; sustained donor and transplanted execution are covered in the transplantation research.

EXEGP song 1 has now been decoded, relocated, and validated through sustained playback in a PvP-based experiment. See [song transplantation](docs/song-transplant.md) for build commands, the startup mixer adjustment, BPS output, and limitations. That earlier experiment used a provisional slot and debugger selection; the unified build now assigns stable IDs and selects the title song during normal startup.

The unified catalog and permanent start-by-ID selection hook are now implemented; see [unified build and pool configuration](docs/unified-catalog.md). The default build plays EXEGP song 1 on the title screen and preserves the original Soundmod selection pools using remapped IDs.

The local manager now provides track previews, names, pool selection, project persistence, and export directly from original ROMs. It shares the checked relocator with the legacy builder, while using a separate original-ROM catalog and fixed slot ranges. EXE4.5 selection reads its existing RNG1 byte; GP reads and mixes a verified scheduler tick. Uniform randomness is not established. Finite tracks do not automatically advance to another song.

ROMs, saves, BPS files, and generated reports remain local and are excluded from version control.

The [Star Force 1 WIN2 experiment](docs/nds-sf1-win2-research.md) tests a roughly 1.4-second score with six staggered track endings, 67 notes and nine samples. Its +3.5 dB ROM/BPS match v10; independent source checks, full natural playback, more than ten seconds of inactive/empty-channel observation and controlled restart checks pass. Short finite cues now use earlier controlled observations and per-frame PCM evidence. The source reference reaches 16 voices while the native mixer remains limited to ten, so identical polyphony is not established. On 2026-10-18 the user reported a mixed/muddy ending and substantial difference from the original; the unfiltered WIN2 is not manually accepted. The [ending diagnosis](docs/nds-sf1-win2-tail-diagnosis.md) finds no missing held-note interiors in the bounded probe and identifies a significant bandwidth mismatch in the high ending notes. The user reports clear improvement with an offline antialiasing control that retains ten channels and the existing mixing rate; this is listening-comparison feedback, not full gameplay acceptance.

The [WIN2 offline antialias experiment](docs/nds-sf1-win2-antialias-research.md) turns that control into an opt-in stdlib converter route with per-key sample caching, periodic loop filter history and compensated tuning. It retains six tracks, all 67 notes, +3.5 dB gain and the ten-channel 10,512 Hz mixer. Thirty-two prepared waves increase the ROM by about 93 KiB versus the unfiltered variant. Source/natural/lifecycle checks and 229 regression tests pass; all 22 accepted ROMs/BPS and the old unaccepted WIN2 rebuild identically. On 2026-10-18 the user reported no issues after the requested ending/timbre checks, ten-second silence, effects, map restoration and repeated encounter starts, accepting this exact v2 ROM. The unfiltered variant remains unaccepted.

The [Star Force 3 WIN2 antialias experiment](docs/nds-sf3-win2-antialias-research.md) reuses the same offline converter without filter or mixer changes: eight tracks, 83 notes and 34 prepared waves, with +3.5 dB gain and ten PCM channels at 10,512 Hz. Its roughly 2.2-second score has eight individual FINE times. Source, natural playback/stop and controlled lifecycle checks pass. On 2026-10-18 the user reported no issues after the requested dense-passage/ending checks, ten-second silence, effects, map restoration and repeated encounter starts, accepting this exact antialias ROM. The source can hold eleven note events at once, so native allocation remains a fidelity limit. The separate unfiltered control matches the archived v10 ROM/BPS exactly.
