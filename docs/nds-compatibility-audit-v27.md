# NDS compatibility audit v27: accepted fifteen-track STUDIO grouping

The scanner adds only the accepted SF3 STUDIO fifteen-to-eight grouping:
`[[0],[1],[2],[3],[4,5,6,7,8,12,14,15],[9],[10],[11]]`. It requires family
`ssr3`, slot4, capacity eight, exactly IDs 0–12/14/15, all tracks looping,
no fitted envelope and no active modulation. Existing shared-control,
fixed-volume, held-note-pan, long-alias/release and conversion guards remain.
The selector and scanner share `SF3_STUDIO_GROUPS`; all eight accepted
standalone outputs remain byte-identical. There is no grouping search or new
converter/native-driver capability.

All seven original variants and three pinned SDATs verify before and after
scanning all 132 slots. Only `ssr3:4 BGM_STUDIO` changes primary conversion
status. Its ROM/BPS exactly match the [accepted standalone experiment](nds-sf3-studio-fifteen-track-research.md):

- ROM CRC32: `91E9AFE6`.
- ROM SHA-256: `0a45586aee5c22835490442cf4536d3d168f21017bcb923c36583183e2f40489`.
- BPS SHA-256: `6837bbaa52b1d15ed55c689c25479d03d9c33c00ca96e3b926e6fdc8b80c0207`.

Primary packing rises from 70 to 71, with 36 exact accepted primary variants
and 41 unique accepted source sequences across both routes. Primary pending
stays 35. All 70 old primary and 29 filtered ROM/BPS pairs retain bytes, routes,
gains and manual-match flags. All 51 remaining primary blockers exceed eight
tracks. Filtered counts stay 29 packed, eleven exact accepted, eighteen pending
and 93 blocked; filtered STUDIO remains capacity-blocked. Acceptance does not
transfer between versions by song name.

All 412 tests pass without skips, including six new scanner cases for pinned
identity/groups, retained guards, plain flags, headroom/packing behavior,
model failures, attributed native/zero-velocity limits and report accounting.
Report checks verify exact accepted ROM/BPS and manifests, old packed outputs,
original inputs, source/scanner hashes, deterministic JSON/CSV/HTML/summary,
actual JavaScript filters and unchanged recursive v10–v26 archive identities.
The fifteen-track filter selects STUDIO alone; prior structure filters retain
their counts. Each known route contributes once to the standard summary column.

Reports attribute the original standalone two-cycle observation to the exact
ROM: 5,202 NOTE calls allocate, no held/starting voice is preempted, and 2,863
release-flagged channels with nonzero envelope are reused. Four source
velocity5 mappings are zero in both grouped and unpacked controls, accounting
for six native calls in that window; grouping adds no zero mappings. Events
remain retained. Fixed-volume ratio rounding and ordinary PCM8/ADSR/tempo
quantization remain. These are scoped observations, not full DS polyphony or
whole-song waveform bounds. This scan does not remeasure native evidence or
add manual acceptance. The standalone held-note crescendo, alias and stereo
checks retain their separate scope. User-reported acceptance does not imply
an independently timed recording, full gameplay trace, linked play, rematch
or comparative listening preference.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v27
```

Use a fresh directory. ROMs, original assets and local research outputs stay
outside Git. Historical artifacts and coverage remain immutable.
