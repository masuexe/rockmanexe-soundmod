# ROOM: first looping-sequence antialias experiment

The standalone ROM/BPS is in `out/nds-research/room-antialias-exe6-v1/`.
On 2026-10-18 the user reported “没有问题” after the requested at-least-
three-minute battle listening, repeated loop joins, chips/Buster coexistence,
native map restoration and at least two additional encounter starts. This
records user-reported acceptance for the exact ROM below, separately from
the two automated native loops. No timed recording or personal execution
trace was supplied; linked play/rematch was not separately reported.
It selects Star Force 3
SSEQ 2 `BGM_ROOM` at title, ordinary virus battle 21 and communication music,
using appended entry 474 on Japanese EXE6 Gregar.

ROM: 8,868,704 bytes, CRC32 `B501C1F1`, SHA256
`87db5657956feec5b111ecb918ddaf48ec980a8ad24e5dabe945a146a575d992`.
Original 474 table entries and undeclared prefix bytes are preserved;
BPS reconstruction passes. Original source and base ROMs are read-only.

## Selection and bounded scope

ROOM has an already accepted unfiltered build and no bend, transposition,
modulation or portamento. Its short sequence period allows two complete
native cycles before the title scene changes. This tests looping-sequence
use of the filter separately from the earlier finite WIN2 experiments.
It does not enable every looping song or broaden pitch/effect support.

`bandlimited_pcm=True` now accepts singleton looping groups as well as
finite groups. Merged source tracks, native LFO and fitted envelopes remain
excluded. Upward bend, transposition, modulation and portamento are still
rejected, including live controls between note-ons. Existing loop matching,
long-gate alias, TIE/EOT, carry and bank-conflict checks remain in effect.
No resampler, native mixer or production manager changes are required.
The new research CLI choice is `--song room-antialias`.

Source: verified `ssr3b.nds`, SDAT 187, sequence file 2, bank 158, sequence
volume 80, source player 1. Six singleton tracks retain all source notes
and controls. The compiled interval has 471 note events and uses 80 prepared
per-key PCM8 waves from fifteen source waves. There are no long-note aliases
or gates carried across the common sequence cut in this song.

The compiler places the common loop at tick 24 with period 1536. Tempo 125
maps to native parameter 126 (100.342201 ticks/second). First and second
compiled jumps occur at approximately 15.55 and 30.85 seconds; subsequent
cycles are about 15.31 seconds apart. Native sound remains ten PCM voices
at 10,512 Hz, gain +3.5 dB. The source holds at most eight simultaneous note
events in the compiled interval, but DS reference release tails reach sixteen
voices; original/target allocated polyphony equivalence is not established.

This experiment uses the existing singleton compiler, with priorities mapped
below native effects. The older accepted `room-exe6-v2` uses the direct
converter and its original priority policy. For a fair filter comparison,
`unfiltered-control/` uses the same singleton compiler, events, priorities,
notes, schedules and tempo as the antialias version. Those invariants are
checked by `build-control.py`. Its ROM is 8,582,460 bytes; filtering adds
286,244 bytes (about 280 KiB). It is not the old accepted ROOM artifact.

## Evidence

- The pinned independent DS software renderer runs sixty seconds. All 1,806
  source note events, 127 source controls and fifteen unique PCM16 wave
  decodings match. The source is software synthesis, not hardware recording;
  matching decoded sources does not prove filtered-wave fidelity.
- Natural title playback checks all six native track states through the
  intro and two complete sequence loops: 1,844 frames, final clock 3,097,
  all 80 prepared samples observed, changing PCM, and no clock restarts.
  This covers both compiled GOTO boundaries without CPU/RAM injection or
  overriding a game music request. Three-minute gameplay is still manual.
- Controlled effects 100/129, numbered/communication dispatch, queued stop,
  native restoration and three restart cycles pass. These helper probes
  inject CPU context; they are separate from actual battles and linked play.
- Thirty-second native previews cover the first GOTO only. Antialias output
  peaks at 15,058; its matched unfiltered control peaks at 14,647. The source,
  control and antialias recordings are whole-clip normalized in the portable
  `comparison/listen.html`; they are not sample-aligned or fidelity scores.
- Existing DSP regressions cover alias rejection, DC, sample-loop periodic
  history, analytic sine continuity, compensated tuning and one-shot tails.
  New regressions cover an allowed looping TIE/EOT alias with an inter-note
  gap, rejected source merging/effect modes, and the full ROOM export.
  Existing live-alias overlap rejection is retained.
- `validation-summary.json` and `regression-tests.txt` record the final test
  run: all 232 tests pass. All 24 previously accepted ROM/BPS variants and two unaccepted WIN2
  controls rebuild identically with their original options. Archived v10
  routes, counts, fingerprints and acceptance associations are unchanged.

Prepared PCM totals 456,786 bytes, with 854 clamped quantizer values (0.187%).
This includes full-scale rounding and possible FIR overshoot, not full-mix
clipping. The largest stored-frequency rounding error is 0.000443 cents;
it does not measure all native tuning effects. Bandwidth, PCM8, phase/filter
quantization, envelope/pan/volume and allocation differences remain. CPU or
hardware performance has not been benchmarked.

## Reproduce and listen

Use fresh output directories:

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song room-antialias --event 1 --event 21 --event scene:communication \
  --out out/nds-room-antialias-example
mkdir out/nds-room-antialias-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-room-antialias-example/source.sdat 2 60 \
  out/nds-room-antialias-example/reference
python3 scripts/validate_nds_experiment.py out/nds-room-antialias-example \
  --reference out/nds-room-antialias-example/reference --lifecycle \
  --out out/nds-room-antialias-example/runtime
python3 scripts/validate_song.py out/nds-room-antialias-example/unified.gba \
  --unified out/nds-room-antialias-example/build.json --id 474 \
  --loop-cycles 2 --frames 2200 --out out/nds-room-antialias-example/natural-loops
```

Use a virus or communication battle to listen continuously for at least
three minutes. Check timbre, balance and repeated joins (first around 15.55
seconds, then every 15.31 seconds), no clicks, gaps, hanging voices or gradual
corruption. Use chips/Buster during playback. Finish the battle, verify native
map music restores, and start at least two more encounters to check restart.
The title preview is a short comparison; it does not establish prolonged
battle playback. `manual-testing.json` now records user-reported acceptance
on 2026-10-18 for this exact ROM; automated loop coverage remains two cycles.
