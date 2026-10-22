# SF3 STUDIO: antialias preparation for upward pitch bends

This separate experiment filters the accepted STUDIO fifteen-to-eight grouping
without changing its notes or live bend/expression controls. Selector
`sf3-studio-upward-antialias` uses Japanese `ssr3b` sequence4, groups
`[[0],[1],[2],[3],[4,5,6,7,8,12,14,15],[9],[10],[11]]`, ten PCM voices,
10512 Hz and +3.5 dB. The native driver/mixer is unchanged. Archived v28 still
rejects filtered STUDIO; this experiment adds no scanner route or group search.

## Conservative pitch preparation

The explicit converter flag `bandlimited_upward_support` requires plain
looping filtered tracks. It excludes native modulation, fitted envelopes,
finite/release and mixed-ending modes, and retains transpose, portamento,
sweep, grouping/control, long-alias, sample-budget and conversion-model guards.
Merged tracks additionally require the existing explicit merged-filter flag.
Default filtered conversion still rejects upward bends.

The converter first measures each source track's maximum positive effective
pitch in1/64-semitone units across all executed states. Every physical
wave/root/source-key identity receives the maximum bound across all of its
source uses, before sample-cache allocation. This avoids a first-use cache
error when two sources share a key but have different bend ranges. The filter
prepares at source key plus the ceiling of this bound in semitones, leaving
the played key and all bend commands intact. Preparation rejects a shift over
one octave or a key above127; it does not clamp either. The existing periodic
loop/tuning correction and 90% nominal FIR cutoff remain.

STUDIO requires396 units (6.1875 semitones) for source2 and204 units
(3.1875 semitones) for source10. Of131 prepared waves,124 use shift0, two use
shift7 and five use shift4. Independently reconstructed source bounds and
shared identities match every preparation key. Maximum nominal cutoff at the
bound is about0.900319 of mixer Nyquist after loop/tuning rounding, below1.
This is a nominal FIR cutoff bound, not a brick-wall response, zero-aliasing
proof or audible-error bound. One early feasibility check incorrectly expected
all prepared playback rates to stay below10512 exactly; integer loop-period
rounding can exceed that slightly even with shift0. The final guard checks the
actual nominal cutoff including rate/tuning rounding and the existing filter
transition margin. The DSP algorithm and native runtime are unchanged.

## Schedule, source reference and wave identity

All3,431 mappings, including twelve duplicated tuples, match the accepted
plain grouped baseline. All14,149 compiled commands are byte-identical except
for relocated GOTO pointer words; within-track jump offsets remain exact.
The existing910 volume-ratio mappings, maximum linear-velocity rounding error
about0.46594 and four source-velocity5 mappings to native0 remain unchanged.
The unpacked plain control already has those four zero mappings; filtering
adds none. Two source2 long-note aliases remain127/126. All eight compiled
tracks retain their two-cycle note/gate/timing validation.

The pinned180-second independent software DS reference is reused only after
matching the exact SDAT and recursive output identities, and rerunning the
source validator. It matches6,936 notes,22 decoded source waves,6,936 ADSR
note-on snapshots and508,954 per-voice timer updates; all attacks are instant.
SDAT SHA-256 remains
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
This is reused software synthesis, not a new renderer run or DS hardware capture.

Preparation uses903,042 PCM8 bytes; maximum source step is about16.826, within
the existing bound32 and4 MB budget. All131 prepared waves/headers,222 keyed
tone slots, source roots, ADSR and pans are recomputed and checked after
relocation. Maximum stored tuning error is about0.001623 cents; this is not a
whole-song pitch or waveform bound. A separate unpacked fifteen-track filtered
control yields the same mapped source-note fields and all131 prepared wave
bytes/headers. It uses the same DSP and cannot run in the eight-track target.
Synthetic tests independently check sine frequency and shared-key bounds;
existing DSP tests retain their passband, alias-rejection, loop and tail scope.

Analysis-only instrumentation reproduces all prepared bytes and measures1,097
clamped stored points out of903,042 (about0.1215%):700 negative and397 positive.
Unclamped values range about-142.55 to143.40 PCM8 units. These storage counts
are not time-weighted playback or audible distortion bounds. FIR overshoot and
PCM8 endpoint quantization remain explicit. No per-wave normalization is added.

## Original native playback

Common entry remains4800 ticks, period5184, joins9984/15168. Source tempo141
maps to MPlay142, about112.774 versus113.084 ticks/second. Natural frontend
playback uses verified Start input at frames180–190 and reaches clock15170
in8,013 frames, covering two common cycles and all131 waves. There is no
RAM/register injection, forced repeat, header redirect or clock restart.
Original NOTE-handler bytes match the pinned EXE6 base.

Read-only entry/allocation/exit and pre-unlink observation reaches clock15185
in8,021 frames. All5,202 scheduled calls allocate with exact wave, owner, key,
ADSR, gate, velocity and priority. All source-note identities and clocks match
the plain baseline;115 allocation slot choices differ. No held/starting voice
is preempted. There are2,866 release-flagged reuses with nonzero envelope,
three more than the plain baseline's2,863; filtering can change sample endings
and slot choices. This is a scoped observation, not full DS polyphony or an
audible-error bound. The merged group has multiple gated sources in3,497
frames. Six original zero-velocity NOTE calls allocate with both channel
volumes zero at ticks564/1332/5748/6516/10932/11700.

All24 long-alias uses stay held and release in their original windows. Saved
BEND/BENDR/TUNE/PAN/VOL bytes pass320,840 comparisons, including source effective
pitch, computed native pitch and singleton pan. The three held-note crescendos
around0:26/1:12/1:58 retain27/27/28 snapshots, with monotonic left-plus-right
channel volume51→81 through nine levels each. All360 source5 initial stereo
snapshots retain left/center/right contrast. These establish native control
behavior; they are not sample-aligned DS amplitude, frequency or pan bounds.
Frame-clock residual stays within1.88 ticks of fixed-tempo emulated frames,
inside two ticks; this is not wall-clock/hardware timing.

Controlled effects100/129, continuation, queued stop and three native-restore/
restart helper cycles pass using PC/LR/argument injection into a disposable
emulator. They do not establish real battle/map transitions, linked play or
rematches. The thirty-second preview peaks at17124 and includes the first
crescendo/upward bend, but not the common entry or either GOTO. The local
`comparison/upward-filter-ab.html` offers plain/filtered native recordings at
the same configured gain without extra loudness normalization; they are not
sample-aligned. The normalized software DS/native page is separate.

## Regression and accepted exact ROM

All427 prospective-source tests pass without skips, including five new cases
for analytic sine pitch, shared-key maximum selection, explicit-mode/effect
exclusions, un-clamped preparation limits and full STUDIO mapping/prefix
preservation. Root migration matches frozen tested hashes and the focused
five cases pass. All49 accepted and two unaccepted control ROM/BPS pairs
rebuild identically. Production CLI reproduces all eight native-tested files
byte for byte; recursive v10–v28 archive identities remain unchanged.

Initial focused tests imported an existing TestCase class and accidentally
included its six cases; the final module imports the fixture module instead.
A negative test also now accepts the existing earlier mixed-mode rejection
message. Initial failed logs remain distinct from the final five-case pass;
these fixture corrections do not change the native-tested ROM.

- ROM CRC32: `C5EE00C5`; size9,391,252 bytes.
- ROM SHA-256: `02a180120dfd02e4e4e6f16ab6ae1bd38c02c1b72f44a7ed1c607aa8776a82d4`.
- BPS SHA-256: `6fa7f736a7deb4e6db3dceee5b97a85d82eadb9dcfcc94ec6035e123ff09dc2e`.
- Local folder: `out/nds-research/sf3-studio-upward-antialias-exe6-v1/`.

On 2026-10-22, the user reported “测试没有问题” for this exact ROM and the
requested three-minute virus-battle listening (including upward bends, timbre/
distortion and joins), repeated chip/Buster effects and three battle→map→battle
checks. This is user-reported acceptance; no independently timed recording,
full gameplay trace, linked play or rematch is inferred. Comparative filtered/
unfiltered preference was not separately reported. Tail reuse, sample clipping,
extreme-soft-note loss and PCM8/ADSR/tempo quantization remain. Automated proof
and user-reported acceptance stay distinct and bind only this exact ROM.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-studio-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-studio-upward-antialias-exe6-v1
```

Use a fresh directory. ROMs, source assets, captures and local outputs stay
outside Git. Automated proof and user-reported manual acceptance stay distinct.
