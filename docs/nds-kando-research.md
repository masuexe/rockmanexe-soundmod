# Star Force 3 KANDO experiment

The next conversion candidate is Star Force 3 SSEQ 31, `BGM_KANDO`.
Its seven source tracks are retained individually, using fourteen original
PCM waves. An intro and frequent pan changes provide different coverage
from [ROOM](nds-import-research.md) and [BATTLE](nds-battle-research.md).
The independent source model, one natural GBA loop and controlled lifecycle
checks pass. The user confirms the requested listening/gameplay sequence has
no issues: sustained battle listening, chips/Buster effects, victory/map music
restoration and the next encounter. KANDO is accepted as a second gameplay
baseline alongside BATTLE for the reported test configuration.

## Selection and conversion changes

The existing pinned Star Force 3 SDAT was inspected using the bounded
execution parser, rather than relying on the earlier structural inventory.
Other at-most-eight-track candidates expose additional unsupported features:
HOKORA needs non-instant attacks, BURAI/SABISHI/LOSE use active modulation,
and FRIEND executes envelope overrides. They remain future research work.
KANDO uses the existing supported note/control subset and instant attacks;
it requires neither track merging nor new envelope approximation.

Two direct-converter limitations were corrected:

- Tempo parameters now accept the full one-byte range, 1–255, already used
  by the BATTLE compiler. Source tempo 150 maps to MPlay 151, approximately
  119.973 versus 120.251 ticks/second (GBA about 0.232% faster).
- The expected repeated-note model now uses the recorded source loop action
  index. A loop may start between two events at the same tick, so filtering
  notes only by timestamp can incorrectly repeat a prefix note. A synthetic
  fixture explicitly covers this case.

KANDO enables the optional direct-converter music-priority mapping: source
priorities 121–127 become 0–6 with song priority 20, below the native test
effect priorities. ROOM retains its original conversion settings. KANDO's
fourteen waves retain the existing PCM8 quantization, tuning and approximate
envelopes. Gain remains +3.5 dB, carried forward as an experimental default;
it has not been independently calibrated for this song.

## Artifacts and verification

Output directory: `out/nds-research/kando-exe6-v1/`.

- `unified.gba`, `unified.bps`, `build.json`: Japanese EXE6 Gregar, 8,642,416
  bytes, adding 253,808 bytes. SHA-256
  `66bf627c23eae7f84bbfd0e4e474d871cbc452ee9da85d24425df79c4cbcdd83`.
  BPS reconstruction matches. Events 1, 21 and `scene:communication` select
  KANDO at appended entry 474. Native entries 0–473 and declared-prefix
  preservation checks pass. No manager project or input ROM is modified.
- `conversion.json`, `dependencies.json`: seven original tracks, fourteen
  waves, 250,044-byte generated MPlay container. Every source track has a
  3,072-tick period. Most track states begin repeating at tick 144; track 4
  reaches its repeated state at tick 1,536. GBA decoding checks note keys,
  instruments, velocities, gates and timing.
- `reference/` and `lifecycle/reference-validation.json`: an 80-second
  software DS reference covers repeated source loops. All 2,630 note events,
  274 pan/bend/expression observations and fourteen decoded PCM16 wave arrays
  match the Python source execution/decoder. This is SSEQPlayer synthesis,
  not a DS hardware recording.
- `sustained-one-loop/validation.json`: natural title start, no CPU/header
  redirection. All seven track states match every frame through 2,290 frames,
  music clock 4,609; all fourteen waves trigger and the PCM output changes.
  The explicitly requested coverage is **one period after every track's
  loop start**, not the default two. This crosses the latest loop boundary
  before the title's approximately 43-second music-ending transition.
- `lifecycle/runtime.json`: native effect initialization, continued music,
  ordinary battle dispatch using the original ROM descriptor, communication
  selection, queued stop and three controlled stop/native-restore/rematch
  cycles pass. Imported voices clear on stop; native songs resume and
  communication restart resets the clock. PC/LR/arguments and a synthetic
  communication descriptor are injected; no actual results screen, map
  transition or linked battle is executed by this probe.
- `preview/preview.wav`: 24-second natural mGBA SDL mix, peak 14,607.
  `listen/listen.html` compares it with the software DS reference after RMS
  normalization. This page compares balance/timbre and masks raw volume
  differences. The preview is shorter than a complete loop.

The software DS reference reaches sixteen voices in coarse snapshots, so
GBA's ten-voice PCM budget remains a possible audible limitation. Exact
source timing/control comparisons do not prove identical audible synthesis.
The already accepted ROOM v2 and BATTLE virus-build ROMs rebuild byte-identically
after the direct-converter changes.

All 125 Python regression tests pass, including fixtures for full-byte tempo
encoding, optional effect-priority headroom, loops between simultaneous events
and actual-ROM KANDO BPS/native-data preservation. The focused NDS suite has
22 passing tests. The natural GBA loop check explicitly requests one period;
the validator's default two-period coverage remains unchanged.

## User test sequence

Run the new GBA directly or apply its BPS to the original Japanese Gregar ROM.
To reuse a save, copy it under the new ROM's basename and keep the original.

1. Listen in a virus or communication battle for at least two full periods
   (about 70 seconds covers the intro and two periods), checking loop joins,
   pan changes, missing parts and volume.
2. Use chips and the Mega Buster during playback.
3. Win and return to the map, checking normal music restoration and residual
   battle sounds; enter another virus battle and check the song restarts.

The user reports all requested checks above passed. This is KANDO-specific
acceptance, recorded in `manual-testing.json` and `validation-summary.json`.
The requested listening duration was approximately 70 seconds; no timed trace
or recording was supplied. The report does not separately identify virus and
communication listening runs. Communication-specific playback and rematches
can extend that coverage separately.

With BATTLE and KANDO accepted, the next research stage can select a
representative Star Force 1/2 song and check archive, bank and sequence
compatibility across games before exposing broader NDS selection in the manager.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song kando \
  --event 1 --event 21 --event scene:communication --out out/nds-kando-example

python3 scripts/validate_song.py out/nds-kando-example/unified.gba \
  --unified out/nds-kando-example/build.json --loop-cycles 1 --frames 2500 \
  --out out/nds-kando-example/sustained-one-loop

python3 scripts/validate_nds_experiment.py out/nds-kando-example \
  --lifecycle --out out/nds-kando-example/lifecycle
```

`validate_song.py` still defaults to two periods. The reference renderer and
comparison commands are documented with the ROOM experiment; render source
slot 31 for 80 seconds for this candidate. `--song room` remains the default
research build. NDS imports are not yet available in the manager.
