# WIN2 ending: bounded fidelity diagnosis

On 2026-10-18 the user reported that the ending of the Star Force 1 WIN2
experiment sounds mixed together and substantially different from the original.
The [first build](nds-sf1-win2-research.md) is recorded as
`user_reported_fidelity_issue`, not manually accepted. Its successful functional
checks remain valid; they did not establish sound fidelity.

Artifacts: `out/nds-research/sf1-win2-tail-diagnosis-v1/`.
`diagnosis.json` records measurements, exact fingerprints and limits;
`comparison/listen.html` is a portable, normalized six-second comparison.
The original test ROM and archived v10 scan are unchanged. This investigation
changes no shared converter, engine or manager code.

## Findings

| Internal control | Peak native channels | Missing held-note interior frames | Last channel update |
| --- | ---: | ---: | ---: |
| Baseline: original samples, ten channels | 10 | 0 | 114 |
| Same conversion, twelve channels | 12 | 0 | 114 |
| Ten channels, release multiplier zero | 9 | 0 | 85 |
| Ten channels, offline bandlimited per-key samples | 10 | 0 | 114 |

The natural channel probes observe 180 root sound callbacks, with no CPU/RAM
injection. They inspect active PCM channels, including release tails after
FINE unlinks the owner. Expected held notes are compared only inside their
gates, with a three-tick margin on both sides. No missing held-note interiors
are observed in any variant. This does not rule out changes between sampled
updates, boundary effects or truncation of release voices.

The twelve-channel variant mainly retains additional release tails. This
weakens the claim that missing sustained notes from the ten-channel budget
are the principal cause. It does not prove equal allocation or inaudibility
of the extra tails. Removing all release tails frees channels and shortens
the ending, but also changes the original arrangement; it is an ablation,
not a proposed release-envelope fix. Inspection found no wrong ADSR bytes
or sequence END times in the baseline.

There is also a concrete bandwidth mismatch. The late high line uses source
instrument 56, wave 13, root key 69, effective sample rate 32,040.14 Hz.
Key 83 plays those samples at approximately 71,928 Hz. The current converter
quantizes the original samples to PCM8 and the native mixer resamples them
at 10,512 Hz, without an offline pitch-dependent antialiasing filter.
A high playback rate alone does not prove audible aliasing; actual bandwidth
also matters.

`analyze-spectrum.py` checks isolated source notes using nearest-neighbor
PCM16 synthesis at the reference renderer's 44.1 kHz output rate and a
2048-point Hann FFT over 20–66.44 ms of each note. About 19.1% / 19.9% of
power for keys 81 / 83 lies above the native 5,256 Hz Nyquist limit.
Keys 78 / 80 yield 6.8% / 6.4%. This is an isolated, unenveloped-note bandwidth
measurement, not a whole-mix alias-energy percentage or perceptual score.
It makes resampling artifacts a credible additional contributor. It does
not establish a single cause of the user's listening impression.

## Offline control and cost

`build-bandlimited.py` creates 32 per-key PCM8 waves from the original decoded
PCM16 samples, using ffmpeg's offline resampler (`filter_size=64`, cutoff 0.90).
Each is pre-pitched to 10,512 Hz and tuned to play at that rate in the existing
engine. The control keeps the same ten native channels, mixing rate, note
commands, gates, pan, gain and tone ADSR. Byte/state checks confirm those
invariants; natural playback matches all six decoded tracks through clock
194 and observes all 32 new waves.

The diagnostic ROM grows by 228,204 bytes (about 223 KiB), to 8,766,616 bytes.
It adds no mixing channels or higher real-time sample rate. CPU performance
has not been benchmarked, and no gameplay/lifecycle acceptance is claimed.
Original converted waves remain in this diagnostic image; a supported
converter could omit unused copies.

The control has rounded input rates/loop positions and resampler edge
filtering that is not yet periodic across loop boundaries. It retains native
PCM8, phase/tuning, pan/volume, envelope and allocation differences. It is
not a release candidate. The user reported a clear improvement over the
baseline on 2026-10-18, limited to this listening comparison. This supports
continuing the offline approach without establishing full fidelity or gameplay
acceptance. The subsequent [buildable antialias experiment](nds-sf1-win2-antialias-research.md)
adds periodic loop treatment and retains ten native channels. Compare DS,
baseline and bandlimited versions before deciding whether the audible benefit
justifies turning this into a supported conversion route. Twelve-channel and
zero-release controls are available under the page's internal-controls foldout.

## Recommendation and reproduction

A bounded offline sample-resampling improvement is worth evaluating before
expanding or rewriting the real-time mixer. If the control substantially
improves the ending, implement periodic loop treatment and bounded per-key
sample caching, then perform normal regression, lifecycle and manual tests.
If the listening improvement is small, keep WIN2 outside the accepted set
and avoid a large engine investment for this cue.

From the project root, scripts in the artifact directory reproduce the
controls, channel probes, bandwidth measurements and listening page. Their
output directories must be fresh. `build-controls.py` creates `native12`
and `no-release10`; `build-bandlimited.py` creates `bandlimited10`.
`probe-channels.py LABEL` accepts those labels and `baseline`.
Use `render_preview.py` to capture each control for six seconds before
`make-listening-page.py`; `summarize.py` checks invariants and assembles the
report after `validate_song.py` checks the bandlimited control. The captured
ffmpeg version is recorded alongside the scripts.
