# NDS manager library v10: forty-one registered songs

This batch appends two independently accepted configurations, preserving the
first39 tuples, slots8954–8992, gains, track counts and finite flags. Changes
are registry data and count/roster fixtures. Converter, DSP, native driver/mixer,
relocator, realtime/cache, browser runtime and project schema remain unchanged.

| Slot | Song | Selector | Tracks | Gain | Playback |
| --- | --- | --- | ---: | ---: | --- |
| 8993 | SF3 FRIEND | `sf3-friend-envelope` | 8 | +3.5dB | Loops |
| 8994 | SF1 SABISHI | `sf1-sabishi-variable-late-envelope` | 8 | +3.5dB | Loops |

[FRIEND](nds-envelope-research.md) retains its accepted note-on release snapshots
115/120 and native triangle pitch-LFO approximation, with23 original PCM8 waves.
[SF1 SABISHI](nds-sf1-sabishi-variable-late-envelope-research.md) retains six
source tempos40/65/70/75/90/100, track3 late enable at tick1440, fitted attack100
mapped to74, and14 raw waves. No filtering is added to these modulation modes.
The separate SF3 SABISHI sequence remains outside this batch; its differing
source schedule and acceptance cannot substitute for SF1 by matching song name.

## Source identity and diagnostics

Both fresh Falzar preparations exactly match their accepted compiled blobs and
parsed dependencies. SABISHI's conversion report matches strictly. FRIEND's
older report lacks empty `long_note_loop_carries`/`voice_context_splits` and eight
`gate_checked_until_ticks` diagnostics. Those values are pinned to8496 for
tracks0–6 and8519 for track7. Removing only those ten additions restores exact
report equality; no operative difference is allowed. The original nonmatching
strict-report preflight stays separate from the successful reconciliation.
Eight negative report mutations across both candidates are rejected.

All41 blobs and dependencies match accepted standalone artifacts.37 conversion
reports match strictly; four legacy reports use explicitly checked diagnostic/
wording reconciliation (BATTLE, KAICYOU, NESSIE and now FRIEND). Original accepted
ROM/manual fingerprints and BPS reconstruction are checked. This reuses prior
independent source/DS and per-song native evidence under those identities,
without a new DS render, expanded source scan or transferred manual acceptance.

The toolchain identity remains unchanged; all39 existing Falzar cache entries
hit disk with zero conversions. Metadata load converts nothing. The two new
configurations prepare separately; all41 then use normal manager paths. A v9
saved project preserves keys, slots and playback pools. Expanding the table to
8995 changes ROM bytes; earlier exact-ROM acceptance does not transfer.

## Regression and integration

Fresh34-case manager/cache/lazy-preview/realtime regression and three JavaScript
suites pass without skips. The550-case full suite is reused from the cache-scope
experiment under exact unchanged audio/runtime/config/test identities except
registry data and two roster/count fixtures. Removing SONGS/TRACK_COUNTS restores
the prior whole catalog AST. This is not a fresh550-case run.

All41 real agbplay starts produce nonzero stereo. A separate Falzar41-song pool
packs23,298,400 bytes and checks distinct headers/tone banks, exact per-song PCM,
safe exact-content resource
sharing, BPS reconstruction and the32MiB bound. Packing does not establish every
random runtime selection or manual acceptance. Actual HTTP checks cover41 entries,
byte-equal Falzar export and three-second mGBA previews of both additions. Repeated
previews reuse cached jobs and preserve project pools. No manual Falzar gameplay
acceptance is inferred.

## Retained sound and evidence limits

FRIEND's older native envelope evidence is bounded to1800 audio updates, with
13102 step comparisons and5560 release observations. It does not establish
complete loops or equal source/target sound. The new composite loop/lifecycle
observation remains separate from that older envelope/model trace.

SABISHI's prior native trace covers two common cycles, all14 waves,1400 observed
NOTE allocations without rejection and65584 track-LFO comparisons. Successful
allocation does not exclude shortened release tails. Its source supplies no
carried-positive-depth update coverage; no new such claim is made. The historical
344-case suite had one external-input skip; this history remains distinct from
the current fresh34-case and reused550-case no-skip evidence.

Triangle versus sine, shared LFO phase/note resets, fitted ADSR/onset and release
approximation, original PCM aliasing, PCM8, ten voices/10512Hz and tempo rounding
remain. No new full NOTE-allocation, waveform-fidelity or zero-preemption proof
is added. All previous per-song limits, including AJITO's fourteen held/starting
preemptions, STUDIO soft-note quantization, CHANGE's four preemptions and SF3
DEMPAJIKEN's three rejected NOTE calls in old bounded traces, remain.

## Exact delivery and requested review

- Gregar ROM CRC32: `6C7BFA04`; size9111888 bytes.
- ROM SHA-256: `00035de52ac4de5b2e9f093293ef7706ff15333b4be5b34aca1afc5777984e54`.
- BPS SHA-256: `01bc56fb09534e33c26ab16149270d0f08a3a626a1144ee13fad2d9dab12656e`.
- Prepared41-song Falzar manager: `http://127.0.0.1:8787/`.

The Gregar patch selects FRIEND for title and SF1 SABISHI for ordinary virus and
communication battle requests. Other pools retain native music. Requested manual
checks:41-song roster/two previews and save/reload/export; title FRIEND at least180
seconds and virus SABISHI at least180 seconds, including release tails, late
enable, tempo changes, gradual onsets and joins; chip/Buster effects and three
battle→map→battle cycles. The user reports these checks passed. Comparative DS fidelity,
arbitrary exports/roles, linked play/rematches and manual Falzar remain separate.

The final validated BPS overwrites `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`
with byte/SHA-256 equality recorded in the delivery record. Delivery is transport
only. Records live in `out/nds-research/nds-manager-library-v10/` and
`out/nds-research/nds-manager-library-exe6-v10/`; ROMs/assets/caches stay out of Git.
Archived v10–v38 compatibility audits remain unchanged historical evidence.

## Remaining source investigation

The metadata shortlist now has13 unregistered source sequences with at least
one accepted standalone record. This is not13 newly verified manager songs.
Future entries still need exact configuration/audio/report identity and scope
review. Alternative SATELLITE variants count once, and its filtered revision's
limited missing-accent acceptance is not expanded by this inventory.

## Final native verification

The exact composite passes15,010 ordinary frames between controlled calls.
FRIEND reaches clock9217, beyond entry3888 plus two2304-tick periods and the
extended track7 gate diagnostic8519. SABISHI reaches11141, beyond entry4512
plus two3072-tick periods. All23/14 waves are observed with ownership by the
active music tracks; these two relocated banks share no physical wave addresses.
Both eight-track looping headers retain statusFF in their checked windows.

Effects100/129, three controlled native-restore/title/battle/communication-restart
cycles and queued stop pass, with no imported tails after native restoration.
The fixture injects PC/LR/arguments and disposable scene RAM between ordinary
frames. It does not establish actual battle/map/linked-play/rematch outcomes,
inspect every NOTE allocation or revalidate all LFO/envelope steps. The longer
requested listening and actual gameplay remain separate manual checks; their
user-reported acceptance is recorded below.

## Exact-ROM user acceptance

The user reported “测试没有问题，可以推送并继续推进。” in response to all three
requested checks for ROM6C7BFA04. ROM, BPS and the Windows test copy were verified
again when recording acceptance. The41-song roster and both new previews,
save/reload/export, title FRIEND and virus-battle SF1 SABISHI for at least180
seconds each including release tails/late enable/tempo/onset/loop windows,
chips/Buster and three battle→map→battle cycles with native restoration and
fresh starts are recorded as user-reported passes.

These are user reports, not independently timed or observed checks. They do
not establish comparative DS fidelity, zero-note-loss, arbitrary exports/roles,
linked play/rematches or manual Falzar gameplay. Original-PCM, native triangle
LFO/shared phase, fitted ADSR and release/tempo quantization, voice-budget and
all previous per-song limits remain. Fresh34-case focused regression and reused
550-case full-suite evidence stay separately identified. Acceptance recording
changes documentation only; source tests were not rerun for this step.
