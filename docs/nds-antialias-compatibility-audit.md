# Antialias variants in the compatibility audit

The v11 report is in `out/nds-research/compatibility-audit-v11/` (schema 9).
It scans the same 132 SSEQ slots from the three pinned Star Force archives,
with two separate results per slot: the established primary route and an
optional offline-antialias singleton variant. It does not replace the primary
route, treat a second version as a new song, run batch gameplay, or infer a
listening pass from conversion success. Archived v10 files remain separate.

`index.html` is the portable, searchable report with an antialias result
filter; `report.csv` provides one row per source slot with separate variant
columns. `report.json` retains attempts, errors, gain retries, ROM/BPS
fingerprints, prepared PCM budgets and manual-evidence associations.
`summary.md` summarizes both evidence sets.

## Results and next candidates

Primary results remain 54 packed songs, with all 54 ROM/BPS fingerprints,
routes, statuses and gains identical to v10. Antialiasing produces 25 additional
versions of those same songs, not 25 additional source songs. Four variants
exactly match accepted artifacts; 21 need independent listening/gameplay tests.
There are no antialias-only newly packable source songs. All 25 use +3.5 dB.

| Archive | Slots | Primary packed | Antialias packed | Exact accepted antialias | Antialias pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 30 | 14 | 2 | 12 |
| ssr2 | 43 | 15 | 6 | 0 | 6 |
| ssr3 | 51 | 9 | 5 | 2 | 3 |

The four ready variants are SF1 LAST, SF1 WIN2, SF3 ROOM and SF3 WIN2.
Their build options and links to existing ROMs are in `ready-variants.md`.
They have exact-version acceptance; this does not remove each experiment’s
native coverage, timing or allocation limits. Primary variants separately
have 21 exact manual matches. Across both result sets, 24 unique source
sequences have an exact match; multiple accepted versions are not extra songs.

Of 122 nonempty/nonsilent candidates, 97 do not pass the antialias route:

- 59 exceed singleton track capacity, including SF3 BATTLE, whose primary
  path uses the existing special merge and remains available.
- 33 encounter the guard against upward bend, transposition, modulation or
  portamento. These are executed-state checks, including live controls.
- Two require non-instant attack fitting: SF2 DEMPAJIKEN and SF3 HOKORA.
- SF2 WIN2 uses unsupported D3 release overrides.
- SF1 SETSUNAI has a note-free conductor track; the singleton converter
  currently raises `max() iterable argument is empty` when processing it.
  This is a converter limitation to investigate, not an invalid source song.
- SF1 HOKORA retains its source sequence-analysis failure.

Current prepared PCM budgets range from 46,356 to 1,208,770 bytes; none of
the 25 passing variants reaches the 4,000,000-byte limit. ROM-size changes
relative to the primary variants range from -50,924 to +735,312 bytes. These
differences also reflect direct versus singleton compilation where applicable.

Recommended next tests, all with an already accepted unfiltered counterpart:

| Priority | Candidate | Tracks / prepared waves | Purpose |
| --- | --- | --- | --- |
| 1 | SF2 / 30 WIN | 7 / 89 | First accepted antialias test from the second game; compare against its existing baseline |
| 2 | SF1 / 23 KINCHO | 8 / 86 | Eight-track tension music with known unfiltered behavior |
| 3 | SF3 / 31 KANDO | 7 / 84 | Compare another established looping baseline |

`pending-candidates.csv` lists all 21 unaccepted filtered variants. The shortlist
is a test recommendation, not a perceptual score. Neither it nor the full scan
creates gameplay acceptance or adds these choices to the production manager.

All 240 Python regression tests pass. `validation.json` verifies all 132 rows,
both summaries, CSV/JSON/HTML consistency, JavaScript syntax, unchanged v10
files and exact matching against existing accepted ROMs and manifests.

## Policy and evidence

Every nonempty sequence within the eight-track capacity gets an independent
singleton attempt. All-END sources use the finite converter; looping sources
use its existing loop model. The first gain is +3.5 dB; an explicit volume
headroom failure permits a recorded 0 dB retry. No unsupported track merge,
native LFO, fitted envelope, upward bend, transposition, modulation or
portamento is silently substituted. Downward bends and the existing alias,
TIE/EOT and loop-carry validators remain supported within their bounds.

The offline FIR, source step 1/16–32, 1,000,000-sample per-wave limit and
4,000,000-byte song PCM budget are the existing converter policy. The native
mixer remains at 10,512 Hz with ten channels for this scan. Allocation,
PCM8, filter/phase quantization, envelope and tuning differences remain.
Filtering can change timbre, so a successful build is a candidate for testing,
not evidence that its audio improved. Recorded PCM8 quantizer clamping is
separate from clipping or saturation of an actual native full mix.

A packed variant passes independent MPlay reparsing, shared export bounds,
native-data preservation and BPS reconstruction. ROM and BPS fingerprints
are retained; the audit writes reports rather than generating a collection
of new ROM files. Per-slot checkpoints keep partial scans explicitly marked
incomplete until all archives and original-input checks finish.

Manual evidence requires `user_reported_pass`, a matching actual ROM and
build-manifest fingerprint, and an exact matching output SHA for the same
family and sequence. A rejected unfiltered build or a listening-only diagnostic
improvement does not qualify. An older accepted unfiltered ROM does not
accept a different antialias ROM. The exact existing reports retain their
own measured versus user-reported scope; the batch does no new playback.

## Verification and reproduction

The report validator checks all baseline packed ROM/BPS fingerprints, routes,
gains and statuses against v10, all 132 secondary results, counters, CSV/JSON/
HTML agreement, JavaScript syntax and exact manual matches against the real
artifacts. An archived-file hash inventory confirms v10 is not rewritten.
Unit regressions cover separate-variant accounting, finite/loop selection,
neutral-gain retry, capacity skips, model versus packing failures, and strict
manual manifest checks, in addition to the established converter tests.

Use a fresh output directory:

```bash
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-antialias-audit-example
```

Omit `--antialias-variants` for primary-only scanning. Neither mode adds songs
to the production manager. Scan timing depends on offline FIR preparation;
its standard-library implementation is deliberately bounded and does not
change the native mixer.
