# NDS compatibility audit v21: accepted nine-track HOKORA grouping

The scanner adds only the accepted SF2 HOKORA grouping: source tracks 0/4
share one target track, and the remaining seven source tracks stay separate.
The route requires pinned family `ssr2`, slot 20, capacity eight, source IDs
0–8, all tracks looping, no fitted envelope and no active modulation. Existing
control, fixed-volume, pan and conversion guards still run. It does not search
for groups or waive the ordinary singleton capacity limit for other songs.
The standalone selector and scanner share `SF2_HOKORA_GROUPS`; all eight
accepted HOKORA output files reproduce byte for byte after this refactor.

## Results and provenance

All seven registered Japanese original ROM variants and three pinned family
SDATs verify before and after this scan. The restored second SF2 variant matches
its registered fingerprint and archive. Historical v19 observations and v20's
six-source scan selection/separate seven-source check remain unchanged.

All 132 SSEQ slots are scanned. Primary packing rises from 64 to 65, and the
57 remaining blockers all exceed eight tracks. Only `ssr2:20 BGM_HOKORA` changes
conversion status; its ROM/BPS match the exact
[accepted standalone artifact](nds-sf2-hokora-nine-track-research.md):

- ROM SHA-256: `7aeb1033001844fd1eeb44ce4e911cdee4f651b6ea6a3d70d85d6f03227184a5`.
- BPS SHA-256: `6064e1908404e868b1bf7e8052d5c5c375d8a9bf0b4cb0895bfe767e1adc5ec7`.

All 64 old primary and 29 filtered ROM/BPS pairs retain their bytes, routes and
gains. SF3 SABISHI now also matches its newly accepted exact standalone record;
its bytes and conversion status do not change. Primary exact accepted variants
rise from 28 to 30, and 35 unique source sequences have an exact accepted version.
Primary pending is 35. Filtered counts remain 29 packed, eleven exact accepted,
eighteen pending and 93 blocked candidates. The filtered HOKORA route remains
capacity-blocked; acceptance is not transferred to a different variant.

## Verification and limits

All 360 regression tests pass. Six new cases cover exact identity/structure
selection, explicit grouping and plain flags, approximation exclusions,
original guard failures, headroom/packing handling, model failures and exclusive
JSON/CSV/HTML/summary accounting. Report validation checks all old packed pairs,
accepted ROM/BPS/manifests, all seven source fingerprints, source/scanner hashes,
deterministic rendering, real JavaScript filter counts and unchanged archived
v10–v20 identities. The new HTML grouping filter returns only `ssr2:20`.

This adds batch conversion, packing, patch and report evidence. It adds no new
native playback or manual tests. Standalone HOKORA and SF3 SABISHI retain their
user-reported listening/effects/three-encounter checklists and exact fingerprints.
No independent timed recording, full gameplay trace, linked-play/rematch result
or comparative preference is inferred. Ten-voice mixing, release tails, PCM8,
ADSR and source/target tempo differences remain separate limits.

## Continuing source investigation

A bounded source-only grouping search finds plain conversion candidates among
fourteen remaining unmodulated, unfitted looping blockers. Search is limited to
256 grouping states per song and is not exhaustive. No batch route or acceptance
is added for these candidates. SF3 KINCHO is the next smaller case: ten source
tracks can become eight by grouping 2/4/6, all fixed at volume 100. It adds
three-source grouping and note-on pan baking without extra velocity ratios;
a separate native/reference experiment must finish before a new manual check.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v21
```

Use a fresh output directory. Source assets, ROMs and ignored local research
outputs remain outside Git; local hashes, logs and verification helpers retain
provenance. Archived report counts are not rewritten after later acceptances.
