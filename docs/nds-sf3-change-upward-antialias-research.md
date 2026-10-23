# SF3 CHANGE: filtered large bends and an intro-only sounding source

This standalone experiment applies the accepted upward-pitch preparation
mode to CHANGE's accepted thirteen-to-eight grouping. Selector
`sf3-change-upward-antialias` uses Japanese `ssr3b` sequence47 and
`[[0],[1],[2],[3],[4,6,7,9,14,15],[5],[8],[13]]`, ten PCM voices,
10512 Hz and +3.5 dB. It adds no converter/native-driver capability. Existing
explicit merged-filter/upward modes retain control, alias/release,
unsupported-effect, one-octave/key, sample-budget and model guards. Archived
v30 still blocks filtered CHANGE; no scanner route or group search is added.

## Source schedules and conservative preparation

All855 mappings, duplicate multiplicity, source tracks, priorities, long alias
and two-cycle note/gate/timing validations match the accepted plain grouped
baseline. All5,599 compiled commands are byte-identical except relocated GOTO
pointer words; within-track targets remain exact. The existing161 fixed-
volume ratio mappings retain maximum absolute linear-velocity rounding error
about0.48036. No source note is removed or newly quantized to zero. The merged
sources retain fixed volumes110/100/110/110/80/70 normalized110.

Source9 plays six intro notes and then loops through rests. It remains in the
merged group without repeating those intro notes, discarding the source or
flattening its control schedule. The independent180-second source reference
and the original native two-cycle window both contain exactly those six
source9 NOTE calls. One source5 long-note key76 retains alias127 on singleton
native track5, including its live pitch/pan changes. No common-loop carry is
required.

The pinned180-second software DS reference is reused after exact SDAT and
recursive output identity checks, and its source-only validator is rerun.
It matches5,070 notes,20 decoded source waves,5,070 ADSR note-on snapshots and
386,046 per-voice timer updates; all attacks are instant. This is reused
software synthesis, not a new renderer run or DS hardware capture. SDAT SHA-256
remains `bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.

Preparation uses78 filtered waves and646,861 PCM8 bytes. Of these,58 use
shift0, three shift1, eight shift6, seven shift9 and two shift12. Track maxima
include756 positive units for source1,570 for source5,282 for source8 and372
for source13, in1/64-semitone units; shared physical wave/root/source-key uses
take the maximum bound before sample allocation. The twelve-semitone upper
limit is exercised without relaxing or clamping it. These track-wide maxima
are conservative for individual notes and can reduce unbent-note bandwidth;
listening must judge whether the changed timbre is useful.

Source-derived bounds and preparation keys match all78 waves. Maximum nominal
FIR cutoff at the bound is about0.900162 of mixer Nyquist after loop/tuning
rounding. This is not a brick-wall, zero-aliasing or audible-error bound.
Maximum source step is about13.689, within32; maximum stored tuning error is
about0.001023 cents, not a whole-song pitch or waveform bound. All855 mappings,
92 keyed tone slots and78 prepared wave headers/data are recomputed and
checked after relocation, including source roots, ADSR and note-on pan.
An unpacked thirteen-track filtered control yields identical mapped source-
note fields and all78 filtered waves/headers. It uses the same DSP and cannot
run in the eight-track target. Existing analytic DSP tests retain their own
passband, alias-rejection, loop, tuning and tail scope.

Analysis-only instrumentation reproduces every prepared byte and measures
1,043 clamped stored points out of646,861 (about0.1612%):477 negative and566
positive. Unclamped values range about-148.18 to141.40 PCM8 units. FIR overshoot
and endpoint quantization remain; storage counts are not time-weighted
playback or audible distortion bounds. No per-wave normalization is added,
and the native mixer is unchanged.

## Native playback, long-note control and allocation limits

Common entry remains1320 ticks, period1536, joins2856/4392. Source tempo114
maps to MPlay114, about91.179 source versus90.786 native ticks/second. Natural
frontend playback uses verified Start input at frames180–190 and reaches
clock4393 in2,891 frames, covering two common cycles and all78 waves. It uses
no RAM/register injection, forced repeat, header redirect or clock restart.
Original NOTE-handler bytes match the pinned EXE6 base.

Read-only entry/allocation/exit and pre-unlink observation reaches clock4409
in2,901 frames. All1,339 scheduled NOTE calls allocate with exact owner, wave,
key, ADSR, gate, velocity and priority. Note identities and clocks match the
plain baseline;159 slot choices differ. Multiple gated sources in the merged
group occur in1,373 observed frames. These are windowed frame/slot facts, not
waveform or audible-error bounds.

Four held/starting voices are still preempted. Their clocks352/360/372/376
and displaced source/note/key/gate identities match the known plain-baseline
cases: source13 once and source14 three times. There are188 release-flagged
reuses with nonzero envelope, five more than the plain baseline's183.
Filtering can change sample endings and slot choices. Successful allocation
does not establish full DS polyphony; sustained-note truncation and release-
tail shortening remain explicit. No zero-velocity native NOTE call is observed.

Both observed uses of alias127 remain held and release in their original
windows. Saved BEND/BENDR/TUNE/PAN bytes pass92,832 comparisons against compiled
commands and source effective pitch/singleton pan, including computed native
pitch. During the long alias's held sweep,141 snapshots retain fifteen source
pitch values, nine pan values and fifteen distinct actual channel-frequency
words. This establishes changing frequency reaches a held native voice, not
only a track control. It is not DS waveform or absolute-frequency equivalence.
All107 source6 initial stereo snapshots retain left/right contrast:56 at pan14,
six at pan112 and45 at pan114, with median signed balances about-0.810/+0.767/
+0.814. This is initial channel-volume contrast, not a waveform pan bound.
Player-clock residual remains within1.48 ticks of fixed-tempo emulated frames,
inside two ticks; this is not wall-clock or hardware timing.

Controlled effects100/129, continuation, queued stop and three native-restore/
restart helper cycles pass using PC/LR/argument injection into a disposable
emulator. They do not establish real battle/map transitions, linked play or
rematches. The thirty-second preview peaks at12395 and covers the intro,
known early preemptions, held sweep and common entry around0:15, but not the
first join around0:31 or second around0:48. Full natural checks are separate.
`comparison/upward-filter-ab.html` presents plain/filtered native recordings
at the same configured gain without extra normalization; they are not
sample-aligned. The normalized software DS/native page remains separate.

## Regression and accepted exact ROM

All443 prospective-source tests pass without skips, including two new cases
for complete CHANGE mapping/control/alias/intro-only/prefix preservation and
source-family/capacity guards. Root migration matches frozen tested hashes and
the two focused cases pass. All51 accepted and two unaccepted control ROM/BPS
pairs rebuild identically. Production CLI reproduces all eight native-tested
files byte for byte; recursive v10–v30 archive identities remain unchanged.

The initial focused fixture copied AJITO's maximum preparation shift2;
CHANGE's actual source-derived maximum is12. The assertion was corrected
before the full frozen-source run without changing the converter or ROM.
The failed initial log remains distinct from the final two-case pass.

- ROM CRC32: `B8944A0E`; size9,074,860 bytes.
- ROM SHA-256: `3fe1e8918677ceafe0f5f6b9b4704c6fe8c42dc416e1a7634b666cb3e31b0774`.
- BPS SHA-256: `33ce38337a99b6c1c9da6177e9d7d763ce4979f93af303137dfc90e0a39fa594`.
- Local folder: `out/nds-research/sf3-change-upward-antialias-exe6-v1/`.

On 2026-10-23, the user reported “没有问题” for this exact ROM, accepting the
three requested checks: at least three minutes of virus-battle listening
including timbre, held pitch/pan, tails and loop joins; repeated chip/Buster
effects; and three battle→map→battle encounters with native-map restoration
and a fresh imported start. This is user-reported manual acceptance, separate
from automated evidence. Comparative filtered/plain timbre preference was not
separately reported. Linked play, rematches, independent timing and a full
manual event trace were not established by this report. Ten-voice held-note/
tail limits, conservative bandwidth reduction, clipping and PCM8/ADSR/tempo
quantization remain. Acceptance binds only the fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-change-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-change-upward-antialias-exe6-v1
```

Use a fresh directory. ROMs, original assets, captures and local outputs stay
outside Git. Automated proof and user-reported manual acceptance stay distinct.
