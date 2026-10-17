# Live pitch-LFO on/off: Star Force 1 BOSS

This experiment converts SSEQ 28 `BGM28BOSS` from the pinned Japanese
Star Force 1 Dragon archive. Track 4 first sounds at tick 0, enables depth
35 at tick 3840 and disables it at tick 5952, repeating on later loops.
On 2026-10-17 the user reported no issues after the requested four-minute
battle listening and gameplay checks for this exact ROM.

Artifact: `out/nds-research/sf1-boss-toggle-exe6-v1/`.
CLI song: `sf1-boss-toggle`.

## Bounded support and approximation

`native_pitch_lfo_live_toggle=True` requires the native pitch-LFO and delay
flags. It permits depth zero or one fixed positive depth per source track;
pitch type, speed, range and delay must remain fixed at note-on and after
activation. Positive-depth changes remain rejected. The flag cannot combine
with the separate positive live-depth experiment. Singleton tracks, fixed
tempo, representable parameters and existing resource constraints still apply.
Default fixed-delay and live-depth modes retain their activation restrictions.
Batch routes do not automatically opt into the new flag.

Inactive notes preload the quantized delay while MOD/LFOS are zero. Their
delay counter does not advance until modulation is enabled. Ordered MOD/LFOS
updates enable modulation without reloading that counter; every new note
retains the existing shared delay/phase reset. The tick-3840 note precedes
the depth control at the same timestamp, preserving original command order.
Disabling uses MOD=0/LFOS=0 to clear the target pitch-modulation value.

DS depth zero freezes each voice's phase and delay counter; parameter updates
do not reset them. GBA disabling resets the shared phase/value, preserving
the shared delay count. Re-enabling an older voice therefore starts from
the target's shared zero phase instead of the DS voice's retained phase.
This is a documented approximation. Triangle shape, quantized pitch, new-note
resets of overlapping voices/release tails, PCM8, envelopes, tempo and the
ten-voice budget retain their existing differences.

## Configuration

Japanese `ssr1d.nds` supplies SDAT file 667, SSEQ file 27, bank 39, volume 65
and source player 0. Seven tracks and 21 PCM samples are retained. No envelope
fitting mode is enabled. Japanese EXE6 Gregar uses eight-track capacity, ten
PCM voices at 10,512 Hz and +3.5 dB imported gain. Title (1), ordinary virus
music (21) and communication scenes select slot 474. Original table entries
and prefix bytes outside declared hook/configuration ranges are preserved;
BPS reconstruction passes and original ROM inputs are unchanged.

Source tempo 145 maps to target parameter 146 (116.270 ticks/second).
Active depth 35/speed 25/range 1/delay 10 map to MOD 4/LFOS 21/LFODL 7.
Rounded phase displacement is 51.604 ms versus the DS 52.095 ms wait;
total native delay wait is 60.205 ms including the baseline zero-phase tick.
Target enable/disable times are about 33.03/51.19 seconds, recurring every
54.494 seconds. Compiled loop start/period are 10176/6336 ticks, with first
jumps near 142/197 seconds. Warmup unrolls music without added silence.

- ROM: 8,803,620 bytes, CRC32 `A6AE1A3D`.
- SHA-256: `7f8e180e834d60cb72faadef8b37f94071c894361eac36fbedebe9f859ce0fa3`.

## Evidence and limits

The independent 180-second software DS reference covers at least two complete
source loops on every track: 5,873 notes, all 21 decoded PCM16 samples,
401 ordinary controls, ten depth controls and 7,960 active sine observations.
Delay checks cover 1,320 waiting updates and 132 observed activations.

At each BOSS disable control, track 4 has no held or releasing DS voices.
The source therefore proves the control executes but does not exercise
disabling a live voice. UpdateMod rows at actual depth-control timestamps
show 12 voice enable updates and no disable updates. Reused channel slots
at unrelated note-on timestamps are excluded from these toggle counts.
The checker explicitly reports the missing carried-disable coverage rather
than treating empty-voice controls as that evidence.

`lfo-window/validation.json` checks 2,400 natural BOSS frames through clock
4671 against actual MPlay RAM, including the first enable at clock 3841,
with 81 delayed zero-phase snapshots. It does not reach tick 5952 or a
compiled jump before the title scene changes. `preview/preview.wav` and
`comparison/listen.html` provide 30-second native audio and normalized
software-DS/GBA comparison, before the first BOSS enable.

`out/nds-research/boss-toggle-research-v1/held-note-probe/` supplements this
coverage with an explicitly synthetic one-track sequence using original
bank/sample resources. One 96-tick note enables depth 35 at tick 12 and
disables at tick 48, within a natural title window. The 120-frame native
probe observes both transitions, including zero modulation value after
disable while the note is still held. A separate 30-second independent
DS reference covers three notes and three enable/disable cycles, including
three disables preserving nonzero counter/phase state. It passes the strict
carried-disable requirement. These are synthetic engine/source checks,
not the original BOSS score or a gameplay test. The saved
`build-held-note-probe.py` reproduces the disposable SDAT/ROM from read-only
pinned inputs; only the copied sequence program is replaced.

`runtime/` checks original effects 100/129, ordinary/synthetic communication
dispatch, continuation, queued stop, native restoration and three restart
cycles. Controlled helper calls do not establish actual linked play or map
transitions. Instrumented original BOSS disable and full-loop execution remain
outside the automated window. The user reports no issues with the requested
listening checks; instrumented original-song coverage remains bounded.

All 198 Python tests pass. All fourteen earlier accepted ROMs and BPS patches
rebuild byte-identically; fingerprints are recorded in
`out/nds-research/boss-toggle-research-v1/accepted-rebuilds.json`.
Regression tests cover opt-in gating, conflicting flags, unsupported parameter
changes, initial wait retention, target disable-phase approximation, independent
observer corruption/coverage, same-tick order, BPS and original-data preservation.
`validation-summary.json` collects final checks; `manual-testing.json` records
user-reported acceptance for this exact ROM on 2026-10-17. The requested
checks cover four-minute battle listening, modulation enable/disable and
repetitions, held notes/overlaps/release tails, loop joins, chips/Buster
coexistence, map restoration and next-encounter restart. No timed recording
or full-loop execution trace was supplied; specific linked play and rematches
were not separately reported. Shared-phase and disable-phase approximations
remain. The archived v6 scan is unchanged.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-boss-toggle --event 1 --event 21 --event scene:communication \
  --out out/nds-boss-example
mkdir out/nds-boss-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-boss-example/source.sdat 28 180 out/nds-boss-example/reference
python3 scripts/validate_nds_experiment.py out/nds-boss-example \
  --reference out/nds-boss-example/reference --lifecycle --out out/nds-boss-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-boss-example --frames 2400 \
  --reference out/nds-boss-example/reference --out out/nds-boss-example/lfo-window
```

Use fresh output directories. Listen in battle for four minutes, focusing
on enable/disable around 33/51 seconds and later repetitions, held notes,
overlaps/release tails and joins near 142/197 seconds. Use chips and the
Buster, finish the battle, confirm native map music restoration and start
another encounter to check BOSS restarts. Title playback ends too early
for disable and full-loop listening.
