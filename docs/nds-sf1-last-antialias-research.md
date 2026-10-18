# Star Force 1 LAST: antialiasing with long-note boundary EOT

The standalone ROM/BPS is in
`out/nds-research/sf1-last-antialias-exe6-v1/`. It selects `BGM17LAST`
at title, ordinary virus battle 21 and communication music, using appended
slot 474 on Japanese EXE6 Gregar. On 2026-10-18 the user reported “没有问题”
after the requested at-least-four-minute battle listening, extreme high-note
timbre, jumps around 89/152/214 seconds, boundary long-note endings, effects,
native map restoration and at least two additional encounter starts. This
records user-reported acceptance of the exact ROM below. No timed recording
or personal execution trace was supplied; linked play/rematch was not
separately reported. Automated natural coverage remains a bounded window.

ROM: 9,649,856 bytes, CRC32 `BFB760B8`, SHA256
`2ef1f1b95486dffc49072b9d0336ba173340ae7599f4e76090911f980056dec0`.
Gain stays +3.5 dB, ten PCM voices at 10,512 Hz. Original 474 entries and
undeclared prefix bytes are preserved; BPS reconstruction passes. The ROM
is 735,312 bytes (about 718 KiB) larger than the accepted unfiltered LAST.
No production manager or native engine change is made.

## Source and scope

The pinned Japanese Dragon ROM supplies SDAT 667, SSEQ 17, file 16, bank 39,
tempo 142. Eight singleton tracks retain 1,972 mapped note events through
the common compiled interval. Twenty-nine source waves become 158 cached
per-key PCM8 waves. The CLI choice is `--song sf1-last-antialias`.

This reuses the looping antialias route introduced for ROOM, with the same
periodic sample-loop filter guard and compensated tuning. Four high keys of
instrument 71 exceed the former source-step limit of sixteen: the largest
is approximately 23.015 samples per native output sample. The bounded
resampler now permits steps from 1/16 through 32. A new ratio-24 DSP test
checks periodic DC and rejection of a tone that would otherwise alias to
DC. All existing accepted outputs are checked for byte identity. The
native mixing rate and voice count do not increase.

The prepared PCM totals 1,208,770 bytes, with 3,839 clamped quantizer values
(0.318%). This includes PCM8 full-scale rounding and possible FIR overshoot,
not full-mix clipping. Maximum stored-frequency rounding error is 0.000725
cents; this is not a measurement of complete native tuning. Bandwidth,
PCM8, filter/phase quantization, envelopes and voice allocation still differ
from DS. Extreme high-note timbre needs listening, not just command checks.

## What happens at the sequence boundary

The common sequence loop starts at tick 3072, period 7104. Gates of 312/384
ticks retain their TIE/EOT aliases and original sounding keys. In particular,
track 7 uses source key 59 through alias 127 at tick 9792 for 384 ticks.
Its gate ends exactly at tick 10176, the first generated loop jump. EOT is
executed after that GOTO at the same timestamp. This is a note ending at
the boundary, not a note remaining held for positive time beyond it.
`long_note_loop_carries` is empty for this song. Genuine carried intervals
remain a separate converter case; no claim of their full-song execution is
made by this LAST experiment.

Tempo maps to native parameter 143 (113.880434 ticks/second). First, second
and third jumps are approximately 89.36, 151.74 and 214.12 seconds. The title
scene changes before the first full loop, so sustained gameplay remains
manual. No title-music request is suppressed to manufacture natural coverage.

## Evidence

- Reused pinned 180-second DS software source reference: the new and old
  LAST SDAT bytes match. All 4,204 notes, 1,069 source controls and 29 unique
  decoded PCM16 waves match. This is software synthesis and original-source
  decoding evidence, not filtered-output waveform equivalence.
- Independent static MPlay decoding checks mapped gates through the intro
  and two complete loops. The export regression verifies aliases keep the
  original sounding keys and EOT appears at the boundary timestamp.
- All 158 prepared waves pass packed header, length, loop/tuning metadata
  and nonzero-data checks, including the extreme high keys. These static
  resource checks do not establish complete native playback.
- Natural original-ROM title execution: 2,150 frames, clock 4098, all eight
  decoded track states match in that window; 87 of 158 prepared waves are
  observed with changing PCM. This is bounded coverage, not a complete loop
  or complete native sample coverage.
- `probe-boundary-eot.py` uses the real converted bank, alias 127 and original
  384-tick gate in a shortened single-voice synthetic sequence. It observes
  four EOT cycles and three GOTO/EOT boundaries (ticks 884, 1384, 1884),
  checking the held note exists immediately before each and no held note
  remains after. The probe changes a disposable ROM's sequence, not CPU/RAM
  registers or the deliverable. It does not execute the original whole song.
- Effects 100/129, stop, native restoration, ordinary/communication dispatch
  and three restart cycles pass in controlled helper probes. These inject
  CPU context and do not establish personal gameplay or linked play.
- The thirty-second native preview peaks at 13,338. The portable comparison
  offers DS software reference, accepted unfiltered LAST and the new antialias
  version, normalized over the clip. These clips contain no original-sequence
  GOTO and are not sample-aligned.
- `validation-summary.json`, `prior-regressions.json` and
  `regression-tests.txt` retain exact checks. All 234 regression tests pass;
  all 25 accepted ROM/BPS variants and two earlier unaccepted controls
  rebuild identically. Archived v10 routes, counts,
  fingerprints and acceptance associations remain unchanged.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-last-antialias --event 1 --event 21 --event scene:communication \
  --out out/nds-last-antialias-example
python3 scripts/validate_song.py out/nds-last-antialias-example/unified.gba \
  --unified out/nds-last-antialias-example/build.json --id 474 \
  --window-ticks 4098 --frames 2200 --out out/nds-last-antialias-example/window
```

Use fresh output directories. The artifact's boundary probe accepts an
experiment directory and `--out`; it deliberately generates an isolated
sequence. Reference and lifecycle commands follow the prior experiments,
using SSEQ 17 and a 180-second source reference.

Listen continuously for at least four minutes in a virus or communication
battle, especially around 89, 152 and 214 seconds. Check high-note timbre,
long-note endings, no hanging/retriggered notes, gaps, clicks or gradual
corruption. Use chips/Buster during playback; finish the battle, verify
native map music returns, then start at least two more encounters to check
restart. `manual-testing.json` now records user-reported acceptance on
2026-10-18 for this exact antialias ROM, separately from the older unfiltered
LAST. The original-song automated native window remains about 36 seconds;
the synthetic probe remains evidence of boundary EOT, not full-song execution.
