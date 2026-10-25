# NDS manager library v5: twenty-three registered songs

This batch appends six existing standalone configurations, two per source
family. The first seventeen tuples/slots8954–8970 are preserved, including gains,
track counts and finite flags. No converter, sample preparation, mixer,
relocator, realtime/cache implementation, browser runtime or project schema changes.

| Slot | Source | Song / selector | Tracks | Gain |
| --- | --- | --- | ---: | ---: |
| 8971 | SF1 | LABO / `sf1-labo-antialias` | 8 | +3.5dB |
| 8972 | SF1 | JIKEN / `sf1-jiken-antialias` | 8 | +3.5dB |
| 8973 | SF2 | BATTLE / `sf2-battle-delay` | 8 | +3.5dB |
| 8974 | SF2 | KAICYOU / `sf2-kaicyou-toggle` | 8 | +3.5dB |
| 8975 | SF3 | BOSSMAE / `sf3-bossmae-merged-antialias` | 8 | +3.5dB |
| 8976 | SF3 | KINCHO / `sf3-kincho-upward-antialias` | 8 | +3.5dB |

All six loop. The SF1 pair uses singleton filtering; SF3 BOSSMAE retains its
accepted twelve-to-eight grouping/filtering and KINCHO its ten-to-eight upward
preparation. The SF2 pair preserves original PCM and its accepted native-LFO
approximation: fixed delay for BATTLE, fitted attacks plus enable-only modulation
for KAICYOU. Neither opts into a new filtered-LFO capability. The existing
shared phase/delay, waveform, envelope, tempo, release-tail and ten-voice limits
remain. Registration does not improve those approximations.

## Actual cache preservation

The conversion dependency fingerprint is unchanged by this registry-only edit.
Loading23 metadata entries performs zero conversions. Normal cache reads for
all seventeen old configurations give17 disk hits and zero conversions. Only
six new source configurations need preparation, preserving the loading-time
improvement reported for the cache-scope update. The table expands to8977;
old projects retain keys/slots/pools while producing different ROM/BPS bytes.
No previous exact-ROM acceptance transfers to those new exports.

## Evidence and regression boundary

Local evidence is under `out/nds-research/nds-manager-library-v5/`. All23 compiled
blobs and parsed dependency values match source-specific accepted standalones.
Twenty-one conversion reports match strictly. The two older SF2 reports retain
all operative values after explicitly whitelisting diagnostic additions:
empty carry/context-split lists and extended gate-check bounds; BATTLE also has
an initialization record and updated descriptive policy wording. Every other
field must match. Actual compiled commands, samples and dependency reports stay
byte/value identical; broad or arbitrary report differences are not accepted.
These identities permit reuse of prior DS-reference/per-song native evidence,
without a new DS render, comparative preference or manager-ROM manual pass.

The first strict report-equality fixture rejected those legacy additions and
stopped before delivery. Its source/log remain separate. A second historical
record-format check found SF2 BATTLE uses `rom_fingerprint` rather than
`expected_build_fingerprint`; the known fallback still checks actual bytes,
manifest output and BPS reconstruction. Historical acceptance files are unchanged.

Fresh direct regression covers34 manager/cache/lazy-preview/realtime cases,
without skips, plus all three JavaScript suites. The previous550-case no-skip
full run is explicitly reused under unchanged audio/runtime/config/test source
identities; this is not a new550-case run. Removing only the SONGS/TRACK_COUNTS
assignments restores the entire previous catalog AST. Only that registry and
its Python/DOM count fixtures differ from the previous full-suite inputs.

All23 actual agbplay starts are nonzero. A separate Falzar title pool packs23
distinct headers/tone banks, with per-song PCM content matching each compiled
source, safe exact-content sample interning and BPS reconstruction below32MiB.
It is an automatic packing artifact, not runtime-selection or manual acceptance.
Real HTTP checks show23 entries, export identical Falzar bytes, preserve project
pools and capture all six new previews. SF2 BATTLE/KAICYOU use12-second clips to
cover delayed/enable-only openings; other four use short3-second clips. These
clips do not establish full loops, full held-note allocation or fidelity.

## Requested exact-ROM review

The delivered Gregar ROM assigns title JIKEN8972 and ordinary virus/communication
battle BOSSMAE8975, with other event pools unchanged. Final manual checks cover
23-song visibility and six added previews (the SF2 pair for at least12 seconds),
project save/reload/export, title JIKEN at least55 seconds, battle BOSSMAE at
least50 seconds, chip/Buster effects and three battle→map→battle cycles.
This exact ROM and requested workflow have the user-reported acceptance below.

Controlled queue/scene/effect helper calls use PC/LR/argument injection and
ordinary frames between calls; they do not establish actual battle/results/map
or linked/rematch gameplay. The final two-song native check observes current
track-owner waves, allowing exact-content samples shared across banks, and
checks source switching, native restoration and queued stop. No exhaustive new
NOTE-allocation trace or complete waveform alignment is claimed.

Other four additions are manager previews, without gameplay acceptance in
this two-song export. Falzar preview/build checks do not infer manual Falzar
acceptance. PCM8, filtering, gain/envelope/tempo and all per-song allocation/
tail limitations remain. ROMs/assets/caches/research outputs stay outside Git.

## Final automatic artifact

The exact Gregar test passes7310 ordinary frames between controlled calls,
covering two common periods per song and all129 JIKEN/81 BOSSMAE waves owned
by the current music tracks. Title reaches clock5839; first battle reaches
clock5666. Three effect/scene/native-restore/restart cycles and queued stop pass.
The23-song automatic Falzar pool is17814760 bytes, within32MiB, and uses23 disk
hits with no conversions. The prepared review server exports the same final
Falzar build from cache; its use does not infer manual Falzar acceptance.

- Gregar ROM CRC32: `FBD9D2FF`; size9903980 bytes.
- ROM SHA-256: `6158e2aa51b0d54d400ec9a5f022fc3584a587156561603484aaf81c9467d203`.
- BPS SHA-256: `1e88f9f076f23a833213f995bfbd8b2b7b0925f197473f8332b76f1fed80bdd8`.
- Exact experiment: `out/nds-research/nds-manager-library-exe6-v5/`.
- Prepared23-song Falzar manager: `http://127.0.0.1:8782/`.
- Manual acceptance: user-reported pass for the three requested checks.

The final validated Gregar BPS overwrites the requested Windows test path with
atomic replacement and destination byte/SHA-256 equality recorded separately
in `patch-delivery.json`. Transport does not establish listening acceptance.

## Exact-ROM user acceptance

The user reported “测试无问题” in response to the three requested checks for
ROM FBD9D2FF. The ROM, BPS and Windows test copy were checked again when recording.
This records the23-song roster/six added previews (both SF2 openings for at
least12 seconds), project save/reload/export, title JIKEN55-second and battle
BOSSMAE50-second listening, chips/Buster and three battle→map→battle cycles
with native restoration and fresh starts as user-reported passes.

These are user reports, not independently observed or timed checks. Full SF2
periods, new comparative fidelity, gameplay for the other four additions,
arbitrary exports/roles, linked play/rematches and manual Falzar acceptance
were not established. Previous allocation/filter/LFO/envelope/tempo/tail limits
and the distinction between fresh34-case checks and reused550-case evidence
remain unchanged.
