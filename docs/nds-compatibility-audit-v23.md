# NDS compatibility audit v23: accepted eleven-track DEMPAJIKEN grouping

The scanner adds only the accepted SF3 DEMPAJIKEN grouping: source tracks
2/4/6 and 5/8 share two native tracks, while the six remaining sources stay
independent. The route requires family `ssr3`, slot 26, capacity eight, exactly
source IDs 0–8/14/15, all tracks looping, no fitted envelope and no active
modulation. Existing shared-control, fixed-volume, held-note-pan, long-note
alias/release and conversion guards remain unchanged. The standalone selector
and scanner share `SF3_DEMPAJIKEN_GROUPS`; all eight accepted standalone outputs
remain byte-identical after the constant refactor. No automatic grouping search
or new conversion/native-driver capability is enabled.

## Results

All seven original variants and three pinned family SDATs verify before and
after scanning all 132 SSEQ slots. Only `ssr3:26 BGM_DEMPAJIKEN` changes primary
conversion status. Its ROM/BPS match the
[accepted standalone experiment](nds-sf3-dempajiken-eleven-track-research.md):

- ROM SHA-256: `55bbdc6711c395c32b78ad5159fcd0622b20e973829b86dfb4d34f60d06188ef`.
- BPS SHA-256: `f71d64bdef737adaf7428a2a87ce77ec487ab7c4231962f1fb1d9e26c7c0f195`.

Primary packing rises from 66 to 67, with 32 exact accepted primary variants
and 37 unique accepted source sequences across primary/filtered variants.
Primary pending remains 35. All 66 old primary and 29 filtered ROM/BPS pairs
retain bytes, routes, gains and manual-match flags. The remaining 55 primary
blockers exceed eight tracks. Filtered counts stay 29 packed, eleven exact
accepted, eighteen pending and 93 blocked; filtered DEMPAJIKEN stays capacity-
blocked. Different variants do not inherit acceptance by song name.

## Verification and limits

All 376 regression tests pass, including six new scanner cases for identity
and structure restrictions, exact groups and plain flags, retained converter
guards, headroom/packing behavior, visible model failures, limit metadata and
report/summary accounting. Report checks verify accepted fingerprints and
manifests, old packed identities, original inputs, source/scanner hashes,
deterministic reports, actual JavaScript filters and unchanged archived
v10–v22 identities. Eleven-, ten- and nine-track filters each select only their
explicit known song, contributing once to the standard summary column.

JSON, CSV and HTML retain an explicitly attributed standalone native limit:
999 observed NOTE calls included three source-14 key-64 allocation rejections
under the ten-voice budget, one per cycle. The user reported the requested
exact-ROM listening/effects/three-encounter checklist passed and the omission
was inaudible. The batch scan neither remeasures allocations nor establishes
new runtime or manual acceptance. Original alias release evidence and a
separate modified-score EOT diagnostic retain their separate scopes. Native
voice limits, possible release-tail stealing and quantization remain; no
independent timing, full gameplay trace, linked-play/rematch result or
comparative preference is inferred.

## Continuing investigation

A separate SF3 BOSSMAE candidate studies twelve sources in eight native tracks,
using three equal-volume groups (0/3/4, 5/7 and 13/15). Its source, native voice
allocation, stereo and lifecycle checks are independent of this scan and need
a new exact-ROM manual checklist. It remains outside batch grouping.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v23
```

Use a fresh directory. Local evidence, hashes and logs stay in ignored research
outputs; ROMs and source game assets stay outside Git. Historical audit counts
and evidence remain immutable.
