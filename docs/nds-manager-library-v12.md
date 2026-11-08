# NDS manager library v12: forty-five registered songs

This batch appends two independently accepted configurations. It preserves the
first43 tuples, slots8954–8996, gains, track counts and finite flags. Only
registry data and two test fixtures change. The converter, DSP, native
sound driver and mixer, relocator, realtime and cache implementation, browser
runtime, project schema and other tests remain unchanged.

| Slot | Song | Selector | Tracks | Gain | Playback |
| --- | --- | --- | ---: | ---: | --- |
| 8997 | SF1 FMPLANET | `sf1-fmplanet-delay` | 7 | +3.5dB | Loops |
| 8998 | SF1 GOWAIINCHO | `sf1-gowaiincho-delay` | 8 | +3.5dB | Loops |

[FMPLANET](nds-delayed-lfo-research.md) keeps source track2 depth15, speed25,
range1 and delay10 at source tempo115. Its fixed-delay mode encodes LFODL6 and
uses native LFOS26/MOD2. The first note preloads delay at depth zero, and the
same-tick depth control then enables it. [GOWAIINCHO](nds-pre-note-lfo-research.md)
keeps depth20, speed25, range1 and delay10 at tempo105. It initializes depth at
tick24 before its first note at tick688, encodes LFODL5 and uses native
LFOS29/MOD2. Neither song enables envelope fitting, live depth or live toggling.

## Source identity and cache preservation

Both fresh Falzar preparations strictly match their accepted compiled blobs and
parsed dependencies. Their first reports need only known legacy fields. The
reconciliation removes empty `long_note_loop_carries` and `voice_context_splits`,
pins the actual `gate_checked_until_ticks` values and, for FMPLANET, pins the
fixed-delay initialization and exact corrected policy wording. It then requires
full report equality. Fourteen negative operative mutations are rejected. No broad
key is ignored and no emitted audio difference is repaired.

All45 blobs and dependencies match their own accepted standalone records. SF1
WIN2 still uses its accepted-v2 folder. Thirty-nine reports match strictly. Six
reports keep explicit reconciliations: the four prior BATTLE/KAICYOU/NESSIE/FRIEND
legacy cases and the two new pinned cases. Exact accepted ROM/manual fingerprints
and BPS reconstruction are checked. Prior independent source and per-song native
evidence is reused under these identities. No new DS render, source scan or
manual acceptance transfer occurs.

The audio toolchain identity stays unchanged. In the registry run, all43 previous
Falzar cache entries hit disk with zero conversions before that run accessed the
two new entries. Fresh candidate preflight had already prepared both additions
separately. Metadata load converts nothing. All45 use normal manager load,
preview and export paths. A saved v11 project preserves the song-key strings
`nds-ssr3-33:33` and `nds-ssr2-37:37` at slots8995/8996, and their pools. The expanded8999-entry table changes its ROM bytes, and old
exact-ROM acceptance does not transfer.

## Regression and integration

Fresh34-case manager/cache/lazy-preview/realtime Python regression and three
JavaScript suites pass without skips. Root source and test hashes are frozen
before the run and verified unchanged afterward. The prior550-case full suite is
reused under unchanged audio, dependency, toolchain and non-registry catalog AST
conditions. Only `scripts/nds_catalog.py`, `tests/test_nds_manager.py` and
`tests/test_manager_ui.mjs` differ from the prior scope. This is not a fresh
550-case full-suite run.

All45 real agbplay starts produce nonzero stereo. A separate Falzar45-song pool
packs24,000,680 bytes. It checks distinct song headers and tone banks, exact
per-song PCM sets, exact-content resource sharing, BPS reconstruction and the
32MiB bound. Packing does not prove every runtime selection or manual acceptance.
Actual HTTP checks cover45 entries, a byte-equal Falzar export and two new
three-second mGBA previews. Repeated previews reuse jobs and preserve project
pools. Automatic Falzar evidence does not establish manual Falzar gameplay.

## Final Gregar roles

The final Gregar patch selects FMPLANET for title and GOWAIINCHO for ordinary
virus and communication battle requests. All other pools retain native music.
`build.json` records table entry count8999 and45 library songs. BPS reconstruction
passes against the pinned original ROM.

- ROM CRC32: `29C46BC0`; size9058144 bytes.
- ROM SHA-256: `da418ae05c2dc76702287fae251c947626cc5d7511404ae801153ff80b4eca57`.
- BPS SHA-256: `a36ea4b4fdbe5312bce2e67b022db1e9f82d7b5b9fffac7667a22ebc80f8bdd2`.

## Final native verification

The exact composite passes19,710 ordinary frames between controlled calls.
FMPLANET has7 tracks with active status0x7F. Its5200-frame title warmup reaches
clock7974, beyond entry2976 plus two2304-tick periods, and observes all16 waves.
GOWAIINCHO has8 tracks with active status0xFF. A60-frame battle intro and12800
body frames reach clock18003, beyond entry7800 plus two4704-tick periods, and
observe all24 waves. Status is derived per active role rather than assumed.

Effects100/129, three controlled native-restore/title/battle/communication-restart
cycles and queued stop pass. No imported tail remains after native restoration.
Role-owned wave tracking permits four exact-content shared waves, with no bank
substitution. The fixture injects PC/LR/arguments and disposable scene RAM between
ordinary frames. It does not establish actual battle, map, linked-play or rematch
outcomes, inspect every NOTE allocation or revalidate all LFO/envelope steps.

The older standalone windows for both songs ended before a complete native loop.
The new composite evidence is separate from those bounded observations. It does
not prove exhaustive voice allocation, LFO/envelope step coverage, actual gameplay
or comparative fidelity.

## Retained sound and coverage limits

The native mixer still uses ten voices at10,512Hz with PCM8 storage. Original PCM
aliasing, native triangle modulation, shared phase and note-on resets, fixed delay
rounding, tempo rounding and the ten-voice budget remain. Fitted attacks, ADSR,
filtering and other envelope approximations are unchanged. No comparative
waveform-fidelity or zero-preemption proof is claimed.

Previous per-song limits stay attached to their exact records. These include
SF3 AJITO fourteen held or starting preemptions and1551 release-channel reuses,
SF3 STUDIO extreme-soft zero-velocity mappings, SF3 CHANGE four held or starting
preemptions, SF3 DEMPAJIKEN three rejected NOTE calls and prior SF3 WIN2
allocation tradeoffs. Earlier original-PCM SF2 shared LFO/envelope limits and
all prior release-tail, quantization and clipping observations remain.

## Remaining source investigation

The metadata shortlist now contains9 unique unregistered source sequences with at
least one accepted standalone record. It is not9 newly verified manager songs.
Alternative SATELLITE versions count once, and the filtered revision's limited
missing-accent acceptance remains attached to its exact record and is not
broadened by this inventory.

## Exact-ROM user acceptance

On 2026-11-08, the user reported “ok, 没问题” after the three requested checks
for exact ROM29C46BC0. The45-song roster and both new previews, save/reload/export,
title FMPLANET for at least180 seconds, virus GOWAIINCHO for at least240 seconds
including the requested entry/loop windows, chips/Buster and three actual
battle→map→battle cycles are recorded as user-reported passes.

The local ROM and BPS fingerprints match the delivery record. BPS reconstruction
also passes. The Windows test patch is absent at its recorded path during this
acceptance step. The prior verified delivery record remains unchanged. Its
recorded destination SHA-256 matches the local patch. This step does not claim
a fresh read or a new delivery of that Windows copy.

These reports are not independently timed or observed checks. They do not
establish comparative DS fidelity, zero-note-loss, arbitrary exports/roles,
linked play/rematches or manual Falzar gameplay. All prior sound, allocation,
quantization, delay and source-coverage limits remain. Fresh34-case focused
regression and reused550-case full-suite evidence stay separate. Acceptance
recording changes documentation only; source tests were not rerun for this step.

The primary agent ran the finalizer at the original delivery. It copied the
exact patch through fsync and atomic replacement, then verified byte/SHA-256
equality. Transport evidence and this later user acceptance remain separate.
The prepared Falzar review URL at delivery was `http://127.0.0.1:8789/`.
