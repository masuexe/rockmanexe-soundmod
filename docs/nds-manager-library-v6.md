# NDS manager library v6: twenty-nine registered songs

This batch selects six previously accepted filtered configurations by evidence
and existing capability, rather than requiring two songs from every generation.
The first23 tuples/slots8954–8976, gains, track counts and finite flags remain
intact. No converter, DSP, mixer, relocator, realtime/cache implementation,
browser runtime or project schema changes.

| Slot | Source | Song / selector | Tracks | Playback |
| --- | --- | --- | ---: | --- |
| 8977 | SF1 | ANTENNA / `sf1-antenna-antialias` | 7 | Loops |
| 8978 | SF1 | DEMPAJIKEN / `sf1-dempajiken-antialias` | 7 | Loops |
| 8979 | SF1 | WIN / `sf1-win-antialias` | 7 | Loops |
| 8980 | SF1 | GAMEOVER / `sf1-gameover-antialias` | 8 | Finite |
| 8981 | SF1 | BOSSMAE / `sf1-bossmae-antialias` | 8 | Loops |
| 8982 | SF3 | DEMPAJIKEN / `sf3-dempajiken-merged-antialias` | 8 | Loops |

All six retain their accepted+3.5dB settings. The five SF1 configurations use
existing singleton filtering; GAMEOVER explicitly ends naturally. WIN loops,
retaining its source behavior rather than inheriting WIN2's finite flag.
SF3 DEMPAJIKEN keeps the accepted eleven-to-eight grouping and long alias127;
no grouping search, new capability or changed native voice budget is introduced.
Its prior bounded native trace had999 NOTE calls,996 allocations and three
rejections, matching its plain control. Registration retains that allocation
tradeoff and the existing merged-volume/pan and release-tail limits.

## Cache and source proof

Normal metadata load performs zero conversions. The conversion dependency key
is unchanged. All23 prior Falzar configurations hit disk with zero conversions;
the six new configurations are prepared once during preflight and then read
from cache by the manager. The29-song registry run reads29 disk entries and
makes no conversions. First use in other targets/data directories can still
need preparation. The table grows to8983, so old project keys/pools/slots are
compatible while their exported ROM/BPS fingerprints change.

All six candidates pass strict blob, parsed dependency and conversion-report
comparison to their source-specific accepted standalone artifacts before
registration. All29 manager conversions retain exact standalone blob/dependency
identity. Twenty-seven conversion reports match strictly; the two older SF2
reports retain the previously bounded diagnostic/wording reconciliation from
v5, with all other fields exact. No historical record is rewritten. Existing
DS-reference/per-song native evidence is reused under those identities, not a
new DS render, comparative preference or blanket acceptance of manager exports.

Fresh regression runs34 manager/cache/lazy-preview/realtime cases without
skips and all three JavaScript suites. The previous550-case full no-skip suite
is explicitly reused under unchanged audio/runtime/config/test dependencies,
not described as a new550-case run. Only registry assignments and two count/
roster fixtures differ; removing SONGS/TRACK_COUNTS restores the full previous
catalog AST. Initial native-fixture preparation expected a status-mask check
not present in its parent and stopped before emulator launch. The corrected
fixture changes the actual two title mask checks to seven tracks. The local
failure note remains separate; no production source or ROM was changed by it.

All29 real agbplay starts produce nonzero stereo. A separate Falzar29-song
pool checks distinct headers/tone banks, source PCM identity, exact-content
sample interning and BPS reconstruction below32MiB. It is a packing artifact,
without manual acceptance or proof of every random runtime selection. Actual
HTTP checks cover29 entries, a matching Falzar export and all six new mGBA
previews. GAMEOVER's12-second capture ends with four seconds of zero PCM;
other additions use short clips. Preview caching preserves saved pools.

## Exact-ROM review and limits

The final Gregar ROM assigns SF1 DEMPAJIKEN8978 to title and SF3 DEMPAJIKEN8982
to ordinary virus and communication battle requests, with other pools native.
The two versions retain separate source keys/headers/tone banks; only byte-
identical pointer-free resources may share addresses. Current-role track-owner
observations are used for wave coverage during controlled lifecycle checks.

Requested manual checks cover29-song visibility and six added previews,
GAMEOVER ending plus a ten-second no-replay wait, save/reload/export, at least
50 seconds of title SF1 DEMPAJIKEN and45 seconds of battle SF3 DEMPAJIKEN,
chip/Buster effects and three battle→map→battle cycles. This exact ROM
and requested workflow have the user-reported acceptance recorded below.

Controlled queue/scene/effect calls inject PC/LR/arguments and disposable scene
RAM, with ordinary frames between calls. They do not establish actual battle/
results/map, linked play or rematches. No new exhaustive NOTE-allocation trace,
zero-note-loss proof or complete waveform alignment is claimed. The other
four additions are previews, without gameplay acceptance in the delivered
pair. Falzar build/short preview checks do not infer manual Falzar acceptance.
Prior ten-voice/10512Hz/PCM8, filtering, gain/envelope/tempo, grouping and per-song
allocation/tail limitations remain. ROMs/assets/caches/research stay outside Git.

Local evidence is under `out/nds-research/nds-manager-library-v6/`.

## Final automatic artifact

The exact Gregar test passes6410 ordinary frames between controlled calls,
covering two common periods per role and all104/96 current-track-owner waves.
SF1 title reaches clock5755 after2600 warmup frames, beyond entry774 plus
two2304-tick periods. First SF3 battle reaches clock4347, beyond entry768 plus
two1728-tick periods. Three effect/scene/native-restore/restart cycles and
queued stop pass. This does not count every NOTE allocation.

The29-song automatic Falzar pool is19120060 bytes, within32MiB, and reuses29 disk
entries without conversion. The prepared review manager reproduces its Falzar
export from cache; that is automatic evidence, not manual Falzar gameplay.

- Gregar ROM CRC32: `6E07A6DC`; size9722068 bytes.
- ROM SHA-256: `238cf40073807672c37438df86e678352a7c6f8305646a00e3247efd1a356264`.
- BPS SHA-256: `cc52a4bcc7d44d7197b3e7c1cf7f861e15e8fb3814cdb4d832c85fe34b90504a`.
- Exact experiment: `out/nds-research/nds-manager-library-exe6-v6/`.
- Prepared29-song Falzar manager: `http://127.0.0.1:8783/`.
- Manual acceptance: user-reported pass for the three requested checks.

The final validated Gregar BPS overwrites the requested Windows test path with
atomic replacement and destination byte/SHA-256 equality recorded separately
in `patch-delivery.json`. Transport does not establish listening acceptance.

## Exact-ROM user acceptance

The user reported “测试没有问题” in response to the three requested checks for
ROM6E07A6DC. ROM, BPS and the Windows test copy were checked again at recording.
The29-song roster/six added previews, GAMEOVER ending plus ten-second no-replay
wait, save/reload/export, title SF1 DEMPAJIKEN50-second and battle SF3
DEMPAJIKEN45-second listening, chips/Buster and three battle→map→battle cycles
with native restoration and fresh starts are recorded as user-reported passes.

These are user reports, not independently timed or observed checks. They do
not establish a new three-minute fidelity comparison, zero rejected NOTE calls,
gameplay for the other four additions, arbitrary exports/roles, linked play/
rematches or manual Falzar acceptance. The prior SF3 allocation tradeoff and
all filtering/PCM8/envelope/tempo/tail limits remain, alongside the distinction
between fresh34-case checks and reused550-case full-suite evidence.
