# Star Force 2 WIN: offline antialias experiment

The candidate is `out/nds-research/sf2-win-antialias-exe6-v1/`.
On 2026-10-18 the user reported “没有问题”, accepting this exact ROM after
the requested listening/gameplay checklist. This is the first filtered
candidate from Star Force 2; accepted filtered experiments already cover the
first and third games. The archived v11 report remains a historical snapshot.

## Conversion and identity

Japanese `ssr2d.nds`, SDAT file 975, SSEQ 30 `BGM_WIN` supplies seven tracks
and fifteen original ADPCM waves. The source SDAT is byte-identical to the
[accepted unfiltered WIN experiment](nds-sf2-research.md). Its existing
36-second independent software DS reference is copied into this artifact,
with original notes, controls, PCM and renderer metadata intact.

The new `sf2-win-antialias` build choice uses the existing singleton looping
converter and per-key offline filter. It prepares 89 PCM8 waves, totaling
754,150 bytes, without changing the FIR, runtime mixer or production manager.
The mixer remains ten PCM channels at 10,512 Hz, with +3.5 dB song gain.
The maximum source step is about 7.06434; tuning metadata error stays below
0.001 cent. The 1,033 PCM8 clamped values include quantization at full scale
and FIR overshoot; this is not a count of clipped full-mix output samples.

The generated common loop starts at tick 239 with a 1,536-tick period.
At native tempo 171, the first GOTO is around 13.03 seconds, then every
11.28 seconds. There are 601 mapped notes in the generated intro plus first
period, with no long-note loop carries. These are compilation-schedule
counts, distinct from the longer independent reference comparison.

The ROM is 9,170,420 bytes (CRC32 `4BF18A08`), SHA-256
`eb314a51705f2f9e0bac625d9669ab4a98d2b69376258450613f07d47a56b588`.
The BPS SHA-256 is
`52b91e8f16de5b08ab667fb21a7c40eba8a2ce6fc1f47e7684b0ffe916227316`.
Both match the v11 `ssr2:30` antialias candidate exactly. BPS reconstruction
is verified. The ROM grows by 505,800 bytes (about 494 KiB) versus the old
unfiltered variant; this also reflects direct versus singleton compilation.

## Validation

- Independent reference checks match 1,621 notes, 167 pan/bend/expression
  controls and all fifteen decoded original PCM16 arrays. These checks verify
  source interpretation, not equality of the filtered waveform to the source.
- Natural title playback, without register injection, reaches clock 3313 in
  1,454 frames. It checks two complete sequence loops and observes all 89
  prepared samples. `natural-loops/validation.json` retains the evidence.
- Every prepared wave has valid packed length, loop, tuning metadata and
  nonzero PCM8; see `prepared-wave-validation.json`.
- Controlled runtime checks pass effects 100/129 while music advances,
  ordinary battle and synthetic communication dispatch, queued stop, native
  music restoration and three restart cycles. These helper calls inject
  registers; they do not establish actual linked play or results-screen flow.
- The integration regression checks BPS reconstruction, seven-track loop
  timing, per-key tuning, all three routing rules, original song-table entries
  and preservation of bytes outside declared patch ranges.

The source renderer reaches sixteen voices in coarse observations, while the
native mixer allows ten. Complete voice-allocation or timbre equivalence is
not established by the note and sample checks.

All 241 regression tests pass. Rebuilding the original SF2 WIN and five
shared looping-branch siblings produces byte-identical ROMs and BPS patches;
see `prior-regressions.json`.

## Listening and manual acceptance

`comparison/listen.html` embeds thirty-second source, accepted unfiltered and
new filtered clips, normalized by whole-clip loudness. The old direct converter
and new singleton route have different loop cuts, so this comparison does not
isolate filtering as the only variable. The candidate preview covers two GOTOs.
DS audio is a software reference, not a hardware recording.

Test the exact new ROM in a virus or communication battle for at least three
minutes. Listen around 13, 24 and 36 seconds and subsequent joins for gaps,
clicks or accumulating distortion. Use chips and the Buster, finish the battle,
verify native map music resumes, then start at least two more encounters and
verify playback restarts from the beginning. `manual-testing.json` records the user-reported pass for this exact ROM.
No timed recording or personal execution trace was supplied, and linked play
or rematch was not separately reported. Automated coverage remains two complete
loops; no comparative listening preference is inferred.

Reproduce with:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds \
  --base ../roms/exe6.gba --song sf2-win-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-win-antialias-exe6-v1
```

The output directory must be new when rebuilding.
