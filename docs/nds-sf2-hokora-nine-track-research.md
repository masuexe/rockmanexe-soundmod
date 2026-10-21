# SF2 HOKORA: nine source tracks into eight native tracks

This separate experiment imports verified Japanese SF2 `ssr2d`, sequence 20
`BGM_HOKORA`, into Japanese EXE6 Gregar. The explicit selector is
`sf2-hokora-nine-track`. It exercises the existing merged-track converter with
source groups `[[0,4],[1],[2],[3],[5],[6],[7],[8]]`; it adds no native engine,
mixer, general automatic grouping or production-catalog changes. Archived v20
still records this song as a capacity blocker under its singleton policy.

## Why these two tracks

A source-only investigation of eleven nine-track blockers found that HOKORA
passes the existing plain conversion constraints with 21 pair choices. This
experiment selects source tracks 0 and 4. Both have fixed volume 100 and pan 64,
and pass the shared expression/effective-pitch checks. Their per-note volume
ratio is exactly one, so merging adds no velocity-ratio quantization compared
with an unpacked nine-track singleton control. Both sources retain all notes,
instruments, keys, velocities, ticks and gates. Their distinct priorities are
preserved per note: source priorities 127/122 map to native channel priorities
28/23, including the common song priority. They are not flattened to one
shared note priority.

The nine-track control is a converter comparison only; it is not a runnable ROM
for the eight-track target. Merging can change simultaneous command/allocation
order. Equal controls and preserved note schedules do not establish lossless
audio or identical voice stealing.

## Source, reference and native checks

The source ROM SHA-256 is
`9ea3c6e253d4111eec250d611296be5fab0e2ec2b8f6f25ece71dcc8e3492899`;
the pinned SF2 SDAT SHA-256 is
`eb092e07ab410a3c81db491f0feb905f6259b891fb0b3cedfccaeca78ddc4ab4`.
All nine tracks loop with period 1920 ticks. The shared native entry is 1992;
subsequent joins are at 3912 and 5832. Source tempo is fixed at 125, mapped to
MPlay 126 (about 100.34 native ticks/second versus 99.98 source ticks/second).
There is no active modulation, fitted attack, filter or long-note carry.

The independent 180-second software DS render matches 4,916 notes over all nine
source tracks and 22 unique decoded source waves. Twenty-three prepared native
waves are necessary because source wave 75 is used with root keys 83 and 84;
those require separate tuning headers. The source ADSR check covers 4,916 note-on
snapshots and 468,241 voice timer updates; all attacks are instant. This is
software reference evidence, not DS hardware capture.

All 1,014 mapped notes and velocities match the unpacked nine-track control.
All eight compiled tracks pass two-cycle note/gate/timing comparisons. Packed
resource verification checks all 1,014 mapped notes, 81 keyed tone slots and
23 prepared PCM8 waves against original pan, ADSR, tuning, loop headers and
relocated data. Gain remains +3.5 dB, with ten native voices at 10512 Hz.

Natural frontend playback uses Start at frames 180–190 and reaches clock 5833
in 3,473 frames, covering the intro, two common cycles and all 23 native waves.
It uses no register/RAM injection, header redirection, forced repeat or clock
restart. Read-only NOTE entry/allocation/exit observations cover 1,550 calls
through 3,474 frames to clock 5835, with zero rejected allocations. Every one
of the nine source tracks is represented. Actual allocated wave, owner, key,
ADSR, initial gate, velocity and per-note priority match the compiled/source
mapping. The two merged source wave sets are distinct and observed sounding
together in 775 frames. Handler bytes match the pinned original.

Controlled effects 100/129, continued music, queued stop and three native-
restore/restart cycles pass. These helper calls do not establish actual battle/
map transitions. The thirty-second native preview peaks at 10512. Its normalized
A/B page covers all samples but ends before the first GOTO at about 39 seconds.
The common entry and next joins occur near 0:20, 0:39 and 0:58.

All 354 prospective-source tests pass without skips. Two new integration cases
check all nine source schedules, unchanged velocities versus the unpacked
control, patch reconstruction, native-prefix preservation, source-family
rejection and the unchanged unmerged eight-track capacity guard. Root migration
retains the frozen tested hashes; focused root checks pass. All 41 accepted and
two unaccepted control ROM/BPS pairs rebuild identically. The production CLI
reproduces all eight native-tested output files byte for byte. Archived v10–v20
recursive file identities remain unchanged.

## Exact ROM and manual acceptance

- ROM CRC32: `ED9A184C`; size 8,800,440 bytes.
- ROM SHA-256: `7aeb1033001844fd1eeb44ce4e911cdee4f651b6ea6a3d70d85d6f03227184a5`.
- BPS SHA-256: `6064e1908404e868b1bf7e8052d5c5c375d8a9bf0b4cb0895bfe767e1adc5ec7`.
- Local folder: `out/nds-research/sf2-hokora-nine-track-exe6-v1/`.

On 2026-10-21 the user reported “测试没问题” in response to the final
three-item checklist, accepting this exact ROM. The reported pass covers the
requested three minutes in a virus battle,
listening for missing/truncated rhythm or melody and loop joins; repeated chip/
Buster effects; and three battle→map→battle encounters with native-map music
restored and each new import starting afresh. This user report is separate from
automated evidence. No independent timing, complete gameplay trace, comparative
preference, actual linked play or rematch behavior is inferred.

Ten versus sixteen voice budgets, standard volume/velocity and ADSR mapping,
PCM8 and tempo quantization remain. Successful NOTE allocation does not exclude
release-tail stealing. Native initial gate observations do not independently
establish equal per-voice DS/GBA stop times. Source/target clips are not sample-
aligned. No whole-song fidelity bound is claimed.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-hokora-nine-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-hokora-nine-track-exe6-v1
```

Use a fresh output directory. Independent reference, native allocation and
resource checks, nine-track control comparisons, logs and fingerprints remain
in ignored local research outputs. ROMs and source game assets stay out of Git.
