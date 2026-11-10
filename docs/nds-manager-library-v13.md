# NDS manager library v13: forty-seven registered songs

This batch appends two accepted SF1 configurations. It preserves the first45
entries, slots8954–8998, gains, track counts and finite flags. Only registry
data and two count/roster test fixtures change. The converter, DSP, native
mixer/driver, relocator, realtime/cache, browser runtime and project schema
remain unchanged.

| Slot | Song | Selector | Tracks | Gain | Playback |
| --- | --- | --- | ---: | ---: | --- |
| 8999 | SF1 HOKORA | `sf1-hokora-mixed-delay` | 7 | +3.5dB | Six loop, one ends once |
| 9000 | SF1 PLANETARIUM | `sf1-planetarium-delay` | 8 | +3.5dB | Loops with carried ties |

[HOKORA](nds-sf1-hokora-mixed-delay-research.md) keeps source track6 as a one-shot
track. It closes its last gate at1534 and ends at1536. It never receives GOTO.
The six other tracks use common entry4644 and period3072. Twelve raw PCM8 wave
contexts come from ten source waves. The whole song remains a looping library
entry; its embedded finite track does not make the complete song finite.

[PLANETARIUM](nds-planetarium-research.md) keeps all eight tracks,29 prepared
wave/root contexts, entry7968 and period7008. Track7 alias126 retains source
key53 with a384-tick gate. Its notes cross the entry and later GOTOs:7776–8160,
14784–15168 and21792–22176. The existing TIE/EOT commands must preserve the held
voice across the boundary and release it afterward. No new conversion mode or
filtering is added.

## Source identity and cache proof

Fresh Falzar preparations exactly match both accepted compiled blobs and
parsed dependencies. HOKORA's conversion report matches strictly. PLANETARIUM
only adds an empty `voice_context_splits` diagnostic. Removing that one field
restores complete report equality. Its nonempty `long_note_loop_carries`, gate
checks and all operative fields remain exact. The initial strict-report result
is retained separately from the successful reconciliation. Eight negative
report mutations are rejected.

All47 blobs/dependencies match their own accepted standalone artifacts. Forty
reports match strictly; seven have explicit diagnostic/wording reconciliation:
the previous six plus PLANETARIUM's one empty field. Accepted ROM/manual hashes
and BPS reconstruction are verified. Prior independent source/DS and per-song
native evidence is reused under these identities. No new DS render, source scan
or manual acceptance transfer occurs.

The audio toolchain identity stays unchanged. All45 old Falzar entries hit disk
with zero conversions before the registry run accesses the two new entries.
Their fresh preflight cache is preserved. Metadata load converts nothing. All47
registry entries then use checked cache data. A v12 project keeps its song keys,
slots8997/8998 and pools. The expanded9001-entry table changes its ROM bytes;
old exact-ROM acceptance does not transfer.

## Regression and integration

Fresh34-case manager/cache/lazy-preview/realtime regression and three JavaScript
suites pass without skips. The prior550-case full suite is reused under exact
unchanged audio/runtime/config/test identities except registry and two count/
roster fixtures. Removing SONGS/TRACK_COUNTS restores the prior catalog AST.
This is not a fresh550-case run.

All47 real agbplay starts produce nonzero stereo. A separate Falzar47-song pool
packs24,445,028 bytes, below32MiB. It verifies distinct headers/tone banks,
per-song PCM sets, safe exact-content sharing and BPS reconstruction. Packing
does not establish every random runtime selection or manual acceptance. Actual
HTTP checks cover47 entries, byte-equal Falzar export and three-second mGBA
previews of both additions. Repeated previews reuse jobs without changing pools.
These automatic Falzar checks do not establish manual Falzar gameplay.

## Retained limits

HOKORA retains the explicit weak-LFO approximation and its source/target phase
bounds. Native triangle versus DS sine, shared phase, note-on resets, fixed
modulation delay, raw-PCM aliasing, PCM8/envelope/tempo quantization and ten
versus sixteen voices remain. PLANETARIUM's older carried-note native probe
used a synthetic one-track sequence. Its original full-score loop evidence
was not established by that probe; new composite observations remain separate.

No new exhaustive NOTE-allocation, all-LFO/envelope-step, waveform-fidelity or
zero-preemption proof is claimed. All previous per-song limits remain, including
AJITO held/starting preemptions, STUDIO soft-note quantization, CHANGE's four
preemptions and SF3 DEMPAJIKEN's rejected NOTE calls in prior bounded traces.

## Exact delivery and manual request

- Gregar ROM CRC32: `2F9772D8`; size9164024 bytes.
- ROM SHA-256: `cb60163a0d0a8a7dcae2d48d3e407c118590dacef8e887e66c6ffa910009a2c5`.
- BPS SHA-256: `660388a42ee75bf594cadbeb2975e5c618b0369371fc3747c06f640a7b8f45b7`.
- Prepared47-song Falzar review: `http://127.0.0.1:8790/`.

The Gregar patch selects HOKORA for title and PLANETARIUM for ordinary virus
and communication battle requests. Other pools retain native music. Manual
acceptance is recorded below. The requested checks covered47-song visibility, both new previews and save/
reload/export. Listen to title HOKORA for at least180 seconds. Confirm its
one-shot part ends around15 seconds and does not return at later loop joins.
Listen to virus PLANETARIUM for at least240 seconds. Check bass continuation
and release around the129/189-second loop jumps. Use chips/Buster and complete
three actual battle→map→battle cycles with native restoration and fresh starts.

The finalizer must overwrite
`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps` with this exact final patch.
It must verify destination byte/SHA-256 equality and record transport separately
from manual acceptance. The migrated package structure is preserved. Older
D-drive delivery records remain historical evidence. Local records live in
`out/nds-research/nds-manager-library-v13/` and
`out/nds-research/nds-manager-library-exe6-v13/`. ROMs/assets/caches stay out of Git.
Archived v10–v38 compatibility audits remain unchanged.

The remaining metadata shortlist has seven unregistered source sequences with
at least one accepted standalone record. It is not seven newly verified manager
songs. Each needs identity/scope review. SATELLITE variants count once; its
filtered revision retains its limited missing-accent acceptance.

## Final native observations

The exact composite passes20,010 ordinary frames between controlled calls.
HOKORA reaches clock11267 and all12 waves. Its header has seven tracks, but
its active mask becomes0x3F after track6 ends. The finite track's last owned
active channel occurs at1536. No later START flag occurs; its LFO fields remain
frozen. It stays ended and empty across the7716/10788 common-loop jumps. Its
observed peak is three owned channels. Six looping tracks continue afterward.

PLANETARIUM reaches clock23086 and all29 waves. Original score observations
cover alias126 on native track7 at the7968 entry and14976/21984 GOTO boundaries.
Each384-tick gate has195 held snapshots on the same PCM slot/key/wave, without
a new START flag in the observed held window. Five snapshots after each EOT
show no held alias. The EOT ticks are8160/15168/22176. This observes the original
eight-track arrangement, rather than replacing it with a synthetic score.
It remains a per-frame, one-alias window check, not exhaustive voice allocation
or proof of source/target waveform equality.

Effects100/129, three controlled native-restore/title/battle/communication-restart
cycles and queued stop pass. No imported tail remains after native restoration.
The fixture uses PC/LR/argument and disposable scene-RAM injection between
ordinary frames. It does not establish actual battle/map/linked-play/rematch
outcomes or revalidate every LFO/envelope step. User-reported acceptance is
recorded separately below.

## Exact-ROM user acceptance

The user reported “可以，没问题” after the three requested checks for ROM2F9772D8.
The local ROM, BPS, reconstruction and C-drive test copy were verified again.
The47-song roster and both new previews, save/reload/export, title HOKORA for at
least180 seconds with its one-shot part absent after its ending, virus-battle
PLANETARIUM for at least240 seconds with bass continuation/release at the loop
jumps, chips/Buster and three actual battle→map→battle cycles with native music
restoration and fresh starts are recorded as user-reported passes.

These reports are not independently timed or observed checks. They do not
establish comparative DS fidelity, zero-note-loss, arbitrary exports/roles,
linked play/rematches or manual Falzar gameplay. Original PCM, modulation,
mixed/carry behavior, envelopes, tempo, voice-budget and previous per-song
limits retain their recorded scope. Fresh34-case regression and reused550-case
full-suite evidence stay separate. Acceptance recording changes documentation
only; source tests were not rerun for this step.
