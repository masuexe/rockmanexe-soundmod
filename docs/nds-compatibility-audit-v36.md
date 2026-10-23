# NDS compatibility audit v36: source-specific SF1 ROOM acceptance

This is an acceptance-only refresh using the unchanged scanner and policies.
All seven originals and three pinned SDATs verify before and after132 slots.
All71 prior primary and37 prior filtered ROM/BPS pairs retain bytes, routes,
gains, resources and conversion results. No primary or filtered packing status
changes. Only the filtered exact-manual flag for `ssr1:4` changes false→true,
matching the [accepted SF1 ROOM experiment](nds-sf1-room-antialias-research.md):

- ROM CRC32: `A9FF0FF4`.
- ROM SHA-256: `18d2996a63391686b66b025b7a797436adda1cb369dcc50320fc7ab79722e9dc`.
- BPS SHA-256: `7443451a7c4a657cac77473949954be56b1b9a7a9e2eb6b6f4643f32053bbc3b`.

Primary totals stay71 packed,36 exact accepted,35 pending and51 blocked.
Filtered totals stay37 packed, with exact accepted19→20, pending18→17 and85
blocked (51 capacity,34 conversion). Unique source sequences with an accepted
variant rise41→42. Merged-filter and upward-preparation counts remain eight
and four, respectively. All structure filters keep their counts.

SF2 `ssr2:4` happens to produce identical filtered ROM/BPS bytes. Its manual
flag remains false and it has no related manual record. Both primary ROOM
versions remain unaccepted, and the standalone plain control remains explicitly
`unaccepted_control`. The validator checks these boundaries rather than
transferring acceptance by song name or output hash across source families.
Accepted records are checked against family/index provenance, ROM/BPS and
manifests, preserving the reported three-minute listening/effects/three-cycle
scope. Comparative timbre preference, independent timing, full gameplay
traces, linked play and rematch were not separately reported.

The exact frozen483-test evidence from the accepted ROOM experiment is reused:
all root source and test hashes match that full no-skip run. This refresh does
not claim a new test-suite run. The scanner source itself is unchanged from
v35. New batch validation checks inputs, previous packed identities, precise
manual-flag changes, cross-family isolation, deterministic JSON/CSV/HTML/summary
reports, actual JavaScript filters, source/scanner hashes and recursive
v10–v35 archive identities. The saved reuse record points to the original log
and frozen source map.

This scan adds no new native measurement, conversion capability or listening
acceptance. The standalone ROOM evidence remains distinct:938 allocated NOTE
calls with no rejection or held preemption,479 release reuses versus478 in
its unaccepted plain control, six-track native memory/control checks and
settled source2 stereo diagnostics. Ten-voice tails, conservative filtering,
PCM8/clipping and volume/ADSR/tempo limits remain.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v36
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
Historical artifacts and coverage remain immutable.
