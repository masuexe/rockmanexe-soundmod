# SF3 DEMPAJIKEN: eleven-track merged antialias experiment

This experiment applies the existing explicit merged-filter capability to
accepted SF3 slot26 `BGM_DEMPAJIKEN`, using `SF3_DEMPAJIKEN_GROUPS`:
`[[0],[1],[2,4,6],[3],[5,8],[7],[14],[15]]`. Each merged group retains equal
fixed source volumes (110 and90). Source8 pan is baked per note; singleton
tracks retain live PAN. No converter or native capability is added. Upward
preparation, LFO, attack fitting, finite release and mixed-loop modes are not
enabled. Existing control/grouping, alias/release, held-pan, sample-budget,
unsupported-effect and model guards remain.

All584 source mappings, controls, grouping, timing, velocities and priorities
match the accepted plain conversion. The source2/key64 long alias127 remains
on merged native track2; no loop carry is required. An unpacked eleven-track
control checks source schedules/velocities. A separate unpacked filtered
control reproduces all96 prepared wave headers and raw PCM bytes using the
same DSP implementation; neither control runs in the eight-track target.
All103 keyed tones retain source ADSR/root/pan and relocated wave bytes.
All2,396 playback commands are byte identical except GOTO pointer relocation,
whose relative targets remain exact.

Prepared storage is680,241 PCM8 bytes, maximum source step about11.881, below
the32-step and4MB guards. Maximum stored tuning error is about0.00028434 cents,
not a whole-song native frequency-error bound. Analysis-only instrumentation
reproduces every byte and records5,834 clamped points (2,403 negative,3,431
positive), with unclamped values about−154.929…153.022. These are stored points,
not time-weighted playback, native mixer clipping or an audible-error bound.
No per-wave normalization or runtime mixer change is introduced.

The independent180-second software DS reference is reused from the accepted
plain study. SDAT and both recursive reference copies are pinned; the source
checker is rerun, matching5,067 source notes and17 decoded waves with tempo,
controls and ADSR checks. This is no new renderer run or DS hardware capture.
Source tempo150 maps to native151, about119.973 source versus120.251 native
ticks/s. Common entry768 and period1728 put entry near0:06, with joins near
0:21/0:35. Existing tempo quantization remains.

Natural frontend Start input reaches clock4226 in2,100 frames, covering two
cycles and all96 waves without register/RAM injection, header redirection,
forced repeats or clock restarts. A separate read-only observation of the
unchanged original NOTE handler reaches clock4241 in2,107 frames:999 calls,
996 allocations and three rejections. All original source identities, note
clocks and allocation outcomes match a fresh read-only exact accepted plain
ROM capture over the same window. Rejections remain at clocks696/2424/4152,
source14, key64, instrument19, native track6. The events remain in the score;
the existing ten-voice native allocator rejects them at playback.

There are also three held/starting preemptions in that window. Their clocks
and displaced source/note/key/gate identities match the fresh plain baseline:
source15 key73 at note clocks600/2328/4056, displaced at696/2424/4152, with
observed gate byte96. This is a channel-flag/pre-unlink observation, not a
claim about the audible truncation duration. Release-channel reuses with
nonzero envelope rise522→532 and383 slot choices differ. Rejection success
alone is not a proof of unrestricted polyphony or preservation of tails.
The old plain artifacts stay immutable; fresh baseline outputs are separate.

All996 allocated channels retain gate/key/velocity/source-derived priority.
There are84,280 saved BEND/BENDR/TUNE/PAN/VOL byte comparisons, including
source-derived singleton pitch/pan/volume and expression. Source7 expression
produces nine observed native volume levels4–52. Three original long-alias
uses remain held through their source gates and release afterward despite
same-group sibling activity. Stereo analysis matches the latest original
NOTE identity to each active merged-source8 channel, excluding starting and
release states:668 observations,283 at source pan30 (median signed balance
−0.550) and385 at pan94 (median+0.512). These are saved-state diagnostics, not
waveform alignment or a full-song loudness/stereo-error bound.

The initial window-analysis fixture assumed every NOTE allocated and tried
to read preallocation bytes on rejected records. The final fixture retains
and separately compares all rejection identities, and classifies displaced
channels only for successful allocations. The initial failed log/fixture
remain distinct. Converter and ROM were unchanged. No zero-velocity NOTE call
is observed. Emulated frame-clock residual is at most two ticks against a
two-tick bound, not independent hardware or wall-clock timing.

Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
They do not establish actual chip gameplay, linked play or rematches.
All467 prospective-source tests pass without skips, including two new
builder/family/capacity/filter-guard cases. Root migration matches frozen
source hashes and both focused cases pass. All54 accepted and two unaccepted
control ROM/BPS pairs rebuild identically. Production CLI reproduces all eight
native-tested files byte for byte. Recursive v10–v33 archive identities remain
unchanged. Automated evidence remains distinct from manual acceptance.

## Accepted exact ROM

- ROM CRC32: `E0395A10`; size9,098,008 bytes.
- ROM SHA-256: `5eb54e17c9e4155f975aaab02e8443284f2d49e27336111f42ad7fe39fe03013`.
- BPS SHA-256: `a196b81730d01914eef436dac932e89c60c3c7bcc49e58cb49b2db7fb0a1e50f`.
- Local folder: `out/nds-research/sf3-dempajiken-merged-antialias-exe6-v1/`.

The30-second native preview peaks at16057 and covers entry, first GOTO and
the first two known rejection/preemption clocks, not the second GOTO or third
rejection. `comparison/merged-filter-ab.html` compares native plain/filtered
versions at the same configured gain without extra loudness normalization or
sample alignment. Plain audio is already a GBA conversion. The normalized
software DS/native page is separate. Comparative timbre preference is distinct
from functional acceptance.

On 2026-10-23, the user reported “测试没有问题” for this exact ROM, accepting
the requested three-minute virus-battle listening, repeated chip/Buster
effects and three battle→map→battle encounters with native-map restoration
and a fresh imported start. This is user-reported manual acceptance, separate
from automated evidence. Comparative timbre preference, independent timing,
a full manual trace, linked play and rematches were not separately reported.
Known accompaniment rejections, observed preemptions, ten-voice tails,
conservative filtering, clipping and PCM8/volume/ADSR/tempo quantization remain.
Acceptance binds only the fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-dempajiken-merged-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-dempajiken-merged-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
