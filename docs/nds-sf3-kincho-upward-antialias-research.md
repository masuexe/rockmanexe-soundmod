# SF3 KINCHO: ten-track upward antialias experiment

This experiment applies existing merged-filter and upward-preparation modes
to accepted SF3 slot30 `BGM_KINCHO`, using `SF3_KINCHO_GROUPS`:
`[[0],[1],[2,4,6],[3],[5],[7],[14],[15]]`. The three merged sources keep fixed
volume100 and compatible expression/effective pitch; source6 pan is baked
per note while singleton tracks retain live PAN. No converter or native
capability is added. Existing grouping, held-pan, alias/release, one-octave/key,
filter-budget and unsupported-effect guards remain. LFO, attack fitting,
finite release and mixed-loop modes are not enabled.

All741 source mappings, controls, grouping, timing, priorities and velocities
match the accepted plain conversion. There are no long aliases or loop carries.
An unpacked ten-track control checks source schedules and velocities. A
separate unpacked filtered control reproduces all108 prepared wave headers
and raw PCM bytes using the same DSP implementation; neither ten-track control
is runnable in the eight-track target. All112 keyed tones are checked for
source ADSR/root/pan and relocated wave data. All3,469 compiled commands are
byte identical except GOTO pointer relocation, with relative targets exact.

Shared physical wave/root/source-key maxima prepare94 waves at shift0 and14
at shift2. The bounds are independently reconstructed from source controls
and note definitions. The nominal FIR cutoff at the bound is at most about
0.9002463 of mixer Nyquist after loop/tuning rounding. This is not a brick-wall,
zero-aliasing or audible-error bound. Conservative preparation can reduce
unbent bandwidth. Existing guards reject shifts above twelve semitones or
preparation-key overflow without clamping.

Prepared storage is1,086,559 PCM8 bytes, maximum source step about10.600,
below the32-step and4MB limits. Maximum stored tuning error is about0.0006105
cents, not a whole-song frequency-error bound. Analysis-only instrumentation
reproduces every output byte and counts10,592 clamped points (3,883 negative,
6,709 positive), with unclamped values about−142.706…142.651. These are stored
points, not time-weighted playback or native mixer clipping. No per-wave
normalization or runtime mixing change is introduced.

The independent180-second software DS reference is reused from the plain
KINCHO study. SDAT identity and both recursive reference copies are pinned;
the source checker is rerun, matching3,074 notes and21 decoded waves with
source tempo/controls/ADSR checks. It is not a new renderer run or DS hardware
recording. Source tempo110 maps to native110, about87.980 source versus87.600
native ticks/s. Common entry1560 and period2304 put entry near0:18 and first
joins near0:44/1:10. Tempo quantization remains.

Natural frontend Start input reaches clock6169 in4,207 frames, covering two
cycles and all108 waves without register/RAM injection, header redirection,
forced repeats or clock restarts. A separate read-only observation of the
unchanged original NOTE handler reaches clock6184 in4,217 frames: all1,194
NOTE calls allocate, zero reject, and no held/starting note is preempted.
There are477 nonzero-envelope release-channel reuses. A fresh read-only
capture of the exact accepted plain ROM over the same window has476 release
reuses and no held preemptions;175 slot choices differ. Source identities,
note clocks and allocation success match. The old plain artifacts remain
unchanged and the fresh baseline is stored separately. NOTE allocation alone
does not establish unrestricted polyphony or preservation of release tails.

All1,194 allocated channels retain gate/key/velocity/source-derived priority.
There are168,680 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons,
including source effective pitch and singleton pan/volume. Three held
source0/key73 windows at ticks1536/3840/6144 give7/6/6 snapshots, each with two
pitch values and two actual channel-frequency words (10502→10401). These
short within-note changes do not establish a full sweep on one held voice,
absolute DS-frequency equivalence or a waveform-error bound.

Stereo checks match the latest original NOTE identity to each active source6
channel, excluding starting/release states. All282 settled observations retain
opposing directions:174 at source pan10 with median signed volume balance
about−0.860 and108 at pan117 with median+0.862. Baked pan is also checked in
the packed tones. This is not a whole-song stereo waveform bound.

Initial analysis fixtures assumed allocation records had frame fields and
that a one-shot key36 sample stayed active for its whole nominal gate. Those
assumptions failed: records use note clocks and the sample naturally ends
early. Final checks match allocation clocks to saved frame clocks and observe
key73 within its actual active gate. Initial failed logs and fixtures remain
separate; converter and ROM were unchanged. No zero-velocity NOTE call is
observed. The emulated frame-clock residual stays within1.4 ticks against a
two-tick bound; this is not independently timed hardware playback.

Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
They do not establish actual chip gameplay, linked play or rematches.
All459 prospective-source tests pass without skips, including two new builder
and family/capacity/filter-guard cases. Root migration matches frozen tested
hashes and the two focused cases pass. All53 accepted and two unaccepted
control ROM/BPS pairs rebuild identically. Production CLI reproduces all eight
native-tested files byte for byte. Recursive v10–v32 archive identities remain
unchanged. Automated proof remains distinct from manual acceptance.

## Accepted exact ROM

- ROM CRC32: `A988A6B9`; size9,508,212 bytes.
- ROM SHA-256: `ae6243cff652dc8c028a2ed7d42ebdf38ba001218adec3cbf08231b65260ad01`.
- BPS SHA-256: `87a5c223a77cb9c5c09d341b968a363b632413573c84d6cd6ad37d2380a59a6b`.
- Local folder: `out/nds-research/sf3-kincho-upward-antialias-exe6-v1/`.

The30-second native preview peaks at17831 and covers entry and early bends,
not the first GOTO. `comparison/upward-filter-ab.html` compares native plain
and filtered versions at identical configured gain without extra loudness
normalization or sample alignment. Plain audio is already a GBA conversion;
the normalized software DS/native page is separate. Comparative timbre
preference is distinct from functional acceptance.

On 2026-10-23, the user reported “测试无问题” for this exact ROM, accepting
the requested three-minute virus-battle listening, repeated chip/Buster
effects and three battle→map→battle encounters with native-map restoration
and a fresh imported start. This is user-reported manual acceptance, separate
from automated evidence. Comparative timbre preference, independent timing,
a full manual trace, linked play and rematches were not separately reported.
Ten-voice tails, conservative filtering, clipping and PCM8/volume/ADSR/tempo
quantization remain. Acceptance binds only the fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-kincho-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-kincho-upward-antialias-exe6-v1
```

Use a fresh directory. ROMs, game assets, captures and local outputs remain
outside Git.
