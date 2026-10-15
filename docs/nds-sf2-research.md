# Star Force 2 cross-game experiment

The first Star Force 2 candidate is SSEQ 30, `BGM_WIN`: seven original tracks
and fifteen PCM waves, converted with the existing direct path. Its short
period allows two full periods after every track's loop start to be checked
before the EXE6 title ends playback. Independent source comparisons, natural
two-period GBA execution and controlled lifecycle probes pass. User listening
and gameplay acceptance now pass by user report: sustained battle listening,
chips/Buster effects, victory/map restoration and restarting on the next
encounter. WIN is the first accepted Star Force 2 gameplay baseline.

The test ROM deliberately selects this victory tune during ordinary virus
and communication battles, as well as the title, to make effects and scene
transition checks accessible. This is a playback experiment rather than a
proposed final soundtrack assignment.

## Verified sources and conversion scope

| Source | Game code | ROM SHA-256 |
| --- | --- | --- |
| `ssr2d.nds` | `YRWJ` | `9ea3c6e253d4111eec250d611296be5fab0e2ec2b8f6f25ece71dcc8e3492899` |
| `ssr2s.nds` | `YRVJ` | `dfa8780c1f98059d466509e90004793ad89b87a7f9fce48210fca8ddc0ff3745` |

Both Japanese originals contain a byte-identical SDAT at NDS FAT file 975,
`datbin/com/sound_data.sdat`, 6,795,936 bytes, SHA-256
`eb092e07ab410a3c81db491f0feb905f6259b891fb0b3cedfccaeca78ddc4ab4`.
The builder pins these ROM/archive identities independently of Star Force 1
(file 667) and 3 (file 187). An explicit song-to-game map prevents selecting
a candidate from the wrong source game.

WIN is sequence index 30, SSEQ file 29, bank 61 and source player 1. Its
fifteen used waves are ADPCM. PCM decoding, root tuning, sample loops,
PCM8 quantization and envelope approximation use the existing converter.
No new active-effect handling, track merging or playback-state expansion
was added. Source priorities 121–127 map to 0–6 with song priority 20.
The +3.5 dB song gain is the existing experimental default; it has not been
independently calibrated for Star Force 2.

The bounded inspection also found ROOM and KANDO compatible with the direct
subset. WIN provides another tune and a faster tempo instead of repeating
an already accepted song. HOMETOWN declares ten tracks; ordinary BATTLE has
eight tracks but executes active modulation. Those candidates remain outside
this experiment. Passing WIN does not establish support for all Star Force 2
music or for the entire NDS synthesis engine.

## Artifacts and evidence

Directory: `out/nds-research/sf2-win-exe6-v1/`.

- `unified.gba`, `unified.bps`, `build.json`: Japanese EXE6 Gregar, 8,664,620
  bytes, adding 276,012 bytes. CRC32 `E0A54044`, SHA-256
  `b216c1052047f10fd45c0e9105f5eab21bca0c356896b1134efa5effd7bd5a2e`.
  BPS reconstruction passes. Imported entry 474 is selected on events 1, 21
  and `scene:communication`; original audio entries and declared-prefix
  preservation pass. Special battles requesting other IDs retain their pools.
- `conversion.json`, `dependencies.json`: seven original tracks, fifteen
  samples, 272,240 generated MPlay bytes. Every source track has a 1,536-tick
  period. Most loop states start at tick 192; track 6 repeats from tick 239.
  Source tempo 170 maps to parameter 171: approximately 135.969 versus
  136.179 ticks/second (GBA about 0.154% faster).
- `reference/`, `lifecycle/reference-validation.json`: 36-second software DS
  synthesis. All 1,621 observed source note events, 167 pan/bend/expression
  controls and fifteen decoded PCM16 arrays match the Python execution and
  decoder through repeated source loops. The renderer is SSEQPlayer, not a
  DS hardware/emulator recording.
- `sustained-two-loops/validation.json`: natural title start, no CPU/header
  redirection; all seven track states match each frame through 1,454 frames,
  music clock 3,313. All fifteen samples trigger with changing nonzero PCM.
  The validator's default two-period coverage is used after every track's
  loop start, including the latest repeat at tick 239.
- `lifecycle/runtime.json`: original effect initialization and continued
  music, ordinary battle dispatch from the original descriptor, communication
  selection and queued stop pass. Three controlled cycles stop imported
  voices, resume native songs and reset/restart the new song. These inject
  PC/LR/arguments and a synthetic communication descriptor; actual gameplay
  transitions remain separate user checks.
- `preview/preview.wav`: 30-second natural mGBA SDL mix, peak 9,811.
  `listen/listen.html` embeds equal-duration source/target clips after RMS
  normalization, with Star Force 2 labels. The clip spans two full periods;
  normalization masks raw volume differences.

The DS reference reaches sixteen voices in coarse snapshots; GBA retains
the configured ten-voice PCM budget. Voice allocation, envelopes and sample
resolution can affect the mix despite exact sequence/decoder comparisons.
No hardware performance claim follows from this experiment. The same settings
produce identical archives, generated resources and ROM bytes from both
pinned Star Force 2 originals. The accepted ROOM, BATTLE, KANDO and Star Force 1
KINCHO outputs rebuild byte-identically. Runtime evidence here is Gregar-only.

All 133 Python regression tests pass. New integration checks cover archive
975, source labels, song/source-family mismatches, modified-source rejection,
identical exports from both sources, BPS reconstruction and native table/prefix
preservation.

## User acceptance

Run the new ROM directly or apply its BPS to the original Japanese Gregar
ROM. Copy an existing save under the new ROM's basename if needed, keeping
the original intact.

1. Listen in a virus or communication battle for approximately 45 seconds,
   checking repeated loop joins, parts, volume and pan.
2. Use chips and the Mega Buster while music plays.
3. Win and return to the map, then enter another virus battle; check normal
   restoration, absence of residual battle notes and correct restart.

The user reports the requested tests above have no issues. This song-specific
acceptance is saved in `manual-testing.json` and `validation-summary.json`.
Approximately 45 seconds was the requested listening duration; no timed
recording or gameplay trace was supplied. Separate virus/communication runs
and communication rematches were not individually identified by the report.

All three games now have a user-accepted candidate within the implemented
subset. This does not establish support for every song or NDS synthesis
feature. Active modulation and wider song coverage are the next research
stage before manager integration; communication rematches and performance
measurements can extend coverage separately.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds \
  --base ../roms/exe6.gba --song sf2-win \
  --event 1 --event 21 --event scene:communication --out out/nds-sf2-example

python3 scripts/validate_song.py out/nds-sf2-example/unified.gba \
  --unified out/nds-sf2-example/build.json --frames 2200 \
  --out out/nds-sf2-example/sustained-two-loops

python3 scripts/validate_nds_experiment.py out/nds-sf2-example \
  --lifecycle --out out/nds-sf2-example/lifecycle
```

Use `ssr2s.nds` for the other verified source. The optional renderer takes
source slot 30 for 36 seconds; see the ROOM research for its build steps.
The default room candidate still requires a Star Force 3 source. These are
research CLI capabilities; manager NDS import/preview remains unimplemented.
