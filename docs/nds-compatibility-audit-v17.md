# Star Force compatibility audit v17

Report: `out/nds-research/compatibility-audit-v17/` (schema 14).
This refresh integrates the exact accepted SF2 LOSE mixed/live-depth experiment
across all 132 pinned Japanese SSEQ slots. Inputs are verified before and after
conversion. Archived v10–v16 reports remain separate.

## Explicit mixed live-depth retry

Existing routes retain precedence. Only the mixed fixed-delay route's exact
fixed-parameter `ValueError`, on a score containing both finite and looping
tracks and executed positive depth changes, schedules the new explicit modes.
Plain and fitted attacks remain separate attempts. The converter retains
singleton, fixed-tempo, fixed type/speed/range/delay and positive-depth guards;
the entry may advance by at most one complete common period. Finite gates must
close by END, and the one-shot tracks receive FINE without GOTO. Filtering,
finite-only, release-override and live-toggle combinations remain excluded.

Assertions and unrelated failures do not enable the retry. Each mode retains
its own +3.5 dB/headroom-only 0 dB attempts, and conversion/packing failures
remain visible. The old HOKORA route and the separate looping live/minimum-depth
routes retain precedence and their original policies. Default conversion and
the native manager/driver/mixer are unchanged by this scanner integration.

Two statuses distinguish plain/fitted mixed live/minimum depth. CSV exposes the
complete bounded extension, source periods, finite endings and minimum-depth
policy. HTML's mixed/accepted/minimum filters include the new result. Summary
columns remain exclusive: the mixed minimum-depth column includes its live-
depth subroutes. MOD=1's ten-cent all-phase/five-cent isolated RMS bounds apply
to weak quantization, not whole-song fidelity.

## Results

| Archive | Slots | Primary packed | Filtered packed | Exact accepted filtered | Filtered pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 32 | 15 | 4 | 11 |
| ssr2 | 43 | 17 | 8 | 3 | 5 |
| ssr3 | 51 | 10 | 6 | 4 | 2 |
| Total | 132 | 59 | 29 | 11 | 18 |

All 58 prior primary and 29 prior filtered ROM/BPS pairs retain their bytes,
routes and gains. Only `ssr2:32 BGM_LOSE` changes primary status; its new ROM
and BPS exactly match the separately accepted experiment:

- ROM SHA-256: `78839705aec52526571a6a5ee344e88843b4d47d993c3cee61e034819ca80c8f`.
- BPS SHA-256: `fd88295c5fa59a8835e287a5b2e790bcb0fb4bd6258e39ce8d368e4cd4799e89`.

It retains seven tracks, fifteen prepared waves and +3.5 dB gain, with fitted
attacks and weak/live-depth approximations explicitly enabled. Its finite
track ends once at tick 911; the original entry 864 advances to 1632 before
the established LFO warmup selects 2400. The filtered attempt still rejects
active modulation. No alternate version inherits acceptance by name.

Primary totals rise to 59 packed and 25 exact accepted. Filtered totals remain
29 packed, eleven exact accepted and eighteen pending. Across both routes,
30 unique sequences have an exact accepted version. Two mixed versions and
four minimum-depth versions now pack. Pending lists retain 34 primary and
eighteen filtered versions. Primary blockers total 63 (58 capacity, five
conversion); filtered blockers remain 93.

## Verification and limits

All 311 regression tests pass. New tests cover the explicit plain/fitted modes,
error and structure exclusions, per-mode headroom handling, packing failures,
exclusive summary counts and complete CSV policy. Exact accepted matches are
checked against actual ROM/BPS files and manifests, alongside original inputs,
scanner hashes, deterministic JSON/CSV/HTML/summary output, actual JavaScript
filters and archived v10–v16 integrity.

This scan adds conversion/model/packing/BPS/report evidence. It adds no new
runtime, reference audio, listening or gameplay acceptance. SF2 LOSE acceptance
remains the user's exact-ROM report and original checklist, recorded in the
[standalone experiment](nds-sf2-lose-mixed-live-depth-research.md). No timed
recording, two-peer/rematch result or comparative preference is inferred.

## Continuing research

SF2 VS (`ssr2:37`) is the next fixed-tempo, in-capacity candidate. One track
starts notes at tick 576 before first depth activation at 864, while another
changes positive depth. Combining these behaviors requires an explicit new
capability: restore nonzero LFOS at first enable while preserving count/phase
on positive updates. Disabling and other live parameter changes remain outside
that proposal. The independent source render covers 210 seconds, 6,493 notes,
seventeen original waves and the actual late enable, but does not establish
carried-positive-depth coverage. Source research establishes no GBA playback
or manual acceptance; a new ROM needs full native and final manual checks.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v17
```

Use a fresh directory. Reports, scanner/source/archive fingerprints, scan/test
logs and local verification helpers retain provenance. Original assets and
ROMs stay out of Git.
