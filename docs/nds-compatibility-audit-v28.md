# NDS compatibility audit v28: accepted BOSSMAE merged antialias route

The filtered scanner adds only the accepted SF3 BOSSMAE twelve-to-eight
configuration, under route `known_sf3_bossmae_merged_antialias`. It requires
family `ssr3`, slot27, capacity eight, exactly source IDs
0/1/2/3/4/5/7/8/9/13/14/15, all tracks looping, no fitted attack and no active
modulation. It uses `SF3_BOSSMAE_GROUPS` and the explicit merged-filter flag.
Existing grouping, fixed-volume, shared-control, held-pan, alias/release,
upward-bend and other filter/conversion guards remain. There is no group search
or expansion to other over-capacity songs. Conversion/model/packing failures
remain visible; the pinned route cannot silently retry with fitted attacks.

All seven originals and three pinned SDATs verify before and after all132 slots.
Only the filtered status of `ssr3:27` changes. Its ROM/BPS exactly match the
[user-accepted standalone experiment](nds-sf3-bossmae-merged-antialias-research.md):

- ROM CRC32: `0279DBB2`.
- ROM SHA-256: `dde49b852f1c45e5d988eb45554fe14c029406b9ee976b1a6da1264250813b7c`.
- BPS SHA-256: `90e92561cf2e8108ed8e71220e5d694cd53f72e17ce3bcc85189a9755ee6dfe3`.

All71 old primary and29 old filtered ROM/BPS pairs retain their bytes, routes,
gains and exact-manual-match flags. Primary counts remain71 packed,36 exact
accepted,35 pending and51 capacity-blocked. Filtered packing rises29→30 and
exact accepted matches11→12, with18 pending and92 blocked. The new route adds
an alternate version of an already accepted song: unique source sequences with
an exact accepted variant remain41. Acceptance does not transfer by song name.

All422 tests pass without skips, including six new scanner cases for pinned
identity/structure/groups, explicit flags, retained guards and failure history,
headroom/packing behavior, exact-version acceptance, attributed limits and
primary/filtered report accounting. Validation checks exact accepted ROM/BPS
and manifests, all old packed identities, original inputs, source/scanner
hashes, deterministic reports, actual JavaScript predicates and unchanged
recursive v10–v27 archive identities. The merged-antialias filter selects
BOSSMAE alone; all prior structure filters retain their counts. JSON/CSV/HTML
expose the pinned grouping and separately attributed standalone observations.

The report attributes1,514 allocated NOTE calls, no held/starting preemption,
905 release-flagged reuses with nonzero envelope and4,763 clamped PCM8 stored
points out of513,763 to the exact standalone ROM. It does not remeasure native
allocation or playback. Filtered storage counts are recomputed by conversion,
not time-weighted playback or an audible-error bound. Native tail reuse,
clipping, PCM8/ADSR/tempo quantization and the ten-voice budget remain explicit.
This scan adds no runtime or manual acceptance. The user's functional pass
includes the requested listening/effects/three-encounter checklist; comparative
filtered/unfiltered preference was not separately reported. No independently
timed recording, complete gameplay trace, linked-play or rematch result is
inferred.

A separate source investigation studies conservative upward-pitch preparation
for STUDIO; it is outside this scan and requires a new exact-ROM checklist.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v28
```

Use a fresh directory. ROMs, original assets and local research outputs stay
outside Git. Archived results and coverage remain immutable.
