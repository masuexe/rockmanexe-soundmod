# NDS compatibility audit v30: accepted AJITO upward antialias preparation

The filtered scanner adds only the accepted AJITO configuration under route
`known_sf3_ajito_upward_antialias`. It requires family `ssr3`, slot7, capacity
eight, exactly source IDs0–11/14/15, all tracks looping, no fitted attack and
no active modulation. It uses `SF3_AJITO_GROUPS` and both explicit merged-filter
and upward-preparation flags. Existing control/grouping, fixed-volume,
held-pan, alias/release, unsupported-effect, one-octave/key, sample-budget and
model guards remain. There is no group search or expansion to other
unaccepted over-capacity songs. Failures remain visible; the pinned route
cannot silently retry with fitted attacks.

All seven originals and three pinned SDATs verify before and after all132
slots. Only the filtered status of `ssr3:7` changes. Its ROM/BPS exactly match
the [accepted standalone experiment](nds-sf3-ajito-upward-antialias-research.md):

- ROM CRC32: `FC4C77A2`.
- ROM SHA-256: `1b535b22c63f0da416d55355c63f12c0af3172adab5c68f786119a71312d341c`.
- BPS SHA-256: `24e2ce46c751ac121dce5071012cb848f649258cbe5f39b56f79e0ce085fedf8`.

All71 old primary and31 old filtered ROM/BPS pairs retain bytes, routes, gains
and exact-manual-match flags. Primary counts remain71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered packing rises31→32 and exact
accepted matches13→14, with18 pending and90 blocked. Unique source sequences
with an exact accepted variant remain41; this is an alternate version of an
already accepted source. Acceptance does not transfer by song name.

All441 tests pass without skips, including six new scanner cases for pinned
identity/structure/groups, both explicit flags, retained conversion/model
failures, headroom/packing, exact-version acceptance, metadata scopes and
primary/filtered accounting. Validation checks accepted ROM/BPS and manifests,
old packed identities, original inputs, source/scanner hashes, deterministic
reports, actual JavaScript filters and unchanged recursive v10–v29 archive
identities. The upward-preparation filter selects STUDIO and AJITO; the
merged-filter selector selects both plus BOSSMAE. Prior structure filters
retain their counts. CSV/JSON keep conversion-derived preparation policy and
attributed standalone native observations separate.

Conversion recomputes221 prepared waves:183 with shift0,34 with shift1 and
four with shift2. Shared physical wave/root/source-key identities take the
maximum bound across source uses. Maximum nominal FIR cutoff at the bound is
about0.900246 of mixer Nyquist, including loop/tuning rounding. This is not a
brick-wall, zero-aliasing or audible-error bound. Existing guards still reject
shifts over twelve semitones and preparation-key overflow without clamping.

The report attributes3,964 allocated NOTE calls, fourteen held/starting
preemptions,1,551 nonzero-envelope release reuses and718 slot choices different
from the plain baseline to the exact standalone ROM. All fourteen clocks and
displaced source/note/key/gate identities match the plain-baseline observation;
the validator checks those claims against the saved exact-ROM native proof.
Prepared clipping is9,275 of1,969,559 stored points; no native zero-velocity
NOTE call is observed in that window. The scan does not remeasure native
playback or add manual acceptance. Storage counts are not time-weighted
playback or an audible-error bound. Held-note truncation, tail reuse, clipping
and PCM8/ADSR/tempo quantization remain explicit. The user reported the
requested listening/effects/three-encounter checks passed; comparative timbre
preference was not separately reported. No independently timed recording,
full gameplay trace, linked play or rematch is inferred.

A separate filtered CHANGE experiment studies the existing intro-only sounding
track and held-note pitch/pan sweep at larger preparation shifts. It remains
outside this scan and requires a new exact-ROM checklist.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v30
```

Use a fresh directory. ROMs, original assets and local outputs stay outside
Git. Historical artifacts and coverage remain immutable.
