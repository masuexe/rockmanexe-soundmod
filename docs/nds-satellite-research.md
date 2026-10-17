# Star Force 1 SATELLITE: standalone compatible-bank validation

The standalone ROM/BPS is in `out/nds-research/sf1-satellite-exe6-v1/`.
It selects SATELLITE at title, ordinary virus battle 21 and synthetic
communication dispatch, using appended song 474 on Japanese EXE6 Gregar.
On 2026-10-17 the user reported “没有问题” after the requested four-minute
listening and gameplay checklist. This records user-reported acceptance of
held-note sample/pitch identity, later parts, joins near 83/132/180/229 seconds,
effects coexistence, map restoration and next-encounter restart for this exact
ROM. No timed recording or full-loop execution trace was supplied; linked
play and rematches were not separately reported.

ROM: 8,878,740 bytes, CRC32 `25210DFE`, SHA256
`77ca068cb73ae060b0ce4abb0eede11657d999b149419b21ed224911cbdabd61`.
ROM and BPS fingerprints match the v9 scan's `ssr1:9` variant exactly.
BPS reconstruction, original 474 table entries and undeclared prefix bytes
are checked. Original source/target inputs remain read-only.

## Configuration

Japanese `ssr1d.nds`, SDAT 667, SSEQ 9 `BGM09SATELLITE`, sequence file 8,
bank 39, volume 70, source player 0. All eight tracks remain separate, with
28 PCM sample/root contexts and 15 generated instrument contexts. Source
tempo 138 maps to GBA 139 (110.694968 ticks/second). Imported gain remains
+3.5 dB, with ten PCM voices at 10,512 Hz. No active pitch-LFO approximation
or fitted-attack mode is needed. Standard PCM8/envelope/tempo and native
voice-allocation approximations remain.

Like [URA](nds-ura-research.md), track 7 uses instrument 123/key 96 as
long-note alias 127, while track 3 uses instrument 123/key 60 at that alias.
The compatible-bank allocator keeps the former in voice 4 and the latter
in voice 5, preserving their different samples and pitch keys. The single
split occurs at tick 791. Track 3's intro gate lasts 629 ticks and its EOT
is at 1,420; track 7's second 768-tick gate continues until 1,536.

The common generated loop starts at 3,840 with period 5,376. No long-note
interval crosses this song's common loop cut. Independent decoding compares
the intro and two complete periods through tick 14,592. The first GOTO is
at 9,216, about 83.26 seconds; later joins are 131.82, 180.39 and 228.95
seconds, then every approximately 48.57 seconds. Natural title playback
ends before the first GOTO, so no original-song native full-loop coverage
is claimed by this experiment's automatic probes.

## Evidence and limits

- All 211 regression tests pass. The new song test verifies the v9 fingerprint,
  bank split and original pitch keys, intro EOT, routing, BPS reconstruction
  and native-data preservation. The two existing choices in the modified
  builder branch, LAST and URA, still rebuild byte-identical ROMs and patches;
  see `prior-regressions.json`. The converter itself is unchanged this turn.
- The independent 180-second DS software reference matches 3,775 notes on
  all eight tracks, 5,229 pan/bend/expression/delay controls and 28 decoded
  PCM sample/root comparisons. It covers at least two complete source loops
  per track. Its coarse maximum voice allocation is sixteen, distinct from
  the target's ten-voice allocation budget.
- `natural-window/validation.json` checks 2,159 natural frames through clock
  4,000 (about 36.13 seconds). All eight track states match the independent
  decoder; 25/28 sample pointers and changing PCM output are observed. The
  other samples first start at ticks 4,272 (track 6), 4,416 (track 5) and
  6,816 (track 0), outside the window. No registers/RAM are edited, no headers
  redirected and no restart occurs. This is bounded coverage, not a loop test.
- `native-aliases/validation.json`, reproduced by `probe-native-aliases.py`
  in the artifact directory, follows the actual eight-track intro through
  clock 1,454. Track 3's alias matches its own wave in 352 observations;
  track 7's in 791. Their different waves coexist in 340 observations.
  After EOT 1,420, track 3 has release flags 81 while track 7 stays active
  with flags 17. The probe uses an exact ROM copy without register/RAM edits;
  it neither substitutes a synthetic song nor claims later-loop coverage.
- `runtime/` checks effects 100/129, music continuation, ordinary/synthetic
  communication dispatch, queued stop, native restoration and three restart
  cycles. These helpers inject PC/LR; actual gameplay and linked play remain
  separate manual checks.
- `preview/preview.wav` captures 30 seconds of native output (peak 14,457).
  `comparison/listen.html` provides normalized DS-software/native comparison.
  Normalization does not establish waveform or allocation equivalence.

The archived v9 scan retains its packing-only evidence for SATELLITE.
This standalone experiment adds source and bounded native checks without
changing those archived counts or manual associations. Production manager
integration and other conversion policies remain separate work.

## Reproduce and listen

Use fresh directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-satellite --event 1 --event 21 --event scene:communication \
  --out out/nds-satellite-example
mkdir out/nds-satellite-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-satellite-example/source.sdat 9 180 out/nds-satellite-example/reference
python3 scripts/validate_nds_experiment.py out/nds-satellite-example \
  --reference out/nds-satellite-example/reference --lifecycle --out out/nds-satellite-example/runtime
python3 scripts/validate_song.py out/nds-satellite-example/unified.gba \
  --unified out/nds-satellite-example/build.json --id 474 --window-ticks 4000 \
  --frames 2400 --out out/nds-satellite-example/natural-window
```

Listen continuously in battle for four minutes. Check long-note sample/pitch
identity, later entering parts and joins near 83/132/180/229 seconds for cuts,
repeated attacks or hanging notes. Use chips and the Buster, return to the map
and start another encounter to check native restoration and restart.
`manual-testing.json` records user-reported acceptance on 2026-10-17. Native
automatic coverage remains 25/28 samples in the initial window, with no
complete GBA loop executed by those probes.
