# Star Force 1 KINCHO: offline antialias experiment

The candidate is `out/nds-research/sf1-kincho-antialias-exe6-v1/`.
On 2026-10-18 the user reported “测试没有问题”, accepting this exact ROM
after the requested listening/gameplay checklist. It follows the accepted
filtered WIN experiment from Star Force 2, testing another eight-track
looping score against its previously accepted unfiltered counterpart.

## Conversion and identity

Japanese `ssr1d.nds`, SDAT file 667, SSEQ 23 `BGM23KINCHO` supplies eight
tracks and fifteen original ADPCM waves. Source interpretation and original
archive details are documented in the [unfiltered experiment](nds-sf1-research.md).
The source SDAT is byte-identical to that baseline. Its existing independent
80-second software DS reference is copied into this artifact, preserving
notes, controls, original PCM and renderer metadata.

The new `sf1-kincho-antialias` build choice uses the existing singleton
looping converter and per-key offline filter. It prepares 86 PCM8 waves,
totaling 987,779 bytes, at +3.5 dB gain. The native mixer remains ten channels
at 10,512 Hz. No FIR, resampler, playback engine or production manager changes
are needed. The maximum source step is about 7.68037; stored tuning error
stays below 0.001 cent. The 740 PCM8 clamped values include full-scale
quantization and FIR overshoot, rather than measuring full-mix clipping.

The generated common loop starts at tick 1536 with a 2304-tick period.
There are 643 mapped notes in the compiled intro plus first period. There
are no long-note aliases or loop carries. Static note/gate validation checks
two periods; it is separate from native runtime evidence.

Source tempo 115 maps to native parameter 115, about 91.582 ticks/second.
The first generated GOTO is at tick 3840, about 41.93 seconds after the music
starts; subsequent jumps are every 25.16 seconds, around 67, 92, 117, 143
and 168 seconds. Older direct-converter tracks have individual loop cuts.

The ROM is 9,404,412 bytes, CRC32 `B5F670E2`, SHA-256
`1432dc17f05af1728dac7478b32c6a4d90c55dddfe9b81755e8c1184d41d7158`.
The BPS SHA-256 is
`4fd14209d4af3842acc0862a16047989e43f8323bb0963caa6d3a48d2ccea39c`.
Both match the archived v11 `ssr1:23` antialias candidate exactly. BPS
reconstruction is verified. The ROM grows by 701,556 bytes (about 685 KiB)
versus the unfiltered baseline; the increase also reflects direct versus
singleton compilation. Archived v11 evidence remains a historical snapshot.

## Validation and limits

- Independent reference checks match 1,200 notes, 111 pan/bend/expression
  controls and fifteen exact original decoded PCM16 arrays. This validates
  source interpretation, not equality of filtered waveforms to the source.
- Natural title playback checks one complete generated loop without register
  injection, using the same coverage policy as the accepted unfiltered KINCHO.
  It reaches clock 3842 after 2,506 frames and observes all 86 prepared
  samples. Evidence is in `natural-one-loop/validation.json`; repeated battle
  loops remain part of the manual checklist.
- Every prepared wave has valid packed length, loop, tuning metadata and
  nonzero PCM8; see `prepared-wave-validation.json`.
- Controlled helper checks cover effects 100/129 while music advances,
  ordinary battle and synthetic communication dispatch, queued stop, native
  music restoration and three restart cycles. These inject registers and do
  not establish actual linked play or results-screen/map transitions.
- The new integration regression checks eight-track timing, per-key tuning,
  three routing rules, BPS reconstruction, original table preservation and
  bytes outside the declared patch ranges.

The DS reference reaches sixteen voices in coarse snapshots, while the
native mixer remains limited to ten. Complete voice-allocation or timbre
equivalence is not established by note/sample matching. Source tempo
quantization, native envelopes and PCM8 remain fidelity limits.

All 242 regression tests pass. The accepted unfiltered KINCHO and six shared
looping-branch siblings rebuild to byte-identical ROMs and BPS patches; see
`prior-regressions.json`.

## Listening and manual acceptance

`preview/preview.wav` is thirty seconds of natural GBA playback.
`comparison/listen.html` embeds equal-duration 24-second DS software,
accepted unfiltered and new filtered clips, normalized by whole-clip loudness.
The older baseline capture is 24 seconds. Neither clip reaches the first
GOTO. The direct and singleton converters also differ, so this is not a
single-variable filter comparison or a hardware DS recording.

Test this exact ROM in a virus or communication battle for at least three
minutes. Listen particularly at about 42, 67, 92 and subsequent loop joins
for gaps, clicks, missing parts or accumulating distortion. Use chips and
the Buster, finish the battle and verify native map music resumes, then start
at least two more encounters and verify playback restarts from the beginning.
`manual-testing.json` records the user-reported pass for this exact ROM.
No timed recording or personal execution trace was supplied; linked play or
rematch was not separately reported. Automated native coverage remains one
complete loop, separately from the two-period static note model and user report.
No comparative listening preference is inferred.

Reproduce into a new output directory:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-kincho-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-kincho-antialias-exe6-v1
```
