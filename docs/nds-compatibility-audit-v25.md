# NDS compatibility audit v25: accepted thirteen-track CHANGE grouping

The scanner adds only the accepted SF3 CHANGE grouping. Sources 4/6/7/9/14/15
share one native track; the remaining seven sources stay independent. The route
requires family `ssr3`, slot47, capacity eight, exactly source IDs 0–9/13–15,
all tracks looping, no fitted envelope and no active modulation. Existing
shared-control, fixed-volume, held-note-pan, alias/release and conversion guards
remain unchanged. Fixed-volume ratio mapping retains its existing velocity
quantization. The selector and scanner share `SF3_CHANGE_GROUPS`; all eight
accepted outputs remain byte-identical. There is no automatic grouping search
or new converter/native-driver capability.

## Results

All seven original variants and three pinned family SDATs verify before and
after scanning all 132 slots. Only `ssr3:47 BGM_CHANGE` changes primary
conversion status. Its ROM/BPS match the
[accepted standalone experiment](nds-sf3-change-thirteen-track-research.md):

- ROM SHA-256: `34a58369565907c3713ca92bef337cabf7dd14435fe401fb10ff34387aa36575`.
- BPS SHA-256: `901420858ca8bde5d9ad7222a3ddfae1f791d248fbff9fe27e2ba924fc5a550a`.

Primary packing rises from 68 to 69, with 34 exact accepted primary variants
and 39 unique accepted source sequences across both routes. Primary pending
stays 35. All 68 old primary and 29 filtered ROM/BPS pairs retain bytes, routes,
gains and manual-match flags. All 53 remaining primary blockers exceed eight
tracks. Filtered counts stay 29 packed, eleven exact accepted, eighteen pending
and 93 blocked; filtered CHANGE remains capacity-blocked. Different variants
do not inherit acceptance by name.

## Verification and limits

All 396 tests pass, including six new scanner cases covering exact identity,
structure and groups, explicit plain flags, retained converter guards,
headroom/packing behavior, visible model failures, attributed native limits,
velocity-quantization metadata and report accounting. Reports verify accepted
ROM/BPS/manifests, old packed identities, original inputs, source/scanner hashes,
deterministic rendering, actual JavaScript filters and unchanged archived
v10–v24 identities. The thirteen-track filter selects CHANGE alone; the
nine-/ten-/eleven-/twelve-track filters retain their one known song each.
All contribute once to the standard summary column.

Reports pin the standalone native observation to its exact ROM SHA-256:
1,339 NOTE calls allocate, but four held/starting channels are preempted in the
intro at clocks352/360/372/376, plus 183 release-channel reuses with nonzero
envelope. The additional fixed-volume ratio quantization also remains explicit.
This scan neither remeasures these limits nor adds native/manual acceptance.
The standalone source9 intro-only reference checks, long-alias holds/releases,
source/native control checks and user-reported listening/effects/three-encounter
acceptance retain their separate scopes. No independently timed recording,
full gameplay trace, linked-play/rematch result or comparative preference is
inferred. A packed exact variant does not imply full DS waveform fidelity.

## Continuing investigation

A separate SF3 AJITO experiment studies fourteen sources in eight native tracks,
using the existing fixed-volume ratio mapping. Its long common cycle, four long
aliases, independent changing volume/expression, source/native evidence and
new exact-ROM manual checklist are separate. No AJITO route or generic search
is enabled by this scan.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v25
```

Use a fresh directory. ROMs, original assets, captures and ignored local research
outputs stay outside Git. Historical audit files and coverage remain immutable.
