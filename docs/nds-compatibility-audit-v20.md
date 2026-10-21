# NDS compatibility audit v20: variable tempo with late enable and attack fitting

The scanner integrates the accepted SF1 SABISHI capability as a separate retry
after an explicit fixed-tempo error on the envelope/pitch-LFO route. All source
tracks must loop. Both variable-tempo compensation and bounded fitted attacks
are explicit; depth-zero notes may precede a single late enable, after which
positive depth and all other modulation parameters must remain fixed. Active
delays, disabling, live changes, minimum depth, filtering and finite/mixed tracks
remain excluded. Existing fit limits, eight-tempo/128-change budgets and the
non-modulated conductor guard are unchanged. Old routes keep precedence.

## Source coverage and results

The same six verified ROM variants and three pinned family SDATs as v19 cover
all 132 SSEQ slots. The six-source selection retains the v19 snapshot, where `ssr2s.nds` had an
unregistered fingerprint and different SDAT. During this work the current file
again matches the registered original. Separate verification confirms all seven
original ROMs, identical within-family SDATs and unchanged representatives. The
conversion scan remains explicitly scoped to its six selected variants; current
seven-source verification is recorded separately. No original asset was changed
by this workflow. The full regression run executes the second-variant equivalence
check successfully; historical v19 error/skip observations remain unchanged.

Primary packing rises from 61 to 64. Only SF1/SF2/SF3 SABISHI (`ssr1:36`,
`ssr2:36`, `ssr3:33`) change status. All 61 prior primary and 29 filtered ROM/BPS
pairs retain their bytes, routes and gains. SF1 SABISHI exactly matches its
[accepted standalone ROM](nds-sf1-sabishi-variable-late-envelope-research.md),
SHA-256 `c8469f1b4554886c72dd24865d327c95d63b4a9470391ad7c3426f400b8212ed`,
and BPS SHA-256
`af3c5f8b176b35dc321cc7fe06c6f4c70342974bde2db684ff47c879d4c12146`.

There are now 28 exact accepted primary variants and 33 unique source sequences
with an exact accepted variant. Filtered counts remain 29 packed, eleven exact
accepted and eighteen pending. Primary pending rises to 36. The remaining 58
primary blockers all exceed the eight-track conversion capacity; no in-capacity
conversion blocker remains in this pinned source set. Filtered blockers remain
93. This is bounded conversion coverage, not general support for arbitrary NDS
music or playback acceptance of all packed songs.

Six new scanner tests cover exact retry triggers, fit/loop restrictions,
explicit flags, old-route precedence, headroom/packing failure and exclusive
CSV/HTML/summary accounting. The full 350-test run passes all 350 cases, including the restored second-variant
equivalence check. Report verification checks old pairs, accepted
fingerprints, source/scanner hashes, deterministic rendering, real JavaScript
filters and unchanged archived v10–v19 file identities.

## Manual and runtime limits

Batch conversion adds no native playback, reference rendering or manual checks.
SF1 acceptance retains the exact standalone checklist and its recorded limits.
SF2 happens to generate the same ROM/BPS as SF1, but this report preserves
family-specific manual-record matching: it does not invent an SF2 report.
SF3 differs and remains pending. A separate SF3 standalone investigation checks
its original note gates, resources and native behavior before any new manual
request. Acceptance never transfers by song name alone.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir out/nds-research/compatibility-audit-v19-preparation/verified-sources \
  --base ../roms/exe6.gba --antialias-variants \
  --out out/nds-research/compatibility-audit-v20
```

Use a fresh output directory. The verified source directory contains only six
symlinks, as recorded in v19. Local reports retain exclusions, inputs, scanner
and archive fingerprints, logs and independent verification helpers. Original
assets, ROMs and ignored research outputs stay out of Git.
