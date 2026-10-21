# SF1 SABISHI: variable tempo, late activation and fitted attack

This separate capability experiment targets `ssr1d`, sequence 36
`BGM36SABISHI`, in Japanese EXE6 Gregar. The new explicit
`sf1-sabishi-variable-late-envelope` option combines bounded variable-tempo
pitch compensation with initial depth-zero notes before a single late enable,
and the existing fitted attack mode. Default routes and fixed-tempo guards
retain their behavior. This capability has not been added to batch retrying.

## Source and bounds

The pinned SF1 SDAT SHA-256 is
`2b162eced95dadba3362316e0eb49b95b2990014a7fcb119fb9d21c1b01c1fd7`.
Eight source tracks loop with period 3072 ticks. Source track 3 first sounds at
tick 528 and enables depth 10 at tick 1440; type/speed/range/delay stay fixed
at pitch/20/1/0, and positive depth remains ten thereafter. An inactive depth-zero
track's nonzero delay is not active modulation. Conductor tempos are
40/65/70/75/90/100. The shared native loop begins at 4512, with subsequent
joins at 7584 and 10656.

The extension requires both variable-tempo and fitted-envelope modes explicitly.
It permits initial depth-zero notes across earlier ticks, then requires fixed
positive depth. It excludes disabling, live parameter changes, active delays,
minimum-depth quantization, finite/mixed tracks, filtering and release overrides.
The conductor and eight-tempo/128-change budgets retain their original guards.
Positive LFOS tempo updates preserve shared phase/count; the actual enable
restores depth and current-tempo speed without resetting that state.

Source attack 100 maps to native attack 74. Fit RMS/max error is about
0.10193/0.28374, within the existing 0.12/0.30 limits; no fit limit is relaxed.
The candidate uses fourteen raw PCM8 waves, ten native voices at 10512 Hz and
+3.5 dB gain. No native driver, mixer or production catalog changes are needed.

## Independent and native evidence

The pinned software source renderer's 180-second trace matches 1,845 notes,
fourteen decoded waves, 25 tempo controls and six depth controls. All 396
observed modulation updates preserve phase/count. The actual late enable has
four allocated voice updates; this song supplies no carried-positive-depth
update coverage. Envelope observations include 1,845 note-on snapshots,
456,281 per-voice timer updates and 3,094 noninstant attack updates.

Natural mGBA playback, using frontend Start at frames 180–190, covers the intro
and two common native cycles: 8,197 frames to clock 10657, all fourteen waves,
no clock restart, header redirection or register/RAM injection. Nineteen
frame/clock rate windows cover all six tempos within 1.01 ticks. Isolated mapped
LFO frequency error reaches about 1.26% for these configurations; this is not a
whole-song fidelity bound. All 992 packed notes, 114 keyed tone slots and fourteen
waves match their source-derived pan, fitted ADSR, tuning and relocated data.
Natural title envelope observations pass 14,068 native steps, including 105
slow-attack and 4,269 release observations. Controlled helper checks cover effects
100/129, continued music and three stop/native-restore/restart cycles.

The thirty-second native preview has peak 11768. Its normalized A/B page covers
the initial late enable, but not the later tempo dip or native loop joins.
Software DS rendering is not hardware capture or sample-aligned synthesis.
Triangle versus sine LFO, shared phase and note resets, ten versus sixteen voices,
ADSR fitting, PCM8 and speed quantization remain approximations. Controlled helper
calls do not establish actual battle/map transitions, linked play or rematches.

## Manual status and reproduction

On 2026-10-20 the user reported “没有问题” in response to the final three-check checklist, accepting the exact ROM below:

- ROM CRC32: `BE214D55`; size 8,715,852 bytes.
- ROM SHA-256: `c8469f1b4554886c72dd24865d327c95d63b4a9470391ad7c3426f400b8212ed`.
- Local folder: `out/nds-research/sf1-sabishi-variable-late-envelope-exe6-v1/`.

The user-reported pass covers the requested three-minute virus battle listening
(including late activation, tempo dips and joins), chips/Buster coexistence, and
three battle→map→battle encounters with original-map restoration and fresh imports.
This is separate from automated evidence. No independent timed recording, complete
gameplay trace, linked-play/rematch result or comparative preference is inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-sabishi-variable-late-envelope \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-sabishi-variable-late-envelope-exe6-v1
```

Use a fresh output directory. Local reference, native, allocation, fit, resource,
regression and reproducibility records remain ignored; ROMs and source game
assets stay out of Git.

Final read-only allocation/model verification passes 65,584 native track-state
comparisons over 8,198 frames to clock 10658, with 1,400 observed NOTE handler
calls and zero allocation rejections. The original handler bytes match the pinned
base. Only source track 3 develops active modulation. A fabricated rejection at
an observed reset is rejected at clock 1489; a NOTE without an observable state
change cannot serve as this negative control. The initial observer run's overly
exclusive speed-change coverage assertion failed on inactive initialization;
its logs are retained, and the full corrected run passes. Actual state-model
comparisons were not relaxed. Diagnostic clock-aligned DS/target pitch error
on track 3 is about 6.13 cents RMS, 14.06 cents maximum; allocations and audio
samples are not aligned.

All 344 prospective-source regression cases complete with 343 passes and one
explicit external-input skip (the unverified local `ssr2s.nds` still fails the
original guard). Five new tests cover required explicit modes, late opt-in,
fixed parameter restrictions, old bytes and incompatible mode combinations.
All 39 accepted and two unaccepted control ROM/BPS pairs rebuild identically.
Migrated root files match the frozen tested source hashes, and the root-focused
suite passes. The production CLI reproduces all eight native-tested output
files byte for byte. Archived v10–v19 file/path identities remain unchanged.

BPS SHA-256:
`af3c5f8b176b35dc321cc7fe06c6f4c70342974bde2db684ff47c879d4c12146`.
Manual acceptance applies to the fingerprint above; no other ROM inherits it
from MIZUUMI or the source song name.
