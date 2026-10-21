# Star Force compatibility audit v18

Report: `out/nds-research/compatibility-audit-v18/` (schema 15).
This refresh integrates the exact accepted SF2 VS late-activation/live-depth
mode across all 132 pinned Japanese SSEQ slots. Inputs are verified before and
after conversion; archived v10–v17 snapshots remain separate.

## Guarded late activation

Only the plain positive-live-depth route's exact activation-timestamp
`ValueError` schedules the new separate route, after existing routes. All source
tracks must loop, fit capacity and need no fitted envelope. It explicitly
enables the accepted singleton delayed positive-depth/late-enable mode.
The converter retains fixed tempo/type/speed/range/delay guards; disabling,
fitting, minimum-depth quantization, filtering, mixed/finite structures and
toggle combinations remain excluded. Assertions and unrelated errors do not
schedule this retry. Each mode keeps independent +3.5 dB/headroom-only 0 dB
attempts and visible conversion/packing failures.

At late enable, MOD and nonzero LFOS restore the configured frequency without
resetting shared phase/count. Other compiler modes, native driver and DSP
remain unchanged by this scanner integration. CSV exports the complete late-
activation policy; HTML adds a separate late-enable filter. Its distinct status
contributes once to the existing plain live-depth summary column.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 32 | 15 | 4 | 11 |
| ssr2 | 43 | 18 | 8 | 3 | 5 |
| ssr3 | 51 | 10 | 6 | 4 | 2 |
| Total | 132 | 60 | 29 | 11 | 18 |

All 59 old primary and 29 filtered ROM/BPS pairs retain their bytes, routes and
gains. Only `ssr2:37 BGM_VS` changes primary status, and its ROM and BPS exactly
match the accepted standalone experiment:

- ROM SHA-256: `9f8e72d738aeb88d289145508efe12e6b2c347efc0b9c4b5b0d02f639ce2f215`.
- BPS SHA-256: `4aa58848895032367bc60be5ec4bd05752b061555cae2bf6db326b8b586f170b`.

It retains eight tracks, eighteen prepared waves and +3.5 dB gain. No fitted
attack or minimum-depth mode is added. The filtered route still rejects active
modulation, and no alternate version inherits acceptance by name.

Primary counts rise to 60 packed and 26 exact accepted. Filtered counts stay
29 packed, eleven exact accepted and eighteen pending. Across both routes,
31 unique source sequences have an exact accepted version. Mixed/minimum-depth
counts remain two/four. Pending lists retain 34 primary and eighteen filtered
versions. Primary blockers fall to 62 (58 capacity, four conversion); filtered
blockers remain 93. The four remaining in-capacity conversion blockers all use
variable tempo: SF1/SF2/SF3 SABISHI and SF2 MIZUUMI.

## Verification and limits

All 323 regression tests pass. New cases cover the explicit late retry, error/
structure/fitting exclusions, old-route precedence, per-mode headroom handling,
packing failure, exclusive counts and CSV/HTML policy. Report verification
checks every old packed pair, exact accepted matches against actual ROM/BPS
and manifests, original inputs, source/scanner hashes, deterministic report
rendering, real JavaScript predicates and archived v10–v17 file identities.

This scan adds conversion/model/packing/BPS/report evidence. It adds no native
playback, reference render, listening or gameplay acceptance. The
[standalone VS record](nds-sf2-vs-late-depth-research.md) retains the user's
explicit confirmation that all three requested checks passed for its exact
ROM. No independently timed trace, two-peer/rematch result or comparative
preference is inferred. Source VS itself has no carried-positive-depth
reference coverage; that limitation remains separate from native model checks.

## Continuing research

SF2 MIZUUMI (`ssr2:6`) is the next bounded candidate: eight looping tracks,
six executed tempos (80/85/90/100/110/120), instant attacks and fixed zero-delay
pitch modulation on tracks 2/7. Its independent 180-second source render
matches 4,217 notes, 24 decoded waves, 25 tempo and eight depth controls.
A new explicit variable-tempo mode needs frequency compensation at global
tempo changes and current-tempo note initialization while preserving phase.
Simply removing the fixed-tempo guard would change modulation frequency.

This investigation is separate from the v18 counts and acceptance. A later
native experiment must check actual tempo rates, held-note phase, complete
loops, allocation evidence, packed resources and old ROM/BPS identities, then
request one final exact-ROM listening/gameplay checklist.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v18
```

Use a fresh directory. Reports, source/archive fingerprints, scan/test logs,
`audit-scanner.py` and local verification helpers retain provenance. Original
assets, ROMs and ignored research outputs stay out of Git.
