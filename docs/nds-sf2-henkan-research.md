# Star Force 2 HENKAN: finite cue and repeated starts

The standalone ROM/BPS is in `out/nds-research/sf2-henkan-finite-exe6-v1/`.
It selects HENKAN at title, ordinary virus battle 21 and synthetic
communication dispatch, using appended song 474 on Japanese EXE6 Gregar.
On 2026-10-17 the user reported “没有问题” after the requested complete cue,
ten-second post-song wait, effects during/after playback, map restoration and
at least two additional encounter starts. This records user-reported acceptance
for the exact +3.5 dB ROM below. No timed recording or personal gameplay trace
was supplied; linked play and rematches were not separately reported.
It deliberately plays once, then stays
silent until another music request.

ROM: 8,493,168 bytes, CRC32 `F43FB736`, SHA256
`4a67c5e057d16d106fc505712d0519714bea423b4908b2c13fec5a7b1b982286`.
Both ROM and BPS fingerprints match the v10 scan's `ssr2:26` variant exactly.
BPS reconstruction, original 474 table entries and undeclared prefix bytes
are checked. Original source/target files remain read-only.

## Configuration and differences

Source: Japanese `ssr2d.nds`, SDAT 975, SSEQ 26 `BGM_HENKAN`, sequence file
25, bank 59, volume 90, source player 0. Four singleton tracks share one
PCM sample and one generated instrument context. All four notes use source
instrument 55, key 50, velocity 127 and a 468-tick gate. Tracks 0/1 start at
zero and finish at 468; tracks 2/3 start at 12 and finish at 480. Independent
track-local alias 127/EOT handling permits the same bank entry on every track.

This uses the already validated [finite mode](nds-henkan-research.md), without
changing its converter policy: fixed tempo, all tracks reach END, all gates
close before or at END, no fitted-envelope or active pitch-LFO mode. Each
EOT precedes FINE at that track's original timestamp; no GOTO is inserted.
Tempo 120 maps to GBA 121 (96.360368 ticks/second), so the pairs finish around
4.86/4.98 seconds. The mixer remains ten PCM voices at 10,512 Hz.

Unlike the Star Force 1 cue's two samples, 534-tick gates and 0 dB headroom
setting, this song uses one sample, 468-tick gates and the standard +3.5 dB
imported gain, which fits VOL headroom. It is a different ROM, not another
manual-acceptance claim for the earlier artifact. PCM8/envelope/tempo and
native allocation approximations remain.

## Evidence and limits

- All 220 regression tests pass. The new song test checks the v10 fingerprint,
  shared sample/voice, original pitch key 50, four staggered notes, individual
  EOT/FINE ends, routing, BPS reconstruction and native-data preservation.
- The existing Star Force 1 HENKAN choice in the modified builder branch
  rebuilds a byte-identical ROM and BPS; see `prior-regressions.json`. This
  experiment changes no converter mappings or runtime-checker logic.
- The independent 15-second DS software reference matches all four notes,
  the decoded PCM sample and six pan/bend/expression/delay controls. It checks
  the entire finite schedule and capture beyond END, without inventing loops.
- `natural-finite/validation.json` checks the entire original arrangement in
  299 natural frames through clock 481: all track states match independent
  decoding, the sample is observed and PCM output changes. Every FINE has
  executed. No emulator register/RAM modifications are used.
- `natural-stop/validation.json`, reproduced by `probe-finite-stop.py` in
  the artifact directory, follows 960 natural sound updates. Four channels
  are observed; the first pair of tracks ends before the second. The native
  player settles inactive at clock 482. It records 661 quiet post-completion
  updates; the final 600 updates have no imported PCM channels and no clock
  restart. This exceeds ten seconds after completion, with no register/RAM
  injection or synthetic sequence.
- The sample is nonlooped and naturally exhausts before the source gates.
  Completion/empty-channel evidence does not claim an envelope release was
  observed at every EOT; the native release-observation count is zero.
- `preview/preview.wav` captures 15 seconds of native output (peak 21,140).
  `preview/audio-tail.json` confirms the final five seconds contain only zero
  samples. `comparison/listen.html` provides normalized DS-software/native
  comparison, which does not establish waveform equivalence.
- `runtime/` checks effects 100/129, music continuation, ordinary/synthetic
  communication dispatch, queued stop, native music restoration and three
  restart cycles. Its controlled helpers inject PC/LR; actual gameplay and
  linked play remain separate manual checks.

The archived v10 report retains packing-only evidence and no manual match
for this variant. This experiment adds source and natural finite-stop checks
without changing the archived counts or acceptance associations.

## Reproduce and listen

Use fresh directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-henkan-finite --event 1 --event 21 --event scene:communication \
  --out out/nds-sf2-henkan-example
mkdir out/nds-sf2-henkan-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-sf2-henkan-example/source.sdat 26 15 out/nds-sf2-henkan-example/reference
python3 scripts/validate_nds_experiment.py out/nds-sf2-henkan-example \
  --reference out/nds-sf2-henkan-example/reference --lifecycle --out out/nds-sf2-henkan-example/runtime
python3 scripts/validate_song.py out/nds-sf2-henkan-example/unified.gba \
  --unified out/nds-sf2-henkan-example/build.json --id 474 --frames 1200 \
  --out out/nds-sf2-henkan-example/natural-finite
```

Let the approximately five-second cue finish in battle, then wait at least
ten more seconds. Silence is expected; check for hanging notes or automatic
repeat. Use chips/Buster both during and after playback, return to the map,
and start at least two more encounters to verify native restoration and
one complete replay per encounter. `manual-testing.json` records user-reported
acceptance on 2026-10-17, separate from the automatic completion/idle evidence.
