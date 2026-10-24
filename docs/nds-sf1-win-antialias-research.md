# SF1 WIN: seven-track singleton antialias validation

This adds only the `sf1-win-antialias` selector for verified SF1 SDAT
sequence30, `BGM30WIN`, using seven singleton tracks and existing FIR
preparation. The source victory song loops; this is not the finite WIN2
experiment. Converter/native code and guards remain unchanged. No merged,
upward/LFO, fitted-envelope, finite-release or mixed-song mode is enabled.
No new conversion capability is claimed. The listening experiment still routes
title/virus-battle/communication triggers to slot474.

A fresh same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-win-plain-control-v1/`. It has no manual record.
The previously accepted SF2 WIN configuration grants no manual acceptance to
this separate SF1 experiment or its plain control.

## New-song automated evidence

All601 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All2,552 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or explicit long-note loop-carry adapters. Ordinary note gates retain
their compiled durations. All89 keyed tones and89 prepared waves retain source
root/pan/ADSR and relocated PCM/header data. Reproduction uses the same DSP
implementation and is not independent audio validation.

Prepared PCM8 storage contains754,150 points and1,033 clamps:622 negative,
411 positive, with unclamped extrema about−140.874/+140.590. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about7.0643; appended size781,812 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches8,018 notes and15
decoded raw waves, tempo/depth controls and source ADSR. Peak is11700 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
Common entry is239 and period1536 ticks. Source tempo170 maps to native
parameter171, about135.969→136.179 ticks/s. Entry is near0:02 and joins near
0:13/0:24; tempo quantization remains.

Natural frontend Start input reaches clock3313 in1,454 frames, covering two
complete cycles and all89 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock3327 in1,460 frames:
all1,110 calls allocate with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while663 slot choices differ. Nonzero-envelope release reuses rise776→785.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

All1,110 allocated channels retain gate/key/velocity/source-derived priority.
There are51,100 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
seven tracks, including source effective pitch, singleton pan and volume/
expression. The RAM track base accounts for the actual first sounding track0.
Source6 stereo diagnostics retain1,306 settled observations, excluding
changed-pan and starting/release states; no low-volume samples are excluded.
Exact source NOTE pan values10/100 are both covered:647 left≤20 and659
right≥100 observations, with median signed balance about−0.857/+0.600.
Definition pan is included; this is not full-song waveform alignment.

Every saved frame matches `1 + floor((frame-1)*171/75)`, with anchored residual
below one tick. Unanchored residual reaches2.24 ticks; no unanchored two-tick
bound is asserted. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Twelve focused cases pass in the prototype and again after exact source
migration: two new WIN cases and ten cases for the five selectors added since
the frozen full suite. They check family/capacity/mode guards, schedule/control
preservation, BPS reconstruction and declared base-prefix patch boundaries.
Formal CLI reproduces all eight native-tested outputs byte for byte. Recursive
v10–v37 archive identities remain unchanged.

Removing exactly the new selector branch and family entry reproduces the whole
accepted KANDO builder AST. Removing all six selector additions reproduces
the entire frozen487-test SCHOOL builder AST. All six branches use singleton
filtering only; other baseline library/test files remain byte-identical.
The parent isolation record and original full-suite log/source map are hashed.
The frozen487-test no-skip run and its58 accepted/two historical control rebuild
record are reused explicitly, not a fresh499-test suite or66-song rebuild.
Fresh integrity checks verify66 archived ROM/BPS pairs reconstruct their
recorded ROMs from the pinned base. This checks artifacts rather than
recompilation through the new selector. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM and delivered test patch

- ROM CRC32: `4BF18A08`; size9,170,420 bytes.
- ROM SHA-256: `eb314a51705f2f9e0bac625d9669ab4a98d2b69376258450613f07d47a56b588`.
- BPS SHA-256: `52b91e8f16de5b08ab667fb21a7c40eba8a2ce6fc1f47e7684b0ffe916227316`.
- Local folder: `out/nds-research/sf1-win-antialias-exe6-v1/`.
- Requested Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

The delivery receipt `patch-delivery.json` records the destination and copied
SHA-256 separately from manual acceptance. A successful copy does not grant
listening/gameplay acceptance.

The30-second native preview peaks at9697. Its nominal sequence-time duration
spans common entry and the first two GOTO points near0:13/0:24. Normal game
lifecycle remains active in previews; independent GOTO execution is established
by the separate original frame observations, not this waveform alone.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at equal configured gain without extra normalization or
sample alignment. The normalized software DS/native comparison is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, moving stereo, tails and joins near0:13/0:24; repeated chip/
Buster effects; and three battle→map→battle encounters with native-map
restoration and fresh imported starts. The delivered Windows patch hash
matched this exact BPS, including when acceptance was recorded. Automated
verification, transport verification and user reports remain separate.
Comparative timbre preference, independent timing, full gameplay traces, linked
play and rematches were not separately reported. No acceptance is inferred for
the plain control or another source family. Recorded voice/filtering/PCM8/
volume/ADSR/tempo and regression coverage limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-win-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-win-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
