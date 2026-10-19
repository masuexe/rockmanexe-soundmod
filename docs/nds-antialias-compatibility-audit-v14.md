# Star Force compatibility audit v14

The report is `out/nds-research/compatibility-audit-v14/` (schema 11).
This scan integrates the already accepted SF2 WIN2 finite-release capability
across all 132 pinned Japanese SSEQ slots. Original NDS/GBA input identities
are checked before and after conversion; v10–v13 snapshots remain separate.

## Guarded release routing

Both primary and filtered routes retain their existing attempts. Only a plain
finite attempt that explicitly fails with unsupported D3 schedules a separate
release-snapshot retry. Primary route `finite_singleton_release` and filtered
route `finite_singleton_antialias_release` use the same explicit converter
flag as the accepted standalone WIN2 experiment. They retain the failed plain
attempt and independent +3.5 dB/headroom-only 0 dB attempts.

The converter requires singleton tracks, fixed tempo, all tracks ending and
every gate closed by its own END. D3 must precede the first note in execution
order on each track. D0–D2, later release updates, non-instant attacks and active
LFO remain outside this route. Existing decay/sustain/release approximations
remain; fitted attacks are not enabled. Other conversion, model or packing
errors do not trigger the D3 retry.

The CSV exports separate primary/filtered release flags and source override
parameters. HTML labels and a dedicated filter distinguish finite release
snapshots from looping fitted attacks. Report summaries retain mutually
exclusive primary statuses and count alternate versions separately.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 30 | 15 | 4 | 11 |
| ssr2 | 43 | 16 | 8 | 3 | 5 |
| ssr3 | 51 | 9 | 6 | 4 | 2 |
| Total | 132 | 55 | 29 | 11 | 18 |

All 54 previously packed primary ROM/BPS pairs and all 28 previously packed
filtered pairs remain byte-identical to v13. Only `ssr2:31 BGM_WIN2` changes
status: its primary and filtered routes both pass. This adds one source
sequence, increasing primary packable songs from 54 to 55. The filtered total
rises from 28 to 29; no filtered-only source song is found.

The new filtered WIN2 output exactly matches its accepted standalone ROM
**and** BPS patch. It retains six tracks, 67 notes, 32 prepared waves and the
single track-3 release=120 initialization at tick 0. Its gain remains +3.5 dB
with the same ten-channel 10,512 Hz mixer. The new unfiltered primary WIN2
build differs and has no manual acceptance; acceptance does not transfer
between its two versions.

Filtered modes are 20 plain looping, six plain finite, two looping fitted
attack and one finite release snapshot. The accepted filtered total rises
from ten to eleven; the same eighteen filtered variants remain pending.
Primary exact accepted matches remain 21. Across both routes, 26 unique
source sequences have an exact accepted variant, up from 25.

The scan links the existing WIN2 user-reported checklist and separately
bounded native/reference results. It performs no new playback, linked play,
manual testing or comparative preference assessment.

## Blockers and follow-up

Of 122 nonempty/nonsilent slots, 93 remain blocked in the filtered route:
59 exceed singleton capacity, 33 execute unsupported upward bend, transpose,
modulation or portamento, and one (SF1 HOKORA) fails source analysis with
`SSEQ loop end without start`. The finite D3 blocker is resolved.

The next research candidate is SF1 HOKORA (`ssr1:20`): establish the executed
loop-control behavior against independent DS execution before changing the
tracer. This is an analysis investigation, not a claim that the song will fit
or convert. `next-research.md` records this bounded proposal. Filtered SF2
HENKAN remains the first existing-route listening candidate, separately from
capability expansion.

## Validation and artifacts

All 265 regression tests pass. Added cases cover finite D3 retries, excluded
looping/unrelated/model failures, independent gain attempts, visible converter
and packing failures, primary fallback and separate CSV/HTML mode reporting.

`validation.json` verifies every row, all prior packed ROM/BPS fingerprints,
eleven exact accepted filtered ROM/BPS pairs, preserved v10–v13 files, source
fingerprints and original input identities. JSON, CSV and embedded HTML data
agree; the JavaScript syntax and actual filter predicate pass. The HTML
filters select 29 packed, eleven accepted, eighteen pending, 93 blocked, two
fitted-attack and one finite-release rows.

`index.html` is the portable searchable table. `ready-variants.md` links the
eleven accepted filtered variants with explicit modes; `pending-candidates.csv`
lists eighteen pending variants and `blocking-details.json` groups blockers.
`report.json`, `report.csv`, `summary.md`, `audit-scanner.py`,
`source-fingerprints.json`, `archives-before.json`, `scan-log.txt` and
`regression-tests.txt` retain results and provenance. The scan writes reports,
not a new batch of ROMs. The production manager and DSP are unchanged.

Reproduce into a fresh output directory:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v14
```

The [v13 audit](nds-antialias-compatibility-audit-v13.md) remains the separate
pre-release-snapshot history. The [standalone WIN2 research](nds-sf2-win2-release-antialias-research.md)
retains its exact-version acceptance and original bounded test evidence.
