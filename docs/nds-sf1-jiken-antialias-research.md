# SF1 JIKEN: eight-track singleton antialias validation

This adds only the `sf1-jiken-antialias` selector for verified SF1 SDAT
sequence22, `BGM22JIKEN`, using eight singleton tracks and existing FIR
preparation. Converter/native code and guards remain unchanged. No merged,
upward/LFO, fitted-envelope, finite-release or mixed-song mode is enabled.
No new conversion capability is claimed.

A fresh same-source plain export remains `unaccepted_control`:
`out/nds-research/sf1-jiken-plain-control-v1/`. It has no manual record.
Matching audit bytes or another game's similarly named song grants no manual
acceptance.

## New-song automated evidence

All1,211 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All5,120 compiled playback commands match apart from relocated GOTO words,
whose relative targets match. There are no zero-velocity mappings, long-note
aliases or loop carries; source gates fit ordinary native note lengths.
All129 keyed tones and129 prepared waves retain source root/pan/ADSR and
relocated PCM/header data. Reproduction uses the same DSP implementation and
is not independent audio validation.

Prepared PCM8 storage contains867,213 points and4,083 clamps:1,710 negative,
2,373 positive, with unclamped extrema about−150.248/+165.581. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about10.2520; appended size902,224 bytes. Conservative filtering,
PCM8 clipping and envelope/volume quantization remain explicit.

A fresh independent180-second software DS reference matches7,220 notes and16
decoded raw waves, tempo/depth controls and source ADSR. Peak is17193 and
coarse100ms maximum voices16. It is a software renderer, not DS hardware.
Common entry is1728 and period1920 ticks. Source tempo150 maps to native
parameter151, about119.973→120.251 ticks/s. Entry is near0:14 and joins near
0:30/0:46; tempo quantization remains.

Natural frontend Start input reaches clock5569 in2,767 frames, covering two
complete cycles and all129 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only observation
of the unchanged original NOTE handler reaches clock5585 in2,775 frames:
all1,858 calls allocate with no rejection or held/starting preemption.
Identities, clocks and allocation outcomes match the unaccepted plain control,
while197 slot choices differ. Nonzero-envelope release reuses rise733→734.
This does not prove preservation of tails or unrestricted polyphony outside
the observed window; tails remain a manual listening focus.

All1,858 allocated channels retain gate/key/velocity/source-derived priority.
There are111,000 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
eight tracks, including source effective pitch, singleton pan and volume/
expression. Source5 has nine observed native volume levels. Multi-position
pan controls on the other tracks remain in those checks. Source4 stereo
diagnostics retain854 settled observations, excluding changed-pan, starting/
release and low-volume states. Exact source NOTE pan values20/100 are both
covered:446 left≤20 and408 right≥100 observations, with median signed balance
about−0.714/+0.592. Definition pan is included; this is not full-song waveform
alignment.

Every saved frame matches `1 + floor((frame-1)*151/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Eight focused cases pass in the prototype and again after exact source migration:
two new JIKEN cases and six DEMPAJIKEN/ANTENNA/COMICAL cases added since the
frozen full suite. They check family/capacity/mode guards, schedule/control
preservation, BPS reconstruction and declared base-prefix patch boundaries.
Formal CLI reproduces all eight native-tested outputs byte for byte. Recursive
v10–v37 archive identities remain unchanged.

Removing exactly the new selector branch and family entry reproduces the whole
accepted COMICAL builder AST. Removing all four selector additions reproduces
the entire frozen487-test SCHOOL builder AST. All four branches use singleton
filtering only; other baseline library/test files remain byte-identical.
The parent isolation record and original full-suite log/source map are hashed.
The frozen487-test no-skip run and its58 accepted/two historical control rebuild
record are reused explicitly, not a fresh495-test suite or64-song rebuild.
Fresh integrity checks verify64 archived ROM/BPS pairs reconstruct their
recorded ROMs from the pinned base. This checks artifacts rather than
recompilation through the new selector. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM

- ROM CRC32: `0DADDC7D`; size9,290,832 bytes.
- ROM SHA-256: `ada89fa7e9c35a25f5b481f2043b07275536f8d8b1b4df7c006770deadf0750f`.
- BPS SHA-256: `e606d3882678a93c56968b13056ffb0c153a9656b604e44a8da21569ff700fb3`.
- Local folder: `out/nds-research/sf1-jiken-antialias-exe6-v1/`.

The30-second native preview peaks at17048 and covers common entry near0:14,
but not the first GOTO, which falls just after30 seconds (about0:30.3), or the
second near0:46. `comparison/filter-ab.html` presents unaccepted plain and
accepted filtered native recordings at equal configured gain without extra
normalization or sample alignment. The normalized software DS/native comparison
is separate. Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
sustained notes, volume changes, moving stereo, tails and joins near0:30/0:46;
repeated chip/Buster effects; and three battle→map→battle encounters with native
map restoration and fresh imported starts. Automated verification and user
reports remain separate. Comparative timbre preference, independent timing,
full gameplay traces, linked play and rematches were not separately reported.
No acceptance is inferred for the plain control or another source family.
All recorded voice/filtering/PCM8/volume/ADSR/tempo and regression coverage
limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-jiken-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-jiken-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
