# Star Force 3 HOKORA: filtered PCM with fitted attack envelopes

The candidate is `out/nds-research/sf3-hokora-antialias-envelope-exe6-v1/`.
On 2026-10-19 the user reported “测试没有问题”, accepting this exact
combined-mode ROM after the requested listening/gameplay checklist. This implements the bounded
combination proposed in [audit v12](nds-antialias-compatibility-audit-v12.md),
using the [accepted unfiltered HOKORA envelope version](nds-envelope-research.md)
as the baseline. It is a separate opt-in research build, outside the production
manager and the archived audit's plain filtered route.

## Combination and invariants

The compiler now accepts `bandlimited_pcm=True` together with
`envelope_support=True` for looping singleton tracks. Both options must be
explicitly selected; neither defaults nor existing song choices change.
Native LFO, merged groups, upward bend, transpose, active modulation and
portamento remain excluded from filtered PCM. Finite-plus-envelope conversion
remains excluded. Poor attack fits still fail the existing error thresholds.

No DSP, resampler, native mixer or envelope-fitting algorithm changes are
needed. Prepared PCM is identified by source archive/wave, root key and played
source key. Envelopes do not change that waveform, so different ADSR snapshots
can share its sample data. Native instrument contexts separately retain the
source instrument and effective note-on ADSR. Distinct roots get distinct
tuning/cache entries; long-note aliases still prepare at the original pitch.
Synthetic tests check these properties, live snapshot differences, long gates
and the remaining guards. The combined report explicitly records fitted
attack envelopes as well as per-key filtering.

Japanese `ssr3b.nds`, pinned SDAT file 187, SSEQ 10 `BGM_HOKORA` retains all
eight tracks. Sixteen unique original waves produce eighteen unfiltered
root-dependent samples in the old version and 48 per-key samples in this
candidate. The source SDAT is byte-identical to the accepted baseline, whose
180-second independent DS software reference is reused without modification.

All 1,064 compiled note mappings, source envelope snapshots, target schedules,
attack fits, tempo, priorities and +3.5 dB gain match the old accepted version.
DS attack 100 still fits native attack 74; instant attack 127 remains 255.
The waveform filter and compensated playback tuning are the added preparation
step. The mixer remains ten PCM channels at 10,512 Hz.

## Output and checks

The ROM is 8,708,124 bytes, CRC32 `57434B31`, SHA-256
`d03562660152f75008fbee878be12709efb62513fc89b89dfcb709b6e983a9fc`.
BPS SHA-256 is
`9425dedbde7d462b0ee07a78e70389f038c28d14dad5db294b02c841365237d9`.
BPS reconstruction is verified. It adds 33,960 bytes (about 33.2 KiB) versus
the accepted unfiltered envelope ROM. Prepared PCM totals 291,162 bytes;
maximum source step is about 7.68119 and stored tuning error stays below
0.001 cent. The 1,330 PCM8 clamped values include full-scale quantization and
FIR overshoot rather than measuring full-mix clipping.

- Independent source checks match 5,758 notes, 1,414 pan/bend/expression/delay
  controls and sixteen exact original decoded PCM16 arrays. Envelope checks
  match 5,758 note-on snapshots and 519,793 per-voice timer updates, including
  19,399 non-instant attack updates. This validates source interpretation,
  not equality of the filtered waveform to the source.
- Actual packed ROM tones are checked for every mapped note: all 48 used
  voice/key slots retain the expected ADSR, source-key pitch and instrument
  pan, and point to exactly the intended prepared waveform bytes. See
  `packed-tone-validation.json`. This complements the per-wave header/loop/
  tuning checks in `prepared-wave-validation.json`.
- Natural title playback without register injection checks one complete
  generated loop: 2,059 frames, final clock 3842, all eight track states
  checked and all 48 prepared samples observed.
- The separate 1,800-frame natural envelope window checks 13,937 exact native
  envelope steps and observes 690 gradual-attack states and 5,409 release
  states. It covers the fitted attack class in the first approximately thirty
  seconds, not every envelope instance throughout the full song. Its final
  clock is 3357, before the first GOTO; full loop coverage belongs to the
  separate track-state validation above.
- Controlled effects 100/129 preserve advancing music. Ordinary battle and
  synthetic communication dispatch, queued stop, native restoration and
  three restart cycles pass. Injected helper calls do not establish actual
  linked play or results-screen/map transitions.

The common loop starts at tick 768 with a 3072-tick period. Native tempo
parameter 140 gives about 111.491 ticks/second. First GOTO is at tick 3840,
about 34.44 seconds, then every 27.55 seconds: roughly 34, 62, 90, 117, 145
and 172 seconds. Two TIE/EOT aliases carry 287–383-tick notes; no note carries
across GOTO. The last long note ends at tick 3839, one tick before the jump.
Static note/gate validation checks two periods; native original-song coverage
remains one complete loop.

The DS renderer reaches sixteen voices in coarse observations, while the
native mixer permits ten. Matching schedules, fitted parameters and allocated
envelope steps does not establish identical audible polyphony or DS timbre.
The fitted attack retains its existing approximation and onset-phase limits.

All 252 regression tests pass. All thirty previously accepted ROM/BPS pairs
and two unaccepted WIN2 controls rebuild byte-identically. See
`regression-tests.txt` and `prior-regressions.json`.

## Listening and manual acceptance

`comparison/listen.html` embeds thirty-second source, accepted unfiltered
envelope and new filtered-envelope clips, normalized by whole-clip loudness.
The two GBA versions share source mappings and fit parameters. Neither clip
reaches the first GOTO. The DS reference is software synthesis, not hardware
output; normalization masks raw loudness differences.

Test the exact new ROM in a virus or communication battle for at least three
minutes. Listen for gradual onsets, high-note balance and long-note releases,
especially joins around 34, 62 and 90 seconds. Use chips and the Buster, finish
the battle and verify map music resumes, then start at least two additional
encounters and verify playback starts from the beginning. `manual-testing.json`
records the user-reported pass for this exact combined-mode ROM. No timed
recording or personal execution trace was supplied; linked play/rematch was
not separately reported. Automated native track coverage remains one complete
loop, and per-step envelope coverage remains the first 1,800 frames. No
comparative listening preference is inferred.

Reproduce into a new output directory:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song sf3-hokora-antialias-envelope \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-hokora-antialias-envelope-exe6-v1
```

The archived v12 JSON/CSV/HTML remain unchanged. Their filtered attempts do
not request envelope fitting; this standalone combination does not silently
reclassify those rows or infer any new manual acceptance.
