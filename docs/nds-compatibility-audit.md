# Star Force 1/2/3 compatibility audit

The latest [v14 antialias-variant audit](nds-antialias-compatibility-audit-v14.md)
adds guarded finite D3 release retries: 55 primary source songs and 29 filtered
variants pack. All prior packed builds remain identical. Its report is
`out/nds-research/compatibility-audit-v14/` (schema 11).
The following primary-route history and v10 snapshot remain distinct.

The v10 batch audit snapshot covers every SSEQ slot in the three pinned Japanese
Star Force archives. Fifty-four candidates pass conversion, independent MPlay
reparsing, shared EXE6 packing and BPS reconstruction. The exclusive success
categories are 26 standard, four LFO-only, two envelope-only, three envelope
plus LFO, eight fixed delayed-LFO, four envelope plus fixed delayed-LFO, one
envelope plus live-depth LFO, one live-toggle LFO and one envelope plus live-toggle
LFO, plus four finite-standard successes. The live-depth-only category has no successes.
These are automated resource/export results; this run performs no new gameplay
or listening tests and does not enable NDS songs in the manager.

Report directory: `out/nds-research/compatibility-audit-v10/` (schema 8):

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
10. For entirely finite sources within capacity, try the explicit singleton
    finite long-gate mode after every existing route. It requires fixed tempo,
    nonempty tracks and every note gate ending before or at its source END.
    Each long gate emits EOT before its track's individual FINE, including
    same-tick ends. Active pitch-LFO and fitted-envelope modes, mixed
    finite/looped tracks and post-END gates remain unsupported. Earlier direct
    finite successes such as GAMEOVER keep their standard category and bytes.

Successful conversion resources pass through the same exporter as the
single-song experiments: dependency relocation, native-data preservation,
output bounds and BPS reconstruction. The pack step was extracted into
`pack_converted_experiment`; all six previously accepted artifacts rebuild
byte-identically after that refactor. The batch writes reports only, retaining
ROM/BPS fingerprints rather than creating fifty-four new ROM files.
All 50 previously packed v9 variants retain their exact ROM and BPS fingerprints,
route, status and gain. The v2/v3/v4/v5/v6/v7/v8/v9 snapshots are preserved separately.
V8 includes matching long-note carries across loop jumps; the entry/exit
intervals must agree and aliases cannot overlap. The independent decoder
continues beyond the note-on window to close every included gate. This does
not constitute native full-loop playback.
V9 additionally allocates a compatible rhythm bank when a shared
`(instrument context, alias)` slot would otherwise map to a different source
key. The first compatible bank is reused, original key/sample and track-local
EOT behavior are preserved, and the 128-voice bank bound remains enforced.

Configuration: original Japanese EXE6 Gregar, eight music tracks, ten PCM
voices at native 10,512 Hz, +3.5 dB imported gain, title/ordinary ID 21/
communication scene pools. A headroom failure can retry the same route at
neutral gain with an explicit record. Star Force 1 HENKAN is the only success
requiring this retry: +3.5 dB fails VOL headroom, then 0 dB matches its accepted
standalone artifact. The other 53 successes use +3.5 dB. Gain and voice allocation are not calibrated by the
audit. Standard conversion still includes PCM8/envelope/tempo approximations.

Only SSEQ is scanned. The archives also contain three SSAR slots (one per
game) and four STRM slots (2/1/1); their contents are outside this conversion
audit. Counts are per `(game, sequence ID)`, so reused tunes across games are
counted separately, not asserted to be distinct musical compositions.

## Coverage

| Game | SSEQ slots | Candidates | Standard | LFO | Envelope | Envelope + LFO | Delayed LFO | Envelope + delayed LFO | Live-depth LFO | Envelope + live-depth LFO | Live-toggle LFO | Envelope + live-toggle LFO | Finite standard | Blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Star Force 1 | 38 | 35 | 16 | 4 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 2 | 5 |
| Star Force 2 | 43 | 40 | 5 | 0 | 1 | 2 | 2 | 3 | 0 | 0 | 0 | 1 | 1 | 25 |
| Star Force 3 | 51 | 47 | 5 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 38 |
| Total | 132 | 122 | 26 | 4 | 2 | 3 | 8 | 4 | 0 | 1 | 1 | 1 | 4 | 68 |

Five slots are empty; five other sequences execute no notes (three dummy
sequences and Star Force 2 KODAI/HERO). Of the remaining 122 candidates,
121 have completed execution traces containing notes. One, Star Force 1
HOKORA, fails execution analysis and remains unresolved rather than being
asserted playable or silent.

The standard-pass list is:

- Star Force 1: `4 ROOM`, `5 LABO`, `6 SCHOOL`, `9 SATELLITE`, `11 DEMPAJIKEN`,
  `16 ANTENNA`, `17 LAST`, `18 URA`, `21 COMICAL`, `22 JIKEN`, `23 KINCHO`, `24 KANDO`, `25 SETSUNAI`,
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
In v8, Star Force 1 URA passes the former boundary guard, but then fails with
`Conflicting per-note alias/instrument definition`; that snapshot retains
the blocked result.
The audit introduces no new listening or runtime evidence.
The subsequent [URA experiment](nds-ura-research.md) resolves that shared-bank
alias conflict with an additional compatible rhythm bank. Its independent
source, natural first loop and actual PCM alias/stop checks pass; the user
reported no issues with the requested listening/gameplay checklist on
2026-10-17. The archived v8 row and counts remain unchanged.

The two newly packed v9 candidates are:

| Game / ID | Song | Route | Tracks / samples | Existing manual match |
| --- | --- | --- | --- | --- |
| Star Force 1 / 9 | SATELLITE | Singleton bend/long gates + compatible bank | 8 / 28 | No |
| Star Force 1 / 18 | URA | Singleton bend/long gates + compatible bank | 8 / 10 | Yes |

Both record the same instrument-123/alias-127 conflict between source keys
96 and 60, resolved by a second compatible bank (new voice 5 at tick 791).
Neither requires the active pitch-LFO or fitted-envelope modes. SATELLITE
has no long-note carry across its generated loop cut; URA retains five.
SATELLITE was the next recommended standalone source/runtime/listening test
at scan time.
The scan supplies packing evidence only; URA's manual match reuses its
existing acceptance, and DEMPAJIKEN now matches its later accepted artifact.
The subsequent [SATELLITE experiment](nds-satellite-research.md) supplies
independent source, bounded natural playback and actual alias/stop checks.
The user reported no issues with its requested listening/gameplay checklist
on 2026-10-17; the archived v9 evidence is unchanged.

The four newly packed v10 candidates are:

| Game / ID | Song | Tracks / samples | Gain | Existing manual match |
| --- | --- | --- | --- | --- |
| Star Force 1 / 26 | HENKAN | 4 / 2 | 0 dB, headroom retry | Yes |
| Star Force 1 / 31 | WIN2 | 6 / 9 | +3.5 dB | No |
| Star Force 2 / 26 | HENKAN | 4 / 1 | +3.5 dB | No |
| Star Force 3 / 39 | WIN2 | 8 / 13 | +3.5 dB | No |

All four use the finite singleton route, with individual source END times
retained in the report. Star Force 1 HENKAN matches its accepted standalone
ROM and BPS. SATELLITE now matches its later accepted artifact too, without
changing its v9 bytes. The other three finite successes have packing evidence
only; no new source reference, native playback or listening is performed by
this scan. Star Force 2 HENKAN was the next recommended standalone test at
scan time: it
uses one sample and ends its pairs at ticks 468/480, differing from the accepted
Star Force 1 variant's two samples and 534/554 ends. Star Force 2 WIN2 still
fails finite conversion with `Unsupported merged-conversion effect 0xd3`;
the new route does not silently drop its release override.
The subsequent [Star Force 2 HENKAN experiment](nds-sf2-henkan-research.md)
provides independent source checks, complete natural playback, sustained
inactive/empty-channel observations and controlled restart/restoration tests.
The user reported no issues with its requested completion, silence, effects,
map restoration and repeated starts on 2026-10-17; the archived v10 evidence
is unchanged.

Twenty packed variants are byte-identical to artifacts with structured
user-reported manual acceptance: Star Force 1 FMPLANET/HOMETOWN/GOWAIINCHO/BOSS/PLANETARIUM/URA/SATELLITE/HENKAN/LAST/KINCHO/BATTLE-LFO,
Star Force 2 NESSIE/DEMPAJIKEN/KAICYOU/WIN/BATTLE and Star Force 3 HOKORA/FRIEND/KANDO/BATTLE. This matching
does not create new manual evidence. The earlier accepted Star Force 3 ROOM
build uses title-only rules and its original priority policy, so the uniformly
configured audit variant is not marked as that previously accepted artifact.
Its historical title listening result remains in the ROOM research.

JSON rows and attempts record separate envelope/LFO/fixed-delay/live-depth/live-toggle flags. Envelope
rows retain attack fitting errors and method limitations; LFO rows retain their
configs, including delay rounding/counter timing where enabled. CSV exposes all
five flags, attack fits, delay mappings, initializations, source depth changes,
toggles, matching long-note carries and voice-context splits. JSON also retains
complete gate-window validation, the carry policy and the compatible-bank
allocation policy. Finite rows additionally retain the bounded finite policy,
individual track ends and complete finite note/gate validation; CSV exposes
`finite_song` and `finite_track_end_ticks`. These describe the new opt-in
compiler mode; older direct finite songs keep their standard route. HTML
offers separate status filters for all eleven success categories.
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
| Conversion blocked | 9 | Current control, envelope, timing or compiler preconditions reject every attempted route |
| Converter model blocked | 0 | All eight earlier boundary assertions are resolved |
| Execution analysis blocked | 1 | Bounded source execution cannot complete |

Source features can overlap these categories. Among blocked candidates,
18 use non-instant instrument attacks, 28 execute envelope overrides, 37
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
V9 passes all 210 tests; `compatibility-audit-v9/validation.json` verifies
JSON/CSV/HTML/summary agreement, JavaScript syntax, the two newly packed rows,
existing manual-evidence matches and identical fingerprints/routes/status/gain
for all 48 earlier packed variants. Original inputs and the archived v8 files
remain unchanged.
V10 passes all 219 tests. Its new regressions check finite fallback gain retry,
classification/report/manual matching, precedence of earlier direct successes,
and rejection/capacity boundaries. `compatibility-audit-v10/validation.json`
records four new successes, the changed Star Force 2 WIN2 diagnostic,
cross-format/JavaScript checks, and identical prior 50 fingerprints/routes/
status/gain. Original inputs and the archived v9 files remain unchanged.

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
was a candidate for further research into its per-note alias/instrument
definition conflict at v8 scan time. The later [URA experiment](nds-ura-research.md)
now converts it with separate compatible banks and has user-reported
listening/gameplay acceptance on 2026-10-17. V9 now packs both URA and SATELLITE,
with an exact accepted-ROM match for URA. SATELLITE's eight-track, 28-sample
variant subsequently passed standalone source/runtime checks and user-reported
listening/gameplay acceptance. A next research candidate is Star Force 1
HENKAN: its finite sequence still fails the singleton compiler's looping-track
requirement and needs explicit long-gate/end-of-song support.
The subsequent [HENKAN experiment](nds-henkan-research.md) adds an explicit
finite singleton mode, with individual EOT/FINE times, independent finite
source checking and natural completion/idle validation. It is not enabled
by the archived v9 scan. The user reported no issues with its requested cue
completion, post-song silence, effects, map restoration and repeated encounter
starts on 2026-10-17. V10 now tries this bounded finite route after prior
routes, packing HENKAN in Star Force 1/2 and WIN2 in Star Force 1/3. Star Force
2 HENKAN subsequently passed standalone source/runtime checks and user-reported
listening/gameplay acceptance; v9's archived counts remain unchanged. The next
recommended finite experiment is Star Force 1 WIN2, whose six tracks have
different END times (156/168/192 ticks) and nine sample contexts.
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

The subsequent [Star Force 1 WIN2 experiment](nds-sf1-win2-research.md)
validates the exact v10 six-track/nine-sample finite variant against independent
source logs, full natural playback, staggered FINE/empty-channel observations
and controlled lifecycle probes. The user subsequently reported a mixed
ending and substantial original/target difference on 2026-10-18; this variant
is not manually accepted. The [ending diagnosis](nds-sf1-win2-tail-diagnosis.md)
provides bounded channel and offline-resampling controls without changing
archived evidence. Source and target polyphony differ (16 observed reference voices versus ten native
PCM channels); this does not change archived packing or manual-match counts.

After the user reported clear improvement with the offline-filtered listening
control, the [WIN2 antialias experiment](nds-sf1-win2-antialias-research.md)
adds an explicit per-key offline conversion route with periodic loop handling.
Its v2 ROM is a separate variant outside archived batch routes and counts.
On 2026-10-18 the user reported no issues after its requested listening/gameplay
checklist, accepting the exact v2 ROM. The unfiltered variant remains unaccepted. All 22 previously accepted variants and old WIN2
retain byte-identical ROM/BPS output with the option disabled.

The subsequent [Star Force 3 WIN2 antialias experiment](nds-sf3-win2-antialias-research.md)
reuses the existing per-key offline filter for eight tracks and 83 notes, with
34 prepared PCM waves. Its unfiltered control matches v10 `ssr3:39` ROM/BPS;
the antialias variant has separate source/runtime evidence. On 2026-10-18
the user reported no issues after its requested listening/gameplay checklist,
accepting this exact antialias ROM. Eleven simultaneous held source notes exceed the ten-channel
native budget; conversion success does not imply allocation equivalence.
Archived routes, counts and acceptance associations remain unchanged.

The subsequent [ROOM looping antialias experiment](nds-room-antialias-research.md)
adds explicit singleton-loop support to the offline filter route, without
changing resampling, mixer settings or automatic batch routes. Source and
native checks cover the six-track song through two complete generated loops.
On 2026-10-18 the user reported no issues after its requested three-minute
battle/listening checklist, accepting this exact new variant. Automated native
coverage remains two complete loops. Archived scan results and previous
accepted variants remain unchanged.

The subsequent [LAST antialias experiment](nds-sf1-last-antialias-research.md)
extends the opt-in offline step limit through 32 for extreme high keys while
retaining long-note aliases and boundary EOT. Original-song native playback
is bounded before the first GOTO; a separate synthetic probe tests the actual
converted note ending at a loop jump. On 2026-10-18 the user reported no
issues after its requested four-minute battle/listening checklist, accepting
this exact new ROM. This does not extend automated natural coverage or alter
archived scan evidence.

The standalone [SF2 WIN2 finite-release experiment](nds-sf2-win2-release-antialias-research.md)
now converts the previously D3-blocked sequence through explicit pre-note
release snapshots, with six tracks, 67 notes and 32 filtered waves. On
2026-10-19 the user reported no issues after its short-cue ending/silence,
battle effects and three battle/map/restart checks, accepting this exact ROM.
Its 260 tests and bounded source/native/helper evidence remain separate from
archived v13 routes and counts; batch integration is the next proposed step.

The subsequent [SF1 HOKORA source-loop analysis](nds-sf1-hokora-loop-analysis.md)
corrects empty-stack LOOPEND fallthrough and independently verifies its
one-shot seventh track. Conversion now reaches the existing all-looping-track
requirement; supporting mixed finite/looping tracks and aligned 1536/3072-tick
periods remains a separate capability. No new native ROM or manual acceptance
is produced, and v14's archived statuses and counts remain unchanged.

The standalone [SF1 HOKORA mixed-delay experiment](nds-sf1-hokora-mixed-delay-research.md)
now supports its finite seventh track and bounded common-loop expansion,
with a separately guarded minimum-depth pitch-LFO approximation. All 278 tests
pass and two natural common cycles are verified with real frontend input.
On 2026-10-20 the user reported that this exact ROM passed the requested extended
battle listening, effects coexistence and three-encounter lifecycle checks. No
timed recording or completion trace was supplied; linked play and rematch were
not separately reported. Archived v14 remains unchanged.

The subsequent [v15 audit](nds-compatibility-audit-v15.md) integrates the accepted
bounded mixed-track route and rescans all 132 slots. HOKORA adds one primary
packable song, bringing the total to 56 and exactly matching its accepted
ROM/BPS. All 55 prior primary and 29 filtered pairs remain identical. Filtered
counts stay at 29 packed, eleven exact accepted and eighteen pending; HOKORA's
filtered route still rejects active modulation. All 285 tests and report,
filter and archived v10–v14 integrity checks pass. The scan records no new
native playback or manual acceptance.

The subsequent [SF1 LOSE experiment](nds-sf1-lose-live-min-depth-research.md)
combines guarded weak-depth quantization, looping live positive-depth controls
and explicit fitted attacks. Its independent source and full-loop native
checks pass. On 2026-10-20 the user reported no issues after its requested
listening, effects and three-encounter lifecycle checklist, accepting that exact
ROM; no timed trace, two-peer or rematch result is inferred.
The standalone route is not integrated into the batch scanner, and v15's
56 primary/29 filtered packed counts remain unchanged.

The subsequent [SF3 LOSE experiment](nds-sf3-lose-live-min-depth-research.md)
reuses the accepted live/weak-depth combination with fourteen waves and no
fitted attacks. Its independent source, two-loop natural playback and native
allocation/LFO checks pass. On 2026-10-20 the user reported no issues after
its requested listening/effects/three-encounter checklist, accepting this exact
ROM; no timed trace, two-peer/rematch result or comparative preference is inferred.
It is not yet integrated into the scanner, and archived v15 remains unchanged.

The subsequent [v16 audit](nds-compatibility-audit-v16.md) integrates the accepted
looping live/weak-depth combination and rescans all 132 slots. SF1/SF3 LOSE add
two primary packed songs (58 total), exactly matching their accepted ROM/BPS.
All 56 prior primary and 29 filtered pairs remain identical. Filtered counts
stay 29 packed/eleven accepted/eighteen pending; 299 tests and report/filter/
archive checks pass. It adds no runtime or manual acceptance and keeps v15's
history unchanged. SF2 LOSE's later finite END remains a separate capability.

The subsequent [SF2 LOSE experiment](nds-sf2-lose-mixed-live-depth-research.md)
implements the bounded mixed/live-depth extension and shifts the entry by one
common period. Finite FINE=911 remains once; two natural loops and actual
finite-channel/LFO checks pass, alongside 306 tests and exact old ROM/BPS
rebuilds. On 2026-10-20 the user reported this exact ROM passed its requested
extended listening, effects and three-encounter checklist. No timed trace,
two-peer/rematch result or comparative preference is inferred. The scanner does
not yet enable this extension; archived v16 remains 58 primary/29 filtered versions.

The subsequent [v17 audit](nds-compatibility-audit-v17.md) integrates the accepted
mixed/live-depth extension after the existing mixed fixed-parameter failure.
SF2 LOSE adds one primary song (59 total), exactly matching its accepted ROM/BPS.
All 58 old primary and 29 filtered pairs remain identical; 311 tests and
report/filter/archive checks pass. There are 25 exact accepted primary versions
and 30 unique accepted sequences across both routes. Filtered totals stay
29 packed/eleven accepted/eighteen pending. It adds no runtime or manual
acceptance; archived v16 remains separate. SF2 VS's late first activation plus
positive depth updates is the next fixed-tempo capability candidate.

The subsequent [SF2 VS experiment](nds-sf2-vs-late-depth-research.md) adds a
separate explicit late-activation/positive-depth mode. Its source reference
matches 6,493 notes and seventeen original waves, with no carried-positive
coverage claimed. Native frontend playback reaches two common cycles and all
eighteen prepared waves; the allocation-aware model checks 91,672 states.
All 317 tests and 37 accepted/two control ROM/BPS rebuilds pass. Exact-ROM
listening, effects and three-encounter checks were explicitly confirmed passed
on 2026-10-20, accepting this exact ROM. No independently timed trace,
two-peer/rematch result or comparative preference is inferred.
The new mode is not in the batch scanner; archived v17 remains 59 primary/
29 filtered versions.

The subsequent [v18 audit](nds-compatibility-audit-v18.md) integrates the accepted
late-enable/live-depth mode only after the plain route's explicit activation
failure. SF2 VS raises primary packed songs to 60, exactly matching its accepted
ROM/BPS. All 59 prior primary and 29 filtered pairs remain identical; 323 tests
and report/filter/archive checks pass. There are 26 exact accepted primary
versions and 31 unique accepted sequences across both routes. Filtered counts
stay 29 packed/eleven accepted/eighteen pending. It adds no runtime or manual
acceptance; archived v17 remains separate. Variable-tempo SF2 MIZUUMI is the next
bounded capability candidate.

The subsequent [SF2 MIZUUMI experiment](nds-sf2-mizuumi-variable-tempo-research.md)
adds explicit zero-delay LFO frequency compensation across six source tempos.
Independent source execution matches 4,217 notes, 24 waves and 25 E1 controls;
native playback reaches two common cycles, 75,440 LFO states and 22 actual
tempo-rate windows. All 333 tests and 38 accepted/two control ROM/BPS rebuilds
pass. On 2026-10-20 the user reported this exact ROM passed the requested
three-minute battle/effects/three-encounter checklist. No independently timed
trace, two-peer/rematch result or comparative preference is inferred. The new mode is not in the batch scanner; archived v18 remains
60 primary/29 filtered versions.

The subsequent [v19 audit](nds-compatibility-audit-v19.md) integrates only the
accepted fixed zero-delay variable-tempo route after its explicit fixed-tempo
failure. Primary counts rise to 61 packed and 27 exact accepted; old 60 primary
and 29 filtered ROM/BPS pairs remain identical. Filtered counts stay 29/11/18;
32 unique source sequences have an exact accepted variant. All 132 slots are
scanned using six verified ROM variants and three unchanged pinned family
archives. The local second SF2 input now has an unregistered fingerprint and a
differing SDAT; it is excluded without changing source files or verification
policy. Of 339 tests, 338 pass and that verified-variant equivalence test is
explicitly skipped. Report and archive checks add no native or manual tests.
The remaining three in-capacity conversion blockers are the SABISHI songs;
SF1's combination of variable tempo, late first activation and fitted attacks
is a separate prospective experiment.

The separate [SF1 SABISHI experiment](nds-sf1-sabishi-variable-late-envelope-research.md)
combines variable tempo, late first activation and bounded fitted attacks only
through explicit options. Independent reference, natural two-cycle playback,
actual allocation-aware LFO states, envelopes, tempo rates, resources and old
ROM/BPS rebuilds pass. Of 344 cases, 343 pass and one unavailable verified second
SF2 input check is skipped. The exact native-tested ROM reproduces through the
production CLI; the user reported the exact-ROM three-item listening/effects/lifecycle checklist
passed on 2026-10-20. This adds no independently timed trace, linked-play/rematch
result or comparative preference. This separate
extension does not alter archived v19 counts or enter the batch scanner.

The [v20 audit](nds-compatibility-audit-v20.md) integrates the accepted variable
late-enable/fitted-attack capability after an explicit envelope/LFO fixed-tempo
failure. Three SABISHI slots become packable: 64 primary variants, 28 exact
accepted primary variants, 33 unique accepted sequences. All 61 prior primary
and 29 filtered pairs retain their bytes, routes and gains. The 58 remaining
primary blockers all exceed eight tracks. The scan retains its six-source
selection; independent current verification checks all seven originals after
the second SF2 source again matches its registered fingerprint and SDAT. All
350 tests pass without skips. Historical v19 restrictions remain recorded.
Batch counts and exact standalone listening/gameplay acceptance stay separate.

A source-only investigation of eleven nine-track blockers finds that SF2 HOKORA
admits 21 pair-merging configurations through the existing plain converter's
control compatibility checks. This has no packed ROM, native playback or manual
acceptance yet; all other nine-track candidates still fail existing constraints.
It is a bounded next investigation after completing the standalone SF3 check.

The separate [SF3 SABISHI experiment](nds-sf3-sabishi-variable-late-envelope-research.md)
validates its distinct source note gates using the existing explicit capability.
Independent reference, native full-loop/all-sample playback, actual NOTE allocation
and LFO states, envelope steps, tempo rates, resources and controlled helper
lifecycle checks pass. All 352 tests and forty accepted/two control ROM/BPS pairs
pass, and all eight production outputs reproduce exactly. On 2026-10-21 the user reported the final exact-ROM listening/effects/three-
encounter checklist passed. No independent timing, full gameplay trace, linked-
play/rematch result or comparative preference is inferred; archived v20 family-
specific acceptance counts remain unchanged.

The separate [SF2 HOKORA nine-track experiment](nds-sf2-hokora-nine-track-research.md)
selects merged tracks 0/4 with fixed equal volume and neutral pan. The original
nine-track schedule and note velocities match an unpacked singleton control;
compiled and actual native per-note priorities stay distinct. Independent source
reference, natural two-cycle/all-sample playback, actual NOTE allocations and
native gate/key/velocity/priority fields, resource and controlled effects/
lifecycle checks pass. All 354 tests, 41 accepted/two control ROM/BPS rebuilds
and eight-file production reproduction pass. On 2026-10-21 the user reported the final exact-ROM listening/effects/three-
encounter checklist passed. No independent timed recording, full gameplay trace,
linked-play/rematch result or comparative preference is inferred. It adds no generic
batch grouping; archived v20 counts and constraints remain unchanged.

The [v21 audit](nds-compatibility-audit-v21.md) adds only the accepted fixed SF2
HOKORA grouping, retaining ordinary control/conversion guards without group
search. All seven original ROM variants and pinned family SDATs verify. Primary
packing rises to 65, with 30 exact accepted primary variants and 35 unique
accepted sequences; all 64 old primary and 29 filtered pairs keep their bytes,
routes and gains. Primary pending is 35 and all 57 primary blockers exceed eight
tracks. Filtered counts remain 29/11/18. All 360 tests and report/filter/archive
checks pass. SF3 SABISHI's exact acceptance updates its manual match, not its
conversion status. No new native playback or manual acceptance is established
by this batch scan. Source-only grouping investigation selects SF3 KINCHO as a
separate prospective ten-to-eight experiment.

The separate [SF3 KINCHO ten-track experiment](nds-sf3-kincho-ten-track-research.md)
groups equal-volume sources 2/4/6, retaining the moving source's note-on pan.
All ten original source schedules and note velocities match an unpacked ten-
track control. Independent reference, natural two-cycle/all-sample playback,
actual NOTE allocation and gate/key/velocity/priority fields, opposing stereo
observations, packed resources and controlled effects/lifecycle checks pass.
All 362 tests, 42 accepted/two control ROM/BPS rebuilds and eight-file production
reproduction pass. On 2026-10-22 the user reported the final exact-ROM listening/effects/three-
encounter checklist passed. No independent timing, full gameplay trace, linked-
play/rematch result or comparative preference is inferred; it adds no generic batch grouping or rewrite
of archived v21 counts.

The [v22 audit](nds-compatibility-audit-v22.md) adds only the accepted fixed SF3
KINCHO grouping under original control/conversion guards, without automatic
search. All seven original variants and pinned SDATs verify. Primary packing
rises to 66, with 31 exact accepted primary variants and 36 unique accepted
sequences; all 65 old primary and 29 filtered pairs retain bytes, routes, gains
and manual matches. Primary pending remains 35 and all 56 primary blockers exceed
eight tracks. Filtered counts remain 29/11/18. All 368 tests and report/filter/
archive checks pass. A separate DEMPAJIKEN experiment studies two equal-volume
groups and a long-note alias, retaining native budget rejections as a limit.
This batch scan establishes no new native playback or manual acceptance.

The separate [SF3 DEMPAJIKEN eleven-track experiment](nds-sf3-dempajiken-eleven-track-research.md)
uses two equal-volume groups, source-note pan and a long-note alias. All original
schedule events remain; 999 native calls produce 996 allocations and three
lowest-priority accompaniment rejections under the ten-voice budget. Original
long-note holds/releases and a separate modified-score EOT-isolation diagnostic
pass, with scopes kept distinct. Independent reference, natural full-loop/all-
sample playback, allocated note fields, stereo, resources and controlled helper
checks pass within those recorded limits. All 370 tests, 43 accepted/two control
ROM/BPS rebuilds and eight-file production reproduction pass. On 2026-10-22 the user reported the exact-ROM
listening/effects/three-encounter checklist passed, explicitly finding the
known accompaniment omission inaudible. No independent timing, full gameplay
trace, linked-play/rematch result or comparative preference is inferred; v22 counts are
not rewritten and no generic batch grouping is added.

The [v23 audit](nds-compatibility-audit-v23.md) adds only the accepted fixed SF3
DEMPAJIKEN eleven-to-eight grouping, retaining control, pan, alias/release and
conversion guards without search. All seven originals and pinned SDATs verify.
Primary packing rises to 67, with 32 exact accepted primary variants and 37
unique accepted sequences; all 66 old primary and 29 filtered ROM/BPS pairs
retain bytes, routes, gains and manual matches. Primary pending stays 35, and
all 55 remaining primary blockers exceed eight tracks. Filtered counts remain
29/11/18. All 376 tests and report/filter/archive checks pass. Reports retain
the separately measured standalone native allocation limit and the user's
inaudible-omission report; the scan adds no native or manual acceptance.
A separate BOSSMAE twelve-track experiment remains outside batch grouping.

The separate [SF3 BOSSMAE twelve-track experiment](nds-sf3-bossmae-twelve-track-research.md)
uses three equal-volume groups under unchanged conversion guards. Independent
source checks, natural two-cycle/all-sample playback, all 1,514 allocated NOTE
field checks, source-7 stereo contrast and controlled helper checks pass.
Pre-unlink observations record no held/starting channel preemption but 905
release-channel reuses with nonzero envelope; tail-shortening remains a manual
listening limit, not a measured audible-error count. All 378 tests, 44 accepted/
two control ROM/BPS rebuilds and eight-file production reproduction pass.
On 2026-10-22 the user reported the exact-ROM listening/effects/three-encounter checklist passed; no independent timing, full gameplay trace, linked-play/rematch result or comparative preference is inferred; v23
counts are not rewritten and no generic grouping search is added.

The [v24 audit](nds-compatibility-audit-v24.md) adds only the accepted fixed SF3
BOSSMAE twelve-to-eight grouping under unchanged control/conversion guards,
without search. All seven originals and pinned SDATs verify. Primary packing
rises to 68, with 33 exact accepted primary variants and 38 unique accepted
sequences; all 67 old primary and 29 filtered ROM/BPS pairs retain bytes, routes,
gains and manual matches. Primary pending stays 35, and all 54 remaining primary
blockers exceed eight tracks. Filtered counts remain 29/11/18. All 384 tests and
report/filter/archive checks pass. Native budget observations remain attributed
to the standalone ROM, not remeasured by the scan; there is no new native or
manual acceptance. A separate thirteen-track CHANGE experiment remains outside
batch grouping.

The separate [SF3 CHANGE thirteen-track experiment](nds-sf3-change-thirteen-track-research.md)
uses existing fixed-volume ratio mapping without relaxing shared controls. All
855 source tuples and duplicate-note multiplicity remain; the independent
reference matches 5,070 notes and twenty unique waves. Intro-only reference
validation now requires exact initial notes and sufficient silent-loop duration
plus independent controls, with negative tests. Natural playback covers two
common cycles and all 25 prepared waves. All 1,339 NOTE calls allocate, but four
held/starting channels are preempted in the intro and 183 release channels are
reused; manual listening must judge those limits and velocity quantization.
Original alias holds/releases and native pitch/pan checks pass. All 390 tests,
45 accepted/two control ROM/BPS rebuilds and eight-file production reproduction
pass. On 2026-10-22 the user reported the exact-ROM listening/effects/three-encounter
checklist passed; no independent timing, full gameplay trace, linked-play/rematch
result or comparative preference is inferred; no
generic batch grouping or rewrite of archived v24 counts is added.

The [v25 audit](nds-compatibility-audit-v25.md) adds only the accepted fixed SF3
CHANGE thirteen-to-eight grouping under unchanged control/conversion guards
and existing fixed-volume ratio mapping, without search. All seven originals
and pinned SDATs verify. Primary packing rises to 69, with 34 exact accepted
primary variants and 39 unique accepted sequences; all 68 old primary and 29
filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Primary
pending stays 35; all 53 remaining primary blockers exceed eight tracks.
Filtered counts remain 29/11/18. All 396 tests and report/filter/archive checks
pass. Native preemptions, tail reuse and velocity quantization remain explicit
and attributed to the exact standalone ROM, with no new native/manual acceptance.
A separate fourteen-track AJITO experiment remains outside batch grouping.

The separate [SF3 AJITO fourteen-track experiment](nds-sf3-ajito-fourteen-track-research.md)
uses existing fixed-volume ratios and four long aliases under unchanged guards.
All 2,472 source tuples remain; the reference matches 4,477 notes and 27 unique
waves. Natural playback covers two common cycles through about 2:44 and all 33
prepared waves. All 3,964 NOTE calls allocate, but fourteen held/starting voices
are preempted and 1,544 release channels are reused; manual listening must judge
those limits and velocity quantization. Fifteen alias holds/releases, 391,120
control-byte checks, independent dynamics, stereo and clock-rate checks pass.
All 398 tests, 46 accepted/two control ROM/BPS rebuilds and eight-file production
reproduction pass. On 2026-10-22 the user reported the exact-ROM listening/effects/three-encounter
checklist passed; no independent timing, full gameplay trace, linked-play/rematch
result or comparative preference is inferred; no generic batch grouping or rewrite of archived v25 counts is added.

The [v26 audit](nds-compatibility-audit-v26.md) adds only the accepted fixed SF3
AJITO fourteen-to-eight grouping under unchanged guards and existing fixed-
volume ratio mapping, without search. All seven originals and pinned SDATs
verify. Primary packing rises to 70, with 35 exact accepted primary variants
and 40 unique accepted sequences; all 69 old primary and 29 filtered ROM/BPS
pairs retain bytes, routes, gains and manual matches. Primary pending stays35;
all 52 remaining primary blockers exceed eight tracks. Filtered counts remain
29/11/18. All 404 tests and report/filter/archive checks pass. Native preemptions,
tail reuse and quantization remain explicitly attributed to the standalone
ROM, with no new native/manual acceptance. A separate fifteen-track STUDIO
experiment remains outside batch grouping.

The separate [SF3 STUDIO fifteen-track experiment](nds-sf3-studio-fifteen-track-research.md)
uses existing fixed-volume ratios and two long aliases under unchanged guards.
All 3,431 source tuples remain; the reference matches6,936 notes and 22 unique
waves. Natural playback covers two common cycles and all 23 prepared waves.
All 5,202 NOTE calls allocate, with no held/starting preemption but 2,863 release
channels reused. Four extremely soft mappings are already zero in the unpacked
control; grouping adds none. Twenty-four long-alias uses, 320,840 control-byte
comparisons, held-voice crescendo, stereo and clock-rate checks pass. All 406
tests, 47 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass.
The user reported the requested exact-ROM listening/effects/three-encounter
checks passed on 2026-10-22; the recorded limits remain. This adds no generic
batch grouping or rewrite of archived v26 counts.

The [v27 compatibility audit](nds-compatibility-audit-v27.md) integrates only the accepted fixed SF3 STUDIO fifteen-to-eight grouping under existing guards and volume-ratio quantization. All seven originals and pinned SDATs verify. Across 132 slots, primary packing rises to 71, with 36 exact accepted primary versions and 41 unique accepted sequences. All 70 old primary and 29 filtered ROM/BPS pairs retain bytes, routes, gains and manual matches; 51 primary capacity blockers remain. All 412 tests and report/filter/archive checks pass. Reports attribute the standalone voice-reuse and existing zero-velocity limits to its exact ROM; the scan adds no native or manual acceptance.

The separate [SF3 BOSSMAE merged-antialias experiment](nds-sf3-bossmae-merged-antialias-research.md) combines its accepted twelve-to-eight grouping with existing per-source-key offline filtering under an explicit plain-loop flag. All 974 mappings and 3,825 playback commands remain intact apart from relocated GOTO pointers; natural playback covers two cycles and all 81 prepared waves. All 1,514 NOTE calls allocate, with no held/starting preemption and 905 release-channel reuses. Prepared PCM8 clipping (4,763 stored points, about0.93%) remains explicit and requires listening judgment. All 416 tests and 48 accepted/two control ROM/BPS rebuilds pass. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-22; comparative timbre preference was not separately reported. Recorded limits and archived v27 counts remain unchanged.

The [v28 compatibility audit](nds-compatibility-audit-v28.md) adds only the accepted SF3 BOSSMAE merged-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 old primary and29 old filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to30 packed and12 exact accepted, with18 pending and92 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All422 tests and report/filter/archive checks pass. Standalone tail-reuse and clipping observations remain explicitly attributed; scanning adds no native or manual acceptance.

The separate [SF3 STUDIO upward-antialias experiment](nds-sf3-studio-upward-antialias-research.md) prepares per-source-key filtered waves at conservative positive-pitch ceilings while retaining original notes and bend/expression commands. All3,431 mappings and14,149 commands remain intact apart from GOTO pointer relocation; natural playback covers two cycles and all131 waves. All5,202 NOTE calls allocate, with no held/starting preemption,2,866 release-channel reuses and115 slot choices different from the plain baseline. All427 tests,49 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Nominal-cutoff, clipping, extreme-soft-note and voice-budget limits remain explicit. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-22; comparative timbre preference was not separately reported. Recorded limits and archived v28 counts remain unchanged.

The [v29 compatibility audit](nds-compatibility-audit-v29.md) adds only the accepted STUDIO upward-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 old primary and30 old filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to31 packed/13 exact accepted, with18 pending and91 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All433 tests and report/filter/archive checks pass. Nominal cutoff metadata is conversion-derived; voice reuse and extreme-soft-note observations remain attributed to the exact standalone ROM. Scanning adds no native or manual acceptance.

The separate [SF3 AJITO upward-antialias experiment](nds-sf3-ajito-upward-antialias-research.md) applies existing preparation modes to its accepted fourteen-to-eight grouping without new converter/native capability. All2,472 mappings and14,177 playback commands remain intact apart from GOTO relocation; natural playback covers two cycles and all221 prepared waves. All3,964 NOTE calls allocate. The fourteen held-preemption clocks/displaced identities match the plain baseline; release reuses rise1544→1551 and718 slot choices differ. Four long aliases, changing expression/volume, native stereo and frame-clock checks pass within those limits. All435 tests,50 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Prepared clipping and voice/quantization limits remain explicit. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-23; comparative timbre preference was not separately reported. Recorded limits and archived v29 counts remain unchanged.

The [v30 compatibility audit](nds-compatibility-audit-v30.md) adds only the accepted AJITO upward-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 old primary and31 old filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to32 packed/14 exact accepted, with18 pending and90 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All441 tests and report/filter/archive checks pass. Fourteen held preemptions and tail/clipping limits remain attributed to the exact standalone ROM and checked against its saved proof. Scanning adds no native or manual acceptance.

The separate [SF3 CHANGE upward-antialias experiment](nds-sf3-change-upward-antialias-research.md) applies existing preparation modes at shifts up to12 semitones without new converter/native capability. All855 mappings and5,599 playback commands remain intact apart from GOTO relocation; natural playback covers two cycles and all78 waves. All1,339 NOTE calls allocate; source9 retains six intro calls with no loop repetition. Four held-preemption clocks/displaced identities match the plain baseline; release reuses rise183→188 and159 slot choices differ. The long alias retains actual held-voice pitch/pan changes. All443 tests,51 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Conservative bandwidth, clipping and voice/quantization limits remain explicit. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-23; comparative timbre preference was not separately reported. Recorded limits and archived v30 counts remain unchanged.

The [v31 compatibility audit](nds-compatibility-audit-v31.md) adds only the accepted CHANGE upward-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 old primary and32 old filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to33 packed/15 exact accepted, with18 pending and89 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All449 tests and report/filter/archive checks pass. Four held preemptions, six intro-only source9 calls and tail/clipping limits remain attributed to the exact standalone ROM and checked against saved proof. Scanning adds no native or manual acceptance.

The separate [SF2 HOKORA merged-antialias experiment](nds-sf2-hokora-merged-antialias-research.md) applies existing filtering to its accepted nine-to-eight grouping without new converter/native capability. All1,014 mappings and4,360 playback commands remain intact apart from GOTO relocation; natural playback covers two cycles and all81 waves. All1,555 NOTE calls allocate with no held/starting preemption. A fresh read-only exact-plain-ROM baseline has385 release reuses versus384 filtered;354 slot choices differ. Dynamic expression, actual held-channel crescendos, settled-frame stereo and emulated frame-clock checks pass. All451 tests,52 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Prepared clipping and voice/quantization limits remain explicit. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-23; comparative timbre preference was not separately reported. Recorded limits and archived v31 counts remain unchanged.

The [v32 compatibility audit](nds-compatibility-audit-v32.md) adds only the accepted SF2 HOKORA merged-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 prior primary and33 prior filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to34 packed/16 exact accepted, with18 pending and88 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All457 tests and report/filter/archive checks pass. Attributed tail reuse and clipping limits are checked against the exact standalone proof and a fresh read-only plain-ROM baseline. Scanning adds no native or manual acceptance.

The separate [SF3 KINCHO upward-antialias experiment](nds-sf3-kincho-upward-antialias-research.md) applies existing preparation modes to its accepted ten-to-eight grouping without new converter/native capability. All741 mappings and3,469 playback commands remain intact apart from GOTO relocation; natural playback covers two cycles and all108 waves. All1,194 NOTE calls allocate with no held/starting preemption. A fresh read-only exact-plain-ROM baseline has476 release reuses versus477 filtered;175 slot choices differ. Native control bytes, actual short held-note bend changes, settled merged-source stereo and emulated frame-clock checks pass. All459 tests,53 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Conservative cutoff, storage clipping and voice/quantization limits remain explicit. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-23; comparative timbre preference was not separately reported. Recorded limits and archived v32 counts remain unchanged.

The [v33 compatibility audit](nds-compatibility-audit-v33.md) adds only the accepted KINCHO upward-antialias configuration under pinned identity, structure and existing guards. All seven originals and pinned SDATs verify across132 slots. All71 prior primary and34 prior filtered ROM/BPS pairs retain bytes, routes, gains and manual matches. Filtered totals rise to35 packed/17 exact accepted, with18 pending and87 blocked; primary totals stay71 packed/36 exact accepted, and unique accepted sequences stay41. All465 tests and report/filter/archive checks pass. Attributed tail reuse and clipping limits are checked against the exact standalone proof and a fresh read-only plain-ROM baseline. Scanning adds no native or manual acceptance.

The separate [SF3 DEMPAJIKEN merged-antialias experiment](nds-sf3-dempajiken-merged-antialias-research.md) applies existing filtering to its accepted eleven-to-eight grouping without new converter/native capability. All584 mappings and2,396 playback commands remain intact apart from GOTO relocation; natural playback covers two cycles and all96 waves. Of999 NOTE calls,996 allocate and three are rejected at the same source14 identities/clocks as a fresh exact-plain-ROM baseline. Three held/starting preemptions retain displaced source15 identities; release reuses rise522→532 and383 slot choices differ. Original long-alias holds/releases, native controls, settled merged-source stereo and emulated frame-clock checks pass within those explicit limits. All467 tests,54 accepted/two control ROM/BPS rebuilds and eight-file reproduction pass. Prepared clipping and voice/quantization limits remain. The user reported the requested exact-ROM listening/effects/three-encounter checks passed on 2026-10-23; comparative timbre preference was not separately reported. Recorded native limits and archived v33 counts remain unchanged.
