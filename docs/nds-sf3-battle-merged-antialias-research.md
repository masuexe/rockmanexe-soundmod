# SF3 BATTLE: eleven-track merged antialias experiment

This experiment applies existing merged filtering to accepted SF3 slot35
`BGM_BATTLE`, using `BATTLE_GROUPS`:
`[[0,9],[1],[2,15],[3],[4,14],[5],[6],[7]]`. No converter or native capability
is added. Existing fixed-volume ratios, shared expression/effective pitch,
held-pan, alias/release, unsupported-effect, filter-budget and model guards
remain. All executed bends are nonpositive. An initial source probe enabled
upward preparation and found only shift0; the final probe and builder omit
that unnecessary mode. LFO, fitted attack, finite release and mixed-loop modes
are not enabled.

All3,030 source mappings, controls, timing, velocities, priorities and grouping
match the accepted plain conversion. An unpacked eleven-track control checks
source schedules and the accepted fixed-volume ratio formula. Group volumes
normalize0/9 to120,2/15 to100 and4/14 to90. There are1,340 ratio-scaled mappings;
maximum absolute linear velocity-rounding error is about0.45939 and no mapping
rounds to zero. This is not a loudness-error bound. Two long aliases on native
track2 remain: source2/key75→127 and source15/key75→126, with no loop carry.

A separate unpacked filtered control reproduces all170 prepared wave headers
and raw PCM bytes using the same DSP implementation. Neither eleven-track
control runs in the eight-track target. All215 keyed tones retain source
ADSR/root/pan and relocated wave data. All12,168 playback commands are byte
identical except GOTO pointer relocation, with relative targets exact.

Prepared storage is1,054,239 PCM8 bytes, maximum source step about9.443, below
the32-step and4MB guards. Analysis-only instrumentation reproduces every byte
and records10,009 clamped points (3,751 negative,6,258 positive), with unclamped
values about−157.283…165.581. These are stored points, not time-weighted
playback, native mixer clipping or an audible-error bound. No per-wave
normalization or runtime mixing change is introduced.

A fresh independent180-second software DS reference is rendered with the
pinned conductor-capable reference executable. SDAT, renderer and recursive
reference outputs are hashed. The source checker matches7,087 notes and24
decoded waves with source tempo, controls and ADSR checks. The software
reference peaks at18499 with a coarse16-voice maximum. It is not a DS hardware
capture. Source tempo153 maps to native154, about122.372 source versus122.640
native ticks/s. Common entry3552 and period5760 put entry near0:29, then joins
near1:16/2:03. Tempo quantization remains.

Natural frontend Start input reaches clock15074 in7,342 frames, covering two
cycles and all170 waves without register/RAM injection, header redirection,
forced repeats or clock restarts. A separate read-only observation of the
unchanged original NOTE handler reaches clock15088 in7,349 frames: all4,877
NOTE calls allocate and none reject. Source identities, note clocks, allocation
outcomes and all slot choices match a fresh read-only capture of the exact
accepted plain ROM. Both have23 held/starting preemptions and3,331
nonzero-envelope release reuses. All23 preemption clocks and displaced
source/note/key/gate identities match, not merely their count. The old accepted
plain artifacts remain unchanged; fresh captures are separate. This does not
establish unrestricted polyphony, full-song equivalence or lossless tails.

All4,877 allocated channels retain gate/key/velocity/source-derived priority.
There are293,960 saved BEND/BENDR/TUNE/PAN/VOL byte comparisons, including
source effective pitch and singleton pan/volume. Shared source2/15 expression
produces14 observed native volume levels10–47. All eight original long-alias
uses remain held through their source gates and release independently;
both aliases are simultaneously active in561 saved snapshots. Two shared
expression-fade windows each provide42 snapshots per alias with constant
envelope255: alias126 channel-volume sum falls10→3 through eight values,
while alias127 falls41→11 through eleven values. These demonstrate actual
held-channel volume changes, not a DS waveform/loudness-error bound.

Moving singleton source6 stereo is checked against original allocations and
source-definition pan, after one stable-pan frame and excluding starting,
release and low-volume quantization states. There are4,257 retained
observations across32 source pan values. Left/right extreme groups contain
1,355/119 observations, median signed channel-volume balance about−0.855/
+0.846. These are saved-state diagnostics, not full-song stereo waveform
alignment.

The copied initial frame-clock fixture assumed an unanchored two-tick bound.
At tempo154 its observed residual reaches2.04 ticks because the first native
snapshot is frame1/clock1. The final diagnostic anchors that origin and checks
every snapshot exactly against `1 + floor((frame-1)*154/75)`. Anchored fractional
residual remains below one tick. This is an emulated fixed-tempo phase check,
not independent hardware/wall-clock timing. The initial failed fixture/log
remain separate; converter and ROM were unchanged.

Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
They do not establish actual chip gameplay, linked play or rematches.
All475 prospective-source tests pass without skips, including two new
builder/family/capacity/filter-guard cases. Root migration matches frozen
source hashes and both focused cases pass. All55 accepted and two unaccepted
control ROM/BPS pairs rebuild identically. Production CLI reproduces all eight
native-tested files byte for byte. Recursive v10–v34 archive identities remain
unchanged. Automated evidence stays distinct from manual acceptance.

## Accepted exact ROM

- ROM CRC32: `89634045`; size9,501,172 bytes.
- ROM SHA-256: `1490032534e505fc145877c291f99dd1c80fa789b5db7fa4325be24cb4ac3c33`.
- BPS SHA-256: `d9199e6ad3079bb54f3ca1e116db71bd7326fb227586e2df6875615fff4d1984`.
- Local folder: `out/nds-research/sf3-battle-merged-antialias-exe6-v1/`.

The30-second native preview peaks at16548 and covers the common entry, not
the first long alias near0:32 or the first GOTO near1:16.
`comparison/merged-filter-ab.html` compares native plain/filtered recordings
at the same configured gain without extra loudness normalization or sample
alignment; plain audio is a fresh capture of the exact accepted GBA conversion.
The normalized software DS/native page is separate. Comparative timbre
preference is distinct from functional acceptance.

On 2026-10-24, the user reported “测试没有问题” for this exact ROM, accepting
the requested three-minute virus-battle listening, repeated chip/Buster
effects and three battle→map→battle encounters with native-map restoration
and a fresh imported start. This is user-reported manual acceptance, separate
from automated evidence. Comparative timbre preference, independent timing,
a full manual trace, linked play and rematches were not separately reported.
Existing preemptions, ten-voice tails, conservative filtering, clipping and
PCM8/volume/ADSR/tempo quantization remain. Acceptance binds only the
fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-battle-merged-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-battle-merged-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets, captures and local outputs stay outside Git.
