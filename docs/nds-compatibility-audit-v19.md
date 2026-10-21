# NDS compatibility audit v19: variable-tempo pitch LFO

The batch scanner now retries the accepted SF2 MIZUUMI capability only after
an explicit fixed-tempo rejection. The retry requires looping tracks, instant
attacks, fixed zero-delay pitch modulation and a non-modulated conductor.
It compensates positive LFOS at global tempo changes while preserving phase
and count. At most eight distinct tempos and 128 unfolded changes are allowed.
Late activation, live depth, fitted attacks, finite/mixed tracks, filtering and
minimum-depth quantization remain excluded from this route.

## Source coverage

This run uses six verified original ROM variants and the same three pinned
family representatives/SDATs as v18, covering all 132 sequence slots. The local
`ssr2s.nds` is excluded: its SHA-256 is
`397744d5de5bc9a278f1f66001913dafc8befd0bc4cf82d449d8501781beb6b7`,
rather than the registered
`dfa8780c1f98059d466509e90004793ad89b87a7f9fce48210fca8ddc0ff3745`.
Its extracted SDAT also differs. The original file and trust policy are
unchanged; this run establishes no equivalence for that variant. Historical
seven-variant audits retain their original provenance.

## Results

Primary packing rises from 60 to 61, with 27 exact accepted primary variants.
Only `ssr2:6 BGM_MIZUUMI` changes status. Its ROM/BPS match the accepted
[standalone experiment](nds-sf2-mizuumi-variable-tempo-research.md):

- ROM SHA-256: `8156879a986056337a69ce9c0b8f6819948914c3439bd42286d1f171de6922b7`.
- BPS SHA-256: `fa57cd3e18359c54b71b66919a82a36199723a286c2470702b78cc834d3daa9b`.

All 60 previous primary and 29 filtered pairs retain their bytes, routes and
gains. Filtered counts remain 29 packed, eleven exact accepted and eighteen
pending; 32 unique source sequences have an exact accepted variant. Primary
pending remains 34. Primary blockers fall to 61 (58 capacity and three
conversion); filtered blockers remain 93. The three remaining in-capacity
conversion blockers are the SF1/SF2/SF3 SABISHI sequences.

## Verification and limits

The 339-test run has 338 passes and one explicit skip: the unavailable verified
second SF2 variant prevents its cross-variant equivalence check. The current
unverified input is still rejected; that rejection is asserted before the
skip. The initial run's external-input error is retained separately. Six new
scanner tests cover retry restrictions, precedence, gain/packing failure and
CSV/HTML counts. Exact accepted fingerprints, old packed outputs, report
rendering, real JavaScript filters and immutable v10–v18 archives are checked.

Batch success establishes conversion, packing, patch reconstruction and report
consistency. It adds no native-runtime or manual acceptance. MIZUUMI's exact
standalone acceptance remains distinct; no new gameplay trace, two-peer result
or comparative preference is inferred.

For reproduction, create a fresh source directory containing symlinks to the
six verified originals (`ssr1d`, `ssr1l`, `ssr1p`, `ssr2d`, `ssr3b`, `ssr3r`),
then run:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /path/to/verified-sources --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v19
```

Use a fresh output directory. Local reports retain input exclusions,
source/scanner hashes, test logs and validation helpers; ROMs and source assets
remain outside Git. SF1 SABISHI is a separate prospective investigation of
variable tempo, late initial activation and bounded fitted attack envelopes.
