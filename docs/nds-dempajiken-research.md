# Star Force 2 DEMPAJIKEN: envelope and carried long note

The standalone ROM/BPS is in
`out/nds-research/sf2-dempajiken-envelope-exe6-v1/`. It replaces title,
ordinary virus battle 21 and synthetic communication dispatch with appended
slot 474 on Japanese EXE6 Gregar. On 2026-10-17 the user reported
“没有问题” after the requested three-minute listening and gameplay checklist.
This records user-reported acceptance of the gradual attack part, carried
long notes and repeated joins, effects coexistence, map restoration and
next-encounter restart for the exact ROM below. No timed recording or later
full-loop execution trace was supplied; linked play and rematches were not
separately reported.

ROM: 8,729,568 bytes, CRC32 `41C2D9D2`, SHA256
`0a727bac00d6a4b393a9d6f2b1c18a5eb3b23d585141d5121af38c59896d3982`.
Both ROM and BPS fingerprints match the v8 scan's `ssr2:11` variant exactly.
BPS reconstruction, original 474 table entries and undeclared prefix bytes
are checked. Original source/target inputs remain read-only.

## Configuration

Pinned Japanese `ssr2d.nds`, SDAT file 975, SSEQ 11 `BGM_DEMPAJIKEN`,
sequence file 10, bank 60, volume 70. All eight source tracks remain separate,
with 19 PCM sample/root contexts and 12 generated instrument contexts.
Tempo 165 maps to GBA 166 (132.196868 ticks/second). Imported gain remains
+3.5 dB; the native mixer remains ten PCM voices at 10,512 Hz.

This song needs envelope fitting but no active pitch-LFO approximation.
Attack 100 maps to native 74; attack 127 maps to 255. The first fitted attack
is track 4's key 53 at tick 1,536, about 11.62 seconds. These are short
12-tick gates, so the test also exercises gradual attacks followed quickly
by release. Note-on ADSR snapshots retain the existing PCM8/envelope/tempo
and voice-allocation approximations; fitting does not establish waveform
equivalence with DS synthesis.

The common loop starts at 1,344 with period 2,304. Track 2's key 86 uses
long-note alias 127: a 239-tick gate starts at 1,224 and ends at 1,463.
The matching repeated instance starts at 3,528, crosses the first GOTO at
3,648, and ends at 3,767. TIE/EOT preserves the held voice across the jump
without another note-on. Entry/exit intervals match from -120 to +119 ticks.
The decoder compares two complete note-on cycles and follows this track's
final included gates through tick 6,079, beyond the 5,952-tick window.

## Evidence

- All 208 regression tests pass. The new song test checks the scan fingerprint,
  fitted attack, carried interval, BPS reconstruction, routing and native data
  preservation. A separate regression checks retrigger detection after many
  command cycles without repeating a one-off intro note.
- The independent 180-second DS software reference matches 5,131 notes on
  all eight tracks, 1,183 pan/bend/expression/delay controls, and 19 decoded
  PCM sample/root comparisons. ADSR validation checks 5,131 note-on snapshots,
  472,076 per-voice updates and 2,240 non-instant attack updates. Source
  repetitions cover at least two complete loops per track.
- `natural-loop/validation.json` checks the original eight-track ROM through
  its intro and one complete generated loop: 1,650 natural frames, clock 3,650,
  all 19/19 sample pointers and changing PCM output. Track states match the
  independent decoder across the first GOTO. No registers/RAM are edited,
  no headers redirected and no music restarts observed. Later complete GBA
  cycles are not covered by this probe.
- `envelope-window-v2/` checks 2,400 natural frames through clock 5,308:
  19,473 mapped channel observations, 17,488 exact native envelope steps,
  96 slow-attack and 7,493 release observations. Its bounded window includes
  the fitted attack and first GOTO/EOT. The report's slow-attack coverage
  means the fitted attack class was observed, not that every later passage
  received native runtime validation.
- `natural-carry-validation.json`, reproduced by `check-natural-carry.py`
  in the artifact directory, follows the original arrangement's carried alias
  for 108 observations. Slot 7, track 2, key 127 retains flags 17 and amplitude
  191 across clocks 3,648/3,650. At clock 3,768, after EOT, that same slot has
  release flags 81 and amplitude 175. This supplies actual first-jump
  continuity and stop evidence with the full arrangement's voice competition.
- `carry-probe/` supplements that observation with a disposable synthetic
  single-track sequence using the actual bank, voice, alias and 239-tick gate.
  A 355-tick cycle and loop start 120 expose three native carried-channel
  jumps at 475/830/1,185 and four EOT cycles. It does not validate later full
  eight-track cycles; no emulator register/RAM injection is used.
- `runtime/` checks effects 100/129, music continuation, ordinary/synthetic
  communication dispatch, queued stop, native restoration and three restart
  cycles. These controlled helpers inject PC/LR and do not establish actual
  gameplay or linked play.
- `preview/preview.wav` captures 30 seconds of native output (peak 13,163),
  including the first GOTO and carried note's EOT.
  `comparison/listen.html` provides normalized DS-software/native comparison.

The first envelope-window probe exposed a checker limitation after the decoded
prefix: it did not identify looped note-ons, so a valid new attack was compared
with the previous voice's sustain step. `note_started_between` now unfolds
only the decoder's command cycle, preserving the half-open tick interval.
The failed report remains in `envelope-window/`; the corrected full rerun
passes in `envelope-window-v2/`. The converter and ROM did not change.
The archived v8 scan retains its original packing-only evidence for this song.

## Reproduce and listen

Use fresh output directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-dempajiken-envelope --event 1 --event 21 --event scene:communication \
  --out out/nds-dempajiken-example
mkdir out/nds-dempajiken-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-dempajiken-example/source.sdat 11 180 out/nds-dempajiken-example/reference
python3 scripts/validate_nds_experiment.py out/nds-dempajiken-example \
  --reference out/nds-dempajiken-example/reference --lifecycle --out out/nds-dempajiken-example/runtime
python3 scripts/validate_song.py out/nds-dempajiken-example/unified.gba \
  --unified out/nds-dempajiken-example/build.json --id 474 --loop-cycles 1 \
  --frames 2400 --out out/nds-dempajiken-example/natural-loop
python3 scripts/validate_nds_envelope.py out/nds-dempajiken-example --frames 2400 \
  --out out/nds-dempajiken-example/envelope-window-v2
python3 scripts/validate_nds_loop_carry.py out/nds-dempajiken-example \
  --out out/nds-dempajiken-example/carry-probe
```

Listen continuously in battle for three minutes, focusing on the gradual
attack part entering around 12 seconds and joins around 28/45/62 seconds,
then every approximately 17.43 seconds. Check held notes for cuts, repeated
attacks and hanging notes. Use chips/Buster, return to the map and start
another encounter to check native restoration and restart.
`manual-testing.json` records user-reported acceptance on 2026-10-17 for
this exact ROM. Instrumented native loop coverage remains one complete cycle.
