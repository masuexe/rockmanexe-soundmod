# SF1 DEMPAJIKEN: singleton antialias validation

This experiment adds only the `sf1-dempajiken-antialias` selector for verified
SF1 SDAT sequence11, `BGM11DEMPAJIKEN`, with seven singleton tracks and existing
FIR preparation. Converter/native code and existing guards remain unchanged.
No merged/upward/LFO, fitted-envelope, finite-release or mixed-song mode is
enabled. No new conversion capability is claimed.

A freshly built same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-dempajiken-plain-control-v1/`. It has no manual record.
Acceptance is not inherited from another game's similarly named song or from
matching audit bytes.

## New-song automated evidence

All819 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All3,549 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or loop carries; source gates fit ordinary native note lengths.
All104 keyed tones and104 prepared waves retain source root/pan/ADSR and
relocated PCM/header data. Reproduction uses the same DSP implementation and
is not independent audio validation.

Prepared PCM8 storage contains528,195 points and5,956 clamps:2,573 negative,
3,383 positive, with unclamped extrema about−148.736/+153.029. These are
storage counts, not time-weighted audible error or native mixer clipping.
Maximum source step is about17.8207; appended size559,596 bytes. Conservative
filtering, PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches6,240 notes and20
decoded raw waves, tempo/depth controls and source ADSR. Its peak is16658 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
The common entry is774 and period2304 ticks. Source tempo165 maps to native
parameter166, about131.970→132.197 ticks/s. Entry is near0:06 and joins near
0:23/0:41; tempo quantization remains.

Natural frontend Start input reaches clock5383 in2,433 frames, covering two
complete cycles and all104 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock5399 in2,440 frames:
all1,431 calls allocate, with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while209 slot choices differ. Nonzero-envelope release reuses rise479→489.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

All1,431 allocated channels retain gate/key/velocity/source-derived priority.
There are85,400 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
seven tracks, including source effective pitch, singleton pan and volume/
expression. Source2 has eight observed native volume levels. Source6 stereo
checks retain1,052 settled observations, excluding changed-pan, starting/
release and low-volume states. Exact source NOTE pan values10/110 are both
covered:339 left≤20 and713 right≥100 observations, with median signed balance
about−0.846/+0.750. Definition pan is included; this is not full-song waveform
alignment. The initial copied fixture incorrectly required three audible pan
values by including initialization-only center64. Its failed log and source
are retained separately; the corrected fixture requires exact equality to the
source NOTE pan set, without changing stereo thresholds or the ROM.

Every saved frame matches `1 + floor((frame-1)*166/75)`, with anchored residual
below one tick. Unanchored residual reaches2.2 ticks; no unanchored two-tick
bound is asserted. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Two focused new-song tests pass in the prototype and again after exact source
migration: source family/capacity/mode guards, full schedule/control retention,
BPS reconstruction and the declared base-prefix patch boundaries. Formal CLI
reproduces all eight native-tested outputs byte for byte. Recursive v10–v37
archive identities remain unchanged.

Prior regression coverage is reused explicitly. Removing exactly the new
selector branch and family entry reproduces the entire accepted SCHOOL builder
AST; all other prior source/test files are byte-identical. The new branch is
restricted to source11, singleton groups and `bandlimited_pcm=True`.
The frozen487-test no-skip SCHOOL run and its58 accepted/two historical
control rebuild record are retained with source/log hashes. They are not a
fresh487/489-test run or a new61-song rebuild. Fresh integrity checks verify
all61 archived ROM/BPS pairs, including SCHOOL, reconstruct their recorded ROM
from the pinned base. This verifies archived artifacts, not recompilation
through the new selector. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM

- ROM CRC32: `AD97BCF1`; size8,948,204 bytes.
- ROM SHA-256: `170bd477bd9e9cf9f2e43b53c271e0c0cbacfa56aa92e080a95494b9d5d67fc9`.
- BPS SHA-256: `0cc9ef340f3cd6132f68a7d3b3d60025ea59c1f1c31c056ef958af0d752f94f2`.
- Local folder: `out/nds-research/sf1-dempajiken-antialias-exe6-v1/`.

The30-second native preview peaks at15624 and covers the common entry and
first GOTO near0:23, but not the second near0:41. `comparison/filter-ab.html`
presents unaccepted plain and accepted filtered native recordings at equal
configured gain without extra normalization or sample alignment. The
normalized software DS/native comparison is separate. Comparative timbre
preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, volume changes, moving stereo, tails and joins near0:23/0:41;
repeated chip/Buster effects; and three battle→map→battle encounters with native
map restoration and fresh imported starts. Automated verification and user
reports remain separate. Comparative timbre preference, independent timing,
full gameplay traces, linked play and rematches were not separately reported.
The plain control and other source families receive no inferred acceptance.
Recorded voice/filtering/PCM8/volume/ADSR/tempo and regression-coverage limits
remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-dempajiken-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-dempajiken-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
