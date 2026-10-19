# Star Force 3 KANDO: offline antialias experiment

The candidate is `out/nds-research/kando-antialias-exe6-v1/`.
On 2026-10-18 the user reported “测试没有问题”, accepting this exact ROM
after the requested listening/gameplay checklist. It follows the accepted
filtered SF2 WIN and SF1 KINCHO experiments, testing another established
looping baseline with frequent pan changes.

## Conversion and identity

Japanese `ssr3b.nds`, SDAT file 187, SSEQ 31 `BGM_KANDO` supplies seven
tracks and fourteen original ADPCM waves. Source archive details are in the
[unfiltered KANDO experiment](nds-kando-research.md). The source SDAT is
byte-identical to that baseline; its existing independent 80-second software
DS reference is copied into this artifact with notes, controls, PCM and
renderer metadata intact.

The new `kando-antialias` choice uses the existing singleton looping converter
and per-key offline filter. It prepares 84 PCM8 waves, totaling 588,497 bytes,
at +3.5 dB gain. The native mixer remains ten channels at 10,512 Hz. No FIR,
resampler, playback engine or production manager changes are needed. The
maximum source step is about 7.92945; stored tuning error stays below 0.001
cent. The 1,858 PCM8 clamped values include full-scale quantization and FIR
overshoot, rather than measuring full-mix clipping.

The generated common loop starts at tick 1536 with a 3072-tick period.
There are 1,246 mapped notes in the compiled intro plus first period, with
no long-note aliases or loop carries. Static note/gate validation checks two
periods; it is separate from native runtime evidence. Native tempo parameter
151 gives about 120.251 ticks/second: first GOTO at tick 4608, around 38.32
seconds, then every 25.55 seconds, around 64, 89, 115, 140 and 166 seconds.
The older direct converter uses individual track loop cuts.

The ROM is 9,008,492 bytes, CRC32 `CDE499F3`, SHA-256
`54c89ce0a85c2a70b15fd3af62eaf39a1b137b13c0b62cd6c9978bf44e1efec3`.
The BPS SHA-256 is
`9db7b30bd9abcd6e8681cd8eb84f3d27c8043d74ef23cfdbd0e5f8b2f862125d`.
Both match archived v11 `ssr3:31` exactly. BPS reconstruction is verified.
The ROM grows by 366,076 bytes (about 357.5 KiB) versus the unfiltered
baseline; this also reflects direct versus singleton compilation. Archived
v11 evidence remains a historical snapshot.

## Validation and limits

- Independent reference checks match 2,630 notes, 274 pan/bend/expression
  controls and fourteen exact original decoded PCM16 arrays. This validates
  source interpretation, not equality of filtered waveforms to the source.
- Natural title playback checks one complete generated loop without register
  injection, using the accepted unfiltered KANDO's coverage policy. It reaches
  clock 4609 in 2,290 frames and observes all 84 prepared samples; see
  `natural-one-loop/validation.json`. Repeated battle loops remain part of
  the manual checklist.
- Every prepared wave has valid packed length, loop, tuning metadata and
  nonzero PCM8; see `prepared-wave-validation.json`.
- Controlled helper checks cover effects 100/129 while music advances,
  ordinary battle and synthetic communication dispatch, queued stop, native
  music restoration and three restart cycles. These inject registers and do
  not establish actual linked play or results-screen/map transitions.
- The integration regression checks seven-track timing, per-key tuning,
  three routing rules, BPS reconstruction, original table preservation and
  bytes outside declared patch ranges.

The DS reference reaches sixteen voices in coarse snapshots, while the
native mixer remains limited to ten. Complete voice-allocation or timbre
equivalence is not established by note/sample matching. Source tempo
quantization, native envelopes and PCM8 remain fidelity limits.

All 243 regression tests pass. The accepted unfiltered KANDO and three
accepted looping antialias siblings across the three source games rebuild
to byte-identical ROMs and BPS patches; see `prior-regressions.json`.

## Listening and manual acceptance

`preview/preview.wav` captures thirty seconds of natural GBA playback.
`comparison/listen.html` embeds equal-duration 24-second DS software,
accepted unfiltered and new filtered clips, normalized by whole-clip loudness.
The older baseline capture is 24 seconds. Neither clip reaches the first
GOTO. The direct and singleton converters also differ, so this is not a
single-variable filter comparison or a hardware DS recording.

Test this exact ROM in a virus or communication battle for at least three
minutes. Listen particularly at about 38, 64, 89 and subsequent loop joins,
and during pan changes, for gaps, clicks, missing parts or accumulating
distortion. Use chips and the Buster, finish the battle and verify native
map music resumes, then start at least two more encounters and verify
playback restarts from the beginning. `manual-testing.json` records the user-reported pass
for this exact ROM. No timed recording or personal execution trace was supplied;
linked play or rematch was not separately reported. Automated native coverage
remains one complete loop, separately from the two-period static note model
and user report. No comparative listening preference is inferred.

Reproduce into a new output directory:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song kando-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/kando-antialias-exe6-v1
```
