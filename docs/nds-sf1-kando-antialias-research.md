# SF1 KANDO: seven-track singleton antialias validation

This adds only the `sf1-kando-antialias` selector for verified SF1 SDAT
sequence24, `BGM24KANDO`, using seven singleton tracks and existing FIR
preparation. Converter/native code and guards remain unchanged. No merged,
upward/LFO, fitted-envelope, finite-release or mixed-song mode is enabled.
No new conversion capability is claimed.

A fresh same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-kando-plain-control-v1/`. It has no manual record.
SF2 KANDO produces identical filtered ROM/BPS bytes, but acceptance remains
source-specific. Neither matching bytes nor the previously accepted SF3 KANDO
configuration grants a manual record to this SF1 experiment or another family.

## New-song automated evidence

All1,246 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All5,140 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or loop carries; source gates fit ordinary native note lengths.
All84 keyed tones and84 prepared waves retain source root/pan/ADSR and
relocated PCM/header data. Reproduction uses the same DSP implementation and
is not independent audio validation.

Prepared PCM8 storage contains588,497 points and1,862 clamps:1,150 negative,
712 positive, with unclamped extrema about−148.177/+153.029. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about7.9295; appended size619,784 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches5,960 notes and14
decoded raw waves, tempo/depth controls and source ADSR. Peak is15250 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
Common entry is1536 and period3072 ticks. Source tempo150 maps to native
parameter151, about119.973→120.251 ticks/s. Entry is near0:13 and joins near
0:38/1:04; tempo quantization remains.

Natural frontend Start input reaches clock7681 in3,816 frames, covering two
complete cycles and all84 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock7697 in3,824 frames:
all2,107 calls allocate with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while732 slot choices differ. Nonzero-envelope release reuses rise1111→1134.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

All2,107 allocated channels retain gate/key/velocity/source-derived priority.
There are133,840 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
seven tracks, including source effective pitch, singleton pan and volume/
expression. The first sounding track is target2; the RAM track base is derived
from the first read minus its actual track index, rather than assuming track0.
All saved track/channel blocks are accounted for. Multi-position source4 pan
controls remain in the frame checks. Source6 stereo diagnostics retain1,998
settled observations, excluding changed-pan, starting/release and low-volume
states. Exact source NOTE pan values20/100 are both covered:979 left≤20 and
1,019 right≥100 observations, with median signed balance about−0.714/+0.619.
Definition pan is included; this is not full-song waveform alignment.

Every saved frame matches `1 + floor((frame-1)*151/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Ten focused cases pass in the prototype and again after exact source migration:
two new KANDO cases and eight cases for the four selectors added since the
frozen full suite. They check family/capacity/mode guards, schedule/control
preservation, BPS reconstruction and declared base-prefix patch boundaries.
Formal CLI reproduces all eight native-tested outputs byte for byte. Recursive
v10–v37 archive identities remain unchanged.

Removing exactly the new selector branch and family entry reproduces the whole
accepted JIKEN builder AST. Removing all five selector additions reproduces
the entire frozen487-test SCHOOL builder AST. All five branches use singleton
filtering only; other baseline library/test files remain byte-identical.
The parent isolation record and original full-suite log/source map are hashed.
The frozen487-test no-skip run and its58 accepted/two historical control rebuild
record are reused explicitly, not a fresh497-test suite or65-song rebuild.
Fresh integrity checks verify65 archived ROM/BPS pairs reconstruct their
recorded ROMs from the pinned base. This checks artifacts rather than
recompilation through the new selector. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM

- ROM CRC32: `557C2017`; size9,008,392 bytes.
- ROM SHA-256: `f2b262ea45ee85778c9a00a30c49fa0db7542d4ee1b15eecb19cd392dad8b03f`.
- BPS SHA-256: `6bb9be14c08ddf4c85bccf123b31fea0150705063377891f36316ce2bf206c6e`.
- Local folder: `out/nds-research/sf1-kando-antialias-exe6-v1/`.

The30-second native preview peaks at13440 and covers common entry near0:13,
but neither first GOTO near0:38 nor the second near1:04.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at equal configured gain without extra normalization or
sample alignment. The normalized software DS/native comparison is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, moving stereo, tails and joins near0:38/1:04; repeated chip/
Buster effects; and three battle→map→battle encounters with native-map
restoration and fresh imported starts. Automated verification and user reports
remain separate. Comparative timbre preference, independent timing, full
gameplay traces, linked play and rematches were not separately reported.
The plain control and byte-identical SF2 KANDO receive no inferred acceptance.
All recorded voice/filtering/PCM8/volume/ADSR/tempo and regression coverage
limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-kando-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-kando-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
