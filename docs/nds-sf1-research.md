# Star Force 1 cross-game experiment

The first Star Force 1 candidate is SSEQ 23, `BGM23KINCHO`, retaining eight
source tracks and fifteen original PCM waves. It uses the existing direct
converter without adding new synthesis approximations. Independent source
comparisons, one natural GBA loop and controlled lifecycle probes pass.
The user confirms the requested sustained battle listening, chips/Buster
effects, victory/map restoration and next-encounter checks all pass. This
song is the first user-accepted Star Force 1 gameplay baseline.

This follows the accepted Star Force 3 [BATTLE](nds-battle-research.md) and
[KANDO](nds-kando-research.md) experiments. It verifies a supported sequence
subset across games; it does not establish general Star Force 1/2 support.

## Source identities and selection

All three local Japanese Star Force 1 originals were checked:

| Source | Game code | SHA-256 |
| --- | --- | --- |
| `ssr1d.nds` | `A6CJ` | `b531571a442d1aadd96ba7fa63637b97a8066b39ee5c54641eb61d4e5808807c` |
| `ssr1l.nds` | `A6BJ` | `5a31dd8472f120dc95808c8d4eeb549909ed75d2fca05af894e949b52de723d8` |
| `ssr1p.nds` | `A6AJ` | `d4ec40d1c0a169925f5ca58952a00e8b6865ac41e1e8300d609688a2c72beb6b` |

Their SDATs are byte-identical: NDS FAT file 667,
`datbin/com/sound_data.sdat`, 10,061,568 bytes, SHA-256
`2b162eced95dadba3362316e0eb49b95b2990014a7fcb119fb9d21c1b01c1fd7`.
Star Force 3 instead uses file 187 and a different SDAT fingerprint. The
research builder now selects the pinned archive descriptor from the verified
ROM identity, checks its hash and rejects song/source-game mismatches.

KINCHO is sequence index 23, SSEQ file 22, bank 39, wave archive 39 and
source sequence player 0. This differs from KANDO's Star Force 3 bank 158
and source player 1. All fifteen used waves are DS ADPCM, decoded to PCM16
and quantized to GBA PCM8 with the existing tuning/loop/envelope conversion.
No track merging or playback-state storage expansion is required.

HOMETOWN and BATTLE were also inspected. Their executed tracks use active
modulation, which the current converters reject. Other candidates require
long gates, more than eight tracks or additional sequence semantics. They
remain future work. This experiment deliberately keeps the implemented
control subset bounded instead of silently dropping effects.

Source tempo 115 maps to MPlay parameter 115: approximately 91.979 versus
91.582 ticks/second (GBA about 0.431% slower). Source priorities 120–127
map to 0–7 with song priority 20, retaining native-effect headroom. The +3.5 dB
gain remains a carried-forward experimental setting, not an independently
calibrated Star Force 1 loudness correction.

## Artifacts and evidence

Directory: `out/nds-research/sf1-kincho-exe6-v1/`.

- `unified.gba`, `unified.bps`, `build.json`: Japanese EXE6 Gregar output,
  8,702,856 bytes, adding 314,248 bytes, CRC32 `82D8B1F0`, SHA-256
  `a45c33eabbe09ba8a5a82bef065c6b425ddde023b5be6fe089076e33adbae77c`.
  BPS reconstruction and native table/prefix preservation pass. Appended
  entry 474 is selected on title event 1, ordinary music event 21 and
  `scene:communication`. Special battles using other music IDs retain their
  original pools. Input ROMs and manager projects remain untouched.
- `conversion.json`, `dependencies.json`: eight original tracks, fifteen
  waves, a 310,420-byte generated MPlay container. Every source track has a
  2,304-tick period. Loop-state starts vary from tick 0 to 1,536; GBA decoding
  checks notes, instruments, velocity, gates, timing and loop periods.
- `reference/`, `lifecycle/reference-validation.json`: 80-second SSEQPlayer
  software DS synthesis covers repeated source loops. All 1,200 observed note
  events, 111 pan/bend/expression controls and fifteen decoded PCM16 arrays
  match the Python execution/decoder. This is not a DS hardware recording.
- `sustained-one-loop/validation.json`: natural title playback without
  CPU/header redirection; all eight track states match each frame through
  2,506 frames and music clock 3,842. All fifteen samples trigger and nonzero
  PCM output changes. The requested coverage is one period after every track
  loop start. It finishes before the title's music-ending transition; it
  does not establish two-period GBA validation or actual battle gameplay.
- `lifecycle/runtime.json`: original effect initialization and music
  continuation, ordinary battle dispatch from the original descriptor,
  communication selection and queued stop pass. Three controlled cycles
  clear imported voices, resume native songs 2/3, and restart imported music.
  These inject PC/LR/arguments and a synthetic communication descriptor;
  actual results-screen/map transitions remain user checks.
- `preview/preview.wav`: 24-second natural mGBA SDL capture, peak 15,724.
  `listen/listen.html` embeds equal-duration software DS and actual GBA clips
  with RMS normalization; its labels now use the source game from the manifest.
  The clip ends before a complete loop and normalization masks raw loudness.

The DS reference reaches sixteen voices in coarse snapshots, while the target
uses all ten configured PCM voices in the first 240 frames. Audible voice
stealing, envelopes, sample resolution and tempo quantization remain limits.
The accepted Star Force 3 ROOM, BATTLE and KANDO outputs rebuild byte-identically.
The same Star Force 1 settings produce identical SDAT, generated resources
and target bytes from each of the three pinned originals; source identity
metadata correctly distinguishes them. Runtime evidence above is from Gregar.

All 129 Python regression tests pass. New integration checks cover archive
selection, correct source labels, song/source mismatch rejection, unverified
source rejection, identical exports from the three source variants, BPS
reconstruction and original table/prefix preservation.

## User acceptance

Run this ROM directly or apply its BPS to the original Japanese Gregar ROM.
Copy an existing save under the new ROM's basename if needed, keeping the
original save intact.

1. Listen in a virus or communication battle for approximately 75 seconds,
   checking two full periods, loop joins, missing parts, pan and volume.
2. Use chips and the Mega Buster alongside the music.
3. Win and return to the map, then enter another virus battle; check normal
   music restoration, lack of residual battle sounds and correct restart.

The user reports all requested checks above passed for this test build.
The song-specific record is in `manual-testing.json`; `validation-summary.json`
retains the automated results separately. Approximately 75 seconds was the
requested listening duration; no timed recording or gameplay trace was
provided. Separate virus/communication listening runs and communication
rematches were not individually identified in the report.

This extends user acceptance from Star Force 3 to the implemented Star Force 1
subset. It does not establish compatibility for every song or source version.
Star Force 2 is the next cross-game candidate; active modulation and performance
measurements remain separate research work.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-kincho \
  --event 1 --event 21 --event scene:communication --out out/nds-sf1-example

python3 scripts/validate_song.py out/nds-sf1-example/unified.gba \
  --unified out/nds-sf1-example/build.json --loop-cycles 1 --frames 2700 \
  --out out/nds-sf1-example/sustained-one-loop

python3 scripts/validate_nds_experiment.py out/nds-sf1-example \
  --lifecycle --out out/nds-sf1-example/lifecycle
```

Use `ssr1l.nds` or `ssr1p.nds` for the other verified source variants. The
optional renderer documented in the ROOM research takes source slot 23 and
80 seconds for this reference. The default `--song room` still requires a
verified Star Force 3 source. NDS imports remain a research CLI feature;
they are not yet exposed in the manager.
