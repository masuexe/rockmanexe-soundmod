# Star Force 3 WIN2: reuse of offline antialiasing

The standalone test ROM/BPS is in
`out/nds-research/sf3-win2-antialias-exe6-v1/`. It selects SSEQ 39 `BGM_WIN2`
at title, ordinary virus battle 21 and communication music, using appended
slot 474 on Japanese EXE6 Gregar. On 2026-10-18 the user reported “没有问题”
after the requested dense-passage/timbre/ending/descending-pitch listening,
ten-second silence, chips/Buster coexistence, native map restoration and at
least two additional encounter starts. This records user-reported acceptance
of the exact ten-channel ROM below, including its measured allocation
tradeoff. No timed recording or personal execution trace was supplied;
linked play/rematch was not separately reported.

ROM: 8,601,340 bytes, CRC32 `19BD2376`, SHA256
`9ed38ec454304c7749f3e37b49efa1795ebfbee3cf952c6c64fe4d2ee31da831`.
Gain is +3.5 dB; mixer settings remain ten PCM channels at 10,512 Hz.
The original 474 table entries and undeclared prefix bytes are preserved;
BPS reconstruction passes. Neither input ROM is modified.

## Source and conversion

Source: verified Japanese `ssr3b.nds`, SDAT 187, sequence file 39, bank 158,
sequence volume 75, source player 2. There are 83 note events, eight source
tracks and thirteen source PCM waves. The existing
[offline resampling route](nds-sf1-win2-antialias-research.md) prepares 34
cached per-key PCM8 waves. It uses the same stdlib windowed-sinc filter,
periodic loop guard and compensated tuning; no converter, filter or native
engine implementation change is needed for this song.

The new CLI choices are `sf3-win2-antialias` and `sf3-win2-finite`. The latter
is an internal unfiltered comparison, matching archived v10 `ssr3:39` ROM
and BPS exactly. Its ROM is 8,599,820 bytes; the antialias version adds only
1,520 bytes. The v10 snapshot is unchanged and does not acquire manual or
runtime evidence from this later standalone experiment.

| Source track | Target track | END tick |
| --- | --- | --- |
| 0 | 0 | 167 |
| 1 | 1 | 192 |
| 2 | 2 | 95 |
| 3 | 3 | 119 |
| 4 | 4 | 119 |
| 5 | 5 | 263 |
| 6 | 6 | 83 |
| 15 | 7 | 119 |

Tempo 150 maps to native parameter 151, about 120.251368 ticks/second.
The score lasts approximately 2.19 seconds, followed by release tails and
silence. All original note gates, controls, velocity, tone pan and ADSR are
retained. Downward bends reach -128; no upward bend, modulation, portamento,
transposition or fitted-envelope extension is needed. The maximum reported
stored-frequency rounding error is 0.000398 cents, not a measurement of the
complete native engine's tuning.

## Evidence and limits

- Independent pinned DS software reference: fifteen seconds, 83 notes,
  43 pan/bend/expression controls and thirteen unique PCM16 source decodings
  match. Reference peak is 16,060, with sixteen active voices at coarse
  observations and no clipped output samples. This is a software source
  rendering, not a hardware recording or filtered-wave equivalence test.
- Complete natural playback: 132 frames, clock 264, all eight decoded track
  states match through their individual FINE times, all 34 prepared waves
  are observed and changing native PCM is checked per frame.
- Natural stop: 960 sound updates, stable inactive clock 265, peak ten
  imported channels, 783 quiet updates after completion. The final 600
  updates have no imported channels or restart. Release flags are observed
  864 times, including tails after FINE. No CPU/RAM injection is used.
- Controlled effects 100/129, numbered/communication dispatch, stop, native
  restoration and three restart cycles pass. Finite timing windows are
  10/5/13/5 frames for warmup/effects/lifecycle/restart. Helper probes inject
  CPU context; personal gameplay and linked play remain separate checks.
- The fifteen-second native preview peaks at 16,885. The final-five-second
  audio-tail result and regression/voice-budget results are recorded in
  `validation-summary.json`. All 230 regression tests pass.
  `comparison/listen.html` offers normalized DS
  software/native audio.
- All four existing siblings of the finite builder branch rebuild with
  identical ROM/BPS: SF1/SF2 HENKAN, unfiltered SF1 WIN2 and accepted SF1
  WIN2 antialias v2. Full tests cover the new export, source track mapping,
  individual endings, prepared waves, native-data preservation and BPS.

This source reaches eleven simultaneously held note events at ticks 36 and
72, exceeding the fixed ten-channel native budget even before release tails.
The natural `voice-budget/` probe records conservative missing-held-note
observations with three-tick margins: four sampled frames show missing
held-note interiors, all before tick 120. These are sampled frames, not four
distinct lost notes or an exact allocator-event trace. Matching all 83 converted note commands does not establish identical
allocated polyphony. Listen especially to dense passages as well as the
ending and descending pitch.

Prepared PCM data totals 194,852 bytes, with 3,489 clamped PCM8 quantizer
values (1.79%). This includes full-scale rounding and possible FIR overshoot,
not clipping of the captured mix. Source wave 4 is itself near full scale
for 1,899 of 11,944 decoded samples. Restricted bandwidth, PCM8, filter/phase
quantization, envelope/pan/volume and voice-allocation differences remain.
No CPU benchmark or hardware performance claim is made.

## Reproduce and test

Use a fresh directory:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-win2-antialias --event 1 --event 21 --event scene:communication \
  --out out/nds-sf3-win2-antialias-example
mkdir out/nds-sf3-win2-antialias-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-sf3-win2-antialias-example/source.sdat 39 15 \
  out/nds-sf3-win2-antialias-example/reference
python3 scripts/validate_nds_experiment.py out/nds-sf3-win2-antialias-example \
  --reference out/nds-sf3-win2-antialias-example/reference --lifecycle \
  --out out/nds-sf3-win2-antialias-example/runtime
python3 scripts/validate_song.py out/nds-sf3-win2-antialias-example/unified.gba \
  --unified out/nds-sf3-win2-antialias-example/build.json --id 474 --frames 1200 \
  --out out/nds-sf3-win2-antialias-example/natural-finite
```

Hear the roughly 2.2-second score and its tails, wait ten seconds after it
finishes, use chips/Buster during and after playback, return to the map and
start at least two additional encounters. Check dense notes, timbre, release
and descending pitch. Silence after the cue is expected.
`manual-testing.json` records user-reported acceptance on 2026-10-18 for
this exact ROM. This does not remove the observed missing-held-note
interiors or establish original/target polyphony equivalence.
