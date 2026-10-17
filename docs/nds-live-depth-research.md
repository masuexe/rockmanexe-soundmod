# Live positive pitch-LFO depth: Star Force 1 HOMETOWN

This experiment converts SSEQ 3 `BGM03HOMETOWN` from the pinned Japanese
Star Force 1 Dragon archive, SDAT file 667. It adds a separate opt-in policy
for positive modulation-depth changes after initial activation, retaining
fixed pitch type, speed, range and delay. On 2026-10-17 the user reported
no issues after the requested listening and gameplay checks for this exact ROM.

Artifact: `out/nds-research/sf1-hometown-depth-exe6-v1/`.
CLI song: `sf1-hometown-depth`.

## Semantics and bounded support

Source track 2 starts with depth 10, speed 25, range 1 and delay 10.
At tick 3072 its depth changes to 20, after a new note at that same timestamp;
the next source loop restores depth 10 at tick 6912, again after a note.
Existing DS release voices receive the new depth while retaining their own
phase and delay count. `Channel::UpdateMod` in the pinned independent core
copies the parameters without resetting those counters.

`native_pitch_lfo_live_depth=True` requires both existing native pitch-LFO
and delay flags. It permits only positive depth changes; type, speed, range
and delay must remain fixed after activation before or at the first note timestamp.
Later activation, disabling modulation and changing other active parameters
remain rejected. All active states must fit the existing native mapping.
Singleton source tracks and a fixed tempo remain required. The default
compiler policy and archived v5 audit routes are unchanged. The later
[v6 audit](nds-compatibility-audit.md) tries this opt-in policy after the
existing routes, separately labeling live-depth and envelope/live-depth
successes. HOMETOWN is its only newly packed candidate and matches this ROM.
The subsequent [GOWAIINCHO correction](nds-pre-note-lfo-research.md) also
admits initialization before the first note; archived v6 results are unchanged.

Depth controls emit MOD alone, in original execution order. They do not
emit LFOS=0 or LFODL, so they preserve the shared target phase and delay
count. Notes retain the existing phase/delay reset policy. At tick 3072,
the first note therefore executes with the prior depth before the same-tick
MOD update takes effect. Synthetic held-note regressions additionally check
depth changes during an unfinished delay and during active modulation.

Source tempo 105 maps to target parameter 105 (83.619 ticks/second).
Track 2 maps depths 10/20 to MOD 1/2, LFOS 29 and LFODL 5. Its rounded
phase displacement is 47.836 ms versus the DS delay of 52.095 ms; the
59.795 ms total target counter wait includes the baseline zero-phase tick.
Track 4 uses depth 10, speed 20 and zero DS delay, mapping to MOD 1/LFOS 23.

This is an approximation: target triangle and quantized depth replace a DS
sine, and all target voices on one track share phase and delay. New notes
reset older voices and release tails. PCM8, envelopes, tempo and ten-voice
allocation retain their documented limits. Positive depth updates do not
remove these differences.

## Build and evidence

The export retains all eight tracks, 19 PCM samples and +3.5 dB gain.
It also enables the existing envelope mode: source attack 90 fits native
attack 66, while attack 127 maps to 255. The first attack-90 note occurs
at tick 6156, approximately 73.6 seconds into target playback.
Title (1), ordinary virus music (21) and communication scenes select slot
474. Original table entries and prefix bytes outside declared hook/config
ranges remain preserved. BPS reconstruction passes; input ROMs are unchanged.

- ROM: 8,844,192 bytes, CRC32 `F7ED8E70`.
- SHA-256: `bc42473b384a63f1e64edea0fe6dc6992f422f28a3a810f64ae4f9d031c69340`.
- Compiled loop start/period: 13068/6912 ticks. The first two compiled jumps
  occur near 239 and 322 seconds. Warmup unrolls existing music without silence.

The independent 260-second software DS reference covers at least two complete
source loops per track: 4,292 notes, all 19 decoded PCM16 samples, 142 ordinary
controls, 11 depth controls, 248,798 sine modulation observations and 606,924
envelope timer updates. It includes 810 non-instant attack updates.
Delay holds and activation match the independent counter model.

The new `modulation-changes.csv` observes UpdateMod before/after state.
Its 24 positive depth transitions include reused slots; six transitions
carry nonzero phase or delay state. All preserve both counters. Existing
release voices at tick 3072 provide concrete carried-phase observations.
The renderer's new hooks only observe parameters; synthesis is unchanged.
Its duration cap rises from 180 to 300 seconds to cover this longer source.
`reference-player-depth-v2/build.json` records hashes and compiler provenance;
all 31 recovered upstream files matched the prior pinned original hashes.

`lfo-window-v2/validation.json` checks 2,400 natural frames, including the
first depth change and both modulated tracks, against actual MPlay RAM.
`envelope-window-v2/validation.json` checks the same bounded title duration.
The later attack-90 instrument falls outside this window; its native slow
attack coverage remains explicitly incomplete. The envelope probe now bases
its required slow-attack observations on source notes reached in the window.
Independent DS envelope checks cover the later notes; manual battle listening
must still assess that section.

`runtime/` checks effects 100/129, music continuation, ordinary/synthetic
communication dispatch, queued stop, native restoration and three restart
cycles. These controlled helper calls do not establish actual gameplay.
`preview/preview.wav` and `comparison/listen.html` provide 30-second native
audio and normalized software-DS/GBA comparison, before the first live change.
The longer RAM window covers that change; neither probe executes a full GBA loop.

All 188 Python tests pass. All twelve previously accepted configurations rebuild to identical ROM and
BPS bytes; see `out/nds-research/live-depth-research-v1/accepted-rebuilds.json`.
Regression tests cover opt-in gating, held-note phase/count continuity,
unsupported changes, independent observer corruption, same-tick ordering,
BPS reconstruction and original-data preservation. `validation-summary.json`
collects results; `manual-testing.json` records user-reported acceptance for
this exact ROM on 2026-10-17. The requested checks cover six-minute battle
listening, live depth changes, later gradual attack, loop joins, chips/Buster
coexistence, map restoration and next-encounter restart. No timed recording
or full-loop execution trace was provided. Specific linked play and rematches
were not separately reported. Automated coverage remains bounded; the later
attack and complete GBA loops have listening evidence, without instrumented
native execution coverage.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-hometown-depth --event 1 --event 21 --event scene:communication \
  --out out/nds-hometown-example
python3 scripts/build_nds_reference.py --core /path/to/pinned/SSEQPlayer \
  --out out/nds-depth-reference-example
mkdir out/nds-hometown-example/reference
out/nds-depth-reference-example/nds-reference \
  out/nds-hometown-example/source.sdat 3 260 out/nds-hometown-example/reference
python3 scripts/validate_nds_experiment.py out/nds-hometown-example \
  --reference out/nds-hometown-example/reference --lifecycle \
  --out out/nds-hometown-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-hometown-example --frames 2400 \
  --reference out/nds-hometown-example/reference --out out/nds-hometown-example/lfo-window
python3 scripts/validate_nds_envelope.py out/nds-hometown-example --frames 2400 \
  --out out/nds-hometown-example/envelope-window
```

Use fresh output directories. Listen in battle for six minutes, focusing on
depth changes around 37/83 seconds, gradual attacks after about 74 seconds,
overlapping notes/release tails and joins near 239/322 seconds. Use chips and
the Buster, finish the battle, confirm native map music restoration and start
another encounter to check HOMETOWN restarts. Title playback ends too early
for the later sections. Manager integration remains unchanged.
