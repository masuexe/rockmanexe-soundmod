# Star Force 1/2/3 compatibility audit

The updated batch audit covers every SSEQ slot in the three pinned Japanese
Star Force archives. Forty-eight candidates pass conversion, independent MPlay
reparsing, shared EXE6 packing and BPS reconstruction. The exclusive success
categories are 24 standard, four LFO-only, two envelope-only, three envelope
plus LFO, eight fixed delayed-LFO, four envelope plus fixed delayed-LFO, one
envelope plus live-depth LFO, one live-toggle LFO and one envelope plus live-toggle
LFO. The live-depth-only category has no successes.
These are automated resource/export results; this run performs no new gameplay
or listening tests and does not enable NDS songs in the manager.

Report directory: `out/nds-research/compatibility-audit-v8/` (schema 6):

- `index.html`: standalone searchable/filterable report, with every route,
  source feature, error and manual-evidence association available per row.
- `report.csv`: all slots for spreadsheet inspection.
- `report.json`: complete evidence and aggregate counts.
- `summary.md`: compact per-game summary.

## Scope and method

The scanner verifies all seven available ROMs against the existing source
fingerprints, extracts their expected SDAT files, and checks within-game byte
identity. It audits one representative per distinct archive: Star Force 1
Dragon (file 667), Star Force 2 `ssr2d` (975), and Star Force 3 Black Ace (187).
Source identities are documented with the [Star Force 1](nds-sf1-research.md),
[Star Force 2](nds-sf2-research.md) and [initial research](nds-import-research.md)
experiments. All source and original target bytes are checked again afterward;
inputs remain unchanged.

Slot presence and original names come directly from bounded INFO/SYMB reads,
without ndspy or the old structural inventory. The symbol reader handles
directory sizes that exclude trailing zero alignment while the SYMB block
length includes it, as used by Star Force 2/3. Actual sequence execution uses
the current bounded parser, including the corrected 16-bit modulation delay.

Each nonempty slot receives execution/resource inspection. Routes are tried
in this order, within the target's eight-track capacity:

1. Direct conversion, with native-effect priority headroom.
2. The existing singleton compiler for bend and long gates.
3. For executed nonzero modulation depth, the explicit pitch-LFO approximation:
   singleton tracks, fixed tempo, active pitch-only modulation with zero DS
   delay and representable nonzero rate/range.
4. If inspected definitions use non-instant attack, or executed controls use
   D0/D1/D2/D3 overrides, try the singleton envelope approximation. Overrides
   accept 0..127; note-on ADSR snapshots select independent voice contexts.
   Attack-only fitting rejects RMS amplitude error above 0.12 or maximum
   error above 0.30. Onset alignment can differ by one GBA frame; decay,
   sustain and release retain their existing approximation.
5. If that envelope candidate also executes nonzero pitch depth, try the
   combined envelope/pitch-LFO route, retaining all the LFO preconditions.
6. If source execution reaches active nonzero delay, try the fixed delayed-LFO
   approximation, then its envelope combination when envelope features are
   present. Detection includes activation after a note at the same tick,
   rather than relying only on note-on state. The converter requires fixed
   per-track delayed modulation after initialization before or at the first note timestamp;
   later activation or parameter changes remain rejected. Delays map to
   LFODL with the existing one-tick zero-phase onset and must fit 1..255.
7. If executed controls change between positive depths, try the opt-in
   live-depth pitch-LFO approximation, followed by its envelope combination
   when needed. Detection includes controls after the last note at the same
   tick. Type, speed, range and delay remain fixed; activation must still
   occur before or at the first note timestamp. Positive depth changes emit ordered
   MOD updates, retaining shared phase and delay count. Disabling modulation,
   later activation and unrepresentable depths remain rejected. These routes
   follow all existing routes, preserving earlier successful variants.
8. For executed positive depth, try the separate binary on/off pitch-LFO
   approximation and its envelope combination when needed. Each track may
   use depth zero or one fixed positive depth. Type, speed, range and delay
   remain fixed; disabling and later activation are supported. Toggle updates
   preserve the preloaded delay count, but GBA disabling clears shared phase
   while DS voices retain their independent phases. Combining positive depth
   changes with toggling remains unsupported. These fallback routes follow
   earlier routes, preserving previously successful variants.
9. The existing verified Star Force 3 BATTLE mapping is the only over-capacity
   exception. Other songs do not receive guessed merges or dropped tracks.

Successful conversion resources pass through the same exporter as the
single-song experiments: dependency relocation, native-data preservation,
output bounds and BPS reconstruction. The pack step was extracted into
`pack_converted_experiment`; all six previously accepted artifacts rebuild
byte-identically after that refactor. The batch writes reports only, retaining
ROM/BPS fingerprints rather than creating forty-eight new ROM files.
All 46 previously packed v7 variants retain their exact ROM and BPS fingerprints,
route, status and gain. The v2/v3/v4/v5/v6/v7 snapshots are preserved separately.
V8 includes matching long-note carries across loop jumps; the entry/exit
intervals must agree and aliases cannot overlap. The independent decoder
continues beyond the note-on window to close every included gate. This does
not constitute native full-loop playback.

Configuration: original Japanese EXE6 Gregar, eight music tracks, ten PCM
voices at native 10,512 Hz, +3.5 dB imported gain, title/ordinary ID 21/
communication scene pools. A headroom failure can retry the same route at
neutral gain with an explicit record; none of the forty-eight successes needed
that retry in this run. Gain and voice allocation are not calibrated by the
audit. Standard conversion still includes PCM8/envelope/tempo approximations.

Only SSEQ is scanned. The archives also contain three SSAR slots (one per
game) and four STRM slots (2/1/1); their contents are outside this conversion
audit. Counts are per `(game, sequence ID)`, so reused tunes across games are
counted separately, not asserted to be distinct musical compositions.

## Coverage

| Game | SSEQ slots | Candidates | Standard | LFO | Envelope | Envelope + LFO | Delayed LFO | Envelope + delayed LFO | Live-depth LFO | Envelope + live-depth LFO | Live-toggle LFO | Envelope + live-toggle LFO | Blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Star Force 1 | 38 | 35 | 14 | 4 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 9 |
| Star Force 2 | 43 | 40 | 5 | 0 | 1 | 2 | 2 | 3 | 0 | 0 | 0 | 1 | 26 |
| Star Force 3 | 51 | 47 | 5 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 39 |
| Total | 132 | 122 | 24 | 4 | 2 | 3 | 8 | 4 | 0 | 1 | 1 | 1 | 74 |

Five slots are empty; five other sequences execute no notes (three dummy
sequences and Star Force 2 KODAI/HERO). Of the remaining 122 candidates,
121 have completed execution traces containing notes. One, Star Force 1
HOKORA, fails execution analysis and remains unresolved rather than being
asserted playable or silent.

The standard-pass list is:

- Star Force 1: `4 ROOM`, `5 LABO`, `6 SCHOOL`, `11 DEMPAJIKEN`, `16 ANTENNA`,
  `17 LAST`, `21 COMICAL`, `22 JIKEN`, `23 KINCHO`, `24 KANDO`, `25 SETSUNAI`,
  `30 WIN`, `33 GAMEOVER`, `34 BOSSMAE`.
- Star Force 2: `4 ROOM`, `21 COMICAL`, `24 KANDO`, `30 WIN`, `33 GAMEOVER`.
- Star Force 3: `2 ROOM`, `28 COMICAL`, `31 KANDO`, `35 BATTLE`, `40 GAMEOVER`.

The LFO-approximation list is Star Force 1 `8 YUMENOSHIMA`, `15 GOWADENNO`,
`19 KAKUSHI` and `27 BATTLE`. The source names in the report retain their full
original symbols. Every new candidate still needs song-specific listening,
long playback, effects coexistence and lifecycle checks before acceptance.

The envelope-only passes are Star Force 3 `10 BGM_HOKORA` and the newly
unblocked Star Force 2 `11 BGM_DEMPAJIKEN`. Its subsequent
[standalone experiment](nds-dempajiken-research.md) supplies independent
source/runtime checks and user-reported listening/gameplay acceptance on
2026-10-17; these later results do not change the v8 scan snapshot. The combined passes
are Star Force 2 `14 BGM_FRIEND` and `15 BGM_NESSIE`, and Star Force 3
`29 BGM_FRIEND`. HOKORA and Star Force 3 FRIEND match the accepted
[envelope experiments](nds-envelope-research.md). The two Star Force 2
candidates were new automated packing results at scan time, without new
independent DS reference, runtime or listening evidence from that scan.
The subsequent [NESSIE experiment](nds-nessie-research.md) adds independent
reference/native-window checks and user-reported listening/gameplay acceptance;
the v4 report retains its original evidence snapshot. NESSIE uses DS attack
90/100/127, fitted to GBA attack 66/74/255 within the same error policy.

The fixed delayed-LFO pass list is:

- Star Force 1: `2 FMPLANET`, `7 GOWAIINCHO`, `10 DEMPA`, `12 TRUCK`,
  `13 PLANETARIUM`, `29 LASTBOSS`.
- Star Force 2: `1 TEKI`, `27 BATTLE`.

The envelope plus fixed delayed-LFO pass list is:

- Star Force 2: `2 BURAI`, `5 SKI`, `38 WIFI`.
- Star Force 3: `24 BURAI`.

FMPLANET matches the accepted [fixed-delay experiment](nds-delayed-lfo-research.md).
The [Star Force 2 BATTLE experiment](nds-sf2-battle-research.md) subsequently
passed independent reference/runtime checks and user-reported listening.
The [GOWAIINCHO experiment](nds-pre-note-lfo-research.md) also has user-reported
acceptance and now passes the scanner's corrected pre-note initialization check.
The [PLANETARIUM experiment](nds-planetarium-research.md) matches the v8
output exactly and has user-reported listening/gameplay acceptance.
The other eight fixed-delay variants still need song-specific reference,
runtime and listening validation; this scan supplies packing evidence only.

The only newly packed v6 candidate was Star Force 1 `3 BGM03HOMETOWN`, using
the envelope plus live-depth route. Its eight tracks and 19 samples match the
accepted [HOMETOWN experiment](nds-live-depth-research.md) exactly. The new
scan does not supply fresh runtime or listening evidence. Other candidates
with positive depth changes still fail the compiler's remaining constraints.

The three newly packed v7 candidates are:

| Game / ID | Song | Route | Tracks / samples | Existing manual match |
| --- | --- | --- | --- | --- |
| Star Force 1 / 7 | GOWAIINCHO | Fixed-delay, setup before first note | 8 / 24 | Yes |
| Star Force 1 / 28 | BOSS | Live toggle | 7 / 21 | Yes |
| Star Force 2 / 16 | KAICYOU | Envelope + live toggle | 8 / 24 | No |

GOWAIINCHO and BOSS match their accepted standalone experiments exactly.
At v7 scan time KAICYOU still needed independent source, runtime, sustained
listening and lifecycle validation; automatic packing did not establish those checks. No new
runtime or listening test was performed by the scan.
The subsequent [KAICYOU experiment](nds-kaicyou-research.md) supplies a
standalone ROM and song-specific automated checks, followed by user-reported
listening and gameplay acceptance on 2026-10-17. Its later evidence does not
change this scan's snapshot.

The two newly packed v8 candidates are:

| Game / ID | Song | Route | Tracks / samples | Existing manual match |
| --- | --- | --- | --- | --- |
| Star Force 1 / 13 | PLANETARIUM | Fixed-delay + carried long note | 8 / 29 | Yes |
| Star Force 2 / 11 | DEMPAJIKEN | Envelope + carried long note | 8 / 19 | No |

PLANETARIUM carries track 7 key 53 from 192 ticks before the jump to 192
ticks afterward. DEMPAJIKEN carries track 2 key 86 from 120 ticks before
the jump to 119 ticks afterward, using alias 127. Its fitted attack 100 maps
to native attack 74; it needs no pitch-LFO mode. DEMPAJIKEN is the recommended
next standalone reference/runtime/listening experiment at scan time.
The subsequent [DEMPAJIKEN experiment](nds-dempajiken-research.md) checks the
source, natural first loop and actual carried channel through its EOT;
the user reported no issues with the requested listening/gameplay checklist
on 2026-10-17. The archived v8 manual-match count remains sixteen.
Star Force 1 URA also passes the former boundary guard, but then fails with
`Conflicting per-note alias/instrument definition`; it remains blocked.
The audit introduces no new listening or runtime evidence.

Sixteen packed variants are byte-identical to artifacts with structured
user-reported manual acceptance: Star Force 1 FMPLANET/HOMETOWN/GOWAIINCHO/BOSS/PLANETARIUM/LAST/KINCHO/BATTLE-LFO,
Star Force 2 NESSIE/KAICYOU/WIN/BATTLE and Star Force 3 HOKORA/FRIEND/KANDO/BATTLE. This matching
does not create new manual evidence. The earlier accepted Star Force 3 ROOM
build uses title-only rules and its original priority policy, so the uniformly
configured audit variant is not marked as that previously accepted artifact.
Its historical title listening result remains in the ROOM research.

JSON rows and attempts record separate envelope/LFO/fixed-delay/live-depth/live-toggle flags. Envelope
rows retain attack fitting errors and method limitations; LFO rows retain their
configs, including delay rounding/counter timing where enabled. CSV exposes all
five flags, attack fits, delay mappings, initializations, source depth changes,
toggles and matching long-note carries. JSON also retains complete gate-window
validation and the carry policy; HTML offers separate status filters for all ten success categories.
`summary.md` counts the categories exclusively;
combined rows must not be added twice when discussing envelope/LFO coverage.
The earlier envelope audit regressions cover envelope/combined selection,
manual matching and CSV/summary classification, unnecessary route exclusion
and failed fitting remaining blocked. The over-capacity fixture also includes
envelope/delay features to verify they do not authorize guessed merges. Three
v5 audit tests cover delay/combined route and report selection, active delay
set after the last note at the same tick, and rejected live changes never
counting as packing success.
Three v6 tests cover positive depth detection after the last note, live-depth
and envelope/live-depth fallback flags/report classification/manual matching,
and precedence of existing routes. Rejection and over-capacity fixtures also
include the new route's feature to ensure it cannot override either failure.
Three v7 tests cover on/off controls after the last note, separate toggle and
envelope/toggle flags/reports/manual matching, and priority of fixed-delay
success over the new routes. Existing rejection fixtures now exercise the
toggle fallback too, ensuring unsupported parameter changes stay blocked.

## Blockers and next priorities

The primary result categories are exclusive:

| Result | Count | Meaning |
| --- | ---: | --- |
| Capacity blocked | 58 | More than eight source tracks and no registered mapping |
| Conversion blocked | 15 | Current control, envelope, timing or compiler preconditions reject every attempted route |
| Converter model blocked | 0 | All eight earlier boundary assertions are resolved |
| Execution analysis blocked | 1 | Bounded source execution cannot complete |

Source features can overlap these categories. Among blocked candidates,
18 use non-instant instrument attacks, 28 execute envelope overrides, 41
contain gates above 223 ticks, and 13 have modulated note states with a
nonzero delay. A long gate alone is not a general blocker: existing TIE/EOT
conversion already handles some songs. These counts describe investigation
work, not independent sets to add together or promises of compatibility after
one feature is implemented.

## Resolved loop-boundary assertions

The earlier v2 scan had eight assertion failures. All now pass the singleton
bend/long-gate route and shared packing in v3; this table retains their
original diagnostics for comparison:

| Game | ID / symbol | Assertion |
| --- | --- | --- |
| 1 | 5 `BGM05LABO` | Merged note/gate/timing differs on track 7 |
| 1 | 11 `BGM11DEMPAJIKEN` | Merged note/gate/timing differs on track 3 |
| 1 | 16 `BGM16ANTENNA` | Merged note/gate/timing differs on track 3 |
| 1 | 17 `BGM17LAST` | Unclosed tied notes in compiled loop |
| 1 | 21 `BGM21COMICAL` | Merged note/gate/timing differs on track 3 |
| 1 | 22 `BGM22JIKEN` | Merged note/gate/timing differs on track 7 |
| 2 | 21 `BGM_COMICAL` | Merged note/gate/timing differs on track 3 |
| 3 | 28 `BGM_COMICAL` | Merged note/gate/timing differs on track 3 |

Star Force 1 `20 BGM20HOKORA` produces `SSEQ loop end without start` in the
current source executor. This is a parser/model research item, not a finding
that the pinned original ROM is corrupt. Route errors are retained verbatim
in the report, including failures before any later successful route.

Seven failures came from filtering expected notes by the decoder's final
repeat timestamp. The decoder can stop between simultaneous commands, after
already decoding a note at that timestamp. LAST instead had a live TIE whose
EOT is the first command after jumping to the loop start. Both are valid
command schedules that the old checker truncated.

`validate_loop_notes` now unfolds the independently decoded command cycle in
its original order. It compares the intro and two complete musical loops,
including EOT commands at the final boundary, against the source schedule.
Missing/extra notes, wrong keys or gates, unmatched EOTs, live alias collisions,
unclosed ties and incorrect periods still fail. This changes validation and
report metadata only; generated MPlay and ROM bytes are unchanged. All six
previously accepted ROMs rebuild byte-identically; fingerprints are recorded
in `compatibility-audit-v3/accepted-rebuilds.json`. The v2 report is retained.

The eight earlier boundary regressions cover same-tick decoder closure, a TIE
ending after the loop jump, a simultaneous one-off intro note, and the invalid
note/gate/EOT/alias/period cases above. The v3 run passed all 155 tests at that stage; the current
v4 run passed all 167 tests, and v5 passed all 181 Python regression tests.
The v6 validation also checks prior fingerprints and JSON/CSV/HTML/summary
agreement, including exclusive categories and manual acceptance associations.
V6 passed all 191 Python regression tests. The current report's JavaScript
passes the Node syntax check. `compatibility-audit-v7/validation.json` records
the complete scan, cross-format checks, prior 43 fingerprint comparisons and
the three changed results. All 201 Python regression tests pass for v7.
The v8 scan passes all 206 tests; `compatibility-audit-v8/validation.json`
records cross-format agreement, JavaScript syntax validation, identical
fingerprints/routes/status/gain for all 46 earlier packed variants, the two
newly packed rows and URA's changed failure diagnostic. Inputs and archived
v7 files remain unchanged.

Each of the eight recovered songs also has a 180-second independent software
DS reference in `out/nds-research/loop-boundary-validation-v1/`. Source notes
cover at least two complete loops on every track; notes, pan/bend/expression
controls and decoded PCM16 samples match. Per-song `validation.json` files
record the renderer command and source/resource fingerprints; the root file
collects the results and renderer fingerprint. This is source execution and
resource evidence, not new GBA runtime or listening acceptance.

The subsequent [Star Force 2 BATTLE experiment](nds-sf2-battle-research.md)
validated the eight-track fixed-delay candidate; the user reported no issues
on 2026-10-17. This later acceptance does not change the v5 scan snapshot.
The v6 activation-equality diagnostic conflated setup before the first note
with activation afterward. Subsequent source inspection shows GOWAIINCHO
track 2 sets depth at tick 24 before first sounding at 688, and PLANETARIUM
track 2 sets it at 0 before first sounding at 24. In contrast, BOSS track 4
first sounds at 0 and activates at 3840; Star Force 2 KAICYOU track 2 first
sounds at 48 and activates at 768. The
[GOWAIINCHO experiment](nds-pre-note-lfo-research.md) now admits pre-note
initialization in the compiler. V7 now uses that correction, without changing
the archived v6 scan. In v7, PLANETARIUM remains blocked by `Long note crosses merged
loop boundary` after passing the old activation check. The subsequent
[PLANETARIUM experiment](nds-planetarium-research.md) permits matching carried
TIE/EOT intervals, with independent full-gate decoding and a synthetic native
channel probe; the user subsequently reported no issues with the requested
original-song listening and gameplay checklist on 2026-10-17. This later
evidence does not change the archived scan. LOSE/VS also retain further
activation/parameter constraints requiring inspection.
Only positive depth changes under the documented fixed-field policy were
added by v6. Star Force 1
HOKORA remains a bounded source-parser investigation.
The later [HOMETOWN experiment](nds-live-depth-research.md) separately enables
positive depth changes with fixed speed/range/type/delay. The user reported
no issues with the standalone ROM's requested listening and gameplay checks
on 2026-10-17. Its policy is now included in v6, while the v5 snapshot is
unchanged.
The subsequent [BOSS experiment](nds-live-toggle-research.md) adds a separate
binary on/off compiler flag, independently checks native held-note toggles
and provides a song-specific ROM accepted by user-reported listening and
gameplay checks on 2026-10-17. V7 now tries this flag and its envelope
combination after existing routes. KAICYOU subsequently passed its standalone
automated and user-reported listening/gameplay checks; the archived v6 and v7
counts remain unchanged. V8 now includes PLANETARIUM and the newly unblocked
Star Force 2 DEMPAJIKEN. The latter subsequently passed standalone source/runtime
validation and user-reported listening/gameplay checks. Star Force 1 URA
remains a candidate for further research into its per-note alias/instrument
definition conflict; it is not yet convertible.
Expanding the native player or devising new mappings for over-capacity songs
remains separate from raising PCM channel count. Manager integration should
expose the measured support policy and approximation/acceptance state once
those core boundaries are sufficiently covered.

## Reproduce

```bash
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms \
  --base ../roms/exe6.gba --out out/nds-compatibility-example
```

The output directory must be new. At least one pinned original per game is
required; other available pinned variants are verified too. `exe6f.gba` may
be selected explicitly for a separate Falzar packing audit, but the numbers
above belong to Gregar. The scanner does not register every passing ID in
`build_nds_experiment.py --song`, alter manager projects or run emulator tests.
