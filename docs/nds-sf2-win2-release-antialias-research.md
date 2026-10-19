# Star Force 2 WIN2: finite release snapshots with filtered PCM

The explicit `sf2-win2-release-antialias` experiment converts previously blocked
SF2 `BGM_WIN2` (SSEQ 31). Its single D3 command initializes track 3's release to
120 before its first note at tick 0. The instrument's default release is 98;
ignoring the command would give all eleven notes on that track the wrong tail.
The existing native conversion maps release 120 to 177 rather than default 237.

## Scope

`finite_release_support=True` requires finite singleton tracks, fixed tempo,
closed gates by each source END, no native LFO and no fitted attacks. It accepts
D3 initialization only before the first note in execution order on each track,
rejecting later changes even at the same tick. D0–D2 remain unsupported in this
mode. Existing instrument attacks must be instant. Per-note ADSR snapshots
reuse independent rhythm-bank voice contexts, while PCM caching stays separate
from envelope identity. Existing decay/sustain/release quantization remains an
approximation to DS timing; this does not fit a new release curve.

The builder explicitly opts into this mode and offline per-key filtering.
Default compiler behavior, the production manager and mixer are unchanged.
The v13 batch audit still uses its original routing and counts; this standalone
success does not silently update its 54-song snapshot or add manual acceptance.

## Artifact

Directory: `out/nds-research/sf2-win2-release-antialias-exe6-v1/`.
ROM SHA-256: `5f624d8cc8483812d5e702ac8c233a394e24b1e3bae6c1b6d3978cdd72744913`.

Six source tracks (0, 1, 2, 3, 4, 6), all 67 notes and nine decoded source waves
remain. Filtering prepares 32 waves (228,828 PCM8 bytes); seven voice contexts
retain note-on envelopes. The ROM appends 246,484 bytes to the base and uses
+3.5 dB, ten PCM channels and the unchanged 10,512 Hz mixer. Title event 1,
virus-battle event 21 and the communication scene trigger play slot 474.

| Source track | Last gate closes | Source END |
| --- | ---: | ---: |
| 0 | 168 | 168 |
| 1 | 168 | 168 |
| 2 | 192 | 192 |
| 3 | 228 | 240 |
| 4 | 168 | 168 |
| 6 | 192 | 192 |

This cue lasts roughly two seconds and ends naturally; it is not looped.

## Validation

Independent SSEQPlayer software-reference logs match all 67 notes, 35 controls,
nine source PCM decodes, 67 ADSR snapshots and 5,187 per-voice envelope updates.
The reference validator now handles finite envelope schedules without attempting
to unfold a nonexistent loop. Native envelope validation accepts the separate
release-snapshot manifest marker without labelling it fitted-attack support.

All 67 relocated note tones and 32 prepared-wave headers/bytes pass checks.
Natural playback reaches clock 242 in 107 observed frames and plays all 32
prepared waves. A separate 960-frame envelope window checks 702 native envelope
steps and observes 266 release states. Track 3 specifically has 111 allocated
channel observations, all with native release 177, including eleven observed
release states. A natural completion probe verifies each
track's FINE, no clock restart and empty imported channels for the final 600
frames. The 15-second emulator recording has exactly zero samples throughout
its final five seconds.

Controlled helper probes verify two effects, ordinary/communication dispatch,
queued stop, native-song restoration and three restart cycles. These use
injected helper calls and do not establish actual results-screen transitions,
a communication match or a two-peer test. On 2026-10-19 the user reported
“没问题” after the requested title ending and ten-second wait, battle effects,
and three battle/map/restart cycles, accepting this exact ROM. This is
user-reported checklist acceptance without an independent timing trace;
no separate two-peer or comparative preference is inferred. The bounded
automated coverage above remains unchanged. See `manual-testing.json` and
`manual-testing.txt`.

All 260 regression tests pass, including the release-tone mapping, rejected
late/other-ADSR/fitted combinations and independent finite-envelope checks.
All 32 previously accepted ROM/BPS pairs and both unaccepted WIN2 controls
rebuild identically. The regression log and these rebuild results are recorded
in `validation-summary.json`. The comparison page is `comparison/listen.html`:
software DS reference versus actual mGBA output, normalized over equal-duration
clips, not sample-aligned or an original-hardware comparison.

## Reproduce

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds \
  --base ../roms/exe6.gba --song sf2-win2-release-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-win2-release-antialias-exe6-v1
```

Use a fresh output directory for repeated builds or validation. Full commands,
source fingerprints and bounded native results remain beside the artifact.
The next step is to integrate this accepted guarded
finite-release route into a new compatibility audit, preserving v13 as history.
