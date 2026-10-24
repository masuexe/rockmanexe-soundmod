# SF1 SCHOOL: singleton antialias validation

This new source-song experiment uses the existing singleton FIR preparation
and unchanged EXE6 native mixer. The public `sf1-school-antialias` selector
pins verified SF1 SDAT sequence6, `BGM06SCHOOL`, to seven singleton tracks.
It enables no merged, upward, fitted-envelope, release-snapshot, finite-song,
mixed-song or LFO extension. Source/base identities, track capacity and existing
exporter guards remain mandatory. No new conversion capability is claimed.

A separate same-source plain export is explicitly `unaccepted_control`:
`out/nds-research/sf1-school-plain-control-v1/`. It is freshly built and does
not inherit acceptance from its audit bytes, song name or another source family.
The filtered exact SF1 ROM has user-reported acceptance below; the plain control remains unaccepted.

## Automated evidence and limits

All1,827 mappings match expanded raw SSEQ schedules and the plain export.
All7,409 compiled playback commands match apart from relocated GOTO pointer
words, whose relative targets match. Source controls, priorities, note timing,
loop carries and voice contexts remain unchanged, with no zero-velocity mapping.
All121 keyed tones and120 prepared waves retain source root/pan/ADSR and
relocated data. Per-wave source-key resampling reproduces the packed bytes;
this uses the same DSP implementation and is not independent audio validation.

There are663,833 stored PCM8 points, including1,750 clamped values
(718 negative,1,032 positive); unclamped extrema are approximately−166.301 and
161.520. These are storage counts, not time-weighted audible error or native
mixer clipping. Maximum source step is about12.6066 and appended size708,032
bytes. Conservative filtering, PCM8 limits and envelope/volume quantization
remain explicit.

A fresh independently executed180-second software DS reference matches4,253
notes and24 decoded raw waves, tempo/depth controls and source ADSR. Reference
peak is17195 and coarse100ms maximum voices16. It is a software renderer,
not DS hardware. A failed initial ad-hoc inspection used a nonexistent trace
field; its error is recorded locally and corrected inspection uses the actual
notes/actions fields. That inspection failure changed no converter or ROM and
is separate from the passing evidence.

The common entry is3072 and period5376 ticks. Source tempo138 maps to native
parameter139, about110.375→110.695 ticks/s. Common entry is near0:28 and GOTO
joins near1:16/2:05. Tempo quantization remains.

Natural frontend Start input reaches clock13825 in7,460 frames, covering two
complete cycles and all120 waves without register/RAM injection, header
redirection, forced repeats or clock restarts. A separate read-only observation
of the unchanged original NOTE handler reaches clock13841 in7,469 frames:
all2,972 calls allocate, with no rejection or held/starting preemption. Source
identities, clocks, allocation outcomes and every slot choice match the
unaccepted plain control. Both variants reuse1,154 nonzero-envelope release
channels. This does not prove preservation of all tails or unrestricted
polyphony outside the observed window.

All2,972 allocated channels retain gate/key/velocity/source-derived priority.
There are261,415 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
seven tracks, including source effective pitch and singleton pan/volume.
The source4/key48 long-note alias127 retains all three original288-tick holds
and releases at source starts1536/6912/12288. No forced repetition is used.
Source3 stereo diagnostics retain1,645 settled observations across five pan
values, excluding changed-pan, starting/release and low-volume states.
Left≤20 and right≥100 groups contain403/706 observations, with median signed
balance approximately−0.857/+0.590. Source-definition pan is included. These
checks do not establish full-song waveform alignment. Final review corrected
an offline grouping threshold that had included536 center-pan observations in
the right group; the original grouping and correction are preserved locally.
Reanalysis uses source PAN≥100 and changes no ROM or native/control evidence.

Every saved frame matches `1 + floor((frame-1)*139/75)` with anchored fractional
residual below one tick. This is an emulated phase check, not independent
hardware/wall-clock timing. Controlled helper effects100/129, continuation,
queued stop and three restore/restart cycles pass using disposable emulator
PC/LR/argument injection. Actual gameplay, linked play and rematches remain
separate manual scope.

All487 prospective-source tests pass without skips, including two new
builder/family/capacity/explicit-mode guard cases. Root migration matches
frozen source hashes and both focused cases pass. All58 accepted and two
historical unaccepted control ROM/BPS pairs rebuild identically; the current
SCHOOL plain control is separate. Production CLI reproduces all eight
native-tested files byte for byte. Recursive v10–v37 archive identities remain
unchanged. Matching previously unaccepted `ssr1:6` filtered audit bytes grants
no new native or manual acceptance by itself.

## Accepted exact SF1 ROM

- ROM CRC32: `3D5D2ED1`; size9,096,640 bytes.
- ROM SHA-256: `72920d4362632bdd27d03c1a9473509893b4300e0a66400fd7a88decec82833e`.
- BPS SHA-256: `51fbfe7b9679c2db75f8189f90ab1cdbc2de80675231312b307027f1e5289bec`.
- Local folder: `out/nds-research/sf1-school-antialias-exe6-v1/`.

The30-second native preview peaks at17752 and covers the first long note's
hold/release and common entry near0:28, but not the first GOTO near1:16.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
recordings at equal configured gain without extra normalization or sample
alignment. The normalized software DS/native comparison is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试没有问题”. This covers three-minute virus-battle listening including
long notes, moving stereo, tails and joins near1:16/2:05; repeated chip/Buster
effects; and three battle→map→battle encounters with native-map restoration
and fresh imported starts. Automated verification and user-reported acceptance
remain separate. Comparative timbre preference, independent timing, full
gameplay traces, linked play and rematches were not separately reported.
The plain control and other source families receive no inferred acceptance.
All recorded voice, filtering, PCM8/volume/ADSR/tempo limits remain.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-school-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-school-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
