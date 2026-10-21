# SF2 MIZUUMI: fixed pitch LFO across changing tempo

This standalone experiment follows the accepted SF2 VS route and the
[v18 audit](nds-compatibility-audit-v18.md). The user reported the requested exact-ROM checklist passed on 2026-10-20. Artifact: `out/nds-research/sf2-mizuumi-variable-tempo-exe6-v1/`.

- ROM SHA-256: `8156879a986056337a69ce9c0b8f6819948914c3439bd42286d1f171de6922b7`.
- ROM CRC32: `A8EAA31F`; 8,836,540 bytes.
- BPS SHA-256: `fa57cd3e18359c54b71b66919a82a36199723a286c2470702b78cc834d3daa9b`.

## Bounded variable-tempo mode

SF2 `BGM_MIZUUMI` (SSEQ 6) has eight looping tracks, instant attacks and six
executed tempos: 80/85/90/100/110/120. Tracks 2/7 use fixed zero-delay pitch
modulation, speed 20, depths 15/5. DS modulation runs from its voice timer;
native triangle modulation advances on sequence ticks. Keeping a single LFOS
while changing sequence tempo would also change vibrato frequency. The old
native-LFO fixed-tempo guard remains intact.

The explicit `native_pitch_lfo_variable_tempo=True` mode is limited to looping
singleton tracks with fixed per-track pitch modulation and zero source delay.
Source track 0 owns tempo and must not use active modulation. Tempo initializes
at tick zero, with two to eight distinct values and at most 128 unfolded real
changes. Conflicting different tempos at the same tick are rejected; repeated
identical initialization is allowed. Initial depth enabled just after the
first note at the same tick is retained in source order.

At each global tempo change, active tracks receive the corresponding nonzero
LFOS without MOD/LFODL writes or phase/count resets. Every new note uses the
current global tempo for its existing reset and one-tick onset delay. Fixed
state guards reject live parameter changes, late enable, delayed modulation,
fitting, minimum-depth quantization, filtering, mixed/finite structures and
other live-depth/toggle modes. This is a separate capability; it does not
combine all prior approximation modes or remove their default guards.

The source period is 4800 ticks. Latest entry 624 plus existing LFO warmup
selects common entry 5424; GOTOs are 10224/15024, observed near 1:47/2:38.
The encoded intro/body has 2,542 mapped notes, 173 keyed tone slots, 24 prepared
waves and thirty LFOS compensation events. The build appends 447,932 bytes at
+3.5 dB, ten PCM channels and 10,512 Hz. Title, ordinary virus battle and the
communication trigger select slot 474. Native manager/driver/mixer/DSP and
source game assets are unchanged by this extension.

## Independent source and packed checks

The pinned software DS renderer runs the original source for 180 seconds.
All 4,217 notes, 24 original PCM16 wave decodes, 137 ordinary controls,
25 tempo controls and eight depth controls match. All 180,277 observed sine
updates and source ADSR snapshots/timer transitions pass. Attacks are instant.
The source reaches sixteen voices at sampled observations. This is software
synthesis, not DS hardware/emulator capture or equal native allocation.

The separate variable-tempo reference checker unfolds source track 0 by its
executed loop action, preserving repeated same-tick commands. It requires two
complete source cycles and all declared tempos, and rejects missing, altered,
wrong-track or truncated controls. It never treats a constant tick rate as a
source timing reference. Packed checks verify all mapped notes, all 173 keyed
tone slots, original ADSR/pan/roots, raw PCM8 and relocated wave headers/data.

## Native evidence

Natural title playback followed by ordinary frontend Start input passes
9,429 frames through both complete common cycles and all 24 waves, ending at
clock 15025. KEYINPUT is checked. There is no register/RAM injection, header
redirect, keep-song mechanism or clock restart.

The read-only NOTE entry/allocation/exit observer passes 9,430 frames, clock
15027 and 75,440 track LFO comparisons. All 3,753 NOTE calls reach the observed
successful allocation branch; no rejection appears in this run. This does not
exclude stealing release tails under the ten-channel budget. Handler bytes
match the pinned original. A fabricated rejection of an observed allocated
note fails at clock 1, track 2; exact evidence passes.

The first observer run retained the earlier live-depth experiment's requirement
that depth change. This song's depth is fixed, so that run fails its coverage
assertion and remains recorded as failed. The complete rerun instead requires
both modulated tracks' six frequency states and invariant depths 2/1, while
retaining every allocation and frame/model comparison. No failed run is
relabeled passed.

Twenty-two windows independently compare actual frame/sequence-clock advances
with the encoded tempo rate, away from control boundaries, within 1.01 ticks
per window. All six tempos occur. Twelve isolated depth/tempo mappings have
maximum frequency error about 1.26% for this song, a diagnostic rather than a
general converter guarantee. Held-note tests verify positive LFOS writes retain
phase/count and later notes initialize at the new frequency. Controlled chip/
Buster effects, continuation, dispatch, queued stop, native restoration and
three restarts pass; these helper calls do not establish actual gameplay
transitions, two-peer communication or rematches.

All 333 regression tests pass. New cases cover phase continuity, current-tempo
note resets, same-tick initialization, default rejection, mode/parameter
exclusions, complete source tempo evidence and tempo/change budgets. All
38 previously accepted ROM/BPS pairs and two unaccepted controls rebuild
identically. Archived v10–v18 reports remain separate and unchanged. The batch
scanner does not enable this new variable-tempo mode.

## Fidelity and final manual check

Sequence-clock diagnostics compare allocated DS voices with shared native
tracks using the latest source timer observation. Tracks 2/7 show RMS pitch
differences about 9.32/4.19 cents, with maxima 25/10.94 cents. No waveform
alignment, equal allocations or whole-song fidelity bound is established.
Triangle versus sine, shared phase and note resets, voice budget, ADSR, PCM8
and tempo/frequency rounding remain approximations.

The actual 30-second mGBA preview peaks at 12,289 without a 16-bit ceiling hit.
The normalized comparison page covers the early tempo dip near twelve seconds,
but not the later ritardando near 48–51 seconds or either GOTO. It establishes
no comparative preference or manual acceptance. The requested checklist for
the exact ROM above was:

1. Listen in virus battle for at least three minutes. Check the intended
   tempo transitions near 12 and 48–51 seconds, plus joins near 1:47/2:38.
   Check accompaniment, vibrato and tails for abrupt jumps, thinning,
   distortion, repeated starts, hangs or crackles.
2. Repeatedly use chips and the Buster; check effects/music coexistence.
3. Return to the map and start another battle, for three encounters total;
   check native map restoration and a fresh imported start each time.

On 2026-10-20 the user reported “测试没有问题”, accepting the exact ROM
above for the requested three-minute battle listening, effects coexistence
and three-encounter lifecycle checklist. No independently timed recording or
completion trace was supplied; two-peer communication, rematches and comparative
preference are not inferred. `manual-testing.json` records this user-reported
acceptance separately from automated evidence and its limits.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-mizuumi-variable-tempo --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-mizuumi-variable-tempo-exe6-v1
```

Use fresh directories. Source provenance, failed original coverage assertion,
frontend-input source, applicable observer/negative control, tempo-rate checks,
packed resources, old rebuilds and final source fingerprints retain local
evidence. Original assets, ROMs and ignored outputs stay out of Git.
