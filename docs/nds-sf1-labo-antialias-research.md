# SF1 LABO: eight-track singleton antialias experiment

This experiment adds a pinned selector for SF1 slot5 `BGM05LABO`, using the
existing singleton filtered converter. All eight source tracks remain separate.
No converter/native capability or merged mode is added. Upward preparation,
LFO, fitted attack, finite release and mixed-loop modes remain disabled.
Existing capacity, unsupported-effect, alias/release, filter-budget and model
guards remain. This is a new song with no prior manual acceptance.

All2,254 mapped notes, source controls, timing, priorities and velocities match
a new same-exporter plain control. The raw SSEQ trace is checked after JSON
type normalization; source actions expand to common entry2112 and period6144
without flattening or control removal. The source3/key56 alias127 is retained
and no loop carry is required. No mapping rounds to zero. The plain control
is explicitly `unaccepted_control`, with no manual or previous-version claim.

All146 keyed tones and145 prepared waves retain source ADSR/root/pan and
relocated PCM bytes. All9,236 playback commands are byte identical to the
plain control except GOTO pointer relocation, with relative targets exact.
Prepared storage is959,856 PCM8 bytes, maximum source step about12.919, below
the32-step and4MB guards. Analysis-only instrumentation reproduces every byte
and records6,028 clamped points (2,277 negative,3,751 positive), with unclamped
values about−146.976…149.440. These are stored points, not time-weighted playback,
native mixer clipping or an audible-error bound. No normalization or runtime
mixing change is introduced.

A fresh independent180-second software DS reference is rendered with the
pinned conductor-capable executable. SDAT, renderer and recursive reference
outputs are hashed. The source checker matches5,377 notes and25 decoded waves
with tempo, controls and ADSR checks. The reference peaks at20869 with a
coarse16-voice maximum; it is not DS hardware audio. Source tempo137 maps to
native138, about109.575 source versus109.899 native ticks/s. Common entry2112
is near0:19, with joins near1:15/2:11. Tempo quantization remains.

Natural frontend Start input reaches clock14402 in7,828 frames, covering two
cycles and all145 waves without register/RAM injection, header redirection,
forced repeats or clock restarts. A separate read-only observation of the
unchanged original NOTE handler reaches clock14417 in7,836 frames: all3,931
NOTE calls allocate, with no rejection or held/starting preemption in either
filtered ROM or plain control. All source identities, note clocks and allocation
outcomes match, while2,759 slot choices differ. Nonzero-envelope release reuses
rise951→1115. This does not prove preservation of tails, unrestricted polyphony
or inaudibility of those changes; tail behavior remains a listening focus.

All3,931 allocated channels retain gate/key/velocity/source-derived priority.
There are313,440 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
eight tracks, including source effective pitch and singleton pan/volume.
The four original long-alias uses remain held through their source gates and
release afterward. Source6 moving stereo is checked against original
allocations and source-definition pan after one stable-pan frame, excluding
starting/release and low-volume quantization states. There are1,775 retained
observations across19 pan values; left/right extreme groups contain525/125
samples with median signed balance about−0.843/+1.000. These diagnostics do
not establish whole-song stereo waveform alignment.

Every saved frame matches `1 + floor((frame-1)*138/75)`, with anchored fractional
residual below one tick. This is an emulated phase check, not independent
hardware/wall-clock timing. Controlled helper effects100/129, continuation,
queued stop and three native restore/restart cycles pass using disposable
emulator PC/LR/argument injection. They do not establish actual chip gameplay,
linked play or rematches.

All485 prospective-source tests pass without skips, including two new
builder/family/capacity/explicit-mode guard cases. Root migration matches
frozen source hashes and both focused cases pass. All57 accepted and two
historical unaccepted control ROM/BPS pairs rebuild identically; the current
LABO plain control is separate. Production CLI reproduces all eight native-tested
files byte for byte. Recursive v10–v36 archive identities remain unchanged.
The ROM/BPS also match the previously unaccepted `ssr1:5` filtered audit bytes;
that match alone supplies no native or manual acceptance.

## Accepted exact SF1 ROM

- ROM CRC32: `E7A73FAF`; size9,398,172 bytes.
- ROM SHA-256: `a6996410dbe6d95b6108dbabbaae695fd0a27294b9d18030717d857653b4a5bb`.
- BPS SHA-256: `52640008bcfcdf1dc224ed2edf5965a7dcb221b217286bd6b01f9004628c5351`.
- Local folder: `out/nds-research/sf1-labo-antialias-exe6-v1/`.

The30-second native preview peaks at18175 and covers entry and the first long
note onset near0:28, not its full release near0:31 or the first GOTO near1:15.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at the same configured gain without extra normalization or
sample alignment. The normalized software DS/native page is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM checks passed on 2026-10-24:
“测试无问题”. This covers the requested three-minute virus-battle listening,
long notes, moving stereo, tails and joins near1:15/2:11; repeated chip/Buster
effects; and three battle→map→battle encounters with native-map restoration
and fresh imported starts. This is user-reported acceptance, separate from
automated verification. Comparative timbre preference, independent timing,
full gameplay traces, linked play and rematches were not separately reported.
The plain control and other source families remain unaccepted. Ten-voice tails,
conservative filtering, PCM8/clipping and volume/ADSR/tempo limits remain.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-labo-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-labo-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
