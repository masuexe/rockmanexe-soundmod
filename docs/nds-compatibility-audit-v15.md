# Star Force compatibility audit v15

The report is `out/nds-research/compatibility-audit-v15/` (schema 12).
It integrates the already accepted SF1 HOKORA mixed-track capability into the
same 132 pinned Japanese SSEQ slots. Input ROM/SDAT identities are checked
before and after conversion. Archived v10–v14 reports remain separate.

## Mixed-track routing

Existing routes take precedence. Only an in-capacity score containing both
finite and looping source tracks receives additional singleton mixed attempts:
plain, then fixed-delay native pitch LFO when active modulation is present.
The explicit minimum-depth retry is scheduled only after that mixed LFO
attempt raises the established parameter-representation `ValueError`.
Model assertions, unrelated conversion errors and packing failures do not
schedule the minimum-depth retry. Each mode preserves its failed attempts
and independent +3.5 dB/headroom-only 0 dB retry.

The converter retains the accepted experiment's limits: fixed tempo, finite
notes closing their gates by their own END, and finite tracks ending no later
than the original shared loop entry. Finite tracks receive FINE once; looping
tracks expand to a common period of at most 16,384 ticks and at most eight
times each source period. Intro-only tied closures stay outside the repeated
body. Filtering, fitted attacks and release overrides are excluded.

Minimum-depth pitch modulation retains the explicit MOD=1 approximation,
with all-phase pitch difference bounded by ten cents and isolated one-second
RMS error bounded by five cents. Source controls remain intact. Native shared
track phase, triangle versus DS sine, voice budget and envelope differences
remain fidelity limits. This scan does not expand that policy to purely
looping or purely finite scores.

The report exports mixed finite ENDs, source periods, common entry/period and
minimum-depth policy as separate CSV fields and full JSON metadata. Dedicated
HTML filters select mixed, minimum-depth and exact accepted mixed versions.
Primary status categories remain mutually exclusive; filtered versions are
counted separately.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 31 | 15 | 4 | 11 |
| ssr2 | 43 | 16 | 8 | 3 | 5 |
| ssr3 | 51 | 9 | 6 | 4 | 2 |
| Total | 132 | 56 | 29 | 11 | 18 |

All 55 previously packed primary ROM/BPS pairs and all 29 previously packed
filtered pairs retain their exact bytes, routes and gains. Only SF1 HOKORA
(`ssr1:20 BGM20HOKORA`) changes status. Its primary route now packs through
mixed fixed-delay LFO with minimum-depth quantization. Its ROM and BPS match
the exact standalone version accepted by the user on 2026-10-20. The filtered
route now reaches conversion and rejects active modulation; it receives no
acceptance from the unfiltered version.

HOKORA preserves seven tracks, twelve prepared PCM waves, finite track 6's
END at tick 1536, source periods 1536/3072, and common entry/period 4644/3072
after the existing LFO warmup. Gain remains +3.5 dB with ten PCM channels at
10,512 Hz. Its ROM SHA-256 is
`27fa4091ba1b2037379049a60b8277cf329314c4e79d303437f15d43591a13ad`;
BPS SHA-256 is
`a4062af4c31013952041b58c9865ab206145d716eeb0fe6683dae296dca114cb`.

All 122 nonempty/nonsilent candidates now complete source analysis. Primary
packing rises from 55 to 56 songs, with 22 exact accepted primary versions.
Filtered totals remain 29 packed, eleven exact accepted and eighteen pending.
Across both routes, 27 unique source sequences have an exact accepted version.
The scan finds no additional packable song beyond HOKORA and no filtered-only
song. Primary and filtered pending versions remain separate artifacts;
packing success alone does not establish listening or gameplay acceptance.

## Verification and coverage

All 285 regression tests pass. Added audit cases cover plain/delayed mixed
routing, minimum-depth retry guards, independent gain attempts, old-route
precedence, pure-score/capacity exclusions, visible packing failures and
exclusive report counts with separately exported parameters.

`validation.json` checks all prior packed fingerprints, every manual match
against the actual ROM/BPS/manifest, and exact HOKORA conversion metadata.
The final renderer reproduces JSON/CSV/HTML/summary bytes; embedded data and
exclusive summary counts agree. Actual JavaScript filter predicates and
syntax pass. All archived v10–v14 files and scanner source fingerprints
retain their identities; original game inputs remain unchanged.

This is batch conversion, native-command-model, packing and BPS reconstruction
evidence. It performs no new emulator playback, DS reference rendering,
listening or gameplay tests. HOKORA's earlier bounded native/reference checks
and user-reported acceptance remain in the
[standalone research record](nds-sf1-hokora-mixed-delay-research.md). Its manual
scope is not enlarged by this scan. The user's temporary silent environment
does not affect these automated checks; new listening acceptance remains
pending for unmatched versions.

## Artifacts and follow-up

`index.html` is the portable searchable report. `ready-variants.md` links exact
accepted primary and filtered versions. `pending-primary-candidates.csv` and
`pending-candidates.csv` retain 34 primary and eighteen filtered versions
without exact manual matches. `blocking-details.json` groups 66 primary and
93 filtered blockers. These are version counts and may share source songs.

`report.json`, `report.csv`, `summary.md`, `audit-scanner.py`,
`source-fingerprints.json`, `archives-before.json`, `scan-log.txt`,
`regression-tests.txt`, `validate-report.py` and `html-filter-validation.json`
retain provenance and reproducible checks. The audit writes reports rather
than another batch of ROMs. The production manager and mixer are unchanged.

The remaining blockers and a bounded next research proposal are recorded in
`next-research.md`. A source-only preflight of the eight remaining in-capacity
blocked scores identifies SF1 LOSE, followed by SF3 LOSE, as a useful next
candidate: seven looping tracks at fixed tempo 115 combine live positive
depth changes with weak depth 3 modulation. Combining those two established
approximations requires independent execution and phase/delay evidence before
extending conversion. SF2 LOSE separately has a finite END after the current
mixed-entry limit; SABISHI and MIZUUMI need tempo-aware modulation work. These
preflight observations establish no new playback or conversion support.

Filtered SF2 HENKAN remains an existing-route listening candidate for a later
session with sound; it is not automatically accepted.

Reproduce into a fresh directory:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v15
```
