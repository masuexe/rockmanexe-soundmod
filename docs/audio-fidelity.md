# Audio fidelity diagnosis

A structurally correct transplant can sound different from the original game. The same song data runs through the target audio driver and its mixer configuration. The manager's **Play now** uses agbplay's enhanced source-ROM mixer; it is not a recording of the exported game. Compare both ROMs through mGBA before attributing a difference to transplantation.

## EXE1 opening drum correction

The reported noisy percussion is in `exe1:0`. This track was not included in the initial three-song comparison. Its fixed-step PCM drums exposed a specific error that sequence and encoded-wave equality checks did not detect: type-8 PCM consumes one sample byte per mixer output sample, ignoring the wave-header frequency for its stepping. EXE1 mixes 176 samples per VBlank; GP mixes 264. Copying the same fixed-step drum data into GP plays it 1.5 times faster and shortens its duration.

Actual mGBA cursors establish the difference. At music clocks 100–104, the original drum advances through byte positions 704, 880, 1056, 1232 and 1408. The uncorrected GP copy advances through 1056, 1320, 1584, 1848 and 2112. Ordinary PCM notes in the same run advance at nearly identical source positions. The PSG/control registers also match at the drum snapshots. This identifies a fixed-step PCM rate issue independently of channel-budget differences.

The shared exporter now creates private, rate-adapted copies of fixed-step PCM waves when the fingerprint-pinned donor rate differs from the target rate. EXE1 JP and EXE4 Red Sun JP profiles supply their verified 10,512 Hz rate; verified target layouts supply their effective rates. Other donor rates are not guessed from sample headers.

Signed 8-bit linear interpolation adapts the copied wave to the target's fixed-step rate. Type 8 is retained so notes still ignore key, bend and modulation as in the original driver. Clearing the fixed-mode flag would change that behavior in EXE1 tracks that use modulation. Normal PCM instruments sharing the original sample keep a separate original copy. Adapted copies are deduplicated across songs, and their rate, offsets, sizes and hashes are recorded in each import's `audio_adjustments`. Pointer provenance records the final adapted pointer. Export validation reparses each song and checks both original and declared adapted PCM contents.

One-shot duration error is less than one target sample. Looped waves retain an exact repeat period by repeating enough source loop cycles to form an integer target period, with interpolation across the loop seam. For `exe1:22`, the original 34,191-sample loop becomes a two-cycle 102,573-sample target loop: both represent exactly the same duration at their respective rates. This avoids cumulative loop-period drift.

Validation evidence:

- `out/fidelity-research/exe1-0-baseline/` records the uncorrected source/GP pair. `exe1-0-fixed/` records the corrected GP copy and includes a single-track test ROM/BPS.
- `out/fidelity-research/exe1-0-listen.html` embeds the original, old GP and corrected GP recordings with RMS normalization. It is portable and opens without adjacent WAV files.
- `probes/exe1-0-cursors/` records the accelerated old cursors. `probes/exe1-0-fixed/` reaches clock 256 with both runs passing 1,626 track-state checks. Corrected drum positions map exactly to the original positions at clocks 100–104 and 256; the previously shortened kick is still active at clock 256.
- All twenty currently importable EXE1 songs export together successfully in `exe1-all-selected/`. Its 44 fixed-tone adjustments share the adapted waves safely, its pointer manifest matches the final ROM, and its BPS reconstructs the output.
- `probes/exe1-22-fixed-loop/` runs source and target for 1,280 frames through clock 1024, crossing the adapted loop repeatedly. Both sequence probes pass; mapped cursor error at clocks 512 and 1024 is one-third of an original sample.
- 79 Python tests pass, including signed interpolation, duration bounds, exact loop periods, shared fixed/normal waves, cross-import deduplication, pointer provenance and unknown-rate guardrails. Existing EXE4.5 JP/English output regressions pass.
- The manager was reloaded, its six selected sources and existing pools restored, and a corrected GP ROM/BPS exported through the HTTP workflow. `out/fidelity-research/manager-fixed-export.json` records that export. Original ROM files were not edited.

The correction preserves the normal GP mixer settings and adapts imported data. The source-rate mixer experiment restores the original fixed-wave pointers when it changes the target to the source rate, preventing double adaptation. Linear interpolation is not a claim of bit-identical hardware output; residual balance, reverb, polyphony and filtering differences can remain. The new listening comparison is intended to verify the reported opening noise specifically.

## EXE4 Red Sun correction

`exe4:0` from the fingerprint-pinned Japanese Red Sun ROM has the same fixed-step rate mismatch. Its three fixed PCM drum records run at the original 10,512 Hz mixer rate, while GP runs at 15,768 Hz. mGBA observes source positions 704, 880, 1056, 1232 and 1408 at clocks 16–20; the unadapted GP positions are 1056, 1320, 1584, 1848 and 2112. Thus the drum samples play 1.5 times faster even though encoded note timing is correct.

An isolated trial first enabled the existing adapter for this donor fingerprint, using its measured runtime rate. The verified rate is now enabled in the production donor profile, so normal manager exports automatically apply the same correction. Source, old GP and corrected GP each pass 924 sequence-model comparisons over 132 frames to clock 128. Seven common fixed-PCM cursor pairs in the corrected run map exactly to the source positions. Its three drum adjustments preserve fixed mode and the BPS reconstructs the ROM.

All 34 currently importable EXE4 tracks use fixed PCM. They export together successfully with 87 fixed-tone adjustments and consistent final pointer provenance. Production output matches the validated trial byte-for-byte. The correction reuses the shared adapter and benefits the whole eligible source catalog.

Other differences remain separate. The original uses a four-channel PCM budget and master volume 12, compared with GP's ten-channel budget and volume 15. Reverb is 40 in both. Within this short window, maximum active PCM voices are four in the original, six in the old GP export and seven in the corrected trial. Preserving drum durations can retain more overlapping voices under GP's larger budget. Rate correction therefore addresses a specific pitch/duration error; it does not establish identical overall balance or voice allocation.

Evidence and review artifacts:

- `out/fidelity-research/exe4-0-assessment.json`: measured configurations, cursor comparisons and validation summary.
- `exe4-0-baseline/` and `exe4-0-trial/`: original/old/corrected recordings and single-track GP trial ROM/BPS. Apply the trial BPS to original `exegp.gba`.
- `exe4-0-listen.html`: portable original/old/trial listening comparison, with eight-second RMS-normalized clips.
- `exe4-all-trial/`: mixed-pool export and BPS/pointer validation for all 34 eligible tracks.
- `exe4-enabled/`: production single-track, all-EXE4 and mixed EXE1/EXE4/native-GP builds, plus `validation.json` and the 80-test regression result. Single/all-EXE4 images match the corresponding trial images byte-for-byte. `manager-export.json` records the HTTP export after restoring the user's existing source selection and pools; both EXE1 and EXE4 adjustments appear in that export and its BPS reconstruction passes.

The manager enables automatic fixed-PCM adaptation for this exact EXE4 Red Sun JP revision. Other EXE4/BN4 editions require their own verified donor rate. The original EXE4 ROM fingerprint is CRC32 `CF0E8B05`, SHA-256 `1904692bc383fc2cb7e1d81e1c80bf2d8c616c0d1b1d396c689f71b49a2e3188`.

## First GP comparison

Local evidence lives under `out/fidelity-research/`. The portable `listen.html` embeds all twelve normalized WAVs, so it can be opened directly without a server or adjacent audio files. It compares three representative songs, each with four recordings: original ROM, current GP export, source rate/volume with GP's ten-channel budget, and source rate/volume/channel budget. Every clip is ten seconds, stereo 44.1 kHz, captured from the same mGBA SDL mix including PSG. The internal driver mixing rate is distinct from this output rate.

| Original track | Original PCM budget | Original internal rate | Original master volume | Song reverb | Current GP budget / rate / volume |
| --- | --- | --- | --- | --- | --- |
| EXE1 `exe1:2` | 4 | 10,512 | 13 | 35 | 10 / 15,768 / 15 |
| BN2 `bn2:0` | 4 | 10,512 | 13 | 35 | 10 / 15,768 / 15 |
| EXE6 `exe6:1` | 4 | 10,512 | 15 | 50 | 10 / 15,768 / 15 |

These are measured runtime SoundInfo values, not guesses from a startup literal. Song-header reverb is applied correctly in each target run. The original and target runs use private copies without personal saves. The original audio ID is selected at the first naturally reached music call; the target starts naturally through a single-track title pool. Neither suppresses scene changes. Source captures therefore contain a controlled ID injection; they are not unmodified gameplay recordings.

Whole-clip RMS is normalized to -20 dBFS with 5% peak headroom. The actual gain and achieved RMS are recorded in each `comparison.json`. Clips are approximately aligned, not sample-aligned. A lag-aligned, band-limited waveform experiment is also retained locally, but its correlation is not a perceptual fidelity score: oscillator phase, buffering and internal resampling affect it. No subjective listening result is claimed by the automated checks.

## Sequence and synthesis evidence

`scripts/probe_fidelity.py` checks every frame through music clock 256 against the conservative sequence model, then saves track and PCM-channel states at clocks 64, 128 and 256. It records PSG/control registers as well. Each source and target reaches the same music clock in the same number of frames:

| Track | Frames per run | Track-state model comparisons per run | Maximum active source PCM channels | Maximum active current GP PCM channels |
| --- | --- | --- | --- | --- |
| `exe1:2` | 296 | 1,480 | 2 | 2 |
| `bn2:0` | 275 | 2,200 | 4 | 5 |
| `exe6:1` | 263 | 1,841 | 4 | 8 |

All these short probes pass cursor, wait, pattern nesting, note key/velocity, running command, completion and relocated tone checks. Source and target PCM sample hashes match for common notes; no channel uses a sample outside the analyzed dependency closure. EXE1 has three PSG instruments, so increasing PCM capacity alone cannot explain its whole sound. Its source-matched run has identical PSG/control registers at the three snapshot clocks (excluding live FIFO data), although some drum-related calculated track state and PCM volume rounding still differ.

EXE6 demonstrates an actual voice-allocation difference: the ten-channel GP mixer retains overlapping/release voices that the four-channel original cannot retain. With the research variant restoring four channels, its measured maximum falls back to four while the sequence checks continue to pass. More channels can therefore change the arrangement heard even when all encoded notes and samples are correct. BN2 similarly rises from four to five active channels in this window.

This establishes mixer configuration and voice allocation as concrete compatibility issues. It does not establish that they explain every reported difference, nor does a short probe validate a complete song, all instruments, or all game scenes. The current evidence does not justify rewriting or replacing GP's entire audio driver.

## Reproduce

Requires the same Linux/mGBA/SDL capture dependencies as the manager's recorded preview. No extra Python packages are required. Run from the project root; choose new output directories for new recordings.

```bash
python3 scripts/compare_fidelity.py --seconds 10 \
  --out out/fidelity-research/baseline

python3 scripts/compare_fidelity.py --seconds 10 \
  --baseline out/fidelity-research/baseline \
  --mixer-experiment source-rate-volume \
  --out out/fidelity-research/source-rate-volume

python3 scripts/compare_fidelity.py --seconds 10 \
  --baseline out/fidelity-research/baseline \
  --mixer-experiment source-all \
  --out out/fidelity-research/source-all

python3 scripts/compare_fidelity.py \
  --listen-run out/fidelity-research/baseline \
  --listen-run out/fidelity-research/source-rate-volume \
  --listen-run out/fidelity-research/source-all \
  --listen-out out/fidelity-research/listen.html
```

The default tracks are `exe1:2`, `bn2:0`, and `exe6:1`; repeat `--track KEY` to choose alternatives. `--roms` defaults to the shared `../roms` directory. Reused source captures must match the original fingerprint, source track and requested duration. Source driver discovery is deliberately limited to recognized stock start-by-ID instruction/literal layouts, verified here for EXE1, BN2 and EXE6; unsupported layouts fail instead of guessing. This does not add those games as patch targets.

For a state comparison:

```bash
python3 scripts/probe_fidelity.py \
  --source ../roms/exe6.gba --key exe6:1 \
  --target-rom out/fidelity-research/baseline/exe6-1/unified.gba \
  --manifest out/fidelity-research/baseline/exe6-1/build.json \
  --out out/fidelity-research/probes/exe6-baseline
```

Repeat `--clock N` to select other positive music clocks. This is a bounded sequence/synthesis probe, not full-loop validation. If a normal game transition replaces or restarts the song, the probe reports an interruption instead of redirecting playback.

## Scope of the experimental settings

The two mixer variants change only the target's declared startup SoundMode literal and update the experimental build fingerprint. They retain the original target driver's DAC configuration and song-header reverb. They do not change the production builder, manager defaults, saved projects or original ROMs, and they do not export BPS patches.

Startup SoundMode is global: copying one donor's settings also changes GP's native music and sound effects. It cannot faithfully accommodate a pool containing several different donor configurations by itself. The fixed-step PCM correction above uses private adapted waves instead. A broader production fidelity option should distinguish original voice allocation from expanded polyphony, and explicitly handle native playback and the effects of mixer changes during song transitions. Listening to source-matched variants remains useful before choosing that broader policy.

## Reverse-engineering reuse

The source driver offsets, fingerprints, runtime mixer values, register snapshots, per-track state and sample hashes are reusable evidence for `../rockmanexe-reverse`. Reports include register-injection provenance and distinguish original settings from experimental target modifications. The sibling project has not been edited.

The three source start/core/player-table locations were recognized structurally and then exercised in mGBA:

| Source | Start-by-ID | Player initialization core | Player table |
| --- | --- | --- | --- |
| EXE1 JP | `0x0809C914` | `0x0809CF90` | `0x080A0D7C` |
| BN2 EN | `0x080E71C0` | `0x080E78F4` | `0x080F3718` |
| EXE6 Gregar JP | `0x0815B338` | `0x0815BB18` | `0x08164C8C` |
| EXE4 Red Sun JP | `0x081126B4` | `0x08112DE8` | `0x08155CE4` |
