# Star Force 1 PLANETARIUM: long notes across loop jumps

The standalone experiment is
`out/nds-research/sf1-planetarium-delay-exe6-v1/`. It replaces title music,
ordinary virus battle 21 and synthetic communication dispatch with appended
slot 474 on Japanese EXE6 Gregar. On 2026-10-17 the user reported
“测试没有问题” after the requested four-minute battle listening and gameplay
checklist. This records user-reported acceptance for the exact ROM below: held
notes/bass, joins near 129/189 seconds, effects coexistence, map restoration
and next-encounter restart. No timed recording or full-loop execution trace
was supplied; linked play and rematches were not separately reported.

ROM: 8,870,340 bytes, CRC32 `88BE048C`, SHA256
`6fe56fb239430b3c1b4337654ddd011c4ec2f55b720de4adbb55406458c9098e`.
`unified.bps` reconstructs that ROM from the verified original. Original 474
table entries and all undeclared prefix bytes remain unchanged.

## Boundary and correction

Pinned Japanese `ssr1d.nds`, SDAT 667, SSEQ 13 `BGM13PLANETARIUM` uses
eight tracks and 29 converted PCM sample/root contexts. Source tempo 145 maps
to native parameter 146 (116.269534 ticks/second). Imported gain is +3.5 dB;
the native mixer remains ten PCM voices at 10,512 Hz.

The generated common loop starts at tick 7,968 and repeats every 7,008 ticks.
Track 7's key 53 starts at 7,776, holds for 384 ticks and ends at 8,160.
Its next instance starts at 14,784, crosses the jump at 14,976 and must stop
at 15,168. The old compiler rejected these intervals even though a matching
TIE/EOT pair can carry the voice across GOTO.

The compiler now requires identical carried intervals, relative to the
entry/exit boundaries, for each long-note alias. The warmup's EOT inside
the loop body closes the previous iteration's TIE after the jump. It never
inserts another note-on at the boundary. This track uses alias 126, whose
instrument root preserves source key 53. Overlapping long notes sharing an
alias, insufficient aliases and unmatched entry/exit carries remain rejected.

The independent decoder compares the intro and two complete loop periods.
It now continues beyond that note-on window to close every included tied
gate, while excluding later note-ons from the comparison. Track 7's note-on
window ends at 21,984 and its last gate is checked through 22,176. A missing
or incorrect EOT, wrong gate, duplicated alias or changed note schedule fails.

## Evidence and limits

- All 206 regression tests pass, including synthetic carried gates, incorrect
  duration rejection, insufficient warmup rejection, overlapping-alias
  rejection and the actual PLANETARIUM output/data-preservation checks.
- All sixteen previously accepted experiment ROMs and BPS patches rebuild
  byte-identically; see `prior-regressions.json`.
- The independent 240-second DS reference matches 7,232 note events across
  all eight tracks, 504 pan/bend/expression controls and decoded PCM waves.
  It checks 108,527 sine-modulation observations and 114,527 delay updates,
  including 6,000 waiting updates and 600 onset observations. This covers
  source repetitions, not full GBA loop execution.
- `lfo-window/` checks 2,400 natural title frames through clock 4,671 without
  register/RAM changes: track/note state and track 2's delayed native LFO
  match the MPlay model. It does not reach an original-song jump.
- `carry-probe/` uses a disposable synthetic one-track ROM with the actual
  converted bass bank, voice, alias and 384-tick gate. A 500-tick period and
  192-tick loop start expose three native jumps at 692/1,192/1,692. The same
  active PCM channel survives each jump without START/release flags; four
  EOT cycles are observed. This probe changes the sequence in a ROM copy,
  without emulator register/RAM injection. It does not execute the original
  eight-track arrangement's full loops or its voice competition.
- `runtime/` checks effects 100/129, continued music, ordinary/synthetic
  communication dispatch, stop, native music restoration and three restart
  cycles. These helpers inject PC/LR; actual gameplay remains a manual check.
- `preview/preview.wav` contains 30 seconds of native output (peak 9,459).
  `comparison/listen.html` provides normalized DS-software/native comparison;
  normalization does not establish waveform or voice-allocation equivalence.

Track 2 initializes depth 10 at tick zero before its first note at 24.
The existing fixed-delay approximation maps DS delay 10 to LFODL 7, with
phase onset error approximately -0.491 ms. Native triangle/shared phase,
overlapping-note resets, release-tail behavior, PCM8/envelope quantization,
tempo rounding and ten-voice allocation remain approximations.

The archived v7 audit remains unchanged. Its PLANETARIUM row records the
earlier boundary rejection; this standalone experiment supplies later
evidence. No production manager integration or channel-count expansion is
part of this correction.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-planetarium-delay --event 1 --event 21 --event scene:communication \
  --out out/nds-planetarium-example
mkdir out/nds-planetarium-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-planetarium-example/source.sdat 13 240 out/nds-planetarium-example/reference
python3 scripts/validate_nds_experiment.py out/nds-planetarium-example \
  --reference out/nds-planetarium-example/reference --lifecycle --out out/nds-planetarium-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-planetarium-example --frames 2400 \
  --out out/nds-planetarium-example/lfo-window
python3 scripts/validate_nds_loop_carry.py out/nds-planetarium-example \
  --out out/nds-planetarium-example/carry-probe
```

Use fresh output directories. Listen continuously in battle for four minutes.
Focus on bass/held-note continuity around 129 and 189 seconds, checking for
cuts, repeated attacks or hanging notes. Use chips and the Buster, return to
the map and start another encounter to check native restoration and restart.
Title playback ends too early for the full-song jumps. `manual-testing.json`
records user-reported acceptance on 2026-10-17 for the exact ROM fingerprint.
