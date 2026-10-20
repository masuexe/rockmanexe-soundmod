# Star Force compatibility audit v16

Report: `out/nds-research/compatibility-audit-v16/` (schema 13).
This refresh integrates the accepted SF1/SF3 LOSE live/weak-depth combination
across all 132 pinned Japanese SSEQ slots. Original inputs are verified before
and after conversion. Archived v10–v15 reports remain separate.

## Guarded retry and reporting

Existing routes retain precedence. Only the plain or fitted live positive-depth
route's explicit native-parameter representation `ValueError` schedules its
corresponding minimum-depth retry, after the existing routes. All source
tracks must loop and fit the target capacity. The new attempts reuse exactly
the accepted singleton, fixed-tempo, fixed type/speed/range/delay and initial
activation guards. The fitted mode is explicit; failure history and each
mode's independent +3.5 dB/headroom-only 0 dB attempt remain visible.

Model assertions, unrelated conversion/packing errors, mixed or finite scores,
filtering and live-toggle behavior do not enable this new retry. Default
converters and native DSP/driver behavior are unchanged. The established
HOKORA mixed minimum-depth path remains separate and byte-identical.

Two primary statuses distinguish plain and fitted live/minimum-depth results.
CSV retains both live-depth flags and the complete minimum-depth policy;
HTML's minimum-depth filter now includes both mixed and all-loop results.
The two live-depth summary columns include their separately labeled minimum-
depth subroutes, so all primary columns remain exclusive. Mixed counts remain
separate. MOD=1's ten-cent all-phase/five-cent isolated one-second RMS bounds
apply only to sub-resolution quantization, not the whole song's deeper LFO.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 32 | 15 | 4 | 11 |
| ssr2 | 43 | 16 | 8 | 3 | 5 |
| ssr3 | 51 | 10 | 6 | 4 | 2 |
| Total | 132 | 58 | 29 | 11 | 18 |

All 56 prior primary ROM/BPS pairs and all 29 prior filtered pairs retain their
bytes, routes and gains. Only `ssr1:32 BGM32LOSE` and `ssr3:42 BGM_LOSE` change
primary status; filtered statuses remain unchanged. Both new primary outputs
exactly match their separately accepted standalone ROM **and** BPS patch:

- SF1 LOSE: fitted live/minimum depth, ROM SHA-256
  `6ea941a10b47c5afd0e140fb66fa1608d9a17e4b2679809ec9fc30b8478e7bd5`.
- SF3 LOSE: plain live/minimum depth, ROM SHA-256
  `cdd4cd3c85d7ee962a6df87ec4c52f7ff34752f59b3d36dd275c401371e104c2`.

They retain +3.5 dB gain, seven tracks and their respective sixteen/fourteen
prepared waves. Both filtered attempts remain blocked by active modulation;
no acceptance transfers between alternate versions or games by name.

Primary packable songs rise from 56 to 58, and exact accepted primary versions
from 22 to 24. Filtered totals stay at 29 packed, eleven exact accepted and
eighteen pending. Across both routes, 29 unique source sequences now have an
exact accepted version. There are three minimum-depth primary versions (one
mixed, two looping live-depth); only the two LOSE songs are added by this scan.
No filtered-only source song is found.

## Verification and limits

All 299 regression tests pass. New tests cover independent plain/fitted retries,
mode and error-type exclusions, old-route precedence, per-mode headroom retry,
visible packing failure and exclusive summary/CSV metadata. The source and
native checks supporting LOSE acceptance remain in the separate
[SF1](nds-sf1-lose-live-min-depth-research.md) and
[SF3](nds-sf3-lose-live-min-depth-research.md) research records.

`validation.json` verifies every prior packed fingerprint, all exact accepted
matches against actual ROM/BPS/manifests, source inputs and scanner hashes.
JSON, CSV, embedded HTML and exclusive summary counts agree; the final renderer
reproduces its outputs. Actual JavaScript predicates select three minimum-
depth versions, one mixed version and one exact accepted mixed version.
All archived v10–v15 file identities remain unchanged.

This scan performs conversion/model/packing/BPS and report verification. It
adds no new emulator playback, software DS render, listening or gameplay
acceptance. Existing user-reported acceptance remains tied to the exact ROM
and original checklist, with no independently timed trace, two-peer/rematch
result or comparative listening preference inferred.

`ready-variants.md` links exact accepted primary/filtered versions. The two
pending CSVs retain 34 primary and eighteen filtered versions without exact
manual matches. `blocking-details.json` records 64 primary blockers (58 capacity,
six conversion) and 93 filtered blockers. Alternate version counts may refer
to the same source song. Reports are written without a new batch of ROMs.

## Continuing research

The next bounded candidate is SF2 LOSE (`ssr2:32`). Its finite source track 15
ends at tick 911, with every gate closed by that END, after the current original
shared entry of 864. Its independent 60-second source check passes 2,721 notes
and fourteen wave decodes, with preserved live-depth counters. Selecting a later
common entry by a whole period, and explicitly combining mixed tracks with
live depth/fitted attacks, are separate capabilities not enabled by this scan.
A later native experiment must prove the finite track plays once and remains
ended through both jumps. `next-research.md` retains the bounded proposal.

Reproduce into a fresh directory:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v16
```

`report.json`, `report.csv`, `index.html`, `summary.md`, `audit-scanner.py`,
source/archive fingerprints, scan/test logs, `validate-report.py` and filter
validation retain provenance. Original game assets and ROMs stay out of Git.
