# Star Force 1 SETSUNAI: note-free conductor and antialias conversion

The candidate is `out/nds-research/sf1-setsunai-antialias-exe6-v1/`.
On 2026-10-18 the user reported “测试没有问题”, accepting this exact
filtered ROM after the requested listening/gameplay checklist. This fixes the singleton
converter failure recorded for `ssr1:25` in the archived v11 audit. The
unfiltered primary variant was already packable: this adds a filtered version
of an existing song, rather than increasing the number of unique source songs.

## Cause and bounded fix

Japanese `ssr1d.nds`, pinned SDAT file 667, SSEQ 25 `BGM25SETSUNAI` uses seven
tracks, bank/wave archive 39, player 0, sequence volume 85 and ten ADPCM waves.
Track 0 contains no notes: it sets tempo 98 and loops through waits. Tracks
1–6 supply the music. Source loop periods are 2112 ticks, with individual
loop-state starts from 72 to 1224 ticks.

The singleton compiler used `max()` over each target group's note volumes,
assuming every group contains a note. It now uses the DS initial volume 127
only when that collection is empty. All explicit controls still compile
normally; no source track is removed, no note or dummy voice is invented,
and the conductor remains a separate native track. Existing finite conversion
restrictions are unchanged. The FIR, resampler bounds and native mixer are
unchanged; the production manager is unchanged.

The reference validator previously required every source track to appear in
`notes.csv`. It now requires exactly the sounding tracks, including rejecting
missing sounding tracks and unexpected notes on a conductor. A note-free
loop needs duration evidence for two source periods and independent control
observations. Conductor tempo is checked separately. Truncated control logs
cannot reduce the minimum window; missing, changed and truncated tempo logs
are covered by negative tests.

`scripts/build_nds_reference.py` now instruments E1 tempo commands. The local
`reference-player-conductor-v1` is built from a copied pinned, instrumented
`reference-player-depth-v2/core`, adding only that observation. Its build
manifest records parent/core/renderer/binary hashes and the compiler command;
`build-reference.py` reproduces the copy and addition. Existing reference
binaries and recordings are preserved. No synthesis behavior changes.

## Output and runtime evidence

The filtered candidate retains seven tracks, six sounding, and prepares 72
per-key PCM8 waves totaling 565,558 bytes at +3.5 dB. The native mixer remains
ten channels at 10,512 Hz. One wave/key reaches a source step of about 16.2814,
within the existing 1/16–32 bound. Stored tuning error remains below 0.001
cent. The 724 PCM8 clamped values include full-scale quantization and FIR
overshoot, rather than measuring full-mix clipping.

The common generated loop starts at tick 1224 and lasts 2112 ticks. There
are 524 mapped notes in the compiled intro plus first period, no long-note
aliases or carries, and zero note events on the conductor. At native tempo
98, first GOTO is at tick 3336, about 42.75 seconds, then every 27.06 seconds:
roughly 43, 70, 97, 124, 151 and 178 seconds after the music starts.

The ROM is 8,981,068 bytes, CRC32 `4A30DEAB`, SHA-256
`901397116864b1423aaffe32274eb121fa677816927d1083f30c3b9474df2e22`.
BPS reconstruction is verified. The independently built unfiltered control in
`out/nds-research/sf1-setsunai-exe6-control-v1/` exactly matches the archived
v11 primary ROM and BPS. The filtered ROM adds 345,136 bytes (about 337 KiB)
relative to that control; direct versus singleton compilation also contributes.
The new filtered output has no previously packed v11 counterpart to match.

- A new 100-second software DS reference matches 1,190 notes, 183
  pan/bend/expression/delay controls, the conductor's one tempo command and
  ten exact original decoded PCM16 arrays. Original PCM comparisons validate
  decoding, not equality of the filtered waveform to the source.
- Natural title playback checks one complete common loop without register
  injection: 2,555 frames, final clock 3338, all seven native track states
  checked and all 72 prepared samples observed. Static note/gate checks cover
  two periods; repeated original-song battle execution remains a manual check.
- Every prepared wave has valid packed length, loop, tuning metadata and
  nonzero PCM8. Details are in `prepared-wave-validation.json`.
- Controlled effects 100/129 preserve advancing music. Ordinary battle and
  synthetic communication dispatch, queued stop, native music restoration
  and three restart cycles pass. These helper calls inject registers and do
  not establish actual linked play or results-screen/map transitions.
- The local-ROM integration test checks the retained silent conductor and
  native tempo, seven-track timing, notes, BPS reconstruction, three routing
  rules and original table/prefix preservation. Synthetic tests exercise
  both filtered/unfiltered singleton routes and reference failures.

The DS reference reaches sixteen voices in coarse snapshots, while the native
mixer remains limited to ten. These checks do not establish identical voice
allocation, envelopes, timbre or tempo. The archived v11 report and its counts
remain historical evidence; this experiment does not rerun the full scan.

All 247 full-suite regression tests pass. After strengthening the minimum
control-log window, the three conductor tests were rerun and pass, as does
the actual SETSUNAI reference check. All 29 previously accepted ROM/BPS pairs
and two unaccepted WIN2 controls rebuild byte-identically. Details are in
`regression-tests.txt`, `final-conductor-tests.txt` and `prior-regressions.json`.

## Listening and manual acceptance

`comparison/listen.html` embeds thirty-second software DS, unfiltered control
and new filtered clips, normalized by whole-clip loudness. Neither GBA clip
reaches the first GOTO. The direct and singleton routes also differ, so this
is not a single-variable filter comparison. The DS source is software synthesis,
not hardware output. The filtered ROM now has separate user-reported
acceptance; the unfiltered control remains unaccepted.

Test the exact filtered ROM in a virus or communication battle for at least
three minutes. Listen at about 43, 70, 97 seconds and subsequent joins for
gaps, clicks, missing parts or accumulating distortion, especially high notes.
Use chips and the Buster, finish the battle and verify native map music
resumes, then start at least two more encounters and verify playback restarts
from the beginning. `manual-testing.json` records the user-reported pass for
this exact filtered ROM. No timed recording or personal execution trace was
supplied; linked play/rematch was not separately reported. Automated native
coverage remains one complete loop, separately from the two-period static
model and user report. No comparative preference or unfiltered-control
acceptance is inferred.

Reproduce into a new directory:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --song sf1-setsunai-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-setsunai-antialias-exe6-v1
```

Use `--song sf1-setsunai` for the direct unfiltered control. The original
input ROMs remain read-only.
