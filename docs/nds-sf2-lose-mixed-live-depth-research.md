# SF2 LOSE: later mixed entry, live depth and a one-shot track

This standalone experiment converts SF2 `BGM_LOSE` (SSEQ 32), following the
[v16 compatibility audit](nds-compatibility-audit-v16.md) and the separately
accepted SF1/SF3 LOSE experiments. The user reported this exact ROM passed its requested checklist on 2026-10-20.
Artifact: `out/nds-research/sf2-lose-mixed-depth-min-exe6-v1/`.

- ROM SHA-256: `78839705aec52526571a6a5ee344e88843b4d47d993c3cee61e034819ca80c8f`.
- BPS SHA-256: `fd88295c5fa59a8835e287a5b2e790bcb0fb4bd6258e39ce8d368e4cd4799e89`.

## Bounded policy

Six tracks loop with period 768. Source track 15 ends once at tick 911, and
its last gate closes at that END. The latest original looping entry is 864,
so the default mixed route still rejects the score. The new explicit
`mixed_live_depth_support=True` extension requires singleton mixed tracks,
native pitch LFO, delayed positive-depth mode, fixed tempo and all finite
gates closed by END. It excludes finite-only, release-override, filtering and
live-toggle modes. Existing source period and expansion limits remain.

When a finite END exceeds the original entry, the extension selects a later
entry by a whole common period, capped at **one additional period**. Here
864 becomes 1632. The established LFO warmup then places the emitted common
entry at 2400. This unrolls existing looping music without silence or repeating
the finite track. Shared GOTO boundaries are 3168/3936, near 34.6/43.0 seconds.
Track 15 retains FINE=911, around 9.9 seconds, and never receives GOTO.

Fitted attacks and weak-depth quantization remain separate explicit flags.
The mixed extension permits the already supported fitting and live positive-
depth combination; it does not enable them silently. Source attack 124 retains
fit 229 under the existing amplitude limits. Depths 40/60/100 use ordered MOD
updates with fixed type/speed/range/delay. Weak depth 3 retains MOD=1 and its
ten-cent all-phase/five-cent isolated RMS bounds. These are not whole-song
fidelity bounds. Default mixed, finite and looping routes retain their prior
outputs and guards; no production manager, native driver or DSP change occurs.

The build uses seven tracks, fifteen prepared waves from fourteen source
waves, 1,574 mapped notes through its encoded intro/body and 52 tone slots.
It appends 249,948 bytes at +3.5 dB, ten PCM channels and 10,512 Hz. Title,
ordinary virus battle and communication triggers select slot 474.

## Source and native evidence

The existing pinned software DS renderer runs the original source for
60 seconds. All 2,721 notes match, including the complete 58-note finite track
with no loop unfolding, alongside fourteen PCM16 decodes, 283 ordinary and
59 depth controls. All 37,242 observed sine updates and 99,940 delay-counter
updates pass, with 62,698 waits and 1,611 zero-phase activations. All 844 positive
UpdateMod transitions preserve phase/count; 130 carry nonzero state. Note-on
ADSR and 133,997 envelope updates also pass, including 112 non-instant updates.
This is software synthesis, not DS hardware/emulator audio.

`out/nds-research/sf2-lose-later-entry-research-v1/` preserves pinned source
inputs, the source-only checker and a phase-equivalent note-window model.
Three windows after the selected later entry match; the finite notes remain
once. The actual conversion separately passes the independent reference checks.

Natural title playback checks 2,568 frames through clock 3937: intro, two full
common cycles, all seven tracks and all fifteen samples. No frontend input,
game-RAM/register injection, song retention, clock restart or header redirection
is used. This finishes before the ordinary title attract sequence.

The allocation-aware observer covers 2,569 frames through clock 3938. It checks
all 1,954 native NOTE calls and 17,983 per-frame LFO states. Finite models stop
advancing at FINE; looping command streams unfold through both jumps. There
are 70 rejected note allocations under the unchanged ten-channel policy:
65 on target track 5 (source 7), five on target 6 (finite source 15). A negative
control fabricating success for an observed rejected note fails at clock 194.
These are observed budget differences, not a claim that they are inaudible.

A separate checker reads actual track/channel snapshots throughout natural
playback. The finite track's last active owned channel is at clock 911; its
LFO fields remain frozen after FINE, no new START flags occur, and its channels
stay empty from the shared entry through both GOTOs. It observes a peak of
three finite-owned channels and 74 release snapshots. The later entry does not
replay or revive the one-shot voice.

The native envelope probe checks 13,490 steps, 28 slow-attack observations and
1,737 release observations. Packed checks verify all 1,574 note mappings,
52 tone slots and fifteen wave payloads/headers, roots, pan and fitted ADSR.
Controlled effects, dispatch, queued stop, native restoration and three
restarts pass. These helper injections do not establish actual gameplay,
results/map transitions, two-peer communication or rematches.

All 306 regression tests pass. New cases cover explicit entry advancement,
its one-period budget, finite gate closure, long EOT-before-FINE, mode/singleton
exclusions, explicit fitting/quantization and retained parameter guards.
All 36 accepted ROM/BPS pairs and two unaccepted controls rebuild identically.
Archived v10–v15 files and v16's report/derived outputs remain unchanged.
The new route is not yet enabled by the batch scanner.

## Fidelity and final manual check

Source execution reaches sixteen voices; the native budget stays ten. Sparse
source IDs are mapped explicitly in diagnostics. Weak target tracks 3/5 have
latest-timer/sequence-clock RMS differences about 1.78/2.54 cents (max 6.25).
Deeper tracks show about 26.52–32.52 cents RMS, with maxima up to 78.125 cents;
one track has only nine allocated comparison rows. Triangle versus DS sine,
shared phase/count and note resets, finite-track freezing at FINE, envelopes,
PCM8 and allocation remain approximations. No equal polyphony, sample alignment
or whole-song fidelity bound is claimed.

The actual 30-second mGBA preview peaks at 23,196. The normalized comparison
page covers the finite ending but neither later GOTO. It establishes no manual
preference or gameplay acceptance. For the exact experimental ROM, the requested checklist was:

1. Listen in virus battle for at least three minutes. Check the one-shot voice
   ending around ten seconds, dense accompaniment, echoes/long-note vibrato,
   and joins near 35/43 seconds for abrupt cuts, thinning, distortion, repeated
   starts, hangs or crackles. The one-shot voice must not restart at the joins.
2. Repeatedly use chips and the Buster; check music/effects coexistence.
3. Return to the map and begin another battle, for three encounters total;
   check native map music restoration and a fresh imported start each time.

On 2026-10-20 the user reported “没有问题”, accepting the exact fingerprints
above for this checklist. No timed recording or completion trace was supplied;
two-peer communication, rematches and comparative preference are not inferred.
`manual-testing.json` and `validation-summary.json` record user-reported
acceptance separately from automated evidence and its limits.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-lose-mixed-depth-min --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-lose-mixed-depth-min-exe6-v1
```

Use fresh directories for repeated probes. `validate-allocated-lfo.py`,
`check-finite-track.py`, `check-allocation-evidence.py`, `check-packed-tones.py`,
`rebuild-prior.py` and source fingerprints retain local research evidence.
ROMs, original game assets and ignored research outputs stay out of Git.
