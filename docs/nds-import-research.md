# NDS music import research

Assessment and first experiment date: 2026-10-15. Star Force 3 `BGM_ROOM` now
converts into GBA MPlay resources and plays naturally in Japanese EXE6.
The Gregar experiment passes sustained execution through two loops; Falzar
also passes the start/effect/queue/stop probes. This is a separate research CLI,
and NDS import/preview is not yet available in the manager.

The second [BGM_BATTLE experiment](nds-battle-research.md) now maps eleven
source tracks into eight target tracks without dropping note events. It has
independent source comparisons and controlled scene/stop checks. User testing
passes three-minute communication playback with chips/Buster effects and the
virus-battle start/victory/map/next-encounter sequence. Automated full-loop
state comparison remains incomplete; see its report for the separate evidence.

The next [BGM_KANDO experiment](nds-kando-research.md) retains seven source
tracks and checks a different intro/pan pattern without merging. Source
comparisons, one natural GBA loop and controlled lifecycle checks pass.
The user also confirms its requested sustained listening, effects coexistence,
victory/map restoration and next-encounter tests pass, establishing a second
tested gameplay baseline.

The [first Star Force 1 experiment](nds-sf1-research.md), `BGM23KINCHO`, now
checks the same conversion subset against a second game's archive/bank layout.
Eight tracks and fifteen samples pass independent source comparisons, one
natural GBA loop and controlled lifecycle checks. The user confirms sustained
listening, chips/Buster effects, victory/map restoration and next-encounter
playback all pass for this song;
the three pinned Japanese Star Force 1 originals share an identical SDAT.

The [first Star Force 2 experiment](nds-sf2-research.md), `BGM_WIN`, now
passes independent source comparisons, two natural GBA periods and controlled
lifecycle probes using seven tracks and fifteen samples. Both pinned Japanese
source variants share the verified archive. The user confirms sustained
listening, chips/Buster effects, victory/map restoration and next-encounter
playback pass. All three games now have an accepted candidate within the
implemented subset; general song/effect compatibility remains unestablished.

The next [native pitch-LFO experiment](nds-lfo-research.md) now converts Star
Force 1 ordinary BATTLE using a bounded GBA triangle-LFO approximation. It
retains seven tracks and twenty-two samples and checks source modulation and
actual native-LFO execution. Shared phases and waveform/quantization errors
are explicitly measured. The user reports no issues with the requested long
listening/loop, effects coexistence, map restoration and next-encounter tests,
accepting the approximation in the tested configuration. Automated full-loop
state validation and exact per-voice modulation remain separate limitations.
Other active effect types remain outside this mode.

The [batch audit](nds-compatibility-audit.md) now scans all three pinned
archives directly. Twenty-eight of 122 nonempty/nonsilent SSEQ candidates pass
conversion, shared export and BPS reconstruction; the report distinguishes
standard/LFO routes, exact matches to existing manual evidence and all
blockers. This adds no new runtime/listening acceptance or manager support.

## Existing foundation

Both Japanese EXE6 targets already have verified native audio layouts,
eight-track music players, selected-song packing, scene/pool selection,
resource relocation, BPS reconstruction and native-data preservation checks.
Their configured PCM mixing rate is 10,512 Hz. Source previews and actual
target-ROM recordings are separate; the latter can be used to check a future
converted song. See [EXE6](exe6.md) and [fidelity research](audio-fidelity.md).

The original EXE6 ROM is 8 MiB and the exporter enforces a 32 MiB limit.
This leaves room for a first converted song, subject to its measured final
size and any other selected imports. Sequence track capacity, simultaneous
sounding voices and global PCM channel budget are different limits.

The existing analyzer/relocator consumes GBA MPlay sequences and instrument
records. The new `scripts/nds_music.py` provides a bounded conversion layer,
and `scripts/build_nds_experiment.py` feeds its generated resources through
the existing GBA export/validation core.

## Local source inspection

The supplied Windows path maps to `/home/harp/projects/nds/roms`.
The read-only inspection used ndspy 4.2.0 downloaded into `/tmp`; it added
no production dependencies. Local evidence is in
`out/nds-research/inventory.py` and `out/nds-research/inventory.json`.
The inventory records ROM and SDAT hashes and verifies that each inspected
source ROM still has the same hash after reading.

The inspected Japanese Star Force 3 files are:

| Source | Game code | CRC32 | ROM SHA-256 |
| --- | --- | --- | --- |
| `ssr3b.nds` | `CRBJ` | `1B4DE6F9` | `64ff3011d41dbcb56990f355254fe765c5088daf2915f695e31420114356743a` |
| `ssr3r.nds` | `CRRJ` | `E4CAFD9D` | `eaa53a29170a6740ac2f9476321149ccf95f0bc54835fdb51ca66cf5165aca1b` |

Both contain `datbin/com/sound_data.sdat`, NDS filesystem file ID 187,
8,554,720 bytes. The complete SDATs are byte-identical (SHA-256
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`).
This supports sharing an audio conversion experiment between these two
verified source revisions; it does not establish support for other revisions.

Each SDAT has 51 SSEQ slots, one SSAR, 159 SBNK slots, 159 SWAR slots,
three sequence-player slots and one STRM. SSEQ slots 44, 46 and 49 are empty.
The other 48 decode structurally, including the silent `BGM_DUMMY` at slot 0.
The remaining 47 named sequences are research candidates, not validated imports.
All 1,030 wave entries across the wave archives are ADPCM; this is an archive
entry count, not a count of distinct or required samples.

| SSEQ ID | Internal name | Declared sequence tracks | First-experiment assessment |
| --- | --- | --- | --- |
| 2 | `BGM_ROOM` | 6 | Preferred first conversion candidate |
| 24 | `BGM_BURAI` | 8 | Later candidate near the native track limit |
| 35 | `BGM_BATTLE` | 11 | Requires track mapping/reduction or player research |
| 41 | `BGM_VS` | 12 | Requires track mapping/reduction or player research |

Counts include initial track 0 and tracks opened by BeginTrack commands.
They do not establish actual concurrency or which tracks could be merged.
Ten non-dummy sequences declare at most eight tracks. This is a useful
starting filter, not a claim that ten songs are already convertible.

For `BGM_ROOM`, the instrument switches reference eight instrument IDs.
Including all their key regions gives 25 ADPCM waves totaling 132,380 encoded
bytes. This is a coarse resource set, not a final dependency closure or
converted size. Actual note/key usage, default instrument behavior, decoded
sample length, resampling and deduplication still need analysis.

The decoded event graphs include notes/rests, instrument/volume/pan/tempo
changes, jumps, calls/returns, loops, expression, vibrato, portamento and
envelope overrides. Unreachable bytes are preserved as RawData events by
ndspy; they must not be treated as executed unknown commands automatically.
Structural decoding does not prove execution semantics or audible fidelity.

The first executable conversion exposed an ndspy 4.2.0 parsing discrepancy:
SSEQ `0xE0` modulation delay consumes a 16-bit parameter, while ndspy's event
definition consumes one byte. In `BGM_ROOM`, this incorrectly turns subsequent
bytes into two apparent zero-length notes with invalid velocities. The new
bounded standard-library parser reads the correct width, executes calls and
loops, rejects unsupported executed controls and ignores unreachable bytes.
Its output is checked against the independent SSEQPlayer execution below.
The original structural inventory should not be used as an execution model.

## First conversion result

The CLI accepts the two fingerprint-pinned Star Force 3 originals above,
fixed source SSEQ ID 2, and the existing Japanese EXE6 Gregar/Falzar target
profiles. It currently converts only the required subset, including notes,
rests, tick-zero track openings, instrument/volume/expression/pan/priority,
tempo, calls/returns and loops. Active pitch/modulation effects, envelope
overrides, unsupported instruments and unsupported executed commands fail.
The command does not alter manager projects or source selections.

Six original sequence tracks are retained. Actual executed instrument/key
dependencies use 15 original ADPCM waves, fewer than the coarse inventory's
25 waves. ADPCM is decoded into signed 16-bit values, then quantized into
GBA signed 8-bit PCM. The converter preserves sample lengths/loop positions,
uses the DS timer's effective playback rate, and maps the source root note
into the GBA PCM frequency field. Sparse rhythm children retain each note's
pitch and instrument pan. No full-song recording is embedded in the ROM.

Volume/velocity use the DS attenuation table and quantize to GBA values.
Instant attacks map to instant GBA attacks; decay/release multipliers and
sustain amplitude approximate the DS envelopes at the GBA frame rate.
Envelope timing and voice allocation are still fidelity limitations.
Inactive pitch/modulation configuration has no audible effect and is omitted.

Every source track loops after 1,536 ticks, with no timed intro. DS tempo 125
is mapped to GBA TEMPO parameter 126, retaining every sequence tick and gate.
This minimizes tempo quantization error between the DS driver clock and GBA
frame clock: approximately 99.977 versus 100.342 ticks/second, or 0.365% faster
on GBA. A loop is approximately 15.36 seconds in the software DS reference and
15.31 seconds in the target. This is not sample-exact timing.

The generated MPlay resource container is 187,900 bytes. The Gregar output is
8,580,424 bytes, adding 191,816 bytes including relocated resources, audio
table and selection hook. The original 474 audio entries/resources remain
intact; the imported song occupies appended ID 474, using music player 31.
The default build selects it on native title event 1. Other native events
retain their existing music. The startup mixer uses the existing export
default of ten PCM voices at the native 10,512 Hz rate; imported reverb is zero.

Evidence under `out/nds-research/room-exe6-v1/`:

- `unified.gba`, `unified.bps`, `build.json`: checked Gregar experiment. BPS
  reconstruction equals the generated ROM. ROM SHA-256:
  `239e81a679a184815ae0a28f25430114491c9b972d6060f93a73ff9d41e3ef7f`.
- `conversion.json`, `converted-mplay.bin`, `dependencies.json`: executed
  source model, conversion decisions and GBA dependency closure.
- `sustained/validation.json`: normal title selection with no register/header
  redirection. 1,844 frames reach music clock 3,097; all six tracks match the
  decoded GBA model each frame, covering two complete loops, all 15 PCM waves
  and changing nonzero PCM output. This is execution evidence, not a subjective
  listening judgment.
- `reference/`: 36-second software DS reference rendered by the public
  kode54/SSEQPlayer core. Trace hooks observe sequence ticks and NoteOn
  arguments without changing synthesis. All 1,083 reference note events match
  the executed source model, including original velocities/gates, and all
  15 used ADPCM waves decode to exactly equal signed 16-bit sample arrays.
  This is software synthesis, not a DS emulator or hardware recording.
- `runtime-v2/`: original effect IDs 100 and 129 initialize their native
  players while retaining the imported music header. After normal execution
  resumes, music advances from clock 402 to 452 and retains active voices.
  Original queued all-stop sets the stopped marker and resets the game's music
  indicator. These helper probes explicitly inject PC/LR/arguments; they do
  not establish gameplay-triggered effects or a two-peer battle. The earlier
  `runtime/` run failed because its probe restored the pipelined debugger PC
  instead of the actual function entry; `runtime-v2` corrects the probe.
- `preview/preview.wav`: 24-second natural title playback through the real
  mGBA SDL mix, stereo 44.1 kHz signed 16-bit, peak 9,908. It crosses the first
  loop boundary. `listen-v2/listen.html` embeds equal-duration reference/target
  WAVs with whole-clip RMS normalization and a position-preserving A/B switch.
  Clips are not sample-aligned.

The independent DS renderer reaches sixteen active voices in its coarse
100 ms snapshots. The target reaches its ten-voice budget within the first
240 frames. Losing lower-priority/release voices is therefore a concrete
fidelity concern, even though note timing and resource playback pass. The
24-second source/target clips measure raw RMS of -21.79/-25.28 dBFS before
normalization; loudness alone is not a fidelity score. Hardware CPU cost,
envelope accuracy, complete scene lifecycle, fade behavior and communication
gameplay remain unestablished.

The separate `out/nds-research/room-exe6f-v1/` build uses the Red Joker source
and Falzar target. BPS reconstruction, normal title start, native effect
initialization, music continuation and queued stopping pass there too. The
long loop recording/sustained frame-by-frame evidence above belongs to Gregar.

## Title volume calibration

The user listened directly to the first experiment's `unified.gba` title
screen and reported low volume. This feedback is actual in-game listening,
not a judgment based on the normalized A/B page. The original v1 capture
measured -25.28 dBFS RMS versus -21.79 dBFS in the software DS reference.
That 3.49 dB difference prompted an imported-song volume calibration.

The research builder now defaults to `--song-gain-db 3.5` for its fixed
`BGM_ROOM` candidate. The underlying converter remains neutral by default.
Compensation multiplies imported MPlay VOL values before quantization; it
leaves note velocities, sample bytes, envelopes, pan, tempo, waits and loops
unchanged. No additional global mixer adjustment is made. Non-finite or
out-of-range gains fail; a gain exceeding the VOL parameter's headroom fails
instead of silently clamping. This is empirical compensation for this
candidate/target configuration, not a proof of a universal DS/GBA gain ratio
or a root-cause fix for the remaining fidelity differences.

The revised Gregar artifacts are in `out/nds-research/room-exe6-v2/`:

- `unified.gba`, `unified.bps`, `build.json`: same 8,580,424-byte layout as v1,
  with only imported VOL operand bytes changed. The original-ROM prefix is
  byte-identical between v1 and v2, including the master-volume/mixer setting
  and native effects. BPS reconstructs v2 exactly. ROM SHA-256:
  `fcb025f57c22afe73ecb0a810cda8d3d816c32bc57ae38c4909367ab29d6367f`.
- `preview/preview.wav`: another 24-second natural title capture. RMS is
  -21.58 dBFS, a measured increase of 3.70 dB from v1 and 0.21 dB above the
  software DS reference. Peak is 14,647 (-6.99 dBFS), with zero signed 16-bit
  full-scale samples. This establishes capture headroom over this clip, not
  subjective distortion or hardware performance across all gameplay.
- `sustained/validation.json`: all six tracks/all 15 samples pass again through
  music clock 3,097 in 1,844 naturally executed frames.
- `runtime/`: native effect initialization, continued music, native queue
  stopping and the 1,083 independent DS note comparisons pass again.

`out/nds-research/room-volume-comparison/listen.html` embeds the software DS
reference and both actual GBA recordings **without independent normalization**.
Its accompanying `comparison.json` retains measured levels and clip provenance.
This page preserves the volume difference; earlier normalized listening pages
remain suitable for comparing timbre and balance.

Two additional tests check gain bounds/headroom and that v1/v2 differ only in
imported VOL operands. Full regression now passes 117 Python tests.

## Reproduce the experiment

The converter/exporter needs only Python 3.10+ and no ndspy installation:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song-gain-db 3.5 --out out/nds-room-example

python3 scripts/render_preview.py out/nds-room-example/unified.gba \
  --manifest out/nds-room-example/build.json --id 474 --seconds 24 \
  --out out/nds-room-example/preview

python3 scripts/validate_song.py out/nds-room-example/unified.gba \
  --unified out/nds-room-example/build.json --frames 2400 \
  --out out/nds-room-example/sustained

python3 scripts/validate_nds_experiment.py out/nds-room-example \
  --out out/nds-room-example/runtime
```

All output directories must be new. Capture/runtime commands have the existing
mGBA/SDL/compiler prerequisites. Use `ssr3r.nds` and `exe6f.gba` for Falzar.
Use `--song-gain-db 0` to reproduce the original v1 volume; +3.5 dB is the
current builder default for the fixed BGM_ROOM experiment.
Run `unified.gba` directly or apply `unified.bps` to the matching original
Japanese EXE6 ROM. Title event 1 is the default experiment. Repeat `--event`
to choose additional native music IDs or `scene:communication`; these configure
the existing target hooks and do not establish complete battle validation.

The optional independent reference renderer requires `g++` and a local copy
of [kode54/SSEQPlayer](https://github.com/kode54/SSEQPlayer). The builder copies
that public source into its output directory, fixes its old codecvt guards for
modern GCC and adds two observation hooks. It records hashes of every upstream
source file in its build manifest; the supplied source directory is untouched.

```bash
python3 scripts/build_nds_reference.py \
  --core /tmp/rockmanexe-nds-research-deps/SSEQPlayer-main \
  --out out/nds-reference-example

mkdir out/nds-room-example/reference
out/nds-reference-example/nds-reference \
  out/nds-room-example/source.sdat 2 36 out/nds-room-example/reference

python3 scripts/validate_nds_experiment.py out/nds-room-example \
  --reference out/nds-room-example/reference \
  --out out/nds-room-example/runtime-with-reference

python3 scripts/compare_nds_audio.py out/nds-room-example \
  --reference out/nds-room-example/reference \
  --out out/nds-room-example/listen
```

## Conversion design and remaining work

Prioritize `SSEQ + SBNK + SWAR -> GBA MPlay sequence + tone bank + PCM`, using
the existing EXE6 driver. Preserve the original DS instrument samples where
possible. A MIDI file alone would not preserve the source bank or all DS
control semantics. Full-song PCM rendering is a fallback with different ROM
size and playback requirements; STRM import is a separate experiment.

The original experiment sequence below now has concrete source/conversion/
playback evidence. Fidelity, fades and complete gameplay coverage in step 5
remain further work:

1. Start with black-ace source slot 2, `BGM_ROOM`, and the verified Japanese
   EXE6 Gregar target. Build an executed-event model covering complete loops,
   timing, note lifetimes and actual instrument/key dependencies.
2. Decode DS ADPCM into a GBA-supported PCM representation. Convert sample
   root pitch, key regions, loop points and envelopes; measure duration and
   pitch rather than copying format-specific fields unchanged.
3. Generate MPlay commands for the required event subset, including musical
   timing and control flow. Reject unresolved commands explicitly and retain
   a conversion report for approximated controls. Eight sequence tracks do
   not guarantee that all overlapping voices fit the target mixer budget.
4. Pack the generated GBA resources through the shared export path. Reparse
   dependencies, check size/pointers/native preservation, and reconstruct the
   ROM from the emitted BPS. Start naturally through a single-song pool.
5. Record source DS playback and actual exported EXE6 playback. Check repeated
   loops, pitch, balance, stop/fade and transitions with native effects active.
   Test gameplay timing and communication behavior before making claims about
   battle use. Title playback alone is insufficient.

`BGM_BATTLE` now has a checked eight-track mapping in the separate experiment
linked above; `BGM_VS` remains unconverted. Sequence merging and simultaneous
voice allocation require separate validation. Raising the PCM channel setting alone does
not expand sequence-track storage and does not prove acceptable CPU usage.
Expose NDS source selection and previews in the manager after conversion and
target playback have passed; its current agbplay preview is a GBA player.

## Validation and references

After the first conversion, `python3 -m unittest discover -s tests` passed all
115 tests, including 12 new conversion/revision/native-preservation tests.
These cover the 16-bit modulation-delay alignment, note-wait/polyphony,
calls/finite loops, invalid/unsupported execution, ADPCM nibble/sign/saturation,
MPlay gates/waits, pitch/loop/pan headers and actual-ROM BPS reconstruction.
`node tests/test_manager_ui.mjs` and
`node tests/test_audio_worklet.mjs` passed. These establish the existing
baseline alongside bounded conversion correctness. Audible fidelity still
needs listening. No input ROM, source selection or saved manager project was
changed by this research.

Format/parser references:

- [ndspy SDAT structure](https://ndspy.readthedocs.io/en/latest/appendices/sdat-structure.html)
- [ndspy 4.2.0 SSEQ parser](https://github.com/RoadrunnerWMC/ndspy/blob/v4.2.0/ndspy/soundSequence.py)
- [ndspy 4.2.0 instrument bank parser](https://github.com/RoadrunnerWMC/ndspy/blob/v4.2.0/ndspy/soundBank.py)
- [ndspy 4.2.0 sample parser](https://github.com/RoadrunnerWMC/ndspy/blob/v4.2.0/ndspy/soundWave.py)
- [SSEQPlayer executed track semantics](https://github.com/kode54/SSEQPlayer/blob/main/Track.cpp)
- [SSEQPlayer sample decoding](https://github.com/kode54/SSEQPlayer/blob/main/SWAV.cpp)
- [SSEQPlayer DS conversion functions](https://github.com/kode54/SSEQPlayer/blob/main/common.h)

To reproduce the local inventory, put the public ndspy v4.2.0 source under
`/tmp/rockmanexe-nds-research-deps/ndspy-4.2.0` and run
`python3 out/nds-research/inventory.py`. The script scans whichever `.nds`
files are present at that time. Its source-resource estimates intentionally
include every region of explicitly selected instruments and do not claim
complete default/dynamic-instrument resolution.
