# NDS manager library v14: fifty-four configurations

This batch appends seven existing configurations and preserves the first47
entries, slots8954–9000, gains, track counts and finite flags. Only registry
facts and two count/roster fixtures change. The converter, DSP, native mixer,
relocator, realtime/cache, browser runtime and project schema remain unchanged.

| Slot | Source | Selector | Tracks | Prior artifact |
| --- | --- | --- | ---: | --- |
| 9001 | SF1 BATTLE | `sf1-battle-lfo` | 7 | Accepted-v2 |
| 9002 | SF1 HOMETOWN | `sf1-hometown-depth` | 8 | Accepted-v1 |
| 9003 | SF1 BOSS | `sf1-boss-toggle` | 7 | Accepted-v1 |
| 9004 | SF1 LOSE | `sf1-lose-depth-min` | 7 | Accepted-v1 |
| 9005 | SF3 LOSE | `sf3-lose-depth-min` | 7 | Accepted-v1 |
| 9006 | SF2 LOSE | `sf2-lose-mixed-depth-min` | 7 | Accepted-v1 |
| 9007 | SF1 SATELLITE | `sf1-satellite-upward-antialias` | 8 | Corrected-v2; limited report |

All retain+3.5dB. BATTLE explicitly uses v2. SATELLITE explicitly uses the
corrected future-use filtered v2, not rejected revision1 or the plain version.
Its prior “正常了” report accepts the missing-accent repair only; it does not
establish all later duration, scene, effects or gameplay checks. This batch
requests a new full title-listening check for its exact composite ROM.

The original-PCM/native-LFO routes keep their earlier approximation settings.
HOMETOWN retains fitted attacks and positive depth changes. BOSS retains live
LFO enable/disable. The three LOSE versions retain their own source schedules,
minimum-depth mapping and envelope policies. SF2 LOSE also retains its one-shot
track. SATELLITE retains its existing upward/future-use filter. No new converter
mode or unbounded group search is introduced.

## Identity and cache verification

All seven fresh Falzar preparations match their own earlier compiled blobs and
parsed dependencies exactly. Four reports match strictly. BATTLE, HOMETOWN and
BOSS lack only explicitly pinned newer diagnostics. BATTLE adds the complete
seven-track timing-validation report plus empty carry/split fields. HOMETOWN
adds eight gate-coverage values, empty carry/split fields and two initializations
at tick0 for source tracks2/4. BOSS adds seven gate values and empty fields.
All diagnostic values are pinned; removing only those additions restores exact
report equality. Thirty-five negative report mutations are rejected. The initial
strict preflight remains separate from successful reconciliation.

All54 blobs/dependencies match their own source artifacts. Forty-four reports
match strictly and ten use explicit legacy diagnostic/wording reconciliation.
Accepted ROM/manual hashes and BPS reconstruction are checked. Prior independent
source/DS and per-song native evidence is reused under this identity. There is
no new DS render, relaxed audio comparison or manual acceptance transfer.
SATELLITE's limited prior manual scope remains explicit.

All47 old Falzar cache entries hit disk without conversion before the registry
run accesses the seven new entries. Preflight prepares those entries separately;
the normal run reuses all54 disk entries. Metadata load converts nothing. A v13
saved project preserves keys, slots8999/9000 and pools. The new9008-entry table
changes ROM bytes; earlier exact-ROM acceptance does not transfer.

## Regression and integration

Fresh34-case manager/cache/lazy-preview/realtime tests and three JavaScript
suites pass without skips. The prior550-case full suite is reused under exact
unchanged audio/runtime/config/test identities except registry data and two
count/roster fixtures. Removing SONGS/TRACK_COUNTS restores the prior catalog
AST. This is not a fresh550-case run.

All54 real agbplay starts produce nonzero stereo. A separate54-song Falzar pool
packs25,646,828 bytes, below32MiB. It verifies distinct headers/tone banks, exact
per-song PCM sets, safe exact-content sharing and BPS reconstruction. It does
not prove every random runtime choice or manual acceptance. Actual HTTP checks
cover54 entries, a byte-equal Falzar export and seven new three-second mGBA
previews. Repeated requests reuse jobs without changing project pools. No
manual Falzar gameplay acceptance is inferred.

## Native evidence and retained limits

Each new configuration has its own exact Gregar manager export with one title
selection. A separate natural-playback probe uses verified frontend Start input,
with no PC/LR/RAM injection, header redirect, clock restart or forced repeat.
It checks active track masks, monotonic clocks, all prepared wave addresses under
current music owners, and two common cycles including diagnostic gate tails.
This is not an exhaustive NOTE-allocation or LFO/envelope-state observer.

The first SF2 LOSE probe failed before emulator launch because its complete
finite-track timing record has no `gate_checked_until_ticks`. The corrected
probe uses that record's `checked_until_ticks`. All six looping-only probes
retain the same computed clocks/frames. Their successful evidence is retained
under the preserved original script and exact goal equivalence. Only the affected
SF2 case is rerun. Initial failure logs are retained. No ROM or runtime behavior
changed for this harness correction.

The three LOSE standalone traces retain4/59/70 rejected NOTE calls for SF1/SF3/
SF2. Those are known ten-voice allocation limits, not newly removed losses or
proof that missing notes are inaudible. Their old user reports accepted the
stated listening/gameplay checklists. The new natural probe does not recount
all NOTE allocations or remove those limits. Native triangle/shared-phase LFO,
new-note resets, weak-depth fitting, original PCM aliasing, filtered clipping,
ADSR/tempo quantization, PCM8,10 voices/10512Hz and all prior per-song limits
remain. No comparative waveform-fidelity or zero-preemption claim is added.

## Exact manual delivery

- Gregar ROM CRC32: `14D9DEF4`; size9446584 bytes.
- ROM SHA-256: `47afac6b07ebc233e2fd4080f9c7e333b0c6e5a914a7c9d9aa239e1bde58623b`.
- BPS SHA-256: `2bbd4354691c691d2e25d5e8743595d61c9393866727c9ad745ee7ce396d6203`.
- Prepared54-song Falzar manager: `http://127.0.0.1:8791/`.

The final Gregar ROM selects corrected SF1 SATELLITE for title and SF1 BATTLE-v2
for ordinary virus and communication battle requests. All other pools retain
native music. The user reported “可以，没问题” for this exact ROM and the requested
checks:54-song roster,
seven new previews and save/reload/export; SATELLITE title for at least180
seconds including all four accents around00:20 and later loops; BATTLE virus
music for at least180 seconds including vibrato, held notes, tails and loops;
chips/Buster and three battle→map→battle cycles. Other five new entries have
preview and automatic per-song evidence, not new composite gameplay acceptance.
Arbitrary exports/roles, linked play/rematches and manual Falzar remain separate.

The finalizer must overwrite
`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps` with the exact final patch,
verify byte/SHA-256 equality, and record transport separately from acceptance.
Originals, source assets, caches and local research outputs stay outside Git.
The v10–v38 compatibility archives remain unchanged.

## Full-catalog goal

The [coverage ledger](nds-library-coverage.md) now tracks the full source set:
122 SSEQ entries with notes and four STRM music tracks, plus ten empty/note-free
SSEQ slots kept visible as non-content rows. Sound-effect archives are classified
separately.54 registered configurations do not complete this goal. The remaining
68 sequences include17 historical packed leads and51 capacity blockers; the four
streams also need decoder/playback research. These are remaining work categories,
not grounds to silently drop tracks. The goal remains active after this batch.

## Completed native windows

| Configuration | Frames | Final clock | Prepared waves observed |
| --- | ---: | ---: | ---: |
| `sf1-battle-lfo` | 9640 | 19021 | 22 |
| `sf1-hometown-depth` | 19654 | 27515 | 19 |
| `sf1-boss-toggle` | 12053 | 23462 | 21 |
| `sf1-lose-depth-min` | 2345 | 3595 | 16 |
| `sf3-lose-depth-min` | 1990 | 3050 | 14 |
| `sf2-lose-mixed-depth-min` | 2843 | 4358 | 15 |
| `sf1-satellite-upward-antialias` | 8167 | 15135 | 86 |

SF2 LOSE's track6 remains ended after911, keeps its LFO state frozen, and has
no new START flags. Its channels stay empty from common entry2400 through both
loop joins. These observations apply to that separate exact export.

The final SATELLITE/BATTLE composite passes20,210 normal frames between controlled
calls. SATELLITE reaches clock15754, beyond entry3840 plus two5376-tick periods,
and all86 waves. BATTLE reaches19850, beyond entry9216 plus two4608-tick periods,
and all22 waves. The eight-track title and seven-track battle use active masks
0xFF/0x7F. Effects100/129, three native-restoration/title/battle/communication-restart
cycles and queued stop pass without lingering imported tails after native
restoration. Those helpers inject PC/LR/arguments and disposable scene RAM;
they do not establish actual battles, maps, linked sessions or rematches.
The user reports the requested listening/gameplay checks passed for exact ROM14D9DEF4.
This report is not independently timed or observed and does not establish comparative
DS fidelity, zero note loss, other exports, linked play/rematches or manual Falzar
acceptance. Known standalone LOSE voice-budget rejections remain recorded.
