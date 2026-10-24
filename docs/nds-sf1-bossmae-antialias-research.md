# SF1 BOSSMAE: eight-track singleton antialias validation

This adds only `sf1-bossmae-antialias` for verified SF1 SDAT sequence34,
`BGM34BOSSMAE`, using eight singleton tracks and existing FIR preparation.
Converter/native code and guards remain unchanged. No merged, upward/LFO,
fitted-envelope, finite-release or mixed-song mode is enabled. No new
conversion capability is claimed. This differs from the accepted SF3 BOSSMAE
merged configuration; no acceptance transfers across source families.

A fresh same-source plain export remains `unaccepted_control` at
`out/nds-research/sf1-bossmae-plain-control-v1/`, without a manual record.

## New-song automated evidence

All635 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All2,722 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or explicit long-note loop-carry adapters. Ordinary gates retain
compiled durations. All95 keyed tones and95 prepared waves retain source
root/pan/ADSR and relocated PCM/header data. Reproduction uses the same DSP
implementation and is not independent audio validation.

Prepared PCM8 storage contains598,131 points and3,895 clamps:1,650 negative,
2,245 positive, with unclamped extrema about−145.787/+160.058. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about8.9103; appended size624,668 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches5,406 notes and15
decoded raw waves, tempo/depth controls and source ADSR. Peak is9629 and coarse
100ms maximum voices16. It is software rendering, not DS hardware.
Common entry is576 and period1920 ticks. Source tempo148 maps to native149,
about118.373→118.659 ticks/s. Entry is near0:05 and joins near0:21/0:37;
tempo quantization remains.

Natural frontend Start input reaches clock4417 in2,224 frames, covering two
complete cycles and all95 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock4433 in2,232 frames:
all1,132 calls allocate with no rejection or held/starting preemption.
Identities, clocks and outcomes match the unaccepted plain control, while151
slot choices differ. Nonzero-envelope release reuses rise551→552. This does
not prove preservation of tails or unrestricted polyphony outside the observed
window; tails remain a manual listening focus.

All1,132 allocated channels retain gate/key/velocity/source-derived priority.
There are89,280 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
eight tracks, including source effective pitch, singleton pan and volume/
expression. RAM track-base derivation accounts for the actual first track0.
Source6 stereo diagnostics retain2,192 settled observations, excluding changed
pan and starting/release states; no low-volume samples are excluded.
All source NOTE pan values10/100/110 are covered:1,024 left≤20 and1,168 right≥100
observations, with median signed balance about−0.895/+0.579. Definition pan is
included; this is not full-song waveform alignment.

Every saved frame matches `1 + floor((frame-1)*149/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Fourteen focused cases pass in the prototype and again after exact migration:
two new BOSSMAE cases and twelve cases for the six selectors added since the
frozen full suite. They check family/capacity/mode guards, schedule/control
preservation, BPS reconstruction and declared base-prefix patch boundaries.
Formal CLI reproduces all eight native-tested outputs byte for byte. Recursive
v10–v37 archive identities remain unchanged.

Removing the new selector branch and family entry reproduces the whole accepted
WIN builder AST. Removing all seven additions reproduces the entire frozen487-
test SCHOOL builder AST. All seven branches use singleton filtering only;
other baseline library/test files remain byte-identical. The parent isolation
record and original full-suite log/source map are hashed. The frozen487-test
no-skip run and its58 accepted/two historical control rebuild record are reused
explicitly, not a fresh501-test suite or67-song rebuild. Fresh integrity checks
verify67 archived ROM/BPS pairs reconstruct their recorded ROMs from the pinned
base. This checks artifacts rather than recompilation through the new selector.
Remaining coverage limits are preserved.

## Accepted exact SF1 ROM and delivered test patch

- ROM CRC32: `8B6C5C98`; size9,013,276 bytes.
- ROM SHA-256: `8689b3b47c1b1f6b7d47d9e60bf5d9ae621a367bcd2cd38f5094c2a51a3cad69`.
- BPS SHA-256: `f46d9ad463cee641099c27e171f579444fc36bafa5ae498f66da4d16469d25f8`.
- Local folder: `out/nds-research/sf1-bossmae-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

`patch-delivery.json` records the destination and copied SHA-256 separately
from manual acceptance. Copy success grants no listening/gameplay acceptance.

The30-second native preview peaks at9702. Nominal sequence time spans entry
and the first GOTO near0:21, but not the second near0:37. Normal game lifecycle
remains active in previews; actual two-cycle execution is established by the
separate original frame observations, not this waveform alone.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at equal gain without extra normalization or sample alignment.
The normalized software DS/native page is separate. Comparative timbre
preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, moving stereo, tails and joins near0:21/0:37; repeated chip/
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
  --song sf1-bossmae-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-bossmae-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
