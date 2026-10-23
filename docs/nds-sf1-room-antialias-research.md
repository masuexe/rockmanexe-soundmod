# SF1 ROOM: six-track singleton antialias experiment

This experiment adds a pinned selector for SF1 slot4 `BGM04ROOM`, using the
existing singleton filtered converter. All six tracks remain separate; no
converter/native capability or merged mode is added. Upward preparation,
LFO, fitted attack, finite release and mixed-loop modes remain disabled.
Existing capacity, unsupported-effect, filter-budget and model guards remain.
This is a new source song with no prior manual acceptance.

All471 mapped notes, controls, timing, priorities and velocities match a new
same-exporter plain control. The raw SSEQ trace is compared after JSON type
normalization; its source actions expand to the common entry24 and period1536
without flattening or discarding controls. All six source/native tracks remain
separate, with no long aliases or loop carries. No note mapping rounds to zero.
The plain control is explicitly marked `unaccepted_control`; it has no manual
acceptance and is not presented as a previously validated version.

All80 keyed tones and80 prepared waves retain source ADSR/root/pan and relocated
PCM bytes. All1,969 playback commands are byte identical to the plain control
except GOTO pointer relocation, with relative targets exact. Prepared storage
is456,786 PCM8 bytes, maximum source step about13.683, below the32-step and4MB
guards. Analysis-only instrumentation reproduces every prepared byte and counts
859 clamped points (512 negative,347 positive), with unclamped values about
−138.422…140.590. These are stored points, not time-weighted playback, native
mixer clipping or an audible-error bound. No normalization or runtime mixing
change is introduced.

A fresh independent180-second software DS reference is rendered with the
pinned conductor-capable executable. SDAT, renderer and recursive reference
outputs are hashed. The checker matches5,407 source notes and15 decoded waves,
with source tempo, controls and ADSR checks. The reference peaks at14056 with
a coarse16-voice maximum; it is not DS hardware audio. Source tempo125 maps
to native126, about99.977 source versus100.342 native ticks/s. Common entry24
is near0:00.24 and joins are near0:16/0:31. Tempo quantization remains.

Natural frontend Start input reaches clock3097 in1,844 frames, covering two
cycles and all80 waves without register/RAM injection, header redirection,
forced repeats or clock restarts. A separate read-only observation of the
unchanged original NOTE handler reaches clock3112 in1,853 frames: all938 NOTE
calls allocate, with no rejection or held/starting preemption. Source identities,
note clocks, outcomes and all slot choices match the new unaccepted plain
control. Nonzero-envelope release reuses are479 filtered versus478 plain.
This does not establish unrestricted polyphony or lossless tails.

All938 allocated channels retain gate/key/velocity/source-derived priority.
There are55,590 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across the
six active tracks, including source effective pitch and singleton pan/volume.
Source2 stereo is checked against original allocations and source-definition
pan after one stable-pan frame, excluding starting/release and low-volume
quantization states. There are953 retained observations across three pan
values; left/right extreme groups contain137/110 samples with median signed
balance about−0.714/+0.571. These diagnostics do not establish whole-song
stereo waveform alignment. Every saved frame matches the fixed-tempo model
`1 + floor((frame-1)*126/75)`; anchored fractional residual is below one tick,
not independent hardware or wall-clock timing.

Initial analysis fixtures compared loaded JSON with in-memory tuples and
assumed an eight-track/640-byte track-memory block. The final checks normalize
JSON types and require the actual six-track/480-byte block plus the separate
640-byte channel block, retaining all snapshot-count checks. An initial audio
comparison also ran before the asynchronous preview existed; the final page
is generated after preview completion. Failed setup logs/fixtures remain
separate from final passes. Converter and ROM were unchanged.

Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
They do not establish actual chip gameplay, linked play or rematches.
All483 prospective-source tests pass without skips, including two new
builder/family/capacity/explicit-mode guard cases. Root migration matches
frozen source hashes and both focused cases pass. All56 accepted and two
historical unaccepted control ROM/BPS pairs rebuild identically. The current
ROOM plain control is separate from those old-version regressions. Production
CLI reproduces all eight native-tested files byte for byte; recursive v10–v35
archive identities remain unchanged.

The experimental ROM/BPS also match the previously unaccepted `ssr1:4`
filtered audit output exactly. That audit match supplies no runtime/manual
acceptance by itself. SF2 ROOM happens to produce the same ROM SHA in the
scan, but source-family provenance and manual records remain separate; this
experiment does not grant SF2 acceptance or plain-version acceptance.

## Accepted exact SF1 ROM

- ROM CRC32: `A9FF0FF4`; size8,868,676 bytes.
- ROM SHA-256: `18d2996a63391686b66b025b7a797436adda1cb369dcc50320fc7ab79722e9dc`.
- BPS SHA-256: `7443451a7c4a657cac77473949954be56b1b9a7a9e2eb6b6f4643f32053bbc3b`.
- Local folder: `out/nds-research/sf1-room-antialias-exe6-v1/`.

The30-second native preview peaks at13281 and covers the first join, not the
second. `comparison/filter-ab.html` presents unaccepted plain and pending
filtered native recordings at the same configured gain without extra loudness
normalization or sample alignment. The normalized software DS/native page is
separate. Comparative timbre preference is distinct from functional acceptance.

On 2026-10-24, the user reported “测试没有问题” for this exact SF1 ROM,
accepting the requested three-minute virus-battle listening, repeated
chip/Buster effects and three battle→map→battle encounters with native-map
restoration and a fresh imported start. This is user-reported manual acceptance,
separate from automated evidence. The plain control remains unaccepted and no
SF2-family acceptance is inferred despite matching output bytes. Comparative
timbre preference, independent timing, a full manual trace, linked play and
rematches were not separately reported. Ten-voice tails, conservative filtering,
clipping and PCM8/volume/ADSR/tempo quantization remain. Acceptance binds only
the SF1 provenance and fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-room-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-room-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
