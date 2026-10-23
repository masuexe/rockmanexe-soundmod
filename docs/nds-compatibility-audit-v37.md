# NDS compatibility audit v37: exact SF1 LABO acceptance

This acceptance-only refresh uses the unchanged scanner and route policies.
All seven originals and three pinned SDATs verify before and after132 slots.
All71 prior primary and37 prior filtered ROM/BPS pairs retain bytes, routes,
gains, resources and conversion results. No primary or filtered packing status
changes. Only the filtered exact-manual flag for `ssr1:5` changes false→true,
matching the [accepted SF1 LABO experiment](nds-sf1-labo-antialias-research.md):

- ROM CRC32: `E7A73FAF`.
- ROM SHA-256: `a6996410dbe6d95b6108dbabbaae695fd0a27294b9d18030717d857653b4a5bb`.
- BPS SHA-256: `52640008bcfcdf1dc224ed2edf5965a7dcb221b217286bd6b01f9004628c5351`.

Primary totals stay71 packed,36 exact accepted,35 pending and51 blocked.
Filtered totals stay37 packed, with exact accepted20→21, pending17→16 and85
blocked (51 capacity,34 conversion). Unique source sequences with an accepted
variant rise42→43. Merged-filter and upward-preparation counts remain eight
and four. Structure filters keep their counts.

Acceptance is matched by source family/index and exact ROM/BPS identities,
with the recorded three-minute listening/effects/three-encounter scope.
The primary LABO route and freshly built standalone plain control remain
unaccepted. SF1 ROOM acceptance stays separate from byte-identical SF2 ROOM;
no song-name or output-hash transfer across source families is inferred.
Comparative timbre preference, independent timing, full gameplay traces,
linked play and rematches were not separately reported.

The exact frozen485-test evidence from the accepted LABO experiment is reused:
all root source and test hashes match that full no-skip run. This refresh does
not claim a new suite run. The scanner source is unchanged from v36. New batch
validation checks inputs, previous packed identities, exact manual-flag changes,
source isolation, deterministic JSON/CSV/HTML/summary output, actual JavaScript
filters, source/scanner hashes and recursive v10–v36 archive identities. The
reuse record points to the original log and frozen source map.

This scan adds no native measurement, conversion capability or listening
acceptance. Standalone LABO evidence remains distinct: all3,931 NOTE calls
allocate with no held/starting preemption; source identities/clocks/outcomes
match a newly built unaccepted plain control, with2,759 different slots and
1,115 release reuses versus951. Four original long-alias holds/releases,
moving stereo and the fixed-tempo phase model passed within recorded limits.
Ten-voice tails, conservative filtering, PCM8/clipping and volume/ADSR/tempo
quantization remain explicit.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v37
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
Historical artifacts and coverage remain immutable.
