# SF3 AJITO: filtering with four long aliases and a tighter voice budget

This separate experiment applies the accepted upward-pitch preparation mode
to the accepted AJITO fourteen-to-eight grouping. Selector
`sf3-ajito-upward-antialias` uses Japanese `ssr3b` sequence7 and
`[[0,4,6,7,8,11,14],[1],[2],[3],[5],[9],[10],[15]]`, ten PCM voices,
10512 Hz and +3.5 dB. It adds no converter/native-driver capability. The
existing explicit merged-filter and upward-preparation modes retain their
control, alias/release, unsupported-effect, one-octave/key, sample-budget and
model guards. Archived v29 still blocks filtered AJITO; no scanner route or
group search is enabled by this standalone experiment.

## Source, preparation and score identity

All2,472 source mappings, source tracks, priorities, dynamics, four long
aliases and two-cycle note/gate/timing validations match the accepted plain
grouped baseline. All14,177 compiled commands are byte-identical after
normalizing only relocated GOTO pointer words; within-track jump offsets stay
exact. Existing fixed-volume ratios remain for534 mappings, with maximum
absolute linear-velocity rounding error about0.46594 and minimum native
velocity1. No source note is removed or newly quantized to zero. The merged
sources retain volumes100/100/90/90/100/90/60 normalized100. Source9 expression
and source15 volume70/80 remain independent; the latter must not be folded
into a fixed-volume group.

The pinned180-second independent software DS output is reused after exact
SDAT and recursive output identity checks, and the source-only validator is
rerun. It matches4,477 notes,27 decoded source waves,4,477 ADSR note-on snapshots
and422,065 per-voice timer updates. All attacks are instant. This is reused
software synthesis, not a new renderer run or DS hardware capture. SDAT SHA-256
remains `bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.

Preparation uses221 filtered waves and1,969,559 PCM8 bytes. Of these,183 use
shift0,34 use shift1 and four use shift2. Each shared physical wave/root/source
key takes the maximum positive effective-pitch bound across its source uses.
The original track maxima include123 units for source1,63 for sources3/5 and54
for source15, in1/64-semitone units. Preparation keys and bounds are rebuilt
independently from the source actions/definitions. Maximum nominal FIR cutoff
at the bound is about0.900246 of mixer Nyquist, including loop/tuning rounding;
this is not a brick-wall, zero-aliasing or audible-error bound. Maximum source
step is about23.017, within32, and stored tuning error is below0.000428 cents.
Neither is a whole-song pitch or waveform bound.

All2,472 mappings,303 keyed tone slots and221 prepared waves/headers are
recomputed and checked after relocation, including source roots, ADSR and
note-on pan. An unpacked fourteen-track filtered control yields the same
mapped source-note fields and all221 prepared wave bytes/headers. It uses the
same DSP and cannot run in the eight-track target. Existing analytic DSP tests
retain their separate passband, alias-rejection, loop, tuning and tail scope.

Analysis-only instrumentation reproduces every prepared byte and measures
9,275 clamped stored points out of1,969,559 (about0.471%):3,357 negative and
5,918 positive. Unclamped values range about-145.86 to160.06 PCM8 units. FIR
overshoot and endpoint quantization remain explicit; storage counts are not
time-weighted playback or an audible distortion bound. No per-wave
normalization is added, and the runtime mixer is unchanged.

## Native playback and measured allocation limits

Common entry remains4032 ticks, period5472, joins9504/14976. Source tempo115
maps to MPlay115, about91.979 source versus91.582 native ticks/second. Natural
frontend playback uses verified Start input at frames180–190 and reaches
clock14977 in9,768 frames, covering two common cycles and all221 waves. It
uses no RAM/register injection, forced repeat, header redirect or clock restart.
Original NOTE-handler bytes match the pinned EXE6 base.

Read-only entry/allocation/exit and pre-unlink observation reaches clock14992
in9,778 frames. All3,964 scheduled NOTE calls allocate with exact owner, wave,
key, ADSR, gate, velocity and priority. Note identities and clocks match the
plain baseline;718 allocation slot choices differ. Multiple gated sources in
the merged group are observed in7,182 frames, compared with7,178 in the plain
window. These are frame/slot observations, not waveform or audible-error bounds.

Fourteen held/starting voices are still preempted. Their clocks and displaced
source/note/key/gate identities match all fourteen known plain-baseline cases:
source15 six, source14 six and source11 two. There are1,551 release-flagged
reuses with nonzero envelope, seven more than the plain baseline's1,544.
Filtering can change sample endings and slot choices. Successful new-note
allocation does not establish complete DS polyphony; existing sustained-note
truncation and release-tail shortening remain listening limits. No native
zero-velocity NOTE calls are observed in this window.

All fifteen observed uses of the four aliases stay held and release in their
original windows. Three aliases belong to source2 on native track2; the fourth
belongs to source10 on native track6. Both are singleton tracks, and no common-
loop carry is required. Saved BEND/BENDR/TUNE/PAN/VOL bytes pass391,120
comparisons against compiled commands and source effective pitch/singleton
pan, including computed native pitch. Source9 retains thirteen native volume
levels3–57 and source15 retains23/30. These are track-control checks, not a
sample-aligned held-voice amplitude or absolute-frequency proof.

All435 source8 initial stereo snapshots retain left/center/right contrast:
188 at pan25,29 at pan64 and218 at pan102, with median signed balances about
-0.600/+0.018/+0.607. This is initial channel-volume contrast, not a waveform
pan bound. Player-clock residual remains within1.466667 ticks of fixed-tempo
emulated frames, inside two ticks; this is not wall-clock or hardware timing.

Controlled effects100/129, continuation, queued stop and three native-restore/
restart helper cycles pass using PC/LR/argument injection into a disposable
emulator. They do not establish real battle/map transitions, linked play or
rematches. The thirty-second preview peaks at15768 and covers the first
known held-preemption window around0:12, but not the common entry around0:44
or either join around1:44/2:44. Full natural checks are separate. The local
`comparison/upward-filter-ab.html` presents plain/filtered native recordings
at the same configured gain without further normalization; they are not
sample-aligned. The normalized software DS/native page remains separate.

## Regression and accepted exact ROM

All435 prospective-source tests pass without skips, including two new cases
for full AJITO mapping/control/alias/prefix preservation and source-family/
capacity guards. Root migration matches frozen tested hashes and the two
focused cases pass. All50 accepted and two unaccepted control ROM/BPS pairs
rebuild identically. Production CLI reproduces all eight native-tested files
byte for byte; recursive v10–v29 archive identities remain unchanged.

- ROM CRC32: `FC4C77A2`; size10,451,320 bytes.
- ROM SHA-256: `1b535b22c63f0da416d55355c63f12c0af3172adab5c68f786119a71312d341c`.
- BPS SHA-256: `24e2ce46c751ac121dce5071012cb848f649258cbe5f39b56f79e0ce085fedf8`.
- Local folder: `out/nds-research/sf3-ajito-upward-antialias-exe6-v1/`.

On 2026-10-23, the user reported “测试没有问题” for this exact ROM and the
requested three-minute virus-battle listening (including long notes, bends,
timbre/distortion and joins), repeated chip/Buster effects and three
battle→map→battle checks. This is user-reported acceptance; no independently
timed recording, full gameplay trace, linked play or rematch is inferred.
Comparative filtered/unfiltered preference was not separately reported. The
fourteen held-note preemptions, release-tail reuse, sample clipping and
PCM8/ADSR/tempo quantization remain. Automated proof and manual acceptance
stay distinct and bind only this exact ROM.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-ajito-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-ajito-upward-antialias-exe6-v1
```

Use a fresh directory. ROMs, original assets, captures and local outputs stay
outside Git. Automated proof and user-reported manual acceptance stay distinct.
