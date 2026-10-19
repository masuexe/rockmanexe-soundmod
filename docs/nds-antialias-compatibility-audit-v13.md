# Star Force compatibility audit v13

The latest [v14 audit](nds-antialias-compatibility-audit-v14.md) integrates
finite D3 release snapshots and the accepted WIN2 artifact. The v13 snapshot
and its original next-research proposal below remain separate.

The report is `out/nds-research/compatibility-audit-v13/` (schema 10).
It rescans all 132 pinned Japanese Star Force 1/2/3 SSEQ slots and integrates
the accepted looping filtered-envelope combination into the audit. Archived
v10, v11 and v12 files remain byte-identical.

## Bounded route selection

The primary conversion path remains independent. Each separate filtered
attempt first uses the established plain singleton path. Only a looping
sequence that explicitly fails because non-instant DS attack needs fitting
may retry with `envelope_support=True`. The original failure remains in
`attempts`; the combined mode is named `looping_singleton_antialias_envelope`.
Every attempt records route, fitting flag and gain; each mode has its own
+3.5 dB / headroom-only 0 dB retry handling.

The report retains fitted parameters, explicitly marks gradual attack fitting
in HTML, adds a combined-mode filter, and exports `antialias_envelope_approximation`
and `antialias_attack_fits` CSV columns. Successful combined rows therefore
retain a failed plain attempt, without being classified as blocked.

Finite sequences do not enable fitted envelopes. Other conversion or model
errors do not trigger this retry, nor do packing errors. Existing source
pitch/modulation/portamento, singleton capacity, fitting quality and PCM budget
guards remain in place. Conversion, packing, runtime and manual acceptance
remain separate evidence levels; the audit performs no new batch playback.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 30 | 15 | 4 | 11 |
| ssr2 | 43 | 15 | 7 | 2 | 5 |
| ssr3 | 51 | 9 | 6 | 4 | 2 |
| Total | 132 | 54 | 28 | 10 | 18 |

All 54 primary ROM/BPS pairs, statuses, routes and gains remain identical to
v12 and the preserved v10 baseline. All 26 previously packed filtered ROM/BPS
pairs remain identical to v12. Only two filtered statuses change:

| Sequence | Previous filtered result | v13 result | Tracks / prepared samples |
| --- | --- | --- | --- |
| ssr2:11 DEMPAJIKEN | Non-instant attack fitting required | Filtered + fitted attack | 8 / 91 |
| ssr3:10 HOKORA | Non-instant attack fitting required | Filtered + fitted attack | 8 / 48 |

Both new outputs exactly match their already accepted standalone ROMs **and**
BPS patches. DS attack 100 maps to native 74, while 127 remains 255; the
fitting parameters and original plain failures are retained. They use +3.5 dB
and the unchanged ten-channel 10,512 Hz mixer. None of the 28 filtered results
requires a gain reduction in this snapshot.

There are 26 plain filtered versions and two combined versions. Exact accepted
filtered matches rise from eight to ten; the same eighteen filtered versions
remain pending. Primary exact matches stay at 21; across both routes 25 unique
source sequences have an exact accepted version. These are alternate versions
of the same 54 packable source songs, not additional source songs. No filtered-only
newly packable song is found.

The HOKORA and DEMPAJIKEN records retain their own bounded native, synthetic
and user-reported coverage. An exact match links that existing evidence; the
scan does not create more original-song loops, linked-play tests or a new
comparative listening preference.

## Remaining blockers and next research

Of 122 nonempty/nonsilent slots, 94 remain blocked in the filtered route:

- 59 exceed singleton track capacity.
- 33 encounter executed upward bend, transpose, modulation or portamento.
- SF2 WIN2 requires unsupported D3 release overrides.
- SF1 HOKORA remains blocked in source analysis.

The two non-instant attack blockers are resolved through the explicit combined
mode. The next recommended capability is finite-cue release snapshots, using
SF2 WIN2 (`ssr2:31`). It has six tracks, 67 notes, nine original waves and
only one D3 release=120 command, before track 3's notes at tick 0. All tracks
end naturally and every final gate closes by its track END. It has no
non-instant attacks or executed modulation. Support is still unimplemented;
it must preserve release behavior instead of ignoring D3. `next-research.md`
records the source timings, proposed boundaries and validation requirements.
A successful implementation could add a currently blocked source song.

SF2 HENKAN remains the first existing-route listening option in
`pending-candidates.csv`: its unfiltered baseline is accepted, while its
packable filtered finite version has no separate acceptance. This is a
listening task distinct from the proposed capability expansion.

## Validation and files

All 257 regression tests pass, including explicit fit retry, no finite or
unrelated-error retry, per-mode gain handling and visible fit/model/packing
failures. Report tests cover new CSV parameters and HTML labels/filtering.

`validation.json` verifies all 132 rows, both summaries, all previous primary
and filtered outputs, ten exact accepted filtered ROM/BPS pairs, JSON/CSV/HTML
consistency, JavaScript syntax, unchanged scanner source hashes and preserved
v10/v11/v12 snapshots. Original input identities are rechecked after the scan.

`index.html` is portable and searchable. `ready-variants.md` links all ten
accepted filtered versions with their explicit mode; `pending-candidates.csv`
lists eighteen pending versions and `blocking-details.json` groups 94 blockers.
`report.json`, `report.csv`, `summary.md`, `source-fingerprints.json`,
`archives-before.json`, `audit-scanner.py` and `regression-tests.txt` retain the
underlying data and provenance. The audit writes reports rather than a new
collection of ROM files. The production manager remains unchanged.

Reproduce into a new directory:

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v13
```

The [v12 history](nds-antialias-compatibility-audit-v12.md) retains its original
plain-filter scan and later standalone-experiment records separately.
