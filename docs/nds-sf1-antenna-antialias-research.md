# SF1 ANTENNA: singleton antialias and independent long-note releases

This adds only the `sf1-antenna-antialias` selector for verified SF1 SDAT
sequence16, `BGM16ANTENNA`, using seven singleton tracks and existing FIR
preparation. Converter/native code and guards remain unchanged. No merged,
upward/LFO, fitted-envelope, finite-release or mixed-song mode is enabled.
No new conversion capability is claimed.

A fresh same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-antenna-plain-control-v1/`. It has no manual record.
Matching audit bytes or another game's similarly named song grants no manual
acceptance.

## New-song automated evidence

All2,165 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All8,684 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings or loop
carries. All137 keyed tones and135 prepared waves retain source root/pan/ADSR
and relocated PCM/header data. Reproduction uses the same DSP implementation
and is not independent audio validation.

Prepared PCM8 storage contains923,193 points and5,104 clamps:2,272 negative,
2,832 positive, with unclamped extrema about−147.266/+153.029. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about7.0739; appended size968,768 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches5,422 notes and21
decoded raw waves, tempo/depth controls and source ADSR. Peak is15557 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
Common entry is1560 and period6528 ticks. Source tempo143 maps to native
parameter144, about114.374→114.677 ticks/s. Entry is near0:14 and joins near
1:11/2:07; tempo quantization remains.

Natural frontend Start input reaches clock14617 in7,614 frames, covering two
complete cycles and all135 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock14633 in7,622 frames:
all3,884 calls allocate with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while1,897 slot choices differ. Nonzero-envelope release reuses rise1241→1324.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

Two singleton aliases both use key127 under separate track owners: source1/
key52 holds336 ticks, source5/key59 holds288 ticks. Both source waves loop.
Original starts4608/11136 produce four total alias uses, all held through their
source gates before becoming nonheld/released. There are300 snapshots with
both aliases held. In each cycle,21 snapshots show the shorter alias released
while the longer remains held. This checks independent release without forced
repetition; it does not assert release tails are silent or preserved.
The starts are near0:40/1:37; they occur after the30-second preview.

All3,884 allocated channels retain gate/key/velocity/source-derived priority.
There are266,770 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
seven tracks, including source effective pitch, singleton pan and volume/
expression. Source6 stereo diagnostics retain7,249 settled observations,
excluding changed-pan and starting/release states; no low-volume samples are
excluded in this window. Exact source NOTE pan values20/100 are both covered:
3,695 left≤20 and3,554 right≥100 observations, with median signed balance
about−0.714/+0.600. Definition pan is included; this is not full-song waveform
alignment.

Every saved frame matches `1 + floor((frame-1)*144/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Four focused cases pass in the prototype and again after exact source migration:
two new ANTENNA cases and the two DEMPAJIKEN cases added since the frozen full
suite. They check family/capacity/mode guards, schedule/control preservation,
BPS reconstruction and declared base-prefix patch boundaries. Formal CLI
reproduces all eight native-tested outputs byte for byte. Recursive v10–v37
archive identities remain unchanged.

Removing exactly the new selector branch and family entry reproduces the whole
accepted DEMPAJIKEN builder AST. Removing both selector additions reproduces
the entire frozen487-test SCHOOL builder AST. Both branches use singleton
filtering only; all other baseline library/test files are byte-identical.
The parent isolation record and original full-suite log/source map are hashed.
The frozen487-test no-skip run and its58 accepted/two historical control rebuild
record are reused explicitly, not a fresh491-test suite or62-song rebuild.
Fresh integrity checks verify62 archived ROM/BPS pairs, including the two later
accepted selectors, reconstruct their recorded ROMs from the pinned base.
This checks artifacts rather than recompilation through the new selector.
Remaining coverage limits are preserved.

## Accepted exact SF1 ROM

- ROM CRC32: `E045EF21`; size9,357,376 bytes.
- ROM SHA-256: `fd2c62aea18a6bd4e053bef934a3181a114acc92bcdf3eb9bc12be989de49763`.
- BPS SHA-256: `30d7b186b1155ba4e34f561be319ecda90317e1b14e390241858e84e9321089f`.
- Local folder: `out/nds-research/sf1-antenna-antialias-exe6-v1/`.

The30-second native preview peaks at14765 and covers common entry near0:14,
but neither long-alias start nor the first GOTO near1:11.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at equal configured gain without extra normalization or
sample alignment. The normalized software DS/native comparison is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
overlapping long notes and their separate releases, moving stereo, tails and
joins near1:11/2:07; repeated chip/Buster effects; and three battle→map→battle
encounters with native-map restoration and fresh imported starts. Automated
verification and user reports remain separate. Comparative timbre preference,
independent timing, full gameplay traces, linked play and rematches were not
separately reported. No acceptance is inferred for the plain control or other
source families. Recorded voice/filtering/PCM8/volume/ADSR/tempo and regression
coverage limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-antenna-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-antenna-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
