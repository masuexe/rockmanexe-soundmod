# NDS manager library v18

This batch adds one song from each source game, extending63 to66 entries.
All63 earlier keys, slots, selectors, track counts and finite flags remain
unchanged. Three named routes expose existing guarded singleton conversions.

| Slot | Source | Selector | Tracks | Gain |
| --- | --- | --- | ---: | ---: |
| 9017 | ssr1:29 LASTBOSS | `sf1-lastboss-delay` | 7 | +3.5dB |
| 9018 | ssr2:38 WIFI | `sf2-wifi-envelope-delay` | 8 | +3.5dB |
| 9019 | ssr3:24 BURAI | `sf3-burai-envelope-delay` | 8 | +3.5dB |

All three loop and preserve singleton source-track groups. They use the existing
fixed-delay native pitch-LFO approximation; WIFI and BURAI also enable fitted
attacks. No new filter, mixer, envelope algorithm or native-capacity extension
is added. Original-rate PCM and the ordinary eight-track/ten-PCM configuration
remain. DS sine versus native triangle, shared phase/delay, envelope fitting,
overlapping notes, PCM8 resolution and release-tail behavior retain their
earlier listening limits. Source-specific acceptance is not borrowed from
similarly named songs in other games.

## Identity and regression

Fresh named-route builds reproduce each earlier primary candidate ROM/BPS,
converted blob and complete conversion-report values exactly: LASTBOSS Gregar
CRC`2859C9A7`, WIFI`AB504353`, BURAI`370026F7`, using the same three-event
configuration. This permits reuse of their independent software DS references
and bounded native observations, without transferring manual acceptance.

Reference note matches are4150/5777/4632 respectively. Earlier native NOTE
observers check5577/3939/2558 calls with no rejections or held/starting
preemptions in those windows; they retain1607/1664/891 release-tail reuses.
These are exact standalone-candidate observations, not new exhaustive composite
allocation measurements or every-gameplay/fidelity guarantees.

Both managers list66 songs with zero conversion on metadata load, retain stable
fields for all63 old entries, and prepare three new songs from their own pinned
source families. Cold conversions match earlier blobs/reports on both targets;
real realtime starts are nonzero and a fresh cache instance reparses all three
disk entries without conversion. New routes change the toolchain cache key;
preservation of older disk hits is not claimed.

The HTTP and final native results are recorded in the local validation summary.
All66 songs pack27112856 bytes, CRC32`2813FD49`, SHA-256
`efc9d45285721dc97f0e3aa42430ee4e5421262287e57d755e191820d8159d7a`,
with isolated headers/banks, exact per-song PCM sets and checked BPS reconstruction
under32MiB. This is not evidence for every random runtime selection.

All31 focused tests pass without skips: old/new candidate goldens, manager
save/reload/export/previews, cache, lazy conversion, realtime and16-track guards.
All three JavaScript suites pass. An AST comparison against accepted v17 proves
the converter/catalog structures retain their earlier form after removing only
these three routes and appended registry/count facts. This is not a fresh full
suite; earlier562-test evidence retains its original source-revision scope.

## Final experiment

The normal manager export selects SF1 LASTBOSS at title1, SF3 BURAI at ordinary
virus21 and SF2 WIFI at the separate communication scene. Other pools retain
native music. Both final ROMs are9771764 bytes:

| Target | CRC32 | SHA-256 |
| --- | --- | --- |
| Gregar | `C9F14777` | `ee531ac65f40968c7a0bfc9dd7c060afa79e544976be17d43a43526cbc8628dc` |
| Falzar | `951AC44A` | `b54ed6d893aefbb4c1aaa91cacfd82337e1587bc26b8df3a455cec24816b99a3` |

Gregar BPS SHA-256 is
`9d423c0bad8e61d0fd7b215463f7772f9121863c0e06a722c24bfa4ab5a1fa1c`.
The patch was copied to`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`;
the destination SHA-256 matches this value.

Final native checks use original queue/scene helpers with controlled PC/LR,
arguments and a temporary descriptor, followed by ordinary-frame track-model,
loop and wave observations, effect coexistence, restoration, restart and stop.
They are distinct from actual battle/map/link gameplay and manual listening.
Exact final results and delivery are recorded in the local validation summary.

Both final targets pass. LASTBOSS runs15108 ordinary frames to clock31624 and
all23 waves; BURAI5982 frames to11644 and all22 waves; WIFI7423 frames to14943
and all24 waves. Each exceeds its two-common-period/gate horizon. Track-model
checkpoints total533/282/268 per role on each target, including later effect
and lifecycle windows. Effects100/129 are observed on PSG and133 on PCM in
separate windows; three restore/restart/communication cycles and queued stop
pass. Six-second final-title SDL peaks are9185 Gregar and9183 Falzar; these
clips do not establish full-song listening fidelity.

The user reports “可以，没问题” for exact Gregar`C9F14777` after the requested
checklist. Timings and gameplay were not independently observed. Requested checks are
manager visibility/previews of all three entries; title SF1 LASTBOSS270 seconds;
virus SF3 BURAI120 seconds with chips/Buster and three battle-map-battle cycles;
and communication SF2 WIFI150 seconds with effects, exit/reentry and restoration.
Assess missing notes, balance, modulation, seams and fresh starts. No manual
Falzar coverage, linked sessions or comparative DS fidelity is inferred.

The library now registers66/126 content items.56 sounding SSEQ entries and all
four streams remain unregistered. The complete catalog goal remains open.
