# Star Force 2 KAICYOU: envelope and live modulation enable

This experiment turns the new [v7 audit](nds-compatibility-audit.md) candidate
into a standalone EXE6 ROM. It combines the existing envelope fit and binary
modulation mode without changing converter mappings. The ROM awaits
four-minute battle listening and gameplay acceptance.

Artifact: `out/nds-research/sf2-kaicyou-toggle-exe6-v1/`.
CLI song: `sf2-kaicyou-toggle`.

## Source and conversion

The pinned Japanese `ssr2d.nds` supplies SDAT file 975, SSEQ 16 `BGM_KAICYOU`
(file 15), bank 60, source player 0, volume 50 and tempo 140. Eight singleton
tracks and 24 original samples are retained in 13 voice contexts. The generated
MPlay resource is 376,624 bytes. A 384-tick gate uses TIE/EOT without an added
reattack. Existing attack fitting maps DS 100/127 to GBA 74/255; the first
attack-100 note occurs on track 2 at tick 48, about 0.43 seconds into playback.

Track 2 first sounds at tick 48 and enables depth 10 at tick 768, after a
new note at the same timestamp. Speed 25/range 1/delay 10 map to native
LFOS 21/MOD 1/LFODL 7. Track 4 configures depth 10 at tick 768 before first
sounding at tick 1056, using speed 20 and zero delay, mapping to LFOS 17/MOD 1
and the baseline one-tick onset delay. Both setup controls execute around
6.84 seconds into target playback; track 4 enters around 9.40 seconds.

The source never disables modulation. The opt-in binary mode permits this
enable-only subset. The independent checker now requires disable controls
only when the compiled source trace contains them, while keeping the prior
BOSS disable requirement. It reports zero disable coverage for KAICYOU.
The pre-note reference check also recognizes zero-delay modulation when
the live-toggle flag is enabled; this covers track 4's initialization order.

Source tempo 140 maps to target parameter 141 (112.288 ticks/second). For
track 2, rounded phase displacement is 53.434 ms versus the DS 52.095 ms wait;
total native delay wait is 62.340 ms including the baseline zero-phase tick.
Envelope fit, PCM8, tempo, triangle waveform, pitch quantization, ten-voice
allocation and shared phase/delay remain approximations. New notes reset
older voices and release tails. The binary mode's reset-on-disable difference
remains documented, although this source does not exercise disabling.

Japanese EXE6 Gregar retains eight-track capacity, ten PCM voices at 10,512 Hz
and +3.5 dB imported gain. Title (1), ordinary virus music (21) and communication
scenes select appended entry 474. Original table entries and prefix bytes
outside declared hook/configuration ranges remain preserved. BPS reconstruction
passes and original input ROMs are unchanged.

- ROM: 8,769,116 bytes, CRC32 `1D6D438A`.
- SHA-256: `739726a97c9005ff4905258348c656836802fefc2847b0cdc6ff88b400c86aa5`.
- ROM and BPS fingerprints match the v7 packed variant exactly.
- Compiled loop start/period: 5664/4608 ticks. Jumps occur near 91/133/174/215
  seconds. Warmup unrolls existing music without adding silence.

## Evidence and scope

`reference/` contains a 180-second independent software DS rendering from
the existing pinned `reference-player-depth-v2`, including notes, controls,
decoded PCM16 samples, per-voice envelope and modulation observations.
`runtime/reference-validation.json` checks at least two complete source
loops per track, both initialization orders and source-specific enable-only
behavior. This is software reference evidence, not a DS hardware recording.
It matches 5,128 notes, all 24 PCM16 samples, 576 ordinary controls, 20 depth
controls and 75,827 active sine observations. Envelope checks include 433,448
timer updates and 1,428 non-instant attack updates. Two enable controls and
zero disable controls are reported, without claiming carried-disable coverage.

`lfo-window/validation.json` checks 2,400 natural frames of actual MPlay
note/track states and both LFO tracks. `envelope-window/validation.json`
checks allocated native envelope parameters and steps, including the fitted
attack-100 section. Neither probe changes emulator registers/RAM or reaches
a complete GBA loop. `preview/preview.wav` and `comparison/listen.html` provide
30-second native audio and normalized software-DS/GBA comparison, covering
both the initial attack and modulation enable.
The native envelope window checks 18,392 exact steps, including 168 slow-attack
and 5,961 release observations. Diagnostic clock-aligned RMS pitch differences
are 5.12/6.02 cents on tracks 2/4, with maxima 14.0625/12.5 cents; these do not
establish waveform alignment or equal voice allocation.

`runtime/` checks effects 100/129, ordinary/synthetic communication dispatch,
music continuation, queued stop, native restoration and three restart cycles.
Controlled helper calls do not establish actual linked gameplay or map
transitions. On 2026-10-17 the user reported “测试没有问题” after the requested
four-minute battle listening and gameplay checklist. This is user-reported
acceptance of the loop joins, attacks/modulation, effects coexistence, map
restoration and next-encounter restart for the fingerprint above. No timed
recording or full-loop execution trace was supplied; linked play and rematches
were not separately reported.

New regressions check enable-only reference coverage without weakening the
default disable requirement, both initialization orders, attack fitting,
the v7 ROM fingerprint, BPS reconstruction and original-data preservation.
The existing NESSIE builder branch still produces byte-identical ROM/BPS;
BOSS independent checks still require and match three disable controls.
`prior-regressions.json` records these checks. `validation-summary.json`
collects final results and `manual-testing.json` records user-reported
acceptance for this exact ROM. The archived v7 scan remains unchanged.
All 203 Python regression tests pass.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-kaicyou-toggle --event 1 --event 21 --event scene:communication \
  --out out/nds-kaicyou-example
mkdir out/nds-kaicyou-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-kaicyou-example/source.sdat 16 180 out/nds-kaicyou-example/reference
python3 scripts/validate_nds_experiment.py out/nds-kaicyou-example \
  --reference out/nds-kaicyou-example/reference --lifecycle --out out/nds-kaicyou-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-kaicyou-example --frames 2400 \
  --reference out/nds-kaicyou-example/reference --out out/nds-kaicyou-example/lfo-window
python3 scripts/validate_nds_envelope.py out/nds-kaicyou-example --frames 2400 \
  --out out/nds-kaicyou-example/envelope-window
```

Use fresh output directories. Listen in battle for four minutes, focusing on
the gradual note attacks, modulation after about seven seconds, the part
entering around nine seconds, held notes/release tails and joins near
91/133/174/215 seconds. Use chips and the Buster, finish the battle, confirm
native map music restoration and start another encounter to check KAICYOU
restarts. Title playback ends too early for complete loops.
