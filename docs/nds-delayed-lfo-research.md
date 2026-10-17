# Fixed delayed pitch LFO: Star Force 1 FMPLANET

The first delayed-LFO experiment converts SSEQ 2 `BGM02FMPLANET` from the
pinned Japanese Star Force 1 Dragon archive (SDAT file 667). It isolates a
fixed delay on source track 2, without adding the envelope fitting mode.
Independent DS delay observations, bounded native playback and controlled
effects/lifecycle checks pass. The user reports no issues with the requested
listening/gameplay sequence, accepting this approximation for the tested ROM.
Instrumented full-loop GBA execution remains a separate uncompleted check.

Artifact: `out/nds-research/sf1-fmplanet-delay-exe6-v1/`.
CLI song: `sf1-fmplanet-delay`.

## Bounded semantics and mapping

The independent DS core increments a voice's delay counter once per active
modulation timer update until the configured count is reached. During that
wait, its phase does not advance. The first enabled update emits the current
zero phase before advancing it. Delay and phase are independent per voice;
release voices keep their own modulation state.

MPlay LFODL is an eight-bit per-track sequence-tick counter. This mode resets
shared phase/value at each note and maps a DS delay D to
`LFODL = round(D * target_tick_rate / DS_timer_rate) + 1`. The extra tick
retains the existing zero-delay mode's zero-phase onset. The rounded portion
describes phase displacement; the total counter wait also includes that
baseline onset tick. These are not interchangeable onset measurements.
Counter values above 255 fail rather than saturating or wrapping.

FMPLANET uses depth 15, speed 25, range 1, pitch type 0 and delay 10. At source
tempo 115 and mapped target parameter 115:

- Source timer wait: 10 updates, approximately 52.095 ms.
- Rounded target phase displacement: 5 sequence ticks, approximately
  54.596 ms, a +2.501 ms displacement error under the stated model.
- Encoded LFODL: 6 ticks, approximately 65.515 ms including the baseline
  onset tick; native LFOS 26/MOD 2 approximates the source sine with a triangle.
- Source/target modulation frequencies: approximately 9.373/9.301 Hz.

The first note starts with depth zero, followed by depth 15 at the same source
timestamp. No DS timer update elapses between these commands. The compiler
preserves that order: the first note preloads the delay, then the depth control
enables it. Later notes reset the shared target delay/phase. Reordering that
control before the note would lose the first-note behavior under the existing
note-on reset policy.

The new `native_pitch_lfo_delay` flag requires native pitch-LFO mode and its
existing singleton/fixed-tempo/pitch-only requirements. On a delayed track,
delay and modulation settings must be fixed after initial activation, which
must occur at the first note timestamp. Initial depth activation immediately
after that note at the same tick is allowed. Later activation, changes to
held-note delay/depth/speed/range/type, invalid values and overflowing delays
remain rejected. Zero-delay tracks retain the earlier behavior. The underlying
converter requires an explicit delay flag. The [v5 batch audit](nds-compatibility-audit.md)
now tries this bounded policy for eligible candidates, labeling delayed-LFO
and envelope/delayed-LFO successes separately. FMPLANET has user-reported
acceptance; this does not establish listening acceptance for other songs.

The later [HOMETOWN experiment](nds-live-depth-research.md) adds a separate
opt-in positive-depth update policy. It does not relax this fixed-delay mode
or the v5 batch scan's settings.

Native track sharing remains an approximation: a new note resets older
overlapping voices and release tails, whereas DS voices retain independent
timers. Triangle shape, pitch quantization, sequence/audio-frame timing,
PCM8, envelopes and the ten-voice budget remain fidelity limits.
The native delay count/phase behavior is checked against actual EXE6 RAM;
the related public [MPlay sequence driver](https://github.com/pret/pokeemerald/blob/master/src/m4a_1.s)
provides implementation context rather than a substitute for that check.

## Artifact and evidence

The export retains all seven source tracks and 16 PCM samples, with seven
voice contexts and 238,472 generated MPlay bytes. Japanese EXE6 Gregar retains
eight-track player capacity and ten PCM voices at 10,512 Hz; gain is +3.5 dB.
Title (1), ordinary virus music (21) and communication scenes select appended
entry 474. Original entries and prefix data outside declared hook/configuration
ranges are preserved. BPS reconstruction passes and input ROMs are unchanged.

- ROM size: 8,631,076 bytes; CRC32 `7952EA01`.
- SHA-256: `bda3ca135b8477f15fb0c71314777d581fd4f7c7e1e580f53f49acb3d1fe4a18`.
- Compiled loop start/period: 2976/2304 ticks. First jump is about 58 seconds,
  then about 83 and 108 seconds. The native-LFO warmup unrolls existing music.

The new optional reference hook records per-voice counter/phase before and
after modulation updates, including waiting periods. It adds no synthesis
changes. `reference-player-delay-v1/build.json` records the source/renderer
hashes; the pristine core was recovered from the earlier cached copy and all
31 files were verified against its pinned upstream hashes before building.

`runtime/reference-validation.json` checks a 180-second software DS reference:
3,326 notes, all 16 PCM16 samples, 90 pan/bend/expression/delay controls,
77,820 sine-modulation values and 79,800 counter/phase transitions. Each of
the 198 observed delayed voice starts has ten waiting updates (1,980 total),
with phase held fixed, followed by zero-phase activation. Source notes cover
at least two complete loops on each track.

`lfo-window/validation.json` checks 2,400 natural frames through music clock
3679: every note/track state and native LFO state matches the MPlay model.
Track 2 is active, and 177 delayed zero-phase hold snapshots are observed.
No registers or RAM are changed. This window does not cover a compiled jump.
The diagnostic DS/target comparison has 6,366 allocated-voice comparisons,
RMS pitch difference 10.11 cents and maximum 25 cents; it is sequence-clock
aligned, not waveform aligned or equal voice allocation.

`runtime/runtime.json` passes original effects 100/129, ordinary/synthetic
communication dispatch, queued stop, native restoration and three controlled
restart/rematch cycles. These helper calls inject debugger registers and do
not establish actual linked battles or map transitions. `preview/preview.wav`
and `comparison/listen.html` provide a 30-second actual mGBA mix and normalized
software-DS/GBA comparison.

All 178 Python regression tests pass. All ten previously accepted ROMs
rebuild byte-identically; hashes are in
`out/nds-research/delay-research-v1/accepted-rebuilds.json`. Regressions cover
delay rounding, overflow/invalid values, initial same-tick activation, live
parameter rejection, counter phase holds, note retriggers and native-data
preservation. `validation-summary.json` separates these automated checks
from the `manual-testing.json` user-reported acceptance record. That record
covers sustained listening, delayed vibrato onset, overlap/release behavior,
loop joins, effects coexistence, native map music restoration and restarting
on the next encounter. No timed recording or full-loop execution trace was
supplied; linked play/rematch was not separately reported. The measured
approximation and automated coverage limits remain unchanged.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-fmplanet-delay --event 1 --event 21 --event scene:communication \
  --out out/nds-delay-example
python3 scripts/build_nds_reference.py --core /path/to/pristine/SSEQPlayer \
  --out out/nds-delay-reference-example
mkdir out/nds-delay-example/reference
out/nds-delay-reference-example/nds-reference \
  out/nds-delay-example/source.sdat 2 180 out/nds-delay-example/reference
python3 scripts/validate_nds_experiment.py out/nds-delay-example \
  --reference out/nds-delay-example/reference --lifecycle --out out/nds-delay-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-delay-example --frames 2400 \
  --reference out/nds-delay-example/reference --out out/nds-delay-example/lfo-window
```

Use fresh output directories. Listen in a virus or communication battle for
three minutes. Check held-note onset and vibrato joining, overlapping notes,
release tails and loop joins, alongside chips/Buster effects. Finish the
battle, confirm native map music returns and start another battle to confirm
FMPLANET restarts. The title changes scenes before the first compiled jump.
