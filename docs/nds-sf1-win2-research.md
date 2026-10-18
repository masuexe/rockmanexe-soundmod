# Star Force 1 WIN2: short cue with staggered endings

The standalone ROM/BPS is in `out/nds-research/sf1-win2-finite-exe6-v1/`.
It replaces title, ordinary virus battle 21 and communication music with
SSEQ 31 `BGM31WIN2` in appended slot 474 of Japanese EXE6 Gregar.
On 2026-10-18 the user reported a muddy/mixed ending with substantial
difference from the original. This build is not manually accepted. The
[bounded ending diagnosis](nds-sf1-win2-tail-diagnosis.md) records channel,
release and offline antialiasing controls. The user reports clear improvement
with the earlier diagnostic filter control. The subsequent
[buildable antialias experiment](nds-sf1-win2-antialias-research.md) has its own
user-reported manual acceptance dated 2026-10-18; the original unfiltered ROM
remains unaccepted.

ROM: 8,538,412 bytes, CRC32 `C9FD1875`, SHA256
`a106e5cf16ee2189699bc8527cf760d636d9f3392b4154fc196268417ae7b203`.
ROM and BPS fingerprints match the archived v10 `ssr1:31` variant exactly.
Original 474 table entries and undeclared prefix bytes are preserved;
BPS reconstruction passes. Both prior HENKAN variants rebuild identically.
No converter or production manager changes are needed.

## Configuration

Source: Japanese `ssr1d.nds`, SDAT 667, sequence file 30, bank 39,
sequence volume 60, player 0. There are 67 note events, six singleton
tracks, six instrument contexts and nine PCM samples. Gain is +3.5 dB.

| Source track | Target track | END tick |
| --- | --- | --- |
| 0 | 0 | 168 |
| 1 | 1 | 168 |
| 2 | 2 | 192 |
| 3 | 3 | 156 |
| 4 | 4 | 168 |
| 6 | 5 | 192 |

The existing opt-in finite converter retains each END as FINE, with no
GOTO. This cue has no long notes or active pitch LFO. Source tempo 170
maps to native parameter 171 (136.178701 ticks/second): sequence completion
is about 1.41 seconds, followed by release tails, then silence. Native
PCM8, tuning/pan/envelope and tempo approximations still apply.
The reference reaches 16 voices at coarse 100 ms observations; the native
mixer has ten PCM voices at 10,512 Hz and reaches that limit. Matching all
note events and decoded samples does not establish identical polyphony or
release tails. Dense passages and the ending need manual listening.

## Evidence

- Independent pinned DS software renderer: all 67 notes, 26 source controls
  and all nine PCM16 sample decodings match. This is a software reference,
  not a hardware recording.
- Natural playback: 86 frames, final clock 194, all six decoded track states
  match through FINE and all nine samples are observed. Changing native PCM
  is verified with per-frame snapshots. The original 60-frame interval
  yielded only one observation before this short cue ended; that failed
  attempt is retained in `natural-finite-initial-sparse-pcm/`.
- `probe-finite-stop.py` observes 960 natural sound updates with no CPU/RAM
  injection. Every track follows its individual END, the clock settles at
  194, ten imported channels are observed at peak, and 845 post-completion
  updates have no imported channels. The final 600 updates are inactive,
  empty and clock-stable. Release flags are observed 464 times (observations,
  not distinct voices), including tails after FINE.
- A 15-second native preview peaks at 10,526; its final five seconds contain
  only zeros. `comparison/listen.html` provides normalized reference/native
  playback and does not establish waveform equivalence.
- Controlled runtime probes pass effects 100/129, ordinary/communication
  dispatch, queued stop, native restoration and three restart cycles. Finite
  timing now bounds warmup/effects/lifecycle/restart observations to 17/8/22/8
  frames, within the earliest END. Looping probes retain their 240/30/120/30
  defaults. Helper probes inject PC/LR and do not replace gameplay tests.

The archived v10 report and its acceptance associations remain unchanged.
The artifact's `validation-summary.json` and `regression-tests.txt` record
checks for this standalone build.

## Reproduce and listen

Use fresh output directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-win2-finite --event 1 --event 21 --event scene:communication \
  --out out/nds-sf1-win2-example
mkdir out/nds-sf1-win2-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-sf1-win2-example/source.sdat 31 15 out/nds-sf1-win2-example/reference
python3 scripts/validate_nds_experiment.py out/nds-sf1-win2-example \
  --reference out/nds-sf1-win2-example/reference --lifecycle \
  --out out/nds-sf1-win2-example/runtime
python3 scripts/validate_song.py out/nds-sf1-win2-example/unified.gba \
  --unified out/nds-sf1-win2-example/build.json --id 474 --frames 1200 \
  --out out/nds-sf1-win2-example/natural-finite
```

Let the roughly 1.4-second score and its release tails finish, then wait at
least ten seconds. Check dense notes and the ending, no hanging notes or
automatic repeat, chips/Buster during and after playback, native map music
restoration and at least two additional encounter starts. Silence after
the cue is expected. `manual-testing.json` records the reported fidelity issue. Other checklist
items were not separately reported; functional checks do not establish fidelity.
