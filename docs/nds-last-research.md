# Star Force 1 LAST: tied notes at the loop boundary

This experiment makes `BGM17LAST` available as `--song sf1-last` in the
research builder. It follows the eight recovered candidates in the
[compatibility audit](nds-compatibility-audit.md). Automated bounded playback
and controlled lifecycle checks pass. On 2026-10-16 the user reported no
issues with the requested listening/gameplay sequence, accepting this build.
Instrumented full-loop GBA execution remains a separate uncompleted check.

Artifact directory: `out/nds-research/sf1-last-exe6-v1/`.

## Configuration and boundary

The pinned Japanese Dragon ROM supplies SDAT file 667, SSEQ 17 (file 16),
bank 39, tempo 142. The singleton compiler preserves all eight source tracks
and 29 PCM samples. Gates of 312/384 ticks use TIE/EOT aliases, retaining
their original sounding keys; no pitch-LFO approximation is enabled.

The compiled loop starts at tick 3072, with period 7104. The last long note
on track 7 starts at tick 9792; its EOT runs immediately after the jump at
tick 10176, ending its 384-tick gate. At the mapped GBA tempo parameter 143,
the first compiled jump occurs about 89 seconds after playback begins;
later jumps are about 151 and 214 seconds. These times are approximate.

Original EXE6 Gregar remains at eight music tracks, ten PCM voices and
10,512 Hz, with imported gain +3.5 dB. Title (1), ordinary virus battle (21)
and communication battle events select appended entry 474. All 474 original
entries and prefix bytes outside declared hook/configuration ranges are
preserved. The output is 8,914,544 bytes; SHA-256
`7dae6a3cbf951c94a2544a720e8fb16fd86a53af906f1b8b224322cc1d660a19`.

## Automated evidence

- `unified.gba`, `unified.bps`, `build.json`: original-source fingerprints,
  shared export and exact BPS reconstruction checks pass.
- `conversion.json`, `dependencies.json`: independent command decoding
  validates every mapped note/gate through the intro and two complete loops.
  This is static command evidence, separate from actual emulator playback.
- `runtime/reference-validation.json`: the existing 180-second independent
  software DS reference matches 4,204 notes, source controls and all 29
  decoded PCM16 samples. Reference files are retained under
  `out/nds-research/loop-boundary-validation-v1/ssr1-17/reference/`.
- `window/validation.json`: natural title playback for 2,150 frames reaches
  clock 4098, checking all eight track states every frame. It observes 23/29
  samples and changing nonzero PCM. The new `--window-ticks` validation option
  explicitly reports bounded coverage; full loop coverage is false. The
  title's later scene transition prevents using it for this song's full loop.
- `runtime/runtime.json`: controlled native effects 100/129, ordinary and
  synthetic communication dispatch, stop, native music restoration and three
  restart/rematch cycles pass. Helpers inject debugger registers; this does
  not establish real battles, map transitions or linked play.
- `preview/preview.wav` and `comparison/listen.html`: a 30-second actual mGBA
  recording and normalized software-DS/GBA comparison. Neither covers the
  compiled loop jump. PCM8, envelope, gain/tempo quantization and the GBA
  voice budget remain fidelity limits.

All 156 Python regression tests pass, including the LAST export regression
for its boundary TIE/EOT, alias, source-track mapping and original-data
preservation. `validation-summary.json` collects the automated evidence.

## Listening test

Use `unified.gba` for a virus or communication battle and allow uninterrupted
music for at least four minutes. Listen especially around 89, 151 and 214
seconds for stuck long notes, missing sound, pops or an uneven loop join.
Use chips and the Buster during playback. Then finish the battle, confirm
native map music returns, and start another battle to confirm LAST restarts.
If available, also test a communication rematch. The title is suitable for a
short sound check; use a battle for the complete-loop test.

The user reported no issues after the requested sequence on 2026-10-16.
`manual-testing.json` records user-reported acceptance for sustained listening
and loop joins, chips/Buster coexistence, map restoration and next-encounter
restart, tied to the exact ROM fingerprint above. A timed recording or full
loop execution trace was not supplied. Communication rematch was optional
and remains unreported. `validation-summary.json` retains the automated
bounded-coverage limits separately from this manual acceptance.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-last \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-last-example
python3 scripts/validate_song.py out/nds-last-example/unified.gba \
  --unified out/nds-last-example/build.json \
  --window-ticks 4097 --frames 2400 --out out/nds-last-example/window
python3 scripts/validate_nds_experiment.py out/nds-last-example \
  --reference out/nds-research/loop-boundary-validation-v1/ssr1-17/reference \
  --lifecycle --out out/nds-last-example/runtime
```

Output directories must be new. No manager integration is enabled.
