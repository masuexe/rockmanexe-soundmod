# SF3 STUDIO: fifteen sources, two long aliases and held-note expression

This separate experiment imports verified Japanese SF3 `ssr3b`, sequence4
`BGM_STUDIO`, into Japanese EXE6 Gregar through selector
`sf3-studio-fifteen-track`. Groups are
`[[0],[1],[2],[3],[4,5,6,7,8,12,14,15],[9],[10],[11]]`: fifteen sources become
eight native tracks. The existing plain merged converter, ten PCM voices,
10512 Hz and +3.5 dB gain remain. No converter/native-driver capability is
added. Archived v26 still marks STUDIO capacity-blocked; no generic batch
search is enabled.

## Schedules, ratios and extreme soft-note quantization

The eight-source group has fixed volumes 110/80/90/95/90/110/70/50, normalized
to group volume110 through the existing velocity-ratio formula. Shared
expression/effective-pitch and held-note-pan guards remain unchanged. Sources
with incompatible or changing controls stay independent: source2 retains its
long-note expression crescendo and source10 its volume110/127 changes. Merged
parts keep note-on pan in tones; singleton controls retain their time course.

All 3,431 source note tuples, including multiplicity and twelve duplicated
tuples, match an unpacked fifteen-track singleton control. That control is
not packed or runnable in the eight-track target. There are 910 ratio-scaled
mappings; unscaled velocities match the control. Maximum absolute linear-
velocity rounding error is about 0.46594. This is not a perceived-loudness or
waveform error bound. All eight compiled tracks pass two-cycle note/gate/timing
comparisons. Source priorities and scheduled events remain intact.

Four extremely soft mappings on source15 have original velocity5 and native
velocity0, at ticks564/1332/5748/6516. **The unpacked control has the same four
zero-velocity mappings**; grouping introduces none. The events are retained
rather than silently dropped or clamped upward. In the original native
observation window these correspond to six actual NOTE calls, including the
next loop at 10932/11700; all six allocate with native velocity0 and both
channel volumes zero. This existing volume/velocity quantization limit remains
explicit and separate from new ratio rounding and native voice allocation.

The source SDAT SHA-256 remains
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
The pinned independent 180-second software DS reference matches 6,936 notes,
22 unique decoded waves, source tempo/depth controls, 6,936 ADSR note-on
snapshots and 508,954 per-voice timer updates. All attacks are instant; no
fitting, active LFO or offline filtering is enabled. This is software synthesis,
not DS hardware capture. All 3,431 packed mappings, 222 keyed tone slots and
23 separately tuned prepared waves match source-derived pan, ADSR, roots,
raw PCM8 and relocated wave headers/data.

## Native playback, aliases and held-note crescendo

Common entry is4800 ticks, period5184, joins9984/15168. Tempo141 maps to
MPlay142, about 112.774 source versus 113.084 native ticks/second: entry around
0:42, jumps around 1:28/2:14. Natural frontend playback uses verified Start
input at frames 180–190, reaches clock15170 in 8,013 frames and covers two common
cycles plus all 23 waves. There is no RAM/register injection, forced repeat,
header redirect or clock restart. Original NOTE handler bytes remain identical
to the pinned base.

Read-only NOTE entry/allocation/exit observation reaches clock15185 in 8,021
frames. All 5,202 scheduled NOTE calls allocate, with exact wave, owner, key,
ADSR, initial gate, velocity and source-derived priority. All fifteen sources
are represented. Player clocks stay within 1.88 ticks of the theoretical fixed-
tempo frame rate, inside a two-tick bound. This is an emulated-frame check,
not a wall-clock or hardware recording.

Source2 keys70/72 use aliases127/126 on their singleton native track. All 24
observed long-note uses remain held through their gate windows and release
afterwards; their source waves are looped. No carry across the common loop
boundary is required. Same-group sibling EOT isolation is not relevant to
this singleton source.

Saved BEND/BENDR/TUNE/PAN/VOL bytes pass320,840 comparisons against compiled
commands; computed pitch matches source effective units and singleton pan
matches source controls. Source2 retains ten native VOL values through its
expression changes, and source10 retains native VOL57/76. Source2's expression
changes after note onset: its long key70 note crescendos around 0:26,1:12 and
1:58. Across the three held-note windows, 27/27/28 channel snapshots show
monotonic left-plus-right volume growth from 51 to 81 through nine distinct
levels each. This establishes that the native volume change reaches the held
voice, not merely the sequence/track state. It is not sample-aligned DS
amplitude or waveform equivalence.

The merged group has at least two gated members in 3,497 frames, identified by
actual slot allocations and validated owner/wave without assuming source waves
are distinct. All 360 source5 initial stereo snapshots retain left/center/right
contrast:132 at pan24,36 at pan64 and 192 at pan104, with median signed balances
about -0.636/0/+0.667. This is channel-volume contrast, not a whole-song pan bound.

## Recorded limits and diagnostics

Snapshots immediately before the original chosen-channel unlink call show
**no held/starting-channel preemption** in this two-cycle window. There are
2,863 reuses of release-flagged channels with nonzero envelope, which can
shorten tails. Successful new-note allocation and the absence of observed
held-note preemption do not establish complete original DS polyphony or a
whole-song audible-error bound. Ten native PCM voices versus sixteen DS
software voices, release tails, the four extremely soft zero mappings,
fixed-volume ratio rounding and ordinary PCM8/ADSR/tempo quantization remain.

The existing analysis-only exact-command-echo normalization handles two
terminal echoes in the unchanged saved log. All 5,202 allocated note blocks
and 8,021 frame blocks are still counted and compared; no memory hex or field
comparison is removed. One setup attempt preceded build completion, and one
copy-template anchor needed correction before helper creation; these setup
corrections do not modify the ROM or source converter. Coverage and diagnostics
remain separate from manual acceptance.

Controlled effects100/129, continuation, queued stop and three native-restore/
restart helper cycles pass. Helper calls inject PC/LR/arguments into a disposable
emulator and do not establish real battle/map transitions, linked play or
rematches. The thirty-second native preview peaks at 17760 and covers the first
crescendo, but neither the common entry nor either GOTO. Full natural sequence
checks are separate; normalized DS/native comparison is not sample-aligned.

## Regression and accepted exact ROM

All 406 prospective-source tests pass without skips, including the new source
schedule/velocity/alias and independent-control assertions. Tests explicitly
retain the four existing zero mappings without adding new ones. Root migration
matches frozen tested hashes, and both focused root cases pass. All 47 accepted
and two unaccepted control ROM/BPS pairs rebuild identically. The production
CLI reproduces all eight native-tested files byte for byte. Archived v10–v26
recursive file/path identities remain unchanged; historical source-pin
validators are not rerun against subsequently changed source.

- ROM CRC32: `91E9AFE6`; size 8,839,456 bytes.
- ROM SHA-256: `0a45586aee5c22835490442cf4536d3d168f21017bcb923c36583183e2f40489`.
- BPS SHA-256: `6837bbaa52b1d15ed55c689c25479d03d9c33c00ca96e3b926e6fdc8b80c0207`.
- Local folder: `out/nds-research/sf3-studio-fifteen-track-exe6-v1/`.

On 2026-10-22, the user reported “测试没有问题” for this exact ROM and the
requested three-minute listening, repeated chip/Buster effects and three
battle→map→battle checks. This is user-reported acceptance; no independently
timed recording, full gameplay trace, linked play, rematch or comparative
listening preference is inferred. The voice-reuse and quantization limits above
remain. Automation and manual acceptance are recorded separately.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-studio-fifteen-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-studio-fifteen-track-exe6-v1
```

Use a fresh directory. ROMs, original assets, captures, hashes and local research
outputs stay outside Git. Manual acceptance binds only this exact ROM.
