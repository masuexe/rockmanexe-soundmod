# Note-on envelope snapshots and non-instant attack

Two opt-in Star Force 3 experiments now cover envelope overrides and gradual
attack. Both pass independent DS reference checks, actual native PCM envelope
checks and controlled effects/lifecycle probes. On 2026-10-16 the user reported
no issues with the requested listening/gameplay sequence for both builds,
accepting their approximations in these configurations. The manager is
unchanged. The [v4 batch audit](nds-compatibility-audit.md) now includes these
bounded envelope routes, with four separate success categories. Its 32
packing passes include two new Star Force 2 candidates; the earlier 28-pass
v3 report is preserved as a historical snapshot.

## Semantics and bounded conversion

The pinned `ssr3b.nds` supplies SDAT file 187. The independent SSEQPlayer core
copies attack/decay/sustain/release from either a track override or the bank
definition when a note starts. Later D0/D1/D2/D3 commands affect new notes;
they do not rewrite an existing voice's envelope. The new singleton-only
`envelope_support` mode implements this with separate rhythm-bank voice
contexts keyed by source instrument, pan and effective ADSR. Wave data remains
shared. Same-tick ordering is retained through each source note's state
snapshot. Synthetic regressions exercise overlapping notes with different
release settings and all four changing overrides.

Overrides currently accept 0..127; other values fail explicitly. The default
converter continues to reject overrides/non-instant attacks. Merging multiple
source tracks into one target track is outside this envelope mode. Bank
capacity, alias collisions, unsupported effects and loop/gate checks remain
enforced. Existing note durations and sample tuning are retained.

DS attack uses exponential changes in signed attenuation at about 192 Hz.
Native GBA PCM attack adds an integer amplitude step once per audio frame.
The attack fitter enumerates steps 1..255, minimizing RMS amplitude error
against the DS attack-only curve at timer resolution, plus two GBA frames at
peak. It assumes both first updates at time zero; onset phase can differ by
one GBA frame. Fits above RMS 0.12 or maximum amplitude error 0.30 are rejected.
These are bounded research policy limits, not an established audibility test.

For DS attack 100, the fit chooses GBA step 74: RMS amplitude error 0.10193,
maximum error 0.28374, with 14 DS timer updates to peak. This is an explicit
approximation of the attack shape. Instant attack remains 255. Decay, sustain
and release keep the previous logarithmic-rate mapping and GBA quantization;
they have not received a new whole-envelope fit. PCM8 and voice-budget
differences also remain. Native mixer behavior was checked against actual
EXE6 execution; related MPlay definitions and update code are available in
[pret's structure definitions](https://github.com/pret/pokeemerald/blob/master/include/gba/m4a_internal.h)
and [PCM mixer](https://github.com/pret/pokeemerald/blob/master/src/m4a_1.s).

## Experiments

Both ROMs target Japanese EXE6 Gregar, retaining eight music tracks, ten PCM
voices at 10,512 Hz and +3.5 dB imported gain. Title, ordinary music 21 and
communication scenes select appended entry 474. The original 474 entries and
prefix data outside declared hook/configuration ranges remain preserved.
Exact BPS reconstruction passes. Neither input ROM is changed.

| Experiment | HOKORA | FRIEND |
| --- | --- | --- |
| CLI song | `sf3-hokora-envelope` | `sf3-friend-envelope` |
| Source SSEQ | 10 `BGM_HOKORA` | 29 `BGM_FRIEND` |
| Tracks / PCM samples | 8 / 18 | 8 / 23 |
| Voice contexts | 8 | 9 |
| Feature under test | Bank attack 100 | D3 release overrides 115/120 |
| Extra pitch approximation | None | Existing native triangle pitch LFO |
| Target loop start / period | 768 / 3072 ticks | 3888 / 2304 ticks |
| First compiled jump / period | About 34.4 / 27.6 seconds | About 54.0 / 20.1 seconds |
| ROM bytes | 8,674,164 | 8,720,084 |
| CRC32 | `8B4FB8DC` | `8734543F` |

Artifact directories are `out/nds-research/sf3-hokora-envelope-exe6-v1/` and
`out/nds-research/sf3-friend-envelope-exe6-v1/`. SHA-256 values:

- HOKORA: `259bfc06bb5693e7fdf612d1ddf5ad69f29b6e27adf84392842edf32b8fcbd16`.
- FRIEND: `278d142b5aa637d1f1506a4830c7129c3013e7cfb133a7f4945096b4e4b7ccda`.

FRIEND's release overrides occur at the track beginnings. Its pitch depth
changes occur after note-on while voices are held; note-on modulation depth
alone would miss them. The existing pitch-LFO mode preserves these controls
and now reports those active configurations too. Its shared phase/triangle
limits remain, so FRIEND does not isolate release fidelity from pitch
differences. The override-changing regressions provide the separate dynamic
snapshot test.

## Evidence and limits

The new reference renderer records effective PCM note-on ADSR before voice
allocation and allocated per-voice envelope state before/after each DS timer
update. Observation hooks do not change synthesis. Build inputs and hashes
are recorded under `out/nds-research/reference-player-envelope-v3/build.json`.
Each experiment retains its 180-second reference in `reference-v3/`.

| Check | HOKORA | FRIEND |
| --- | ---: | ---: |
| Independent source notes / ADSR snapshots | 5758 | 7561 |
| Exact decoded PCM16 samples | 18 | 23 |
| Independent DS envelope updates | 519793 | 477246 |
| DS non-instant attack updates | 19399 | 0 |
| Exact native GBA envelope steps | 13903 | 13102 |
| Native gradual-attack observations | 690 | 0 |
| Native release observations | 5405 | 5560 |

`runtime/reference-validation.json` includes source notes, controls, samples,
ADSR and per-voice envelope matches. Source notes cover at least two complete
loops per track. `envelope-window-v2/validation.json` records 1800 natural
audio-update snapshots, about 30 seconds, checking allocated PCM parameters
against mapped tones and the GBA envelope step model. It does not establish
complete loops or equal DS/GBA sound.

The native probe samples root MPlayMain entry at a consistent point before
sequence/mixer updates, using breakpoints without register/RAM changes.
Video-frame pauses can stop halfway through channel initialization: an early
FRIEND probe saw the new stage before its amplitude was initialized. Sampling
at the fixed audio point resolves this observation artifact; ROM bytes did
not change. The probe skips retriggered/stolen slots and newly changed stop
states rather than treating them as ordinary consecutive envelope updates.
Pseudo echo is outside its step model.

`runtime/runtime.json` passes controlled native effects 100/129, dispatch,
queued stop, native restoration and three restart/rematch cycles. Helpers
inject PC/LR/arguments; this is separate from actual battles and linked play.
`preview/preview.wav` captures 30 seconds of actual mGBA mix;
`comparison/listen.html` provides a normalized software-DS/GBA comparison.

All seven previously accepted ROMs rebuild byte-identically, including LAST.
Their hashes are in `out/nds-research/envelope-research-v1/accepted-rebuilds.json`.
All 164 Python regression tests pass, including attack fitting, same-tick and
overlapping envelope snapshots, invalid values, native stage boundaries and
both complete ROM exports with original-data preservation.
Each build's `manual-testing.json` records user-reported acceptance dated
2026-10-16 for sustained listening and loop joins, onset/release behavior,
chips/Buster coexistence, map restoration and next-encounter restart. Records
are tied to the exact ROM fingerprints above. No timed recording or complete
GBA loop execution trace was supplied; specific linked play/rematch was not
separately reported. `validation-summary.json` retains the automated coverage
limits separately from this manual evidence. The waveform/phase, envelope
shape and quantization limits remain; this acceptance does not establish
exact DS/GBA fidelity or general compatibility for all envelope parameters.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-hokora-envelope --event 1 --event 21 --event scene:communication \
  --out out/nds-envelope-example
python3 scripts/build_nds_reference.py --core /path/to/SSEQPlayer \
  --out out/nds-envelope-reference-example
mkdir out/nds-envelope-example/reference
out/nds-envelope-reference-example/nds-reference \
  out/nds-envelope-example/source.sdat 10 180 out/nds-envelope-example/reference
python3 scripts/validate_nds_experiment.py out/nds-envelope-example \
  --reference out/nds-envelope-example/reference --lifecycle \
  --out out/nds-envelope-example/runtime
python3 scripts/validate_nds_envelope.py out/nds-envelope-example \
  --out out/nds-envelope-example/envelope-window
```

Use `sf3-friend-envelope` and reference ID 29 for FRIEND. Output directories
must be new. Listen to each ROM in a battle for at least three minutes,
checking gradual note onsets, release tails, loop joins, chips/Buster
coexistence, native map music restoration and restarting on the next battle.
Use a battle for complete loops, since the title eventually changes scenes.
