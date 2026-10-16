# Star Force 1/2/3 compatibility audit

The updated batch audit covers every SSEQ slot in the three pinned Japanese
Star Force archives. Forty-two candidates pass conversion, independent MPlay
reparsing, shared EXE6 packing and BPS reconstruction. The exclusive success
categories are 24 standard, four LFO-only, one envelope-only, three envelope
plus LFO, six fixed delayed-LFO and four envelope plus fixed delayed-LFO.
These are automated resource/export results; this run performs no new gameplay
or listening tests and does not enable NDS songs in the manager.

Report directory: `out/nds-research/compatibility-audit-v5/` (schema 3):

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
   per-track delayed modulation after activation at the first note timestamp;
   later activation or parameter changes remain rejected. Delays map to
   LFODL with the existing one-tick zero-phase onset and must fit 1..255.
7. The existing verified Star Force 3 BATTLE mapping is the only over-capacity
   exception. Other songs do not receive guessed merges or dropped tracks.

Successful conversion resources pass through the same exporter as the
single-song experiments: dependency relocation, native-data preservation,
output bounds and BPS reconstruction. The pack step was extracted into
`pack_converted_experiment`; all six previously accepted artifacts rebuild
byte-identically after that refactor. The batch writes reports only, retaining
ROM/BPS fingerprints rather than creating forty-two new ROM files.
All 32 previously packed v4 variants retain their exact ROM and BPS fingerprints.
The v2/v3/v4 snapshots are preserved separately.

Configuration: original Japanese EXE6 Gregar, eight music tracks, ten PCM
voices at native 10,512 Hz, +3.5 dB imported gain, title/ordinary ID 21/
communication scene pools. A headroom failure can retry the same route at
neutral gain with an explicit record; none of the forty-two successes needed
that retry in this run. Gain and voice allocation are not calibrated by the
audit. Standard conversion still includes PCM8/envelope/tempo approximations.

Only SSEQ is scanned. The archives also contain three SSAR slots (one per
game) and four STRM slots (2/1/1); their contents are outside this conversion
audit. Counts are per `(game, sequence ID)`, so reused tunes across games are
counted separately, not asserted to be distinct musical compositions.

## Coverage

| Game | SSEQ slots | Candidates | Standard | LFO | Envelope | Envelope + LFO | Delayed LFO | Envelope + delayed LFO | Blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Star Force 1 | 38 | 35 | 14 | 4 | 0 | 0 | 4 | 0 | 13 |
| Star Force 2 | 43 | 40 | 5 | 0 | 0 | 2 | 2 | 3 | 28 |
| Star Force 3 | 51 | 47 | 5 | 0 | 1 | 1 | 0 | 1 | 39 |
| Total | 132 | 122 | 24 | 4 | 1 | 3 | 6 | 4 | 80 |

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

The envelope-only pass is Star Force 3 `10 BGM_HOKORA`. The combined passes
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

- Star Force 1: `2 FMPLANET`, `10 DEMPA`, `12 TRUCK`, `29 LASTBOSS`.
- Star Force 2: `1 TEKI`, `27 BATTLE`.

The envelope plus fixed delayed-LFO pass list is:

- Star Force 2: `2 BURAI`, `5 SKI`, `38 WIFI`.
- Star Force 3: `24 BURAI`.

FMPLANET matches the accepted [fixed-delay experiment](nds-delayed-lfo-research.md).
The other nine newly packed variants still need song-specific reference,
runtime and listening validation; this scan supplies packing evidence only.

Ten packed variants are byte-identical to artifacts with structured
user-reported manual acceptance: Star Force 1 FMPLANET/LAST/KINCHO/BATTLE-LFO,
Star Force 2 NESSIE/WIN and Star Force 3 HOKORA/FRIEND/KANDO/BATTLE. This matching
does not create new manual evidence. The earlier accepted Star Force 3 ROOM
build uses title-only rules and its original priority policy, so the uniformly
configured audit variant is not marked as that previously accepted artifact.
Its historical title listening result remains in the ROOM research.

JSON rows and attempts record separate envelope/LFO/fixed-delay flags. Envelope
rows retain attack fitting errors and method limitations; LFO rows retain their
configs, including delay rounding/counter timing where enabled. CSV exposes all
three flags, attack fits and delay mappings; HTML offers separate status filters
for all six success categories. `summary.md` counts the categories exclusively;
combined rows must not be added twice when discussing envelope/LFO coverage.
The earlier envelope audit regressions cover envelope/combined selection,
manual matching and CSV/summary classification, unnecessary route exclusion
and failed fitting remaining blocked. The over-capacity fixture also includes
envelope/delay features to verify they do not authorize guessed merges. Three
new audit tests cover delay/combined route and report selection, active delay
set after the last note at the same tick, and rejected live changes never
counting as packing success.

## Blockers and next priorities

The primary result categories are exclusive:

| Result | Count | Meaning |
| --- | ---: | --- |
| Capacity blocked | 58 | More than eight source tracks and no registered mapping |
| Conversion blocked | 21 | Current control, envelope, timing or compiler preconditions reject every attempted route |
| Converter model blocked | 0 | All eight earlier boundary assertions are resolved |
| Execution analysis blocked | 1 | Bounded source execution cannot complete |

Source features can overlap these categories. Among blocked candidates,
21 use non-instant instrument attacks, 28 execute envelope overrides, 45
contain gates above 223 ticks, and 18 have modulated note states with a
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
v4 run passed all 167 tests, and the current v5 run passes all 181 Python
regression tests.
The generated report's JavaScript passes the Node syntax check.

Each of the eight recovered songs also has a 180-second independent software
DS reference in `out/nds-research/loop-boundary-validation-v1/`. Source notes
cover at least two complete loops on every track; notes, pan/bend/expression
controls and decoded PCM16 samples match. Per-song `validation.json` files
record the renderer command and source/resource fingerprints; the root file
collects the results and renderer fingerprint. This is source execution and
resource evidence, not new GBA runtime or listening acceptance.

The next song-specific validation can target Star Force 2 BATTLE, a newly
packed eight-track fixed-delay candidate. Remaining delay-route rejections
include activation after the first note timestamp (Star Force 1 GOWAIINCHO,
PLANETARIUM, BOSS and Star Force 2 KAICYOU), and changing delayed modulation
settings (Star Force 1 HOMETOWN/LOSE, Star Force 2 LOSE/VS and Star Force 3
LOSE). These restrictions have not been relaxed by the scan. Star Force 1
HOKORA remains a bounded source-parser investigation.
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
