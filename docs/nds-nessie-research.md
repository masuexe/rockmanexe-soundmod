# Star Force 2 NESSIE: slower attack with native pitch LFO

This experiment validates the next combined-envelope/LFO candidate identified
by the [v4 batch audit](nds-compatibility-audit.md). Its independent DS
reference, bounded native envelope/LFO windows and controlled lifecycle checks
pass. The user reports no issues with the requested listening/gameplay
sequence, accepting this approximation in the tested configuration.
Instrumented full-loop GBA execution remains a separate uncompleted check.

Artifact: `out/nds-research/sf2-nessie-envelope-exe6-v1/`.

## Conversion and artifact

The pinned Japanese `ssr2d.nds` supplies SDAT file 975, SSEQ 15 `BGM_NESSIE`
(file 14), bank 60, source player 0, volume 73 and tempo 125. The research
builder exposes it as `--song sf2-nessie-envelope`, using eight singleton
tracks, 29 original PCM samples and 18 note-on envelope voice contexts.
The generated MPlay resource is 497,824 bytes. Long gates of 264/312 ticks use
a TIE/EOT alias retaining source pitch 87. There is no added gate reattack.

DS attack 90/100/127 maps to GBA attack 66/74/255 under the bounded
[envelope fitting policy](nds-envelope-research.md). Attack 90 reaches peak
in 16 DS timer updates, about 83 ms; its attack-only fit has RMS amplitude
error 0.09575 and maximum error 0.25415 under the stated update alignment.
Its first source note appears at tick 3000, roughly 30 seconds into playback.
The experiment retains the onset-phase, curve-shape, decay/release and PCM8
approximation limits documented with that policy.

Source track 5 uses pitch depth 20, speed 20, range 1 and zero delay. Native
LFOS 19/MOD 2 approximates this with a shared triangle wave. Waveform,
overlapping-note phase resets and release-tail phase differ from DS; this
remains an explicit approximation. No claim of equal DS/GBA synthesis is made.

The compiled loop begins at tick 8496 and repeats every 4608 ticks, after the
existing native-LFO warmup. At target tempo parameter 126, the first compiled
jump is approximately 131 seconds after playback begins; subsequent jumps
are approximately 177 and 223 seconds. The warmup unrolls existing music;
it does not add silence. Use a battle for four minutes to cross these jumps.

The target is original Japanese EXE6 Gregar, eight music tracks and ten PCM
voices at 10,512 Hz, with +3.5 dB imported gain. Title, ordinary music 21 and
communication events select appended entry 474. All 474 original entries
and prefix bytes outside declared hook/configuration ranges are preserved.
The ROM matches the existing batch-generated ROM fingerprint exactly:

- Size: 8,890,324 bytes; CRC32 `99CE77C6`.
- SHA-256: `ae340116b5906d93652491cc76ebdc5c913f313a374086c0fecef1685af440e5`.
- `unified.bps` reconstructs `unified.gba` exactly from original Gregar.

## Automated evidence

- `runtime/reference-validation.json`: 180-second independent software DS
  reference matches 3,802 notes and note-on ADSR snapshots, all 29 decoded
  PCM16 samples, 1,366 pan/bend/expression events, 31,221 pitch-modulation
  observations and 487,971 allocated-voice envelope timer updates. Of those
  envelope updates, 8,144 use non-instant attack. Notes cover at least two
  complete source loops per track. The renderer and source provenance are
  the same as the envelope experiments; reference output is in `reference/`.
- `envelope-window/validation.json`: 1,800 natural audio-update snapshots,
  sampled at root MPlayMain entry, with 13,758 exact native PCM envelope step
  comparisons and 5,155 release observations. Attack stages include 450
  observations at GBA step 74 and three at step 66, confirming that the newly
  slower attack is actually allocated. This is a bounded window, not a full
  GBA loop trace.
- `lfo-window/validation.json`: 2,400 natural video frames, final music clock
  4031, match all eight note/track states and the native pitch-LFO model.
  Active target track 5 is verified. The validator now derives active tracks
  from the bounded model rather than assuming the first SF1 experiment's
  three-track set; diagnostic reference comparison uses those actual tracks.
- `lfo-window/modulation-comparison.json`: 1,932 sequence-clock comparisons
  to allocated DS voices show RMS pitch difference 11.98 cents and maximum
  26.56 cents. This is a diagnostic alignment, not waveform/sample alignment
  or equal voice allocation.
- `runtime/runtime.json`: controlled native effects 100/129, ordinary and
  synthetic communication dispatch, queued stop, native music restoration
  and three restart/rematch cycles pass. These helpers inject debugger
  registers and do not establish actual battles, linked play or map changes.
- `preview/preview.wav` and `comparison/listen.html`: 30-second actual mGBA
  mix and normalized software-DS/GBA comparison. The clip only reaches the
  beginning of the slower-attack passage and does not cover compiled jumps.

All 169 Python regression tests pass, including NESSIE export/native-data
preservation and reference comparisons for a variable set of active LFO tracks.
`validation-summary.json` collects these evidence levels. `manual-testing.json`
records user-reported acceptance for this exact ROM: sustained battle listening,
slower onsets, held-note pitch/release tails, loop joins, chips/Buster
coexistence, native map music restoration and restarting on the next encounter.
No timed recording or full-loop execution trace was supplied; specific linked
play/rematch was not separately reported. Automated bounded-coverage limits
and the documented approximation differences remain. Manager integration is
unchanged.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-nessie-envelope --event 1 --event 21 --event scene:communication \
  --out out/nds-nessie-example
mkdir out/nds-nessie-example/reference
out/nds-research/reference-player-envelope-v3/nds-reference \
  out/nds-nessie-example/source.sdat 15 180 out/nds-nessie-example/reference
python3 scripts/validate_nds_experiment.py out/nds-nessie-example \
  --reference out/nds-nessie-example/reference --lifecycle \
  --out out/nds-nessie-example/runtime
python3 scripts/validate_nds_envelope.py out/nds-nessie-example \
  --out out/nds-nessie-example/envelope-window
python3 scripts/validate_nds_lfo.py out/nds-nessie-example --frames 2400 \
  --reference out/nds-nessie-example/reference --out out/nds-nessie-example/lfo-window
```

Output directories must be new. In a virus or communication battle, listen
for four minutes, checking soft note onsets from about 30 seconds, held-note
pitch, release tails and joins around 131/177/223 seconds. Use chips and the
Buster, finish the battle, confirm native map music returns, then start a new
battle and confirm NESSIE restarts. The title changes scenes too early for a
complete loop check.
