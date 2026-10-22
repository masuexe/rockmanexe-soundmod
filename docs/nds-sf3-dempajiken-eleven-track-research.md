# SF3 DEMPAJIKEN: eleven source tracks, two merged groups and a long-note alias

This separate experiment imports verified Japanese `ssr3b`, sequence 26
`BGM_DEMPAJIKEN`, into Japanese EXE6 Gregar through selector
`sf3-dempajiken-eleven-track`. Source groups are
`[[0],[1],[2,4,6],[3],[5,8],[7],[14],[15]]`: eleven sources become eight native
sequence tracks. It uses the existing plain merged converter and ten PCM voices;
no native driver/mixer, new fitting/modulation mode or general batch search is
added. Archived v22 still marks this source as a capacity blocker.

## Grouping and preserved data

Sources 2/4/6 have fixed volume 110; sources 5/8 have fixed volume 90. Both groups
pass existing shared-expression/effective-pitch and held-note-pan guards. A
source with incompatible expression stays independent. Each merged source's
volume ratio is one, so no extra velocity-ratio quantization is introduced.
Source 8's pan 30/94 is retained per note in its tone definition. All 584 mapped
note tuples and target velocities match an unpacked eleven-track singleton
control. That control is not runnable in the eight-track target.

Source 2 has long key-64 notes, encoded with native alias 127 and TIE/EOT.
Their source gate length is 383 ticks. No carry across the common loop boundary
is needed: EOTs at 767/2495/4223 precede the entry/joins at 768/2496/4224.
All eight compiled tracks pass two-cycle note/gate/timing comparisons. All 584
packed mappings, 103 keyed tone slots and nineteen prepared waves match source-
derived pan, ADSR, tuning, raw PCM8 and relocated loop headers/data.

## Independent source and original native checks

The source retains the pinned SF3 ROM identity and SDAT SHA-256
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
All eleven tracks loop with period 1728. Tempo 150 maps to MPlay151, about
120.25 native versus 119.97 source ticks/second. Gain stays +3.5 dB at 10512 Hz.
There is no active LFO, fitted attack or offline filtering.

The pinned independent 180-second software DS render matches 5,067 notes and
seventeen unique decoded source waves. Nineteen native headers retain distinct
tuned uses. Source ADSR checks cover 5,067 note-on snapshots and 509,634 voice
timer updates, with instant attacks throughout. This is software source
rendering, not DS hardware capture.

Natural frontend playback uses Start at frames 180–190 and reaches clock 4226
in 2,100 frames, covering the intro, two common cycles and all nineteen native
waves. There is no register/RAM injection, forced repeat, header redirection
or clock restart. Read-only NOTE entry/allocation/exit observation extends to
clock 4241 over 2,107 frames so the final long-note release has coverage beyond
the last GOTO. All 999 scheduled calls are observed: 996 allocate and three
are rejected. Every source is represented. Allocated wave, owner, key, ADSR,
initial gate, velocity and priority match the source/compiled mapping. Original
NOTE handler bytes remain identical to the pinned base.

The triple group has at most two simultaneously gated source parts in the
original score. Its initial inherited assertion demanding all three at once
was inapplicable and failed; that run is retained and marked incomplete.
The corrected full run observes overlapping members in 458 frames and both
members of the second group in 221 frames. No event/field comparison is relaxed.
All 166 allocated source-8 notes preserve opposing stereo directions: 66 at
pan30 and 100 at pan94, with median signed channel-volume balances around
-0.55/+0.542. This is stereo contrast, not a whole-song pan-error bound.

All three original long alias uses remain held through their steady gate
windows, then release after their EOTs, including the last GOTO. The original
score does not have a same-track sibling active at those EOTs, so it does not
establish that coverage. A separate disposable modified-score diagnostic uses
the original imported tones and unchanged driver: two aliases are held, the
first EOT releases only alias127 while its sibling continues, then the sibling's
EOT releases it. It passes 18/20/10 frame observations in the respective windows,
before FINE. This diagnostic is not original-arrangement or gameplay acceptance.

## Observed ten-voice budget limit

Source 14 key64, instrument19, is rejected at clocks 696/2424/4152: once per
1728-tick cycle, including the intro observation. It has the lowest source
priority (117) and volume60. All source schedule events are retained, but those
three NOTE calls cannot obtain a channel under the native ten-voice budget.
The final manual checklist explicitly asks whether that accompaniment loss is
acceptable. Allocation success for the other notes also does not exclude
release-tail stealing. Neither limitation is hidden by changing priorities,
removing source events or increasing the mixer voice count.

Controlled effects 100/129, music continuation, queued stop and three native-
restore/restart helper cycles pass; real battle/map transitions remain manual.
The thirty-second native preview peaks at 17233 and covers the first GOTO near
0:21, but not the second near 0:35. Normalized comparison clips are not sample-
aligned. Standard volume/velocity mapping, ADSR, PCM8 and tempo quantization
remain; no whole-song fidelity bound is claimed.

All 370 prospective-source tests pass without skips, including the new eleven-
source/two-group integration and long-alias assertions. Root migration keeps
the frozen tested hashes, and focused root tests pass. All 43 accepted and two
unaccepted control ROM/BPS pairs rebuild identically. The production CLI
reproduces all eight native-tested files byte for byte. Archived v10–v22
recursive file identities remain unchanged.

## Exact ROM and user-reported manual acceptance

- ROM CRC32: `E6F71051`; size 8,663,092 bytes.
- ROM SHA-256: `55bbdc6711c395c32b78ad5159fcd0622b20e973829b86dfb4d34f60d06188ef`.
- BPS SHA-256: `f71d64bdef737adaf7428a2a87ce77ec487ab7c4231962f1fb1d9e26c7c0f195`.
- Local folder: `out/nds-research/sf3-dempajiken-eleven-track-exe6-v1/`.

On 2026-10-22 the user reported passing the three requested checks: at least three minutes in a
virus battle, checking long-note endings, merged instruments, stereo and joins
and judging the known accompaniment omission; repeated chip/Buster effects;
and three battle→map→battle encounters with native-map music restored and each
import starting afresh. The user explicitly reported that the once-per-cycle lowest-priority
accompaniment omission was inaudible. The measured allocation limit remains.
No independently timed recording or full gameplay trace was supplied; real
linked play, rematches and comparative preference are not inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-dempajiken-eleven-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-dempajiken-eleven-track-exe6-v1
```

Use a fresh output directory. Original/diagnostic native evidence, source
reference, budget records, logs and hashes stay in ignored research outputs.
ROMs and source game assets remain outside Git.
