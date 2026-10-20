# SF1 LOSE: live positive depth with bounded weak modulation

This standalone experiment converts SF1 `BGM32LOSE` (SSEQ 32), following the
[v15 follow-up](nds-compatibility-audit-v15.md). Artifact directory:
`out/nds-research/sf1-lose-depth-min-exe6-v1/`.
On 2026-10-20 the user reported “没有问题” after the requested listening,
effects and three-encounter lifecycle checklist, accepting this exact ROM.
No timed recording or completion trace was supplied. Two-peer play and rematch
were not separately reported, and no comparative listening preference is inferred.

- ROM SHA-256: `6ea941a10b47c5afd0e140fb66fa1608d9a17e4b2679809ec9fc30b8478e7bd5`.
- BPS SHA-256: `8388bb0d32ef76a2273cd6deb5f8c5167c5b37d494a4f4b6fd4be8a00d53295b`.

## Explicit combined policy

`sf1-lose-depth-min` enables the existing native delayed pitch LFO and live
positive-depth controls together with explicit minimum-depth quantization.
The latter now also admits this looping singleton live-depth route. Fixed
tempo and existing activation/parameter guards remain: no later activation,
depth disabling, changes to speed/type/range/delay, or merged target tracks.
Mixed/finite tracks, release snapshots, filtering and live-toggle mode are
excluded from this new combination. Fitted attacks remain a separate explicit
flag, as already used by HOMETOWN's live-depth experiment. Default routes and
HOKORA's existing mixed-route metadata remain unchanged.

Source tracks 1/15 change between depths 40, 60 and 100 with speed 31 and
delay 48. They map to native MOD 5/7/12, LFOS 32 and LFODL 24. Track 2 uses
depth 60 and delay 96 (LFODL 47). Tracks 5/7 use depth 3, speed 28 and delay
14: the explicit quantization maps them to MOD 1, LFOS 29 and LFODL 8.
The weak configuration has a 9.375-cent all-phase difference bound and about
3.20-cent isolated one-second RMS error, within the existing ten/five-cent
limits. These limits apply to sub-resolution quantization, not all modulation.
Depth controllers emit ordered MOD alone, preserving shared phase/count;
note-on phase and delay resets retain the native driver's allocation rules.

Instrument 67 on source track 6 needs attack fitting: source attack 124 maps
to 229, with RMS/max normalized amplitude errors about 0.0927/0.2671 under
the established 0.12/0.30 limits. It first sounds at tick 0. Other attacks are
instant. Existing ADSR quantization and note-on snapshots remain approximations.

All seven source tracks loop, with period 768 and latest source entry 864.
The existing warmup places the compiled shared entry at 1632. Source and target
tempo parameters are 115. Common jumps at 2400/3168 occur near 26.2/34.6 seconds;
thereafter the cycle lasts about 8.4 seconds.

The build retains 1,267 mapped notes through its encoded intro/body, 53 native
tone slots and sixteen prepared waves from fifteen source waves. It appends
306,168 bytes, retains +3.5 dB gain and uses ten PCM channels at 10,512 Hz.
Title, ordinary virus battle and communication triggers select slot 474.
The production manager and native mixer are unchanged; no filtered version
is inferred from this active-modulation experiment.

## Independent source execution

The pinned existing SSEQPlayer renderer executes the original source for
60 seconds. All 2,947 notes, 283 ordinary controls, 95 depth controls and fifteen
PCM16 decodes match. All 39,199 observed sine updates and 113,996 modulation
counter updates pass, including 74,797 waiting updates and 1,843 zero-phase
activations. Of 1,158 positive UpdateMod transitions, 175 carry nonzero phase
or count; all preserve both counters. Note-on ADSR and per-voice envelope
updates also pass. This is software DS synthesis, not hardware/emulator audio.

`out/nds-research/sf1-lose-depth-min-research-v1/` retains the source-only
investigation, pinned inputs, renderer provenance and a reproducible checker.
The experimental artifact separately validates the full conversion against
the same byte-identical reference.

## Native execution and the allocation model

Natural title playback passes 2,068 frames through clock 3170: the intro and
two complete native cycles, all seven tracks and all sixteen prepared samples.
No game RAM/register writes, song retention, clock restart, header redirection
or frontend input is used.

The earlier short LFO probe remains a recorded failure: it assumed every NOTE
reloaded the delay counter. EXE6's actual LFODL handler writes only track offset
27 (reload value); the NOTE handler copies it to offset 28 only after choosing
a channel. Disassembly and read-only entry/allocation/exit breakpoints in the
unchanged original driver establish this behavior. A full-loop observer checks
all 1,686 NOTE calls and their reset branches. Four notes are rejected by the
ten-channel allocation policy, on target track 6 (source 15), key 58/velocity
28, at clocks 404/1172/1940/2708. No extra source track or note is invented to
hide this hardware-budget difference.

`LfoModel` now models reload separately and accepts explicit boolean allocation
evidence; absent evidence it retains the successful-note assumption. The
ordinary probe remains strict. The dedicated observer annotates every decoded
NOTE with an actual branch observation, requiring exactly one entry/exit pair
per scheduled NOTE. It then independently checks all 14,476 per-frame native
track LFO states through both jumps. A negative control that fabricates success
for the rejected tick-404 note fails at clock 405. No failed comparison is
ignored or inferred to pass.

Reference diagnostics now map sparse source IDs `[0,1,2,5,6,7,15]` to target
indices explicitly. Latest-timer, sequence-clock comparisons use allocated DS
voices; they are not sample aligned or equal voice allocations. Weak target
tracks 3/5 show RMS differences about 1.79/2.26 cents (max 6.25). Deeper target
tracks 1/6 show about 26.24/34.95 cents (max 78.125); target 2 has only nine
allocated comparison rows. Shared resets and native triangle/DS sine differ
substantially in these deeper configurations. These diagnostic differences
are not a whole-song fidelity bound or a listening pass.

The envelope probe checks 14,367 native steps, 28 slow-attack observations and
1,605 release observations. Packed checks verify all 1,267 mappings, 53 tone
slots, sixteen wave headers/PCM8 payloads, roots, pan and fitted envelopes.
Controlled effects, dispatch, queued stop, native restoration and three
restart cycles pass. These helper injections do not establish actual gameplay,
results/map transitions, two-peer communication or rematches.

All 294 regression tests pass. Thirty-four accepted ROM/BPS pairs and two
unaccepted controls rebuild byte-identically. Archived v10–v14 files and v15's
report/derived outputs remain unchanged. The new combined route is not yet
added to the batch scanner. `validation-summary.json` collects exact artifact
fingerprints, source/native checks, model limits and separate manual status.

## Recorded final manual check

The actual mGBA preview has a 30-second peak of 19,221 and covers the first
common jump, not the second. `comparison/listen.html` compares it with software
DS synthesis using whole-clip loudness normalization. It establishes no
listening preference or gameplay acceptance.

The requested checklist for the exact experimental ROM was:

1. Listen in virus battle for at least three minutes. Check long-note/echo
   vibrato, fitted attacks, and joins near 26/35 seconds for unnatural sound,
   muddiness, repeated starts, missing notes, hangs or crackles.
2. Repeatedly use chips and the Buster; check effects/music coexistence.
3. Return to the map and start another battle, for three encounters total;
   check original map music restoration and a fresh imported start each time.

`manual-testing.json` records user-reported acceptance for the fingerprints
above, separately from automated coverage and its limits. Completed source,
tests and documentation follow the standing commit/push workflow. SF3 LOSE
is the next candidate; acceptance requires matching artifact identity or its
own manual evidence.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-lose-depth-min --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-lose-depth-min-exe6-v1
```

Use fresh directories for reproduction. `validate-allocated-lfo.py`,
`check-allocation-evidence.py`, `check-packed-tones.py`, `rebuild-prior.py`,
`source-fingerprints.json`, renderer provenance and individual transcripts
retain the bounded local research evidence. ROMs/source assets stay out of Git.

The subsequent [v16 audit](nds-compatibility-audit-v16.md) integrates the
explicit looping live/minimum-depth retry, with fitting kept separate.
Its SF1 LOSE ROM/BPS and conversion parameters exactly match this accepted
artifact. Archived v15 remains unchanged; the audit adds no runtime or manual
acceptance beyond the original bounded checks and user report.
