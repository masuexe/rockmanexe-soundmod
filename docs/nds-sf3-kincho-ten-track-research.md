# SF3 KINCHO: ten source tracks into eight native tracks

This separate experiment imports verified Japanese `ssr3b`, sequence 30
`BGM_KINCHO`, into Japanese EXE6 Gregar with selector `sf3-kincho-ten-track`.
It exercises the existing merged-track converter with source groups
`[[0],[1],[2,4,6],[3],[5],[7],[14],[15]]`. It adds no native driver/mixer,
automatic batch grouping, modulation mode or fitted envelope. Archived v21
still treats KINCHO as a capacity blocker under its recorded route policy.

## Group selection and preserved source data

A bounded source-only grouping investigation identified fourteen plain
conversion candidates among the remaining unmodulated, unfitted looping
blockers. KINCHO is the smallest source-count case, with ten source tracks.
The chosen group 2/4/6 reduces that to eight native sequence tracks. All three
sources have fixed volume 100, so their per-note velocity ratio remains one.
Sources 2/4 stay centered, while source 6 alternates pan 10/117 without changing
pan during a held note. Existing shared-expression, effective-pitch, fixed-
volume and held-note-pan guards all pass. Source 6's pan is retained in each
note's instrument tone rather than changing the shared track's pan.

An unpacked ten-track singleton control preserves all 741 mapped note tuples,
including original source track, instrument, key, velocity, tick and duration;
target velocities are identical. All eight compiled tracks pass two-cycle
note/gate/timing checks. Distinct priorities remain per-note: source priorities
127/122/121 map to native channel priorities 28/23/22. The ten-track control is
not a runnable ROM for the eight-track target. Simultaneous command/allocation
order may differ; this is not a lossless-audio claim.

## Independent and native verification

The source ROM and SDAT retain their pinned SF3 identities; SDAT SHA-256 is
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
All ten source tracks loop with period 2304 ticks. The shared entry is 1560,
with subsequent joins at 3864 and 6168. Fixed source tempo 110 maps to MPlay110:
approximately 87.98 source ticks/second versus 87.60 native ticks/second.
There is no active modulation, fitted attack, filtering or long-note carry.

The independent 180-second software DS render matches 3,074 notes over all ten
source tracks and 21 unique decoded waves. Twenty-three native wave headers
retain separately tuned uses. Source ADSR observations match 3,074 note-on
snapshots and 445,055 voice timer updates; all attacks are instant. Packed
verification checks all 741 mappings, 112 keyed tone slots and 23 prepared
PCM8 waves, including source-derived per-note pan, ADSR, tuning, loop headers
and relocated data. The ROM retains +3.5 dB gain, ten PCM voices and 10512 Hz.

Natural frontend playback uses Start at frames 180–190. In 4,207 frames it
reaches clock 6169, covering the intro, two common cycles and all 23 prepared
samples, without register/RAM injection, header redirection, forced repeats
or clock restart. Read-only NOTE entry/allocation/exit observations run 4,208
frames to clock 6171: all 1,192 scheduled NOTE calls allocate successfully,
with every source track represented. Actual wave, owner, key, ADSR, initial
gate, velocity and source-derived priority match the compiled mapping. The
three merged source wave sets are distinct and observed simultaneously in
23 frames. Original native NOTE handler bytes remain identical to the base.

All fifty allocated source-6 notes retain the two opposing stereo directions:
thirty pan-10 notes and twenty pan-117 notes. Their median signed native
channel-volume balances are about -0.860/+0.862. This checks native stereo
contrast, not waveform alignment or a whole-song pan-error bound. The exact
baked tone values are checked separately against source note state.

Controlled effects 100/129, continued music, queued stop and three native-
restore/restart cycles pass. These helper calls do not establish real battle/
map transitions. The thirty-second native preview peaks at 17384; its normalized
A/B page ends before the first GOTO, at approximately 44 seconds. Shared entry
and subsequent joins occur near 0:18, 0:44 and 1:10.

All 362 prospective-source regression tests pass without skips. Two new local
integration cases compare all ten source schedules and velocities with the
unpacked control, check patch reconstruction/native-prefix preservation, and
retain source-family and unmerged-capacity guards. Root migration retains the
frozen tested source hashes; focused root checks pass. All 42 accepted and two
unaccepted control ROM/BPS pairs rebuild identically. The production CLI
reproduces all eight native-tested files byte for byte, and archived v10–v21
recursive identities remain unchanged.

## Exact ROM and manual acceptance

- ROM CRC32: `0418F428`; size 8,740,780 bytes.
- ROM SHA-256: `611a189d5888eba848bf77777f105ed91cf5402238640cc9254a018fdeb37917`.
- BPS SHA-256: `668f8d77a44aecc2f68325d5c06259d0aae3bc4dd763c986efeb28b1c4671135`.
- Local folder: `out/nds-research/sf3-kincho-ten-track-exe6-v1/`.

On 2026-10-22 the user reported “测试没问题” in response to the final
three-item checklist, accepting this exact ROM. The reported pass covers the
requested three minutes in a virus battle,
listening for missing/truncated merged instruments, abnormal stereo and loop
joins; repeated chip/Buster effects; and three battle→map→battle encounters
with native-map music restored and each import starting afresh. This user report
is distinct from automated evidence. No independent timing, full gameplay trace,
linked-play/rematch result or comparative preference is inferred.

Ten-versus-sixteen voice budgets and possible release-tail stealing remain
separate from successful NOTE allocation. Standard velocity/volume mapping,
ADSR, PCM8 and tempo quantization remain. Native initial gate observations do
not independently prove equal DS/GBA per-voice end times. The software DS
reference is not hardware capture, and clips are not sample-aligned. No
whole-song fidelity bound is claimed.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-kincho-ten-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-kincho-ten-track-exe6-v1
```

Use a fresh output directory. Source/reference, native allocation and stereo,
resource/control comparisons, logs and hashes stay in ignored research outputs.
ROMs and source game assets remain outside Git.
