# Native pitch-LFO approximation: Star Force 1 BATTLE

The next experiment converts Star Force 1 SSEQ 27, `BGM27BATTLE`, using seven
source tracks and twenty-two original PCM waves. Three tracks use active pitch
modulation. This is an explicit **native GBA approximation**, not an exact
conversion of DS per-voice modulation. The user reports no issues with the
requested listening/gameplay sequence, accepting this approximation for the
tested configuration. The waveform, shared-phase and measured pitch differences
remain documented limitations.

Current artifact: `out/nds-research/sf1-battle-lfo-exe6-v2/`. The previously
accepted ROOM, BATTLE (Star Force 3), KANDO, KINCHO and WIN builds are separate.

## Semantics and bounded mapping

The inspected source is the pinned Japanese `ssr1d.nds` documented in the
[first Star Force 1 experiment](nds-sf1-research.md), using SDAT file 667.
This song uses SSEQ file 26, bank 39, source player 0 and tempo 147.
Tracks 1, 2 and 3 execute pitch modulation, type 0, range 1, delay 0, with
speeds 16/20 and depths 15/20/25. Portamento and volume/pan modulation are not
enabled by this experiment. Unsupported active types/delays fail explicitly.

The independently instrumented SSEQPlayer core updates DS modulation at about
191.956 Hz. Each voice starts with phase zero. The sine-table adjustment is
`(sine(phase >> 8) * range * depth) >> 8` in 1/64-semitone units; phase advances
by `speed << 6` modulo 32768. Existing voices retain their individual phases
when another note starts, while live track control changes update their
parameters. The Python model matches the actual reference observations.

MPlay instead shares a triangle LFO across each track. Its phase advances
once per **sequence tick**, not once per video frame. This was checked in the
real EXE6 driver with an explicitly controlled RAM probe: LFOS 10, MOD 3 and
zero delay produce phases 10/30/50 at elapsed music clocks 1/3/5. Recorded
modulation values also match the signed integer triangle calculation.
Evidence: `out/nds-research/lfo-research/native-probe-v2.json`.

The target tempo parameter is 148, about 117.862 ticks/second versus source
117.573 ticks/second (GBA about 0.246% faster). LFOS is chosen using the target
sequence tick rate. MOD quantizes the source peak amplitude to native pitch
steps of 1/16 semitone:

| DS speed | DS depth | MPlay LFOS | MPlay MOD | DS frequency | Target frequency |
| --- | --- | --- | --- | --- | --- |
| 16 | 20 | 13 | 2 | 5.999 Hz | 5.985 Hz |
| 20 | 15 | 16 | 2 | 7.498 Hz | 7.366 Hz |
| 20 | 20 | 16 | 2 | 7.498 Hz | 7.366 Hz |
| 20 | 25 | 16 | 3 | 7.498 Hz | 7.366 Hz |

Each note resets native phase through LFOS 0 and uses a one-tick LFODL to
hold the onset at zero. This is coarser than DS's zero-delay, per-voice update.
New notes also reset older voices on the same track. In the converter's first
source-state trace, track 2 has nine modulated note onsets with older held notes; release
tails add further shared-phase differences. This approximation retains every
note instead of claiming independent phases fit in seven native track states.

Long gates of 288/252 ticks use TIE/EOT with distinct aliases 127/126. Their
rhythm-bank children retain sounding keys 72/74. There is no gate splitting
or forced reattack. Source controller order within a tick is retained: several
depth changes follow a note at the same tick. Sorting every control before
every note would incorrectly restore stale per-note depth. V2 corrects that
case and adds regression checks at ticks 0, 2304 and 3072.

For this mode, one complete warmup period is unrolled after the latest source
loop-state start. The common target loop starts at tick 9216 and repeats every
4608 ticks. This is approximately 78 seconds of existing music before the
compiled jump; it does not insert silence or an extra musical intro. Earlier
musical repeats are already represented in the unrolled event stream.

## Artifact and validation

- `unified.gba`, `unified.bps`, `build.json`: Japanese EXE6 Gregar, 8,808,100
  bytes, adding 419,492 bytes. CRC32 `7BC6F2C3`, SHA-256
  `de0441a5cf50ffb63ceeea15c6e412d7ccc1be9b49c466a4843282ce63ed6dff`.
  BPS reconstruction and native table/prefix preservation pass. Events 1, 21
  and `scene:communication` select appended song 474. No playback engine code
  or track storage is expanded; the mixer remains at ten PCM voices/10,512 Hz.
- `conversion.json`, `dependencies.json`: 415,696 generated MPlay bytes,
  twenty-two samples, seven singleton track groups, 3,890 mapped notes in the
  compiled prefix plus period. Independent GBA decoding checks note order,
  gates, aliases and loop periods. Relative music priorities retain native
  effect headroom. Gain remains the experimental +3.5 dB default.
- `reference/`, `lifecycle/reference-validation.json`: 150-second software DS
  synthesis covers repeated source loops. All 4,940 source note events,
  328 pan/bend/expression controls, twenty-two decoded PCM16 resources and
  235,522 per-voice pitch-modulation values match the Python source models.
  Observations do not alter synthesis. The reference was reused from V1 only
  after verifying the source SDAT is byte-identical; target ordering changed.
- `native-lfo-window/validation.json`: 1,500 natural title frames, final music
  clock 2959. All seven decoded note states and every active native phase,
  depth, speed, type, delay and delay counter match the MPlay execution model
  each frame. No RAM/register changes are made by this probe. This is a bounded
  window, not full target-loop validation or a DS synthesis-equivalence test.
- `lifecycle/runtime.json`: native effects and continued music, ordinary
  battle dispatch, communication selection, queued stop and three controlled
  stop/native-restore/rematch cycles pass. These inject PC/LR/arguments and a
  synthetic communication descriptor; actual gameplay remains a user test.
- `preview/preview.wav`: 30-second natural mGBA SDL mix, peak 9,537.
  `listen/listen.html` embeds normalized DS-reference/target clips and clearly
  labels the LFO approximation. The preview ends before the compiled loop.

The isolated one-second curve comparison in `conversion.json` measures RMS
pitch differences of about 4.8–7.8 cents across the four configurations. It
excludes overlapping-note resets and audio-frame quantization, so it is not a
bound on whole-song error. The actual recorded target track values compared
against allocated DS voices by sequence clock give the diagnostic below:

| Track | Comparisons | RMS difference | Maximum difference |
| --- | --- | --- | --- |
| 1 | 5,437 | 11.81 cents | 26.56 cents |
| 2 | 4,579 | 12.19 cents | 28.13 cents |
| 3 | 1,419 | 10.01 cents | 37.50 cents |

See `native-lfo-window/modulation-comparison.json`. This selects the latest
observed DS timer frame at each sequence clock; clips are not sample-aligned
and the DS/GBA voice allocations differ. The numbers demonstrate a remaining
approximation, not an audible-fidelity pass/fail score. The software reference
reaches sixteen voices, while the target still has a ten-voice budget.

All 139 Python regression tests pass. Added checks cover DS sine quadrants,
signed rounding, actual native-probe observations, tick-based LFOS mapping,
unsupported active effects, note resets, long aliases, same-tick depth order,
BPS reconstruction and native-data preservation. All five previously accepted
song builds rebuild byte-identically with the new mode disabled.

## User test

Use the V2 ROM directly or apply its BPS to the original Japanese Gregar ROM.
Copy a save under the new ROM's basename if needed, keeping the original.

1. Listen in a virus or communication battle for approximately three minutes.
   This covers the compiled jump and two periods after its warmup prefix.
   Pay particular attention to melody vibrato, overlapping long notes and
   loop joins. The automated title window cannot reach that jump.
2. Use chips and the Mega Buster during playback.
3. Win, return to the map and enter another virus battle; check normal
   restoration, absence of residual notes and correct restart.

The user reports no issues with this requested test sequence. Song-specific
acceptance is recorded in `manual-testing.json` and `validation-summary.json`:
listening/long loops, effects coexistence, map restoration and next-encounter
restart pass by user report. Approximately three minutes was the requested
duration; no timed recording or full-loop execution trace was supplied.
Separate virus/communication runs and communication rematches were not
individually identified in the feedback.

This establishes usability of the approximation for the tested configuration,
not exact independent-voice modulation. Automated full target-loop validation
remains separate from the manual listening pass. Per-voice fidelity, active
delayed LFO, volume/pan modulation and broader manager integration remain
further work. The next coverage step can audit the three games' remaining
candidates against the implemented subset before selecting more conversions.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-battle-lfo \
  --event 1 --event 21 --event scene:communication --out out/nds-lfo-example

python3 scripts/build_nds_reference.py \
  --core /tmp/nds-lfo-upstream --out out/nds-lfo-reference

mkdir out/nds-lfo-example/reference
out/nds-lfo-reference/nds-reference \
  out/nds-lfo-example/source.sdat 27 150 out/nds-lfo-example/reference

python3 scripts/validate_nds_lfo.py out/nds-lfo-example \
  --reference out/nds-lfo-example/reference --out out/nds-lfo-example/native-lfo-window

python3 scripts/validate_nds_experiment.py out/nds-lfo-example \
  --reference out/nds-lfo-example/reference --lifecycle --out out/nds-lfo-example/lifecycle
```

The optional reference builder expects pristine kode54/SSEQPlayer files. For
this run the cached earlier sources were reversed only through the known
observation/codecvt edits; every resulting file matched its recorded upstream
SHA-256 before rebuilding. The new renderer records per-voice modulation and
its helper-source fingerprint in `out/nds-research/reference-player-lfo-v3/`.
No core synthesis changes were made. Default converters still reject active
modulation unless this explicit research mode is selected.
