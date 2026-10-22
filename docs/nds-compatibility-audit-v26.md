# NDS compatibility audit v26: accepted fourteen-track AJITO grouping

The scanner adds only the accepted SF3 AJITO grouping: sources 0/4/6/7/8/11/14
share one native track; the other seven sources remain independent. The route
requires family `ssr3`, slot7, capacity eight, exactly source IDs 0–11/14/15,
all tracks looping, no fitted envelope and no active modulation. Existing
shared-control, fixed-volume, held-note-pan, alias/release and conversion guards
remain unchanged. Existing fixed-volume ratio mapping retains its velocity
quantization. The selector and scanner share `SF3_AJITO_GROUPS`; all eight
accepted standalone outputs remain byte-identical. No automatic grouping
search or new converter/native-driver capability is enabled.

## Results

All seven original variants and three pinned SDATs verify before and after
scanning all 132 slots. Only `ssr3:7 BGM_AJITO` changes primary conversion status.
Its ROM/BPS match the [accepted standalone experiment](nds-sf3-ajito-fourteen-track-research.md):

- ROM SHA-256: `e7e3331fa5d3c12f75a3719db59a7ae78862439e85a3e091de23966fd09149c1`.
- BPS SHA-256: `fb89025a998c2da15e7f32cf2a216b177a2b03df053d37143f42fe9adb9da7db`.

Primary packing rises from 69 to 70, with 35 exact accepted primary variants
and 40 unique accepted source sequences across both routes. Primary pending
stays 35. All 69 old primary and 29 filtered ROM/BPS pairs retain bytes, routes,
gains and manual-match flags. The remaining 52 primary blockers exceed eight
tracks. Filtered counts stay 29 packed, eleven exact accepted, eighteen pending
and 93 blocked; filtered AJITO remains capacity-blocked. Different variants
do not inherit acceptance by song name.

## Verification and limits

All 404 tests pass, including six new scanner cases covering exact identity,
structure and groups, plain flags, retained converter guards, headroom/packing
behavior, visible model failures, attributed native observations, quantization
metadata and report accounting. Report checks verify exact accepted ROM/BPS
and manifests, old packed identities, original inputs, source/scanner hashes,
deterministic reports, actual JavaScript filters and unchanged archived
v10–v25 identities. The fourteen-track filter selects AJITO alone; the known
nine-/ten-/eleven-/twelve-/thirteen-track filters each retain one song. All
contribute once to the standard summary column.

Reports pin the standalone two-cycle native observation to its exact ROM:
all 3,964 NOTE calls allocate, but fourteen held/starting voices are preempted,
plus 1,544 release-channel reuses with nonzero envelope. Volume-ratio
quantization also remains explicit. This scan neither remeasures these limits
nor adds native/manual acceptance. The standalone long-cycle, four-alias,
control/dynamics and frame-clock proofs retain their separate scopes. The user
reported the requested three-minute listening/effects/three-encounter checklist
passed. No independently timed recording, full gameplay trace, linked-play/
rematch result or comparative preference is inferred; successful packing does
not establish complete DS polyphony or waveform fidelity.

## Continuing investigation

A separate SF3 STUDIO experiment studies fifteen sources in eight tracks under
the existing fixed-volume mapping. Its two long aliases, held-note expression
crescendo, changing singleton volume, extreme soft-note quantization and native
voice-budget evidence require separate checks and a new exact-ROM manual
checklist. No STUDIO route or generic grouping search is enabled by this scan.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v26
```

Use a fresh directory. ROMs, original assets, captures and local research
outputs remain outside Git. Historical files and coverage remain immutable.
