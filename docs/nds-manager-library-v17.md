# NDS manager library v17

This batch adds Star Force2 ROOM, COMICAL and KANDO, extending60 to63 songs.
All60 earlier keys, slots, selectors, track counts and finite flags remain
unchanged. Three named routes expose existing looping singleton conversions
with offline antialias filtering.

| Slot | Source | Selector | Tracks | Gain |
| --- | --- | --- | ---: | ---: |
| 9014 | ssr2:4 ROOM | `sf2-room-antialias` | 6 | +3.5dB |
| 9015 | ssr2:21 COMICAL | `sf2-comical-antialias` | 8 | +3.5dB |
| 9016 | ssr2:24 KANDO | `sf2-kando-antialias` | 7 | +3.5dB |

All three loop and preserve singleton source-track groups. They use the existing
per-key PCM8 preparation,10512Hz mixing rate, periodic loop guard and compensated
tuning. The admitted route retains downward bends and excludes upward bends or
modulation. No native pitch-LFO or fitted-attack option is enabled. The mixer,
filter algorithm, project schema and ordinary eight-track/ten-PCM configuration
remain unchanged; the16-track RAM extension is not enabled.

The existing filter reports859 PCM8-clamped values across456786 prepared output
samples for ROOM,831/591359 for COMICAL and1862/588497 for KANDO. These aggregates
cover all prepared key variants, not the fraction of a song or runtime mix that
clips. Clamps, PCM8 quantization and native tuning/mix approximation remain
listening limits. No normalization hides or removes them in this batch.

## Identity and regression

Fresh named-route builds exactly reproduce the earlier filtered candidate ROMs,
BPS files, converted blobs and complete conversion-report values. The candidate
Gregar CRCs are ROOM`A9FF0FF4`, COMICAL`1FD0E6D4`, KANDO`557C2017`, with the same
title/virus/communication event configuration. Source-specific acceptance is
not borrowed from similarly named songs in other games.

Byte identity permits reuse of each independent software DS reference and
bounded native observation. References match5407/5312/5960 source notes. Earlier
native NOTE observers check946/1399/2163 calls with no rejected notes or
held/starting preemptions in those windows, retaining485/489/1172 release-tail
reuses. These are exact standalone-candidate results, not exhaustive composite
allocation measurements or every-gameplay/fidelity guarantees.

Both managers list63 songs with zero conversions on metadata load. All60 earlier
rows preserve stable fields. Three cold preparations match their own source
artifacts on both targets; real realtime starts are nonzero and a fresh cache
instance reloads all three disk entries without conversion. Adding named routes
changes the toolchain cache key once; old disk-hit preservation is not claimed.

Actual HTTP checks list63 entries, export byte-identical Falzar ROM/BPS, capture
three nonzero three-second mGBA previews, reuse jobs and preserve project pools.
The63-song pool also packs26457560 bytes, CRC32`1C17266C`, SHA-256
`e11153109372862ea3dba4acf028e68719bb62aef7636f21d9bea2c01e208c3d`,
with isolated headers/banks, exact per-song PCM sets and BPS reconstruction.
This is packing evidence, not every random selection at runtime.

All30 focused tests pass without skips, including old SF1/SF2 routes, three new
filtered goldens, manager save/reload/export/previews, cache, lazy conversion,
realtime and16-track guards. All three JavaScript suites pass. An AST comparison
against accepted v16 preserves the converter/catalog structures after removing
only these exact three routes and appended registry/count facts. This is not
a fresh full-suite run; earlier562-test evidence keeps its original scope.

## Final experiment

The normal manager export selects ROOM at title1, COMICAL at ordinary virus21
and KANDO at the separate communication scene. Other pools retain native music.
Both final ROMs are9871340 bytes:

| Target | CRC32 | SHA-256 |
| --- | --- | --- |
| Gregar | `02DF8781` | `928f81c5b6073378946e061d587d829460e34b7f646586124218907c3edb6055` |
| Falzar | `BC18D27E` | `057518a10468988698320e085ca982f5cb51458afc5259784558f90017cd1139` |

Gregar BPS SHA-256 is
`5354bb0481d911cc26b006f1e0a948a1f56279c4c13a9e7672e8aa082a4e04c3`.
The patch was copied to`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`;
the destination SHA-256 matches this value.

The final native checks and delivery are recorded in the local validation
summary. Original queue/scene helpers use controlled PC/LR/arguments and a
temporary scene descriptor, followed by ordinary-frame track models, loop and
wave observations, effects, restoration, restart and stop. These are separate
from actual battle/map/link gameplay. Earlier candidate evidence does not
establish acceptance of this new composite.

Both final targets pass. ROOM runs2005 ordinary frames to clock3367 and all80
prepared waves; COMICAL2933 frames to5513 and all101; KANDO4040 frames to8132
and all84. Each exceeds its two-common-period/gate horizon. Track-model
checkpoints total96/180/156 per role on each target, including later effect
and lifecycle windows. Effects100/129 are observed on PSG and133 on PCM in
separate windows; three restore/restart/communication cycles and queued stop
pass. Six-second final-title SDL peaks are13281 Gregar and13277 Falzar; these
clips do not establish full-song listening fidelity.

The user reports “可以，没问题” for exact Gregar`02DF8781` after the requested
checklist. Timings and gameplay were not independently observed. Requested checks are
manager visibility and previews of the three entries; title ROOM90 seconds;
virus COMICAL90 seconds with chips/Buster and three battle-map-battle cycles;
and communication KANDO90 seconds with effects, exit/reentry and restoration.
Assess missing notes, balance, distortion, seams and fresh starts. Manual
Falzar coverage, linked sessions and comparative DS fidelity are not inferred.

The library now registers63/126 content items.59 sounding SSEQ entries and all
four streams remain unregistered. The full catalog goal remains open.
