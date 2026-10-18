# WIN2: opt-in offline antialiasing experiment

The user reported a clear improvement with the ten-channel offline-filtered
[diagnostic control](nds-sf1-win2-tail-diagnosis.md) on 2026-10-18. That feedback
covers its listening comparison. It does not accept the original unfiltered
WIN2 or this subsequent build, which has different samples and loop treatment.

The new standalone ROM/BPS is in
`out/nds-research/sf1-win2-antialias-exe6-v2/`. It uses Japanese EXE6 Gregar,
appended song 474, title, ordinary virus battle 21 and communication music.
On 2026-10-18 the user reported “没问题” after the requested ending/timbre/
descending-pitch listening, ten-second silence, chips/Buster coexistence, native
map music restoration and at least two additional encounter starts. This
records user-reported acceptance of this exact v2 ROM. No timed recording or
personal execution trace was supplied; linked play/rematch was not separately
reported.

ROM: 8,633,532 bytes, CRC32 `3799C733`, SHA256
`e253a270d7b9b65b0217218c56a90c676c0f48b38ebcb6a2c20afa24a56a0079`.
It is 95,120 bytes (about 93 KiB) larger than the unfiltered WIN2, since the
converter stores the prepared waves directly rather than appending them to
an already packed diagnostic image. The original 474 entries and undeclared
prefix bytes are preserved; BPS reconstruction passes.

## Bounded implementation

`scripts/nds_resample.py` uses Python stdlib, with no ffmpeg requirement for
conversion. The explicit CLI choice `sf1-win2-antialias` enables
`bandlimited_pcm=True` in the finite singleton converter. The default remains
off; it is not a production manager option or an automatic batch-audit route.

The source remains SSEQ 31 `BGM31WIN2`, 67 note events, six tracks, six tone
contexts and nine source PCM waves. Samples are cached by source archive,
wave, root and played key: 32 prepared PCM8 waves serve the 67 notes.
Gates, velocity, track controls, tone pan, note-on ADSR and individual END
positions remain unchanged (156/168/192 ticks). Gain stays +3.5 dB. The native
engine remains ten PCM channels at 10,512 Hz.

Each key gets a Blackman-windowed sinc low-pass resample: 32 lobes, 256
fractional phases, unity DC, cutoff 90% of the smaller input/output Nyquist.
There is no per-wave loudness normalization. PCM8 output is clamped; this
build records 156 clamped quantizer values out of 228,828 samples (0.0682%).
That includes rounding near PCM8 full scale and potential FIR overshoot;
it is separate from clipping of the captured full mix. The native preview
peak is 9,738, below full scale.

Looped waves use an integer output period. A short prefix guard lets the
filter settle into the periodic input before the stored loop begins; the
stored loop therefore has consistent filter history across its join. Native
frequency compensates for rounding the loop period, rather than allowing
the loop period to drift. Reported stored-frequency rounding error is below
0.000253 cents; this is not a measurement of the complete engine's audible
tuning. One-shot waves use zero extension and retain the FIR tail. Initial
looped-wave source phase can shift by at most half an output-sample step.

The route requires finite singleton tracks and currently rejects upward
bends, transposition, pitch modulation and portamento, including live changes
between note-ons. WIN2's downward bends are preserved; filtering remains
conservative as they lower playback pitch. Prepared rates, filter widths,
guard lengths, period lengths and tuning are recorded in each sample's
`resampling` report. Limits are 1,000,000 samples per prepared wave and
4,000,000 PCM bytes per song, with an explicit bounded rate ratio.

This reduces aliasing while retaining PCM8, restricted bandwidth, native
pan/volume/envelope and voice-allocation differences. Loop-period rounding,
filter phase quantization and the changed high-frequency balance are still
approximations. No real-time CPU benchmark or hardware test is claimed.

## Validation and listening

- DSP regressions check suppression of a tone above output Nyquist while
  preserving a low tone's gain, an analytic periodic sine through the loop
  join, constant-loop DC, one-shot tail behavior and invalid/resource limits.
- Converter regressions check per-key cache reuse, live bend bounds, all 67
  note gates, native loop/sample metadata, BPS and original-data preservation.
- Independent DS software reference matches all 67 notes, 26 source controls
  and nine unique PCM16 source decodings. The source rendering is reused from
  the identical verified SDAT; these original-PCM checks do not establish
  filtered-output waveform equivalence.
- Natural playback checks all six track states through all FINEs: 86 frames,
  clock 194, all 32 prepared waves observed, changing native PCM verified.
- The natural-stop probe follows 960 sound updates, clock-stable and inactive
  after completion, with 845 quiet updates and no imported channels in the
  final 600 updates. No CPU/RAM edits or synthetic sequence are used.
- Controlled probes pass effects 100/129, native music restoration, stop,
  ordinary/communication dispatch and three restart cycles. They inject
  helper-call CPU state and do not substitute for actual gameplay.
- `validation-summary.json` records the regression log and old-ROM rebuilds.
  All 229 regression tests pass; all 22 accepted ROM/BPS variants plus the
  old unaccepted WIN2 rebuild identically. The archived v10 scan remains unchanged; its WIN2 fingerprint is the older,
  unfiltered variant and must not be reassigned to this one.

`comparison/listen.html` compares the DS software reference and this build.
Listen to the roughly 1.4-second score and its release tails, especially dense
ending notes, possible sample-loop seams and the descending pitch effect.
After it finishes, wait ten seconds for silence; use chips/Buster during
and after playback, return to the map, then start at least two more encounters.
`manual-testing.json` records user-reported acceptance of this exact ROM
on 2026-10-18, separately from the automatic evidence and earlier diagnostic
listening feedback. The original unfiltered WIN2 remains unaccepted.

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-win2-antialias --event 1 --event 21 --event scene:communication \
  --out out/nds-sf1-win2-antialias-example
```

Use a fresh directory. Reference, natural playback, lifecycle and comparison
commands follow the first WIN2 experiment, using the new output directory.
