# Star Force 3 battle music experiment

Research date: 2026-10-15. The second NDS experiment converts Star Force 3
SSEQ 35, `BGM_BATTLE`, into the Japanese EXE6 Gregar music player. All eleven
source tracks contain notes. Eight target tracks retain all executed note
events without expanding the native track storage. The user reports successful
three-minute communication-scene listening and music continuing normally while
using chips and the Mega Buster. The user also confirms all three virus-build
checks: normal virus-battle playback, victory/return-to-map music transitions,
and imported music restarting on the next encounter. This is the accepted
single-song gameplay baseline. Communication rematches remain a separate
unreported gameplay check. Automated frame-by-frame full-loop validation is
still incomplete; the user listening result is separate evidence.

The pinned source/target identities, ADPCM conversion, envelope approximations
and existing room experiment are described in [NDS import research](nds-import-research.md).
The accepted `room-exe6-v2` artifacts remain separate.

## Track mapping

`scripts/nds_track_merge.py` implements the mapping below. It checks shared
expression and effective bend at every control boundary through the compiled
prefix and two periods. It rejects incompatible controls, unsupported active
effects, changing merged-track volume and pan changes during held notes.

| Target track | Source tracks | Reason merging is possible |
| --- | --- | --- |
| 0 | 0, 9 | Constant expression/bend; separate instrument/velocity contexts |
| 1 | 1 | Independent bend retained |
| 2 | 2, 15 | Echo notes, identical live expression timeline |
| 3 | 3 | Independent pan retained |
| 4 | 4, 14 | Echo notes, identical live bend timeline |
| 5 | 5 | Independent pan/instrument changes retained |
| 6 | 6 | Independent pan/instrument changes retained |
| 7 | 7 | Independent pan retained |

The three merges do not discard the quieter echo parts. Fixed source volume
ratios become note velocities; shared expression remains a live VOL control.
Merged members use per-note instrument pan. The software DS reference observes
neither held nor releasing voices at source track 14's pan changes in its
135-second capture. Release envelopes and pan behavior still follow GBA rules.

Source tracks 2 and 15 have overlapping 335/287-tick notes at the same pitch.
MPlay TIE/EOT handles gates beyond the normal note-command limit. Distinct
keys 127/126 identify those notes for EOT, while rhythm-bank children retain
the original sounding pitch, key 75. An echo's EOT therefore does not cut off
both notes. Aliases are checked for collisions, overlap and loop crossings.

DS bends are converted in units of 1/64 semitone into MPlay BENDR/BEND/TUNE.
Both source bend ranges, 2 and 12, fit exactly in those parameter units.
This arithmetic does not establish identical audible pitch interpolation.
Relative music priorities 117–127 become 0–10 with song priority 20, leaving
headroom below the native test effects' priorities. No native effect data is
changed. Active modulation, portamento, envelope overrides and other
unimplemented controls fail conversion.

All source tracks have a 5,760-tick period. Their executable state repeats
start at different points, including between simultaneous events at one tick.
The converter repeats the recorded action slice, rather than guessing the
body from timestamps. A common target loop starts at tick 3,552 and repeats
every 5,760 ticks. This longer compiled prefix preserves existing music;
it does not insert an extra musical intro. DS tempo 153 maps to MPlay 154,
approximately 122.372 versus 122.640 ticks/second (GBA about 0.219% faster).

## Artifact and evidence

Artifacts: `out/nds-research/battle-exe6-v1/`.

- `unified.gba` / `unified.bps`: 8,786,780-byte Gregar ROM, 398,172 appended
  bytes, SHA-256 `9fab0c63482b788dd00ee0eddfd7bd7937581f65d38760d630553a6caeff15d0`.
  BPS reconstruction matches exactly. Native entries 0–473 remain byte-identical
  in the relocated table; prefix changes are restricted to declared export
  ranges. The imported song is entry 474 on the existing eight-track player.
- `conversion.json` / `dependencies.json`: 28 used waves, 16 instrument/pan
  contexts, eight target tracks. Independent GBA decoding checks all 3,030
  note events in the compiled prefix plus period, including tied gate lengths.
- `reference/`: 135-second SSEQPlayer software DS rendering. All 5,314 observed
  source note events, 663 pan/bend/expression controls and all 28 decoded PCM16
  arrays match the Python execution/decoder. This covers repeated source
  loops; it is not a DS hardware/emulator recording or proof of GBA playback.
- `preview/preview.wav`: 24-second natural title playback captured from mGBA
  SDL output, peak 17,277. `listen/listen.html` embeds normalized reference and
  target clips for comparing timbre/balance. Normalization masks raw loudness
  differences. The builder uses the existing +3.5 dB song gain; this value was
  calibrated for ROOM and has not been independently calibrated for BATTLE.
- `runtime/runtime.json`: natural title start; original effects 100/129
  initialize their native players while preserving imported music. After CPU
  context restoration, music advances from clock 491 to 553 with live voices.
  Controlled communication-scene dispatch and repeat dispatch select the new
  song; ordinary request 21 restores native song 21; queued all-stop stops the
  imported song and clears the indicator. Toolkit and stack remain intact.
  These probes inject PC/LR/arguments and a synthetic battle descriptor.
  They do not establish gameplay-triggered effects or a two-peer match.

The ROM selects BATTLE on title event 1 and `scene:communication`. Native
music ID 21 remains unchanged. The experiment does not identify or replace
the ordinary single-player battle event merely because the source song is
named BATTLE. Falzar is accepted by the research builder, but the battle
runtime evidence above belongs only to Gregar.

Validation passes 122 Python regression tests plus the existing manager UI
and AudioWorklet checks. New tests cover partial-tick loop boundaries, exact
bend parameter arithmetic, incompatible-control rejection, independent long
note aliases, BPS reconstruction and native table/prefix preservation. Rebuilding
ROOM with the current code produces byte-identical accepted v2 output. The
source NDS and original Gregar ROM retain their pinned SHA-256 hashes.

## Limits and next validation

User acceptance reported in this session:

| Check | Result | Evidence |
| --- | --- | --- |
| Converted battle music listening | Passed | User heard no problem |
| Communication-scene continuous playback | Passed | User listened for approximately three minutes |
| Chips and Mega Buster alongside music | Passed | User reports effects did not interrupt music |
| Normal virus-battle music | Passed | User confirms virus-build test 1 |
| Victory and return-to-map music | Passed | User confirms virus-build test 2 |
| Next virus battle restarts imported music | Passed | User confirms virus-build test 3 |
| Communication rematch | Pending | Controlled restart probe passes; no user gameplay result reported |

Acceptance records are saved in each tested build's `manual-testing.json`.
These passes apply to the tested communication and virus configurations. No recording,
exact runtime trace, exhaustive effect coverage or hardware performance
measurement was supplied, so those are not implied by the listening result.

Natural frame-by-frame validation in `sustained/validation.json` matches all
eight track states through frame 2,602, clock 5,341. At frame 2,603 the title
sequence ends the music before the model's loop. The report is correctly
marked incomplete with a mismatch; it must not be counted as a passed loop
test. Sending frontend B input every five seconds did not prevent this
transition (`sustained-with-input/`); that unsuccessful helper was removed
from the tooling. The 24-second preview also ends before a complete period.

The DS reference reaches sixteen voices in coarse samples, while GBA already
uses all ten configured PCM voices in the first 240 frames. Retaining all
sequence notes does not guarantee all sound simultaneously. Priorities,
release-tail stealing, 8-bit PCM and approximate envelopes can affect balance.
Neither voice-budget expansion nor hardware performance has been established.

Virus-battle lifecycle acceptance is complete for the reported test sequence.
Communication rematches and additional fade paths can extend this coverage.
Further exact loop-state or CPU claims need a gameplay
capture or separately documented battle-state harness. Extending title capture
alone cannot supply that evidence. After lifecycle validation, expand song
coverage before adding broader NDS selection to the manager.

## Virus-battle test build

`out/nds-research/battle-exe6-virus-v1/` adds numbered event 21 to the same
title/communication configuration. The original Gregar first battle descriptor
at file offset `0xB4B18` has music byte 2 equal to 21. The controlled probe
uses this actual ROM descriptor with communication flags cleared to verify
that the ordinary battle branch reaches the imported song. The user then
confirmed all three virus-battle gameplay checks below. Other numbered music events retain their normal pools;
special battles requesting a different music ID are outside this replacement.

Use this test sequence on the virus build:

1. Enter a normal virus battle and confirm the Star Force 3 song plays.
2. Win the battle. Listen for the normal results music or stopping behavior;
   check for residual battle notes.
3. Return to the map and confirm its normal music resumes.
4. Enter a second virus battle and confirm the imported song starts again.
5. If testing communication too, rematch and confirm normal music restart.

The original `battle-exe6-v1` remains the accepted communication baseline.
The virus build uses the same converted MPlay resource bytes, samples, gain
and mixer configuration; its additional change is the event-21 selection rule.
Apply its BPS to the original Japanese Gregar ROM or run its GBA directly.
Existing saves need the new ROM's matching basename in most emulators; copy
your save under that name while keeping the original save intact.

The virus ROM is 8,786,792 bytes (CRC32 `03FBA9EF`, SHA-256
`ac5979f3110b689a1ab2eb3e8c4fe4eda8545d64933d525a20793565068d9b8b`).
BPS reconstruction passes. Its `lifecycle/runtime.json` passes three controlled
cycles, including ordinary battle dispatch from the original ROM descriptor.
Native requests 2/3 resume with observed PCM voices; each rematch resets the
music clock from approximately 245 to zero and advances to 60 after 30 frames.
The focused 19-test NDS regression suite passes, including the three explicit
event rules and native-data preservation. `validation-summary.json` records
these results separately from the user-reported gameplay acceptance.
The communication baseline also passes the corrected three-cycle probe in
`battle-exe6-v1/lifecycle-v2/`, restoring native requests 2/21/2.

The optional `validate_nds_experiment.py --lifecycle` probe exercises three
controlled stop/native-music/communication-restart cycles with normal emulator
frames between requests. It checks clock advancement/reset, active voice
cleanup, native music playback, indicator state, stack and Toolkit. It does
not execute a results screen or map transition. Native voice activity is
observed across frames rather than requiring sound at one possibly silent
instant; the first lifecycle attempt exposed that overly strict probe check.

## Reproduce

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song battle \
  --event 1 --event scene:communication --out out/nds-battle-example

python3 scripts/render_preview.py out/nds-battle-example/unified.gba \
  --manifest out/nds-battle-example/build.json --id 474 --seconds 24 \
  --out out/nds-battle-example/preview

python3 scripts/validate_nds_experiment.py out/nds-battle-example \
  --out out/nds-battle-example/runtime
```

For the optional independent reference, build the renderer as documented in
the room research, then render source slot 35 for 135 seconds and pass its
directory to `validate_nds_experiment.py --reference`. The comparison page
command now reads the song name from the build manifest.

To reproduce the virus variant, add `--event 21` to the build command and use
a new output directory. Then run `validate_nds_experiment.py` with
`--lifecycle --out <new-validation-directory>`.
