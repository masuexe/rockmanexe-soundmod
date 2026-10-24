# SF1 COMICAL: eight-track singleton antialias validation

This adds only the `sf1-comical-antialias` selector for verified SF1 SDAT
sequence21, `BGM21COMICAL`, using eight singleton tracks and existing FIR
preparation. Converter/native code and guards remain unchanged. No merged,
upward/LFO, fitted-envelope, finite-release or mixed-song mode is enabled.
No new conversion capability is claimed.

A fresh same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-comical-plain-control-v1/`. It has no manual record.
SF2 COMICAL happens to produce identical filtered ROM/BPS bytes. Acceptance
remains source-specific: neither matching bytes nor a song name grants a
manual record to another source family.

## New-song automated evidence

All789 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All3,443 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or loop carries; source gates fit ordinary native note lengths.
All101 keyed tones and101 prepared waves retain source root/pan/ADSR and
relocated PCM/header data. Reproduction uses the same DSP implementation and
is not independent audio validation.

Prepared PCM8 storage contains591,359 points and831 clamps:416 negative,
415 positive, with unclamped extrema about−166.301/+161.520. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about14.9859; appended size617,880 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches5,312 notes and19
decoded raw waves, tempo/depth controls and source ADSR. Peak is15085 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
Common entry is624 and period2304 ticks. Source tempo140 maps to native
parameter141, about111.974→112.288 ticks/s. Entry is near0:06 and joins near
0:26/0:47; tempo quantization remains.

Natural frontend Start input reaches clock5233 in2,784 frames, covering two
complete cycles and all101 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock5248 in2,792 frames:
all1,399 calls allocate with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while439 slot choices differ. Nonzero-envelope release reuses rise467→489.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

All1,399 allocated channels retain gate/key/velocity/source-derived priority.
There are111,680 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
eight tracks, including source effective pitch, singleton pan and volume/
expression. Multi-position pan controls on the other tracks remain in those
checks. Source6 stereo diagnostics retain955 settled observations, excluding
changed-pan and starting/release states; no low-volume samples are excluded.
Exact source NOTE pan values10/110 are both covered:551 left≤20 and404
right≥100 observations, with median signed balance−1.000/+0.818. Definition
pan is included; this is not full-song waveform alignment.

Every saved frame matches `1 + floor((frame-1)*141/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Six focused cases pass in the prototype and again after exact source migration:
two new COMICAL cases and the four DEMPAJIKEN/ANTENNA cases added since the
frozen full suite. They check family/capacity/mode guards, schedule/control
preservation, BPS reconstruction and declared base-prefix patch boundaries.
Formal CLI reproduces all eight native-tested outputs byte for byte. Recursive
v10–v37 archive identities remain unchanged.

Removing exactly the new selector branch and family entry reproduces the whole
accepted ANTENNA builder AST. Removing all three selector additions reproduces
the entire frozen487-test SCHOOL builder AST. All three branches use singleton
filtering only; other baseline library/test files remain byte-identical.
The parent isolation record and original full-suite log/source map are hashed.
The frozen487-test no-skip run and its58 accepted/two historical control rebuild
record are reused explicitly, not a fresh493-test suite or63-song rebuild.
Fresh integrity checks verify63 archived ROM/BPS pairs reconstruct their
recorded ROMs from the pinned base. This checks artifacts rather than
recompilation through the new selector. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM

- ROM CRC32: `1FD0E6D4`; size9,006,488 bytes.
- ROM SHA-256: `b2876ecaa35cbb266fb8ed48ff7e40cc11aca9af43693c70407381554303e463`.
- BPS SHA-256: `a992cb3171bffe60ddd940d35967fc426e6e20d70769fb74232589bdcca25baf`.
- Local folder: `out/nds-research/sf1-comical-antialias-exe6-v1/`.

The30-second native preview peaks at13042 and covers common entry and the
first GOTO near0:26, but not the second near0:47.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at equal configured gain without extra normalization or
sample alignment. The normalized software DS/native comparison is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, moving stereo, overlapping sounds, tails and joins near0:26/0:47;
repeated chip/Buster effects; and three battle→map→battle encounters with native
map restoration and fresh imported starts. Automated verification and user
reports remain separate. Comparative timbre preference, independent timing,
full gameplay traces, linked play and rematches were not separately reported.
The plain control and byte-identical SF2 COMICAL receive no inferred acceptance.
All recorded voice/filtering/PCM8/volume/ADSR/tempo and regression coverage
limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-comical-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-comical-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
