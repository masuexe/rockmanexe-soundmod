# SF2 VS: late initial activation with positive depth updates

This standalone experiment follows the accepted SF2 LOSE extension and the
[v17 audit](nds-compatibility-audit-v17.md). The user reported listening without issues on 2026-10-20; effects and
three-encounter lifecycle checks await separate confirmation. Artifact: `out/nds-research/sf2-vs-late-depth-exe6-v1/`.

- ROM SHA-256: `9f8e72d738aeb88d289145508efe12e6b2c347efc0b9c4b5b0d02f639ce2f215`.
- ROM CRC32: `0FEB4BD7`; 8,784,856 bytes.
- BPS SHA-256: `4aa58848895032367bc60be5ec4bd05752b061555cae2bf6db326b8b586f170b`.

## Bounded capability

SF2 `BGM_VS` (SSEQ 37) has eight looping singleton tracks and a fixed tempo of
158. Track 5 first plays at tick 576, while its first positive depth is enabled
at 864. Track 2 changes positive depth from 20 to 10 at that same timestamp.
The existing fixed-delay, live-positive and fixed-depth-toggle routes each
reject part of this combination. Defaults keep these guards.

The explicit `native_pitch_lfo_late_depth=True` mode requires native pitch LFO,
delay and positive live-depth support. It permits inactive notes before first
enable, with fixed type/speed/range/delay, then positive depth updates only.
It rejects disabling after activation, other live parameter changes, merged
tracks, mixed/finite structures, filtering, fitted envelopes, minimum-depth
quantization and toggle mode. Fixed tempo, bounded periods, gate timing and
voice-context guards remain. All source attacks are instant.

Inactive note commands stop LFOS and preload LFODL. Every depth control in
this new mode emits MOD and the fixed mapped LFOS, including first enable.
A nonzero LFOS write preserves shared phase/count; a later positive update
therefore changes depth without starting a new delay or resetting phase.
The old live-depth route retains its MOD-only bytes and prior acceptance.
No native manager, driver, mixing rate or DSP changes occur.

The eight source periods are 7296 ticks. The latest entry 2400 plus established
LFO warmup selects common entry 9696, with GOTOs at 16992 and 24288 (about
2:14 and 3:12). The build has 4,162 mapped notes, 159 keyed tone slots and
18 prepared waves from seventeen originals. It appends 396,248 bytes at
+3.5 dB, ten PCM channels and 10,512 Hz. Title, ordinary virus battle and the
communication trigger select slot 474.

## Source evidence and its coverage limit

The pinned independent software DS renderer runs the original source for
210 seconds. All 6,493 notes, seventeen decoded PCM16 waves, 211 ordinary
controls and eighteen depth controls match. All 168,092 sine updates and
173,222 delay-counter updates pass, with 5,130 waits and 513 zero-phase
activations. The same source has sixteen voices at sampled observations.
This is a software synthesis reference, not DS hardware/emulator capture.

At track 5's actual late CA=10 control, the renderer records one held and eight
release voices; eight UpdateMod observations enable depth and preserve zero
phase/count. These are distinct counts, not a claim that all nine were updated.
All 2,072 observed UpdateMod transitions preserve phase/count. Only one
positive-depth voice update coincides with an actual source CA point, and it
has zero phase/count. Reused-voice note initialization is excluded from that
control count.

The existing strict carried-positive-depth source probe fails on this song;
its failed result is retained. It is not marked passed or relaxed globally.
The new mode uses a separate late-activation check requiring the actual late
control and allocated-voice updates, checking every UpdateMod state and
explicitly reporting **no carried-positive-depth coverage**. Existing live-depth
checks retain their original requirement. Synthetic held-note tests cover
positive updates both during and after the initial delay, and reject counter
or phase resets and note-initialization coverage inflation.

## Native evidence

Natural title playback followed by ordinary frontend Start input passes
11,458 frames through both complete common cycles and all eighteen prepared
samples, ending at clock 24289. KEYINPUT is checked; no register/RAM injection,
header redirect, keep-song mechanism or clock restart is used.

A separate read-only NOTE entry/allocation/exit observer passes 11,459 frames
and 91,672 track LFO comparisons through clock 24291. All 5,955 NOTE calls
reach the actual successful allocation branch; no rejected NOTE is observed
in this run. This does not establish sixteen-voice synthesis or absence of
release-tail stealing. Original handler bytes match the pinned base ROM.
A fabricated rejection of an observed allocated delayed note fails at clock 1,
track 2; the unmodified allocation evidence passes.

Before late enable, track 5 remains MOD=0/LFOS=0 with preloaded count=1. At clock
865 it has MOD=1/LFOS=15/count=0/phase=0; subsequent phase advances correctly.
The complete allocation-aware model covers the two GOTO windows. Packed checks
verify every mapped note, all 159 keyed tone slots, wave headers/raw PCM8,
roots, pan and original ADSR. Controlled chip/Buster effects, continuation,
dispatch, queued stop, native restoration and three restarts pass. Those helper
injections do not establish actual gameplay transitions, linked play or rematch.

All 317 regression tests pass. All 37 previously accepted ROM/BPS pairs and
two unaccepted controls rebuild identically. New regressions cover explicit
late activation, preloaded delay, positive phase continuity, default rejection,
mode/parameter exclusions, coverage limits and LFOS emission. Archived v10–v17
files remain separate and unchanged. The batch scanner does not enable this
new late-depth mode.

## Fidelity and final manual check

Sequence-clock diagnostics compare allocated DS voices with shared target
tracks, using the latest observed DS timer frame. Tracks 2/4/5 have RMS pitch
differences about 4.98/5.62/5.27 cents, with maxima 26.56/12.5/12.5 cents.
These are not waveform alignment, equal allocations or whole-song fidelity
bounds. Ten versus sixteen voices, triangle versus sine, shared phase/count,
new-note resets, envelopes, PCM8 and tempo rounding remain approximations.

The actual 30-second mGBA preview peaks at 14,780 without a 16-bit ceiling hit.
The normalized comparison page covers the late enable near 6.8 seconds, but
neither GOTO. It establishes no listening preference or manual acceptance.
The requested checklist for the exact ROM above was:

1. Listen in virus battle for at least four minutes, including the enable near
   6.8 seconds and joins around 2:14/3:12. Check dense accompaniment and release
   tails for abrupt thinning, distortion, hangs, repeated starts or crackles.
2. Repeatedly use chips and the Buster; check effects/music coexistence.
3. Return to the map and start another battle, for three encounters total;
   check native map restoration and a fresh imported start each time.

On 2026-10-20 the user reported “试听没有问题”. The exact-ROM listening
check is recorded as user-reported pass. Effects and three-encounter lifecycle
checks remain pending clarification; they are not inferred from the listening
report. No independently timed recording, completion trace, two-peer/rematch
result or comparative preference is established. `manual-testing.json` retains
partial acceptance, so this version does not yet match the scanner's full
`user_reported_pass` evidence policy. Source/tests/docs can be committed with
this listening-only scope; full checklist acceptance remains separate.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-vs-late-depth --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-vs-late-depth-exe6-v1
```

Use fresh directories for repeated probes. Source provenance, failed strict
source check, frontend-input source, allocation observer/negative control,
packed-tone checks, old rebuilds and source fingerprints retain local evidence.
Original assets, ROMs and ignored research outputs remain outside Git.
