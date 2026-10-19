# Star Force compatibility audit v12

The report is `out/nds-research/compatibility-audit-v12/` (schema 9).
It rescans all 132 SSEQ slots in the pinned Japanese Star Force 1/2/3 archives,
using the current converter and exact-version manual evidence after the
[SETSUNAI conductor fix](nds-sf1-setsunai-antialias-research.md).
Archived v10/v11 files remain byte-identical; this is a new snapshot.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 30 | 15 | 4 | 11 |
| ssr2 | 43 | 15 | 6 | 1 | 5 |
| ssr3 | 51 | 9 | 5 | 3 | 2 |
| Total | 132 | 54 | 26 | 8 | 18 |

All 54 primary ROM/BPS fingerprints, routes, gains and statuses match v11
(and the preserved v10 primary baseline). All 25 previously packed filtered
ROM/BPS pairs also match v11. SETSUNAI (`ssr1:25`) is the only filtered status
change: conversion-blocked becomes packed, matching its newly accepted ROM
and BPS exactly, with seven tracks and 72 prepared waves.

The filtered count increases from 25 to 26; exact accepted filtered versions
increase from four to eight; filtered candidates awaiting exact-version manual
acceptance decrease from 21 to 18. The newly matched records are SF1 KINCHO,
SF1 SETSUNAI, SF2 WIN and SF3 KANDO. The other four are SF1 LAST, SF1 WIN2,
SF3 ROOM and SF3 WIN2. Primary exact manual matches remain 21; across both
routes 25 unique source sequences have an exact accepted variant.

These are alternate versions of the same 54 packable source songs. There
are no filtered-only newly packable songs. Packing does not establish audio
quality, native runtime coverage or gameplay acceptance. Existing manual
records retain their own user-reported duration and test scope.

## Remaining blockers and next research

Of 122 nonempty/nonsilent slots, 96 do not pass the filtered route:

- 59 exceed singleton track capacity.
- 33 encounter the executed-state guard against upward bend, transpose,
  modulation or portamento.
- Two need non-instant attack fitting: SF3 HOKORA and SF2 DEMPAJIKEN.
- SF2 WIN2 needs unsupported D3 release overrides.
- SF1 HOKORA remains blocked in source analysis.

The SETSUNAI empty-note-volume error is no longer a current blocker. The
archived v11 failure remains visible in the previous report.

The recommended next capability is combining offline filtering with the
existing fitted attack envelopes, starting with SF3 HOKORA. Its unfiltered
envelope version already has user acceptance; it has eight tracks, sixteen
source waves, one non-instant attack definition, and no executed modulation,
nonzero bend or envelope overrides. SF2 DEMPAJIKEN supplies a later cross-game
check for the same limitation. This report does not enable the combination,
change the native mixer or add choices to the production manager.

For an additional listening test using existing conversion capabilities,
SF2 HENKAN is the first pending candidate: its filtered finite version packs
and its unfiltered counterpart has acceptance. That is a separate testing
option, rather than the proposed envelope/filter capability expansion.
`next-research.md` describes the proposed scope and evidence requirements.

## Files and validation

- `index.html`: portable searchable report with separate primary/filtered
  results and exact-acceptance filters.
- `report.json`, `report.csv`, `summary.md`: full attempts, summaries,
  gains, ROM/BPS fingerprints, budgets and manual-evidence associations.
- `ready-variants.md`: links and build choices for all eight exact accepted
  filtered versions. `pending-candidates.csv` lists all eighteen pending
  versions; `blocking-details.json` groups the remaining 96 blockers.
- `validation.json`, `validate-report.py`: all 132 rows, both summaries,
  exact ROM/BPS evidence, JSON/CSV/HTML consistency, JavaScript syntax,
  old snapshots and current scanner source hashes are checked.
- `archives-before.json`, `source-fingerprints.json`, `audit-scanner.py`:
  snapshot/source provenance. `regression-tests.txt`: 247 tests pass.

Original input identities are rechecked after the scan. Primary and filtered
attempts retain independent gain/headroom handling and evidence; all 26
filtered successes use +3.5 dB, ten PCM channels and the existing 10,512 Hz
mixer. The audit writes reports, with no new batch audio or gameplay tests,
and no collection of newly exported ROM files.

Reproduce into a new output directory:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v12
```

The [v11 history](nds-antialias-compatibility-audit.md) preserves its original
counts separately from subsequent song-specific acceptance.

## Subsequent combination experiment

The [HOKORA filtered-envelope experiment](nds-sf3-hokora-antialias-envelope-research.md) now enables this combination through a separate opt-in research build. Source, packed-tone, one natural loop, bounded native envelope and controlled lifecycle checks pass. On 2026-10-19 the user reported no issues after the requested listening/gameplay checklist, accepting this exact combined-mode ROM. Automated coverage remains one natural track loop and a separate 1,800-frame envelope window. The archived v12 report and counts remain unchanged, since its filtered route does not request fitted envelopes.
