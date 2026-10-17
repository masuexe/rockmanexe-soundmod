# Star Force 1 HENKAN: finite long gates and natural completion

The standalone ROM/BPS is in `out/nds-research/sf1-henkan-finite-exe6-v1/`.
It selects HENKAN at title, ordinary virus battle 21 and synthetic
communication dispatch, using appended song 474 on Japanese EXE6 Gregar.
On 2026-10-17 the user reported “没有问题” after the requested complete cue,
ten-second post-song wait, effects during/after playback, map restoration and
at least two additional encounter starts. This records user-reported acceptance
for the exact 0 dB ROM below. No timed recording or personal gameplay trace
was supplied; linked play and rematches were not separately reported.
This test deliberately plays once and
then leaves silence until another music request; silence after completion
is the expected behavior.

ROM: 8,882,816 bytes, CRC32 `5266B13B`, SHA256
`2460891b9371ea374aa4934ed8c723307bb9b47907c26e9056128e9da1dedaba`.
BPS reconstruction, original 474 table entries and undeclared prefix bytes
are checked. Original source/target inputs remain read-only.

## Finite conversion policy

Source: Japanese `ssr1d.nds`, SDAT 667, SSEQ 26 `BGM26HENKAN`, file 25,
bank 40, volume 110, source player 0. Four singleton tracks contain one 534-tick note each. Tracks 0/1
start at zero and end at 534; tracks 2/3 start at 20 and end at 554. Two
one-shot PCM samples are shared by two instrument contexts. Source tempo
120 maps to GBA 121 (96.360368 ticks/second), ending the first pair around
5.54 seconds and the second around 5.75 seconds.

The existing direct path rejects gates longer than 223 ticks; the merged
compiler previously required looping source tracks. A new explicit
`finite_support=True` mode accepts only singleton tracks that all reach END,
use one fixed source tempo and finish every gate before or at their own END.
It excludes native pitch-LFO and fitted-envelope modes, mixed finite/looped
tracks, and silent tracks. These remain bounded research constraints.

Long notes retain TIE/EOT. Each EOT is emitted before FINE at its original
track end, including a gate closing at exactly that timestamp. Tracks end
individually; no common-loop padding or artificial GOTO is generated.
The independent decoder checks every note's key, voice, velocity, duration,
explicit EOT and exact FINE time. Missing EOTs, mismatched gates or track ends
fail. The original looping behavior remains the default, so the archived
batch scanner does not automatically opt finite songs into this mode.

The usual +3.5 dB imported gain exceeds this source's native VOL headroom.
This build explicitly uses **0 dB**, preserving the calculated source volume
without clipping the command. The mixer remains ten PCM voices at 10,512 Hz.
PCM8/envelope quantization, tempo rounding and native allocation remain
approximations. This does not integrate NDS finite songs into the manager.

## Evidence and limits

- All 216 regression tests pass. New checks cover same-tick EOT/FINE ordering,
  finite long gates, missing/wrong EOT or end times, opt-in requirements,
  post-END gates, looping sources, excluded approximation modes, finite
  reference completeness and the actual HENKAN routing/data preservation.
- All twenty earlier accepted ROMs and BPS patches rebuild byte-identically;
  see `prior-regressions.json`.
- The independent 15-second DS software reference matches the complete four
  notes, both decoded PCM samples and six pan/bend/expression/delay controls.
  Finite reference validation compares the entire schedule, rejects duplicate
  or omitted notes, and requires capture beyond source END plus one second
  of tail. It does not require or fabricate source loop repetitions.
- `natural-finite/validation.json` checks the entire original four-track song
  in 345 natural frames through clock 555: all track states match independent
  decoding, both samples are observed and PCM output changes. All four FINEs
  have executed at that point. No emulator register/RAM changes are used.
- `natural-stop-v2/validation.json`, reproduced by `probe-finite-stop.py` in
  the artifact directory, follows 960 natural sound updates. It observes all
  four PCM channels, the first pair ending before the second, and all track
  flags clearing. Native player status settles on the next callback at clock
  556. That clock remains fixed, the player is inactive, and no imported PCM
  channels are present for the final 600 updates (more than ten seconds).
  It does not inject CPU/register/RAM state or substitute a synthetic song.
  The first `natural-stop/` report retains the probe's overly early inactive-
  status assertion at clock 555; the corrected probe allows the player's
  final housekeeping callback, then requires sustained inactive state.
- These source samples are nonlooped and can naturally exhaust before END.
  Empty-channel observations prove completion without hanging; they do not
  claim a release-envelope transition was observed at each explicit EOT.
- `preview/preview.wav` records 15 seconds of native output (peak 12,266).
  `preview/audio-tail.json` confirms every sample in the final five seconds
  is zero. `comparison/listen.html` provides normalized DS-software/native
  comparison, which does not establish waveform equivalence.
- `runtime/` checks effects 100/129 while the song is active, continuation,
  ordinary/synthetic communication dispatch, queued stop, native restoration
  and three restart cycles. Those helpers inject PC/LR; real gameplay and
  linked play remain manual checks.

The archived v9 scan retains HENKAN's earlier looping-track rejection and
its original counts. This opt-in experiment supplies subsequent evidence.

## Reproduce and listen

Use fresh directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-henkan-finite --song-gain-db 0 \
  --event 1 --event 21 --event scene:communication --out out/nds-henkan-example
mkdir out/nds-henkan-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-henkan-example/source.sdat 26 15 out/nds-henkan-example/reference
python3 scripts/validate_nds_experiment.py out/nds-henkan-example \
  --reference out/nds-henkan-example/reference --lifecycle --out out/nds-henkan-example/runtime
python3 scripts/validate_song.py out/nds-henkan-example/unified.gba \
  --unified out/nds-henkan-example/build.json --id 474 --frames 1200 \
  --out out/nds-henkan-example/natural-finite
```

In battle, let the approximately six-second cue finish, then wait another ten
seconds. It should stay silent without a cut, hanging note or automatic repeat.
Use chips/Buster both during playback and after it ends. Return to the map,
confirm native music resumes, and start another encounter; repeat that restart
two or three times. `manual-testing.json` records user-reported acceptance
on 2026-10-17. The automatic completion/idle checks and their scope remain
separate from that listening evidence.
