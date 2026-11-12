# NDS manager library v19

This batch adds SF1 YUMENOSHIMA/KAKUSHI and SF2 FRIEND, extending66 to69 entries.
All66 earlier keys, slots, selectors, track counts and finite flags remain
unchanged. Three named routes use the existing guarded singleton conversions.

| Slot | Source | Selector | Tracks | Gain |
| --- | --- | --- | ---: | ---: |
| 9020 | ssr1:8 YUMENOSHIMA | `sf1-yumenoshima-lfo` | 8 | +3.5dB |
| 9021 | ssr1:19 KAKUSHI | `sf1-kakushi-lfo` | 8 | +3.5dB |
| 9022 | ssr2:14 FRIEND | `sf2-friend-envelope` | 8 | +3.5dB |

All three loop and retain singleton source-track groups. FRIEND's source tracks
are0–6 and9, mapped to eight native tracks without dropping source9. An initial
test incorrectly expected0–7; its fixture was corrected without changing the
conversion or ROM. All three use existing native pitch LFO without the delayed
modulation extension. FRIEND also enables fitted attacks. No new filter, mixer,
envelope algorithm or native-capacity extension is added. The ordinary eight
tracks still share ten PCM voices. Shared LFO phase, sine/triangle differences,
envelope fitting, overlapping voices and release tails retain earlier limits.

## Recorded allocation limits

These candidates have actual observed allocation losses. The exact standalone
title traces record:

| Song | NOTE calls | Rejected notes | Held/starting preemptions | Release-tail reuses |
| --- | ---: | ---: | ---: | ---: |
| YUMENOSHIMA | 5483 | 6 | 25 | 1986 |
| KAKUSHI | 8761 | 0 | 16 | 2614 |
| FRIEND | 3113 | 0 | 225 | 1580 |

Those results are not asserted absent or inaudible. Authored source priority does
not establish musical importance. FRIEND in particular needs listening for lost
layers/notes and whether overlapping voices sound acceptable. Track-model and
wave-coverage passes do not prove every note becomes audible. These historical
exact-candidate traces are not new exhaustive composite allocation measurements
or guarantees for all gameplay with effects.

## Identity and regression

Fresh named-route builds reproduce each candidate ROM/BPS, converted blob and
complete conversion-report values exactly: YUMENOSHIMA Gregar CRC`B9ACC156`,
KAKUSHI`8F1D7055`, FRIEND`21D3206C`, under the same three-event configuration.
This permits reuse of independent software DS references and bounded native
evidence; reference note matches are4800/6673/7561. The existing reference,
allocation and natural-playback reports were checked complete and their native
ROM identities match the byte-equal candidates. Manual acceptance does not
transfer to the new composite.

Both real managers list69 songs with zero conversion on metadata load, preserve
stable fields of all66 old entries, and prepare the three from their own source
families. Cold conversions match earlier blobs/reports on both targets. Real
realtime starts are nonzero; fresh cache instances reparse all three disk records
without conversion. New routes change the toolchain cache key; retention of
older disk hits is not claimed.

Actual HTTP checks list69 entries, export byte-identical Falzar ROM/BPS, capture
three nonzero three-second mGBA previews, reuse jobs and preserve project pools.
All69 songs pack27666904 bytes, CRC32`CE93E74F`, SHA-256
`fdff06c92e9bd6c7b665738cef9e98d5cce2d590397697b9da22a5de6ed4b7ec`,
with isolated headers/banks, exact PCM sets and BPS reconstruction under32MiB.
This is packing evidence, not every random selection at runtime.

All32 focused tests pass without skips after correcting the sparse-track
fixture, as do all three JavaScript suites. The final native results are recorded
in the local validation summary. An AST comparison against accepted v18 preserves the old
converter/catalog structures after removing only these three routes and
appended registry/count facts. This is not a new full-suite run; earlier562-test
evidence retains its original source-revision scope.

## Final experiment

The normal manager export selects SF1 YUMENOSHIMA at title1, SF2 FRIEND at
ordinary virus21 and SF1 KAKUSHI at the separate communication scene. Other
pools retain native music. Both final ROMs are9787456 bytes:

| Target | CRC32 | SHA-256 |
| --- | --- | --- |
| Gregar | `7706BEA1` | `24f19988075a0cdedb0af0116e9f3f897650c5428b04e4f4a61deb139a2acf10` |
| Falzar | `74579CF9` | `249107693285e930eb2a536ad9675999734ad492c06621f08859c62211754bb1` |

Gregar BPS SHA-256 is
`737909fd431ce8ea584bec1945acf6fbe635038f229ac238fdd466b6ae2c8729`.
The patch was copied to`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`;
the destination SHA-256 matches this value.

Final native checks use original queue/scene helpers with controlled PC/LR,
arguments and a temporary descriptor, followed by ordinary-frame track-model,
loop and wave checks, effects, restoration, restart and stop. These are distinct
from actual battle/map/link gameplay and manual listening.

Both final targets pass their structural/runtime checks. YUMENOSHIMA runs12586
ordinary frames to clock18459 and all33 waves; FRIEND4595 frames to8821 and
all27 waves; KAKUSHI18386 frames to37016 and all36 waves. Each exceeds its
two-common-period/gate horizon. Track-model checkpoints total449/235/634 per
role on each target, including later effect/lifecycle windows. Effects100/129
are observed on PSG and133 on PCM in separate windows; three restore/restart/
communication cycles and queued stop pass. Six-second final-title SDL peaks
are11413 Gregar and11411 Falzar. None of these checks establishes that the
recorded note losses/preemptions are inaudible or acceptable.

The user reports “可以，没问题” for exact Gregar`7706BEA1` after the requested
checklist. This records acceptance of the requested checks, not proof of zero
losses or their inaudibility in every state. Timings/gameplay were not independently
observed. Requested checks are
manager visibility/previews of all three entries; title YUMENOSHIMA240 seconds;
virus FRIEND90 seconds with chips/Buster and three battle-map-battle cycles;
and communication KAKUSHI330 seconds with effects, exit/reentry and restoration.
Assess missing notes/layers, balance, modulation, seams and fresh starts. No
manual Falzar, linked-session, comparative DS fidelity or inaudibility of the
recorded allocation losses is inferred.

The library now registers69/126 content items.53 sounding SSEQ entries and all
four streams remain unregistered. The full catalog goal remains open.
