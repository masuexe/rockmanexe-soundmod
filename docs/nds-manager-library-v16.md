# NDS manager library v16

This batch adds Star Force1 DEMPA, TRUCK and GOWADENNO, extending57 to60 songs.
All57 earlier keys, slots, selectors, track counts and finite flags remain
unchanged. Three explicit named routes use existing guarded conversions.

| Slot | Source | Selector | Tracks | Gain |
| --- | --- | --- | ---: | ---: |
| 9011 | ssr1:10 DEMPA | `sf1-dempa-delay` | 7 | +3.5dB |
| 9012 | ssr1:12 TRUCK | `sf1-truck-delay` | 8 | +3.5dB |
| 9013 | ssr1:15 GOWADENNO | `sf1-gowadenno-lfo` | 8 | +3.5dB |

All three loop and preserve singleton source-track groups. DEMPA and TRUCK use
the existing fixed-delay native pitch-LFO approximation; GOWADENNO uses the
existing native pitch-LFO route without delayed-modulation support. No fitted
attack, new filter, mixer change or native track-capacity extension is added.
The ordinary player remains eight tracks sharing ten PCM voices. Triangle
versus DS sine, shared note-reset phase, overlapping voices and release-tail
behavior retain their earlier fidelity limits.

## Reused evidence and fresh checks

Fresh named-route Gregar builds reproduce each historical candidate ROM/BPS,
converted blob and complete conversion-report values exactly. The golden ROM
CRCs are DEMPA`831E7C9F`, TRUCK`48BD254D`, GOWADENNO`7FCD4EDB`, with the same
title/virus/communication event configuration. This permits reuse of their
independent software DS references and bounded native observations.

The references match4570,4878 and6470 source notes respectively. Earlier native
NOTE observers check4174,5410 and6417 calls, with no rejected notes or held/starting
preemptions in those windows. They retain1350,1758 and2972 release-tail reuses.
These are historical exact-candidate results, not new composite allocation
measurements, every-gameplay guarantees or comparative listening acceptance.

Both real managers list60 songs without conversion on metadata load. Stable
fields of all57 previous rows match the prior manager catalog. Cold conversion
of each new song matches its source artifact on both targets. Real realtime
starts are nonzero; a fresh cache instance reparses all three disk records
without converting. Adding routes changes the checked toolchain cache key;
there is no claim that older cache entries keep their key.

The actual HTTP checks, complete-library packing and final native checks are
recorded in the local validation summary. The full60-song pool packs26393168
bytes, CRC32`A62FC891`, SHA-256
`46596f7656732c47f38b1db00bf268001057102b7a732be58290e202be40c2e3`.
It preserves distinct headers/banks, exact per-song PCM sets and reconstructs
from BPS under32MiB. This does not establish every random selection at runtime.

All29 focused tests pass without skips, including the old SF2 and new SF1 route
goldens, manager/save/reload/export/previews, conversion cache, lazy conversion,
realtime and16-track capacity guards. All three JavaScript suites pass. This is
not a new full-suite run; the earlier562-test evidence remains scoped to the
accepted16-track source revision.

An AST comparison against the accepted v15 commit also proves the converter and
catalog modules retain their previous structure after removing only these
three named routes and appended registry/count facts. This supports the stated
scope; it does not replace the fresh focused tests or native observations.

## Final experimental delivery

The normal manager export selects DEMPA at title1, TRUCK at ordinary virus21
and GOWADENNO at the separate communication scene. Other pools retain native
music. Both final ROMs are9481204 bytes:

| Target | CRC32 | SHA-256 |
| --- | --- | --- |
| Gregar | `B58B4A8B` | `49e3fa236db09103d93832a41e9b6d049a3894ba8e34bd7f69f74df2ac0f4a9a` |
| Falzar | `A8C87024` | `2110265a7d0ea1768d784965148bbe9c048f153d840d2ff58132509446869734` |

Gregar BPS SHA-256 is
`ed826a93a2f9362a48e27a0bc5ac2e172014a29bd723443a6853522e61bdbf11`.
The patch was copied to`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`;
the destination SHA-256 matches this value.

Final-ROM native observations use controlled original queues and scene hooks,
with injected PC/LR/arguments and a temporary scene descriptor, followed by
ordinary frames. Track models, loop windows, wave ownership, effect coexistence,
native restoration, restart and stop results are recorded separately from
actual battle/map/link gameplay. Existing standalone manual results do not
transfer acceptance to this composite.

Both final targets pass. DEMPA runs9987 ordinary frames to clock18774 and all21
waves; TRUCK12033 frames to22621 and all30 waves; GOWADENNO10807 frames to20316
and all26 waves. Each exceeds its two-common-period/gate horizon. Track-model
checkpoints total362/484/381 per role on each target, including the subsequent
effect/lifecycle windows. Effects100/129 are observed on PSG and133 on PCM in
separate windows. Three restore/restart/communication cycles and queued stop
pass. Six-second final-title SDL captures have peaks9754 Gregar and9757 Falzar;
these short clips do not establish full-song listening fidelity.

The user reports “可以，没问题” for exact Gregar`B58B4A8B` after the requested
checklist. Timings and gameplay were not independently observed. Requested checks are
manager visibility and previews of the three new entries; title DEMPA180 seconds;
virus TRUCK210 seconds with chips/Buster and three battle-map-battle cycles;
and communication GOWADENNO210 seconds with effects, exit/reentry and restoration.
Assess missing notes, balance, modulation, loop joins and fresh starts. No
manual Falzar, linked-session or comparative DS-fidelity result is inferred.

The manager now registers60/126 content items.62 sounding SSEQ entries and all
four streams remain unregistered. The complete catalog goal remains open.
