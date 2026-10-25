# NDS manager library v4: seventeen registered songs

This batch appends six existing standalone configurations, two per source
family. Slots8954–8964 and their previous keys, gains, finite flags and track
counts are preserved. The converter, sample preparation, native mixer,
relocator, realtime engine, cache implementation and project schema are unchanged.

| Slot | Source | Song / selector | Tracks | Playback |
| --- | --- | --- | ---: | --- |
| 8965 | SF1 | COMICAL / `sf1-comical-antialias` | 8 | Loops |
| 8966 | SF1 | KANDO / `sf1-kando-antialias` | 7 | Loops |
| 8967 | SF2 | DEMPAJIKEN / `sf2-dempajiken-antialias-envelope` | 8 | Loops |
| 8968 | SF2 | HOKORA / `sf2-hokora-merged-antialias` | 8 | Loops |
| 8969 | SF3 | WIN2 / `sf3-win2-antialias` | 8 | Finite |
| 8970 | SF3 | GAMEOVER / `sf3-gameover-antialias` | 8 | Finite |

All six retain their accepted standalone+3.5dB settings. DEMPAJIKEN combines
existing fitted envelopes with filtering and retains its carried long note.
HOKORA retains the existing nine-to-eight grouping: source0/4 share a target
track with fixed volume100 and neutral pan64. The two finite SF3 cues preserve
their END behavior. New converter or mixer capability is not introduced.

Catalog loading still performs zero conversions. The enlarged registry changes
the conservative toolchain cache key, so entries from the previous release are
rebuilt on demand. The seventeen-song table has8971 entries. Old projects retain
keys/slots/pools, while their ROM/BPS bytes change; previous exact-ROM acceptance
is not transferred to new exports.

## Verification and scope

Local checks and artifacts are generated under
`out/nds-research/nds-manager-library-v4/`. Fresh blobs, dependency values and
conversion reports for all seventeen configurations are compared against
source-specific accepted standalones. Exact archived acceptance fingerprints
and BPS reconstruction are checked before prior DS-reference and per-song native
evidence is reused. This does not provide a new DS render or comparative timbre
judgment. Realtime starts and recorded previews exercise the real manager paths.

A separate automatically checked title pool packs all seventeen isolated banks
in one ROM, including looping and finite songs. It is a packing/cache regression
artifact, without manual acceptance or proof of every runtime selection.

The intended Gregar manual delivery uses SF1 KANDO for title and SF2 DEMPAJIKEN
for ordinary virus and communication battle requests. The other four additions
are reviewed through the manager. The six-song roster/previews, two finite
endings and ten-second no-replay waits, project save/reload/export, title70-second
and battle55-second listening, chip/Buster effects and three battle→map→battle
cycles form the final requested manual checks. The exact artifact has the bounded user-reported acceptance recorded below.

## Limits

Controlled original queue/scene/effect calls inject PC/LR/arguments and disposable
scene RAM. Normal frames between calls do not establish real battle/results/map
or linked/rematch gameplay. No new exhaustive NOTE-allocation or full-song
waveform-alignment probe is claimed. Short Falzar clips do not establish full
loops or manual Falzar acceptance. Every export has its own exact fingerprint.

Prior ten-voice,10512Hz/PCM8, filtering, volume/envelope/tempo, shared controls,
merged-track and release-tail limitations remain. SF3 WIN2 specifically retains
its previously measured missing-held-note-interior observations and accepted
allocation tradeoff; source-note preservation is not native polyphony equivalence.
No new three-minute fidelity or independent timing/hardware claim is made.

ROMs, assets, PCM caches and local research outputs stay outside Git.

## Completed manager and packing checks

All seventeen fresh conversions match accepted standalone blobs and parsed
conversion/dependency values. Their source-specific archived manual fingerprints
and BPS reconstruction also pass. Seventeen actual agbplay starts produce
nonzero stereo. Source/reference evidence is reused under these identities;
this does not accept a new manager ROM.

Actual HTTP catalog/export tests reproduce the delivery ROM/BPS. All six new
mGBA preview captures are nonzero; both12-second SF3 finite previews contain
zero PCM for their last four seconds. Preview caching leaves project pools
unchanged. A restarted review manager reproduces the final two-song export with
two disk hits and no conversions. A separate Falzar build reconstructs from its
BPS and all six short new-song previews are nonzero, without full-loop/finite
completion or manual Falzar claims.

The seventeen-song title-pool build is14928860 bytes (within32MiB) and uses
seventeen disk hits without conversions. All seventeen sequence headers and
tone banks are distinct, and every song's relocated PCM byte set matches its
compiled source. Exact-content PCM/keymap/PSG interning is an existing exporter
policy: equal pointer-free resource contents can share addresses across banks.
The final KANDO/DEMPAJIKEN pair shares ten identical waves; physical sample
address disjointness is not a valid bank-isolation requirement.

Initial native/all-pool fixtures incorrectly rejected shared sample addresses,
before native playback. They were corrected to use separate headers/tone banks,
source PCM identity and wave observations owned by the currently playing role.
The first generated observation edit also had an indentation error and was
rejected before emulator launch. Failed logs remain local and separate from
passing evidence. These fixture fixes change no ROM, converter or runtime.

- ROM CRC32: `D1A5CB1F`; size9737068 bytes.
- ROM SHA-256: `f1721a7ce5fe6f0fb295a8bb9761bcc2f309e17cd1e8cf050e51265278e5ea80`.
- BPS SHA-256: `0e3fd85d781297e576c37eca16ec88a81504313708b83071baa6809c1a3e8c5e`.
- Exact experiment: `out/nds-research/nds-manager-library-exe6-v4/`.
- Review manager: `http://127.0.0.1:8780/`.
- Manual acceptance: user reports all three requested checks passed; loading delay remains a separate issue.

The exact delivery passes8410 ordinary frames between controlled helper calls.
Title KANDO reaches clock7853 after3900 warmup frames, beyond entry1536 plus two3072-tick
periods. First battle DEMPAJIKEN reaches clock6328, beyond entry1344 plus
two2304-tick periods. Current-role owner observations cover all84/91 waves,
including ten safely shared exact-content addresses. Three effect/native-restore/
title/scene restart cycles and queued stop pass; imported tails clear after
native restoration and stop. This does not provide exhaustive NOTE-allocation
or actual gameplay evidence.

A fresh546-case Python suite without skips and both JavaScript suites pass.
Frozen regression sources and recursive v10–v38 file sets/hashes remain unchanged.
The production change is limited to registry/count facts; tests pin the previous
eleven tuples and the six additions. The final validated BPS is atomically
copied to the requested Windows test path with destination byte/SHA-256 equality
recorded separately in `patch-delivery.json`. Delivery is not manual acceptance.

## Exact-ROM user acceptance and separate loading issue

The user reported “测试均通过。但是试听流星音乐的时候加载要卡很久。这是为什么？”
for the delivered ROM D1A5CB1F. All three requested checks are recorded as
user-reported passes: seventeen-song visibility/six added previews, both finite
endings and ten-second waits, save/reload/export; title KANDO70-second and
battle DEMPAJIKEN55-second listening; chips/Buster and three battle→map→battle
cycles. ROM/BPS and the Windows test copy were rechecked when recording.
These are user reports, not independently observed or timed checks. Other
exports/roles, linked play/rematches and manual Falzar acceptance remain separate.

The reported long NDS preview loading time is tracked separately. Functional
acceptance does not establish that this performance issue is resolved.
