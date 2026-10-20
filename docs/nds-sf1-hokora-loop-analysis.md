# Star Force 1 HOKORA: empty-stack LOOPEND analysis

The v14 audit reports `SSEQ loop end without start` for SF1 `BGM20HOKORA`
(SSEQ 20). This investigation resolves that source-trace error, but does not
produce a new GBA ROM or claim the song is convertible yet. The artifact is
`out/nds-research/sf1-hokora-loop-analysis-v1/`.

## Executed source behavior

The original failure occurs on source track 6 at tick 1536, SSEQ data offset
2500 (`0x9c4`). Its eight subroutine calls have returned, so the loop/call stack
is empty. The command is FC/LOOPEND, immediately followed by FF/END at offset
2501 (`0x9c5`). This track has no loop-start command to return to.

The pinned kode54/SSEQPlayer core tests for a loop frame before LOOPEND can
jump. When the stack is empty it leaves the cursor after FC. An independent
120-second execution with observation-only flow logging confirms exactly one
empty-stack FC on track 6, followed by END at the same tick. There are no later
track-6 notes. The original and instrumented renderers produce byte-identical
PCM and all existing reference logs; their LOOPEND implementation is unchanged.
This is software-reference evidence, not a DS hardware or emulator capture.

The corrected Python tracer follows that observed fallthrough only for an
empty stack and records `loop_end_fallthrough: "empty_stack"` on the executed
action. It retains the command and timestamp; it does not discard a phrase,
construct a loop start or repeat track 6. A LOOPEND atop an active call frame
still fails as outside the supported subset. Return, stack-depth and zero-time
cycle guards remain; counted loops retain their existing behavior.

## Actual track structure

| Source track | Termination | Loop start tick | Period / END |
| --- | --- | ---: | ---: |
| 0 | Loop | 1572 | 3072 |
| 1 | Loop | 1536 | 3072 |
| 2 | Loop | 0 | 3072 |
| 3 | Loop | 0 | 1536 |
| 4 | Loop | 0 | 1536 |
| 5 | Loop | 0 | 1536 |
| 6 | END | — | 1536 |

Track 6 contains 256 notes and plays once; its final gate closes at tick
1534, before its source END at 1536. The trace contains seven tracks,
1,108 note events and ten original ADPCM waves; every used instrument has an
instant attack. Active delayed pitch modulation uses depth/speed/delay
combinations 3/28/14 and 8/31/96. There is no source pitch bend or portamento
and no ADSR override. The 120-second independent logs match all 4,848 unfolded
notes and 242 observed controls, plus exact PCM16 decoding of all ten waves.
Every looping track is observed beyond its intro and two complete periods.

## Remaining conversion limits

With native pitch LFO or the existing delayed-LFO approximation, the converter
now correctly reaches `Merged experiment requires looping source tracks`.
Without LFO support it first rejects executed modulation (CA). The source
analysis problem is resolved; conversion is still blocked.

There are two separate structures to support before a faithful native build:
a finite one-shot track alongside looping tracks, and commensurate 1536/3072
loop periods. Neither is implemented by this tracer correction. Dropping track
6, turning its END into GOTO, or treating all periods as 1536 would alter the
score. The existing offline-filter path also still excludes active modulation;
this work does not change that restriction.

A next experiment can preserve the finite track's original END, validate its
last gates and release tails, and explicitly unfold shorter looping tracks to
a shared 3072-tick cycle while preserving each intro. It must prove no track-6
notes occur on subsequent loops and compare all notes/controllers with the DS
reference before natural native playback, effect/lifecycle probes and manual
listening. This is a proposed capability, not an accepted ROM.

## Verification and provenance

`strict-failure.json` retains the original failed action and empty stack.
`strict-reproduction.json` independently reproduces it from pre-fix Git commit
`509d5b6` using the saved `prior-strict-tracer.py`.
`diagnostic-trace.json` is the initial research-only fallthrough trial;
`corrected-trace.json` records the final production tracer's result.
`reference-player/build.json` pins the copied core, renderer and compiler;
`reference-flow/flow.csv` retains actual stack-depth/control-flow observations.
`analysis-validation.json` checks the independent schedules, original PCM,
reference equivalence and still-enforced converter blockers.
`current-route-diagnostic.json` confirms both primary and filtered routes remain
conversion-blocked; no route reaches packing.

A source-only scope check covers all 132 slots: 126 prior successful analyses
have identical features, five empty slots stay empty, and only SF1 HOKORA
changes from analysis failure to a completed trace. This does not rerun packing
or update the archived compatibility report.

Regression tests cover a bare empty-stack LOOPEND, a completed counted loop
with subroutine returns followed by an extra LOOPEND, preserved invalid-path
guards, and the actual local HOKORA track structure. All 269 regression tests
pass; 33 accepted ROM/BPS pairs and two unaccepted controls rebuild identically. The full logs and exact prior-build results
are recorded in `validation-summary.json`.
Archived v10–v14 reports and their counts remain unchanged; this investigation
does not retrospectively replace v14's analysis status or acceptance evidence.

The subsequent [mixed-delay experiment](nds-sf1-hokora-mixed-delay-research.md)
now implements the proposed bounded mixed structure, plus explicit weak-LFO
quantization discovered during conversion. Its original-song native tests
cover two common cycles and preserve the finite track's END. On 2026-10-20 the
user reported that this later exact ROM passed its requested listening/gameplay
checks; the source-only investigation above remains separate.
