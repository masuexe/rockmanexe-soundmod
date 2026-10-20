# Star Force 1 HOKORA: one-shot track and aligned loops

The explicit `sf1-hokora-mixed-delay` experiment now packs SF1 `BGM20HOKORA`
(SSEQ 20), retaining six looping tracks and the one-shot seventh track. This
extends the preceding [source-loop analysis](nds-sf1-hokora-loop-analysis.md).
The final ROM is `out/nds-research/sf1-hokora-mixed-delay-exe6-v1/unified.gba`.
SHA-256: `27fa4091ba1b2037379049a60b8277cf329314c4e79d303437f15d43591a13ad`.
On 2026-10-20 the user reported “测试没有问题” for this exact ROM after the
requested final checklist: at least three minutes of virus-battle listening
(including the one-shot ending and later loop joins), repeated chip/buster
effects, and three encounters with map restoration and fresh music starts.
This is user-reported acceptance; no timed recording or completion trace was
supplied. Two-peer linked play and rematch were not separately reported, and
no comparative listening preference is inferred.

## Bounded mixed score

`mixed_loop_support=True` accepts only singleton tracks with both finite and
looping members, fixed tempo, and finite notes whose gates close by their END.
Finite tracks must finish by the original shared loop entry. Finite-only,
fitted-envelope, release-override and filtered modes remain separate. Shorter
periods expand to their least common multiple, capped at 16,384 ticks and an
eightfold expansion of any source period. Default routes retain their prior
requirements and outputs.

Source periods 1536 and 3072 become one 3072-tick cycle. Original intros remain;
the existing native-LFO warmup moves the shared entry from tick 1572 to 4644.
Track 6 keeps its FINE at 1536, with its last gate at 1534, and never receives
a GOTO. The six looping tracks retain notes and ordered controllers. An
intro-only tied note ending exactly at entry now closes before the loop label
in this mode; periodic tied closures stay inside it. Synthetic tests cover
both cases and explicit finite EOT-before-FINE ordering.

The seven-track score maps 3,063 note events through its encoded intro and
common cycle, with six instrument contexts and twelve raw PCM waves derived
from ten source ADPCM waves (158,888 PCM8 bytes). It appends 229,076 bytes to
the base, using the existing ten-channel 10,512 Hz mixer and +3.5 dB gain.
Source tempo 129 maps to native parameter 130. The title, virus-battle and
communication triggers play imported slot 474. No production-manager or DSP
change is made, and archived v14 counts remain a separate snapshot.

## Explicit weak-LFO approximation

HOKORA's source depth 3 would round to native MOD=0 and is rejected by the
established native-LFO path. A separate `native_pitch_lfo_min_depth=True` option,
restricted to the mixed native-LFO experiment, maps such nonzero depths to
MOD=1. Defaults continue rejecting them. Controllers and their activation
order are preserved; the effect is not silently disabled.

This option checks all source/target phase combinations against a ten-cent
absolute pitch-difference bound, plus a five-cent RMS limit in the isolated
one-second model. HOKORA's depth 3 / speed 28 / delay 14 configuration has a
9.375-cent all-phase bound and about 2.92-cent isolated RMS error. Depth 8 /
speed 31 / delay 96 uses the existing mapping. Native triangle versus DS sine,
shared track phase, per-note resets, envelopes and ten-versus-sixteen voice
budgets remain fidelity limits. Active-modulation filtering remains unsupported.

## Reference and native validation

The unchanged independent software DS reference runs for 120 seconds. All
4,848 notes, ten PCM16 wave decodes, pan/bend/expression controls, source sine
updates and delayed modulation checks pass. The embedded finite track is
compared against its complete note schedule, without loop unfolding; a
synthetic test rejects invented later finite notes. Delayed-voice checks cover
111,733 timer updates, including waits, active updates and 1,373 zero-phase
activations. This reference is not a hardware or DS-emulator recording.

Unattended title playback is stopped by the game's attract sequence around
43.6 seconds, before the first common-loop jump. A disposable SDL input helper
therefore sends the normal Start key at frames 180–190. KEYINPUT reads at 185
and 195 verify press/release; music header and monotonic clock remain intact.
This uses frontend input, without game-RAM/CPU-register writes, header
redirection, keep-song mode or a modified ROM.

With that input, the original ROM passes 6,225 observed frames through clock
10789: intro and two full common cycles. All twelve samples sound, and decoded
cursor/tone/key/velocity states match every frame. Offline analysis of the same
actual track/channel snapshots compares 43,575 LFO states with unfolded native
MPlay events, including frozen finite-track state after FINE. Track 6's last
owned active channel is observed at clock 1536; it has no post-END START flags
and remains ended and empty through both GOTO boundaries (7716 and 10788).
The finite-channel window contains 1,018 release observations.

A separate 800-frame native LFO probe passes. Its optional strict DS diagnostic
cannot produce errors for tracks 0/1 because the DS logs have no allocated
voices whose modulation delay elapsed there; native track phase can evolve
during rests. The diagnostic records those tracks as unobserved, not zero-error
or equivalent. Actual allocated DS comparisons for tracks 3/5 have 544/1627
observations, with RMS about 2.44/2.70 cents and maxima 6.25/7.8125 cents.
The production diagnostic's strict failure is not turned into a whole-song
DS equivalence claim. Complete native-model checks remain independently passed.

Controlled effects, dispatch, queued stop, native restoration and three
restart cycles pass. These helper calls do not establish real results-screen,
overworld or two-peer gameplay. Manual tests still cover actual transitions.

All 278 regression tests pass. All 33 previously accepted ROM/BPS pairs and
two unaccepted controls rebuild identically. The final converter reproduces
this experiment's ROM/BPS and report after the synthetic boundary correction.
Packed checks verify all mapped tones, envelopes, pan, roots, raw quantization,
wave headers and relocated bytes. Automated coverage and the separately
recorded exact-ROM user-reported acceptance remain in `validation-summary.json`
and `manual-testing.json`.

## Listening and reproduction

`comparison/listen.html` compares the first 30 seconds of software DS synthesis
and actual mGBA output, normalized over equal-duration clips. It covers the
one-shot ending, not the later 75/105-second common-loop jumps. Full native
loop evidence is recorded separately. No listening preference is inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-hokora-mixed-delay \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-hokora-mixed-delay-exe6-v1
```

Use fresh directories for repeated builds/probes. Research scripts beside the
artifact preserve frontend input, channel/LFO checks, comparison scope, prior
rebuilds and source fingerprints. Exact-ROM manual acceptance has been recorded;
the completed implementation and documentation follow the standing commit/push
workflow. ROMs, source assets and local research outputs remain outside Git.
A later compatibility refresh can integrate this explicit bounded route while
preserving v14's history.
