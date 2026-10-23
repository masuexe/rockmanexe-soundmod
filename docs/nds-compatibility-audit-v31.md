# NDS compatibility audit v31: accepted CHANGE upward antialias preparation

The filtered scanner adds only the accepted CHANGE configuration under route
`known_sf3_change_upward_antialias`. It requires family `ssr3`, slot47,
capacity eight, exactly source IDs0–9/13/14/15, all tracks looping, no fitted
attack and no active modulation. It uses `SF3_CHANGE_GROUPS` with both explicit
merged-filter and upward-preparation flags. Existing grouping/control,
fixed-volume, held-pan, alias/release, unsupported-effect, one-octave/key,
sample-budget and model guards remain. No group search or fitted retry is
introduced for this pinned route.

All seven originals and three pinned SDATs verify before and after all132
slots. Only the filtered status of `ssr3:47` changes. Its ROM/BPS exactly match
the [accepted standalone experiment](nds-sf3-change-upward-antialias-research.md):

- ROM CRC32: `B8944A0E`.
- ROM SHA-256: `3fe1e8918677ceafe0f5f6b9b4704c6fe8c42dc416e1a7634b666cb3e31b0774`.
- BPS SHA-256: `33ce38337a99b6c1c9da6177e9d7d763ce4979f93af303137dfc90e0a39fa594`.

All71 prior primary and32 prior filtered ROM/BPS pairs retain bytes, routes,
gains and exact-manual-match flags. Primary counts remain71 packed,36 exact
accepted,35 pending and51 capacity-blocked. Filtered packing rises32→33 and
exact accepted matches14→15, with18 pending and89 blocked. Unique source
sequences with an exact accepted variant remain41. Acceptance requires the
exact version; song names do not transfer acceptance.

All449 tests pass without skips, including six new scanner cases covering
identity/structure/groups, both flags, retained conversion/model guards,
headroom/packing failures, exact-version acceptance, metadata scopes and
primary/filtered accounting. Validation checks exact accepted ROM/BPS and
manifests, old packed identities, original inputs, source/scanner hashes,
deterministic reports, actual JavaScript filters and recursive v10–v30 archive
identities. The upward-preparation filter selects STUDIO, AJITO and CHANGE;
the merged-filter selector selects those plus BOSSMAE. Prior structure filters
retain their counts. CSV/JSON distinguish conversion-derived preparation
metadata from attributed standalone observations.

Conversion recomputes78 prepared waves:58 with shift0, seven with shift9,
eight with shift6, two with shift12 and three with shift1. Shared physical
wave/root/source-key identities use the maximum bound across source uses.
Maximum nominal FIR cutoff at the bound is about0.9001623 of mixer Nyquist,
including loop/tuning rounding. This is not a brick-wall, zero-aliasing or
audible-error bound. Existing guards reject shifts over twelve semitones and
preparation-key overflow without clamping. Conservative preparation can reduce
bandwidth during unbent notes.

The report attributes1,339 allocated NOTE calls, four held/starting preemptions,
188 nonzero-envelope release reuses and159 slot choices different from the
plain baseline to the exact standalone ROM. Preemption clocks352/360/372/376
and displaced source/note/key/gate identities match the plain baseline.
Source9 has exactly six intro NOTE calls and none after the common entry in
the original two-cycle window. The validator checks saved native and baseline
proofs. Prepared clipping is1,043 of646,861 stored points; no native
zero-velocity NOTE call is observed in that window. Storage counts are not
time-weighted playback or an audible-error bound. Ten-voice truncation/tail
reuse, clipping and PCM8/ADSR/tempo quantization remain explicit.

The scan adds no native playback or manual test. The user reported the
standalone listening/effects/three-encounter checks passed; comparative timbre
preference was not separately reported. Independent timing, a full gameplay
trace, linked play and rematch remain outside that report.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v31
```

Use a fresh directory. ROMs, original assets and local outputs stay outside
Git. Historical artifacts and coverage remain immutable.
