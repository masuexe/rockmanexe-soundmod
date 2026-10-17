# Star Force 2 BATTLE: fixed-delay pitch LFO

This experiment turns the next [v5 audit](nds-compatibility-audit.md) candidate
into a standalone EXE6 test ROM. It retains eight source tracks and 24 PCM
samples and uses the accepted [fixed-delay approximation](nds-delayed-lfo-research.md)
at a faster tempo. Automated bounded playback and controlled lifecycle checks
pass. On 2026-10-17 the user reported no issues after the requested listening
and battle checks for this exact build.

Artifact: `out/nds-research/sf2-battle-delay-exe6-v1/`.
CLI song: `sf2-battle-delay`.

## Source and conversion

The pinned Japanese `ssr2d.nds` supplies SDAT file 975, SSEQ 27 `BGM_BATTLE`
(file 26), bank 60, source player 1, volume 55 and tempo 150. All eight tracks
are kept as singleton target tracks. There are ten voice contexts and 434,404
generated MPlay bytes. A 264-tick gate uses TIE/EOT without an added reattack.
The envelope fitting mode is not enabled.

Track 2 uses pitch depth 15, speed 25, range 1 and delay 10. At mapped GBA
tempo parameter 151, LFOS 20/MOD 2 approximates the sine with a shared native
triangle. LFODL is 7 ticks, compared with 6 in FMPLANET at its slower tempo.
The rounded phase displacement is 6 ticks (49.895 ms), versus the DS timer
delay of 52.095 ms, an error of -2.200 ms. The total counter wait is 58.211 ms
including the baseline zero-phase onset tick. These figures do not establish
equal first-nonzero pitch onset, since waveform and pitch quantization differ.

The fixed per-track modulation policy, initial same-tick activation handling,
shared delay/phase resets and rejection of later parameter changes are
unchanged. Overlapping voices and release tails still follow the target
track's shared phase; the source uses independent voice phase. PCM8, envelope,
tempo and ten-voice allocation limits remain documented approximations.

The target is original Japanese EXE6 Gregar, with eight-track music capacity,
ten PCM voices at 10,512 Hz and +3.5 dB imported gain. Title, ordinary music 21
and communication events select appended entry 474. Original entries and
prefix bytes outside declared hook/configuration ranges remain preserved.
Input ROMs are unchanged and exact BPS reconstruction passes.

- ROM: 8,826,808 bytes, CRC32 `73C49C6B`.
- SHA-256: `8957b60bd7bea3e8162bf16df3e59e828a39483031aa0307ed4824a5601b748e`.
- The ROM fingerprint matches the v5 batch variant exactly.
- Compiled loop start/period: 9432/5376 ticks, including native-LFO warmup.
  Compiled jumps occur approximately 123, 168 and 213 seconds after playback
  begins. The warmup unrolls existing music; it adds no silence.

## Evidence and listening scope

`runtime/reference-validation.json` records an independent 180-second software
DS reference, including source notes, all 24 PCM16 samples, controls, sine
modulation values and exact counter/phase transitions during delay holds and
activation. Source notes cover at least two complete loops on every track.
Reference data is in `reference/`, using the existing pinned delay renderer.

`lfo-window/validation.json` checks 2,400 natural frames through clock 4830:
all eight note/track states and the native pitch LFO match the MPlay model.
Track 2 is active, with 200 delayed zero-phase hold snapshots. No registers
or RAM are changed in this probe; it does not reach a compiled jump.
The diagnostic source/target comparison has 3,354 allocated-voice observations,
RMS pitch difference 8.89 cents and maximum 25 cents. This is sequence-clock
alignment, not waveform alignment or equal voice allocation.

`runtime/runtime.json` checks original effects 100/129, ordinary and synthetic
communication dispatch, queued stop, native restoration and three controlled
restart/rematch cycles. Helpers inject debugger registers; these checks do
not establish actual linked battles or map transitions. `preview/preview.wav`
and `comparison/listen.html` provide a 30-second actual mGBA recording and
normalized software-DS/GBA comparison, without full-loop coverage.

All 182 Python regression tests pass. The new export regression checks the
faster-tempo delay mapping, track/sample counts, BPS reconstruction, event
rules and original-data preservation. `validation-summary.json` collects the
automated evidence; `manual-testing.json` records user-reported acceptance for
this exact ROM on 2026-10-17. The requested checks cover four-minute battle
listening and loop joins, chips/Buster coexistence, map music restoration and
next-encounter restart. No timed recording or full-loop execution trace was
provided. Specific linked play and communication rematches were not separately
reported; the bounded automated coverage and synthesis approximations remain.

## Reproduce and test

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-battle-delay --event 1 --event 21 --event scene:communication \
  --out out/nds-sf2-battle-example
mkdir out/nds-sf2-battle-example/reference
out/nds-research/reference-player-delay-v1/nds-reference \
  out/nds-sf2-battle-example/source.sdat 27 180 out/nds-sf2-battle-example/reference
python3 scripts/validate_nds_experiment.py out/nds-sf2-battle-example \
  --reference out/nds-sf2-battle-example/reference --lifecycle \
  --out out/nds-sf2-battle-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-sf2-battle-example --frames 2400 \
  --reference out/nds-sf2-battle-example/reference \
  --out out/nds-sf2-battle-example/lfo-window
```

Use fresh output directories. Listen in a virus or communication battle for
four minutes, checking held-note vibrato onset, overlapping notes, release
tails and joins near 123/168/213 seconds. Use chips and the Buster. Finish the
battle, confirm native map music returns and start another battle to confirm
BATTLE restarts. The title changes scenes too early for complete loops.
Manager integration remains unchanged.
