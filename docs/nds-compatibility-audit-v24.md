# NDS compatibility audit v24: accepted twelve-track BOSSMAE grouping

The scanner adds only the accepted SF3 BOSSMAE grouping. Sources 0/3/4, 5/7
and 13/15 form three equal-volume groups; the other five sources stay
independent. The route requires family `ssr3`, slot 27, capacity eight, exactly
source IDs 0–5/7–9/13–15, all tracks looping, no fitted envelope and no active
modulation. Existing shared-control, fixed-volume, held-note-pan and conversion
guards remain. The standalone selector and scanner share `SF3_BOSSMAE_GROUPS`;
all eight accepted standalone outputs remain byte-identical. No automatic
grouping search or new conversion/native-driver capability is enabled.

## Results

All seven original variants and three pinned SDATs verify before and after
scanning all 132 slots. Only `ssr3:27 BGM_BOSSMAE` changes primary conversion
status. Its ROM/BPS match the
[accepted standalone experiment](nds-sf3-bossmae-twelve-track-research.md):

- ROM SHA-256: `1ada1a4ed7c64d5279021b69e6ceacc49f14b78a6ee012fe17de1870bdacc935`.
- BPS SHA-256: `a5c52e2dc1a2bf7abf4d4bdd15d94b136b1e9d83ce6d42787a4fdc59a123bdf6`.

Primary packing rises from 67 to 68, with 33 exact accepted primary variants
and 38 unique accepted source sequences across both routes. Primary pending
stays 35. All 67 old primary and 29 filtered ROM/BPS pairs retain bytes, routes,
gains and manual-match flags. The remaining 54 primary blockers exceed eight
tracks. Filtered counts remain 29 packed, eleven exact accepted, eighteen
pending and 93 blocked; filtered BOSSMAE remains capacity-blocked. Different
variants do not inherit acceptance by name.

## Verification and limits

All 384 regression tests pass, including six new scanner cases for exact
identity/structure/groups, plain flags, retained converter guards, headroom
and packing behavior, visible model failures, attributed budget metadata and
report/summary accounting. Reports verify old packed identities, exact accepted
ROM/BPS/manifests, inputs and source/scanner hashes, deterministic rendering,
actual JavaScript filters and unchanged archived v10–v23 identities. Twelve-,
eleven-, ten- and nine-track filters each select their one explicit song and
contribute once to the standard summary column.

JSON, CSV and HTML retain attributed observations from the exact standalone
ROM: all 1,514 NOTE calls allocate, no held/starting channel is displaced in
the observed two-cycle window, and 905 release-flagged channels with nonzero
envelope are reused. The latter can shorten tails; counts and channel flags
are not an audible-error bound. Metadata pins the original ROM SHA-256 and
states that this scan does not remeasure native allocations. The user's
listening/effects/three-encounter acceptance remains separate from automation;
no independently timed recording, full gameplay trace, linked-play/rematch
result or comparative preference is inferred. Batch success adds no native
or manual acceptance.

## Continuing investigation

A separate SF3 CHANGE experiment studies thirteen sources in eight tracks.
An equal-volume-only search cannot provide enough compatible merges, so the
candidate uses existing fixed-volume ratio mapping, retaining explicit velocity
quantization and all control guards. Source/native checks and a new exact-ROM
manual checklist are separate. This scan enables neither that grouping nor any
new reference-validation behavior.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v24
```

Use a fresh directory. Original assets, ROMs and local evidence stay outside
Git. Historical audit files and coverage remain immutable.
