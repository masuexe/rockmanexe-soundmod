# SF3 COMICAL: eight-track singleton antialias validation

This adds only `sf3-comical-antialias` for verified SF3 SDAT sequence28,
`BGM_COMICAL`, using eight singleton tracks and existing FIR preparation.
Converter/native code and guards remain unchanged. No merged, upward/LFO,
fitted-envelope, finite-release or mixed-song mode is enabled. No new
conversion capability is claimed. SF1 COMICAL acceptance is not transferred:
this experiment uses the pinned SF3 archive and produces different ROM/BPS bytes.

A fresh same-source plain export remains `unaccepted_control` at
`out/nds-research/sf3-comical-plain-control-v1/`, without a manual record.

## New-source automated evidence

All789 mappings match expanded raw SSEQ schedules and the plain control,
including source identity, gates, velocities, priorities, controls and timing.
All3,443 playback commands match apart from relocated GOTO words, whose relative
targets match. There are no zero-velocity mappings or long-note aliases/carry
adapters. All101 tones and101 prepared waves retain source root/pan/ADSR and
relocated PCM/header data. Resampling reproduction uses the same DSP
implementation, not independent audio validation.

Prepared storage contains590,001 PCM8 points and845 clamps:425 negative,
420 positive; unclamped extrema about−166.364/+161.528. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about14.9859; appended size616,544 bytes. Filtering, PCM8
clipping and envelope/volume quantization limits remain explicit.

A fresh independent180-second software DS reference matches5,312 notes and19
decoded raw waves, tempo/depth controls and source ADSR. Peak is14749 and
coarse100ms maximum voices16. It is software rendering, not DS hardware.
Common entry is624 and period2304 ticks. Source tempo140 maps to native141,
about111.974→112.288 ticks/s. Entry is near0:06 and joins near0:26/0:47;
tempo quantization remains.

Natural frontend Start input reaches clock5233 in2,784 frames, covering two
complete cycles and all101 waves without RAM/register injection, header
redirection, forced repeats or clock restarts. Separate read-only original
NOTE observation reaches clock5248 in2,792 frames: all1,399 calls allocate,
with no rejection or held/starting preemption. Identities, clocks and outcomes
match the unaccepted SF3 plain control, while465 slot choices differ.
Nonzero-envelope release reuses rise421→445. This does not prove preservation
of tails or unrestricted polyphony outside the window; tails remain a manual
listening focus.

All1,399 allocated channels retain gate/key/velocity/source-derived priority.
There are111,680 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons across
eight tracks, including source effective pitch, singleton pan and volume/
expression. Multi-position pan controls on the other tracks remain covered.
Source6 stereo diagnostics retain915 settled observations, excluding changed
pan and starting/release states; no low-volume samples are excluded. Source
NOTE pan10/110 are both covered:518 left≤20 and397 right≥100 observations,
median signed balance−1.000/+0.818. Definition pan is included; this is not
full-song waveform alignment.

The first note-field parser saw1,398 blocks for1,399 allocations because one
exact duplicated PTY command echo interrupted its regex. The failed source/log
are retained. Strict normalization removes four duplicated command lines across
the transcript, deletes no memory data, and recovers all1,399 allocated blocks.
Reanalysis changes no ROM or native capture. Initial parsing is not counted as
passing evidence.

Every saved frame matches `1 + floor((frame-1)*141/75)`, with anchored residual
below one tick. This is an emulated phase check, not hardware/wall timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
Actual chip gameplay, linked play and rematches remain separate manual scope.

## Regression scope and reuse

Eighteen focused cases pass in prototype and after exact migration: two new
SF3 COMICAL cases and sixteen cases for prior additions since the frozen full
suite. They check family/capacity/mode guards, schedules/controls, BPS and base
prefix bounds. Formal CLI reproduces all eight native-tested files byte for
byte; recursive v10–v37 archives retain their identities.

Removing the new branch/family entry restores the whole accepted GAMEOVER
builder AST. Removing all nine additions restores the frozen487-test SCHOOL
builder AST; other baseline libraries/tests remain byte-identical. The new
entry is pinned to SF3/source28/filtering only; previous SF1 entries and the
explicit finite GAMEOVER mode remain separately pinned. Parent/full-suite
records are hashed. The487-test no-skip suite and58 accepted/two historical
control rebuild record are reused, not a fresh505-test run or69-song rebuild.
Fresh integrity checks reconstruct69 archived ROMs from their BPS/base pairs
without recompiling the old songs. Remaining coverage limits are preserved.

## Accepted exact SF3 ROM and test patch

- ROM CRC32: `CE7A1D71`; size9,005,152 bytes.
- ROM SHA-256: `8bf879e8434a23b57dd4abf4c32c2767cad5cd9f8ea6fe2b266636a74bfd47f6`.
- BPS SHA-256: `dffadde500349be1a4414cd161d65e7ce824275b5487c24f076eb39f0cfc95e4`.
- Local folder: `out/nds-research/sf3-comical-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

`patch-delivery.json` records copied SHA-256 separately from human acceptance.
The30-second native preview peaks at12887; nominal sequence time contains entry
and the first GOTO near0:26, but not the second near0:47. Normal game lifecycle
remains active; actual loop coverage is established by separate original frame
observations. `comparison/filter-ab.html` presents unaccepted plain and accepted
filtered native recordings at equal gain without extra normalization or sample
alignment. The software DS/native normalized page is separate. Comparative
timbre preference is distinct from functional acceptance.

On 2026-10-24, the user reported “测试无问题” for this exact ROM and the three
requested checks: at least three minutes listening including joins/tails/stereo,
repeated chip/Buster effects, and three battle→map→battle cycles with map
restoration and fresh starts. ROM, BPS and the delivered test copy were verified
at acceptance. These are user reports, not independently timed/observed checks.
Linked play, rematches, broader gameplay and comparative A/B preference remain
unestablished; no acceptance transfers to the plain control or other families.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-comical-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-comical-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
