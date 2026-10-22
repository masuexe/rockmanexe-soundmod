# NDS compatibility audit v29: accepted STUDIO upward antialias preparation

The filtered scanner adds only the accepted STUDIO configuration under route
`known_sf3_studio_upward_antialias`. It requires family `ssr3`, slot4, capacity
eight, exactly source IDs0–12/14/15, all tracks looping, no fitted attack and
no active modulation. It uses `SF3_STUDIO_GROUPS` and both explicit merged-
filter and upward-preparation flags. Existing grouping, shared-control,
fixed-volume, held-pan, long-alias/release, preparation-key/one-octave,
unsupported-effect, sample-budget and conversion guards remain. There is no
group search or expansion to other over-capacity songs. Failures remain
visible; the pinned route cannot silently retry with fitted attacks.

All seven originals and three pinned SDATs verify before and after all132
slots. Only the filtered status of `ssr3:4` changes. Its ROM/BPS exactly match
the [accepted standalone experiment](nds-sf3-studio-upward-antialias-research.md):

- ROM CRC32: `C5EE00C5`.
- ROM SHA-256: `02a180120dfd02e4e4e6f16ab6ae1bd38c02c1b72f44a7ed1c607aa8776a82d4`.
- BPS SHA-256: `6fa7f736a7deb4e6db3dceee5b97a85d82eadb9dcfcc94ec6035e123ff09dc2e`.

All71 old primary and30 old filtered ROM/BPS pairs retain bytes, routes, gains
and exact-manual-match flags. Primary counts remain71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered packing rises30→31 and exact
accepted matches12→13, with18 pending and91 blocked. Unique source sequences
with an exact accepted variant remain41; this is an alternate version of an
already accepted source. Acceptance does not transfer by song name.

All433 tests pass without skips, including six new scanner cases for exact
identity/structure/groups, both explicit flags, retained conversion/model
failures, headroom/packing, exact-version acceptance, metadata scopes and
primary/filtered accounting. Validation checks accepted ROM/BPS and manifests,
all old packed identities, original inputs, source/scanner hashes,
deterministic reports, actual JavaScript filters and unchanged recursive
v10–v28 archive identities. The upward-preparation filter selects STUDIO alone;
the merged-filter selector selects STUDIO and BOSSMAE. Prior filters retain
their counts. CSV/JSON expose preparation policy separately from standalone
native observations.

Conversion recomputes131 prepared waves:124 with shift0, two with shift7 and
five with shift4. Shared physical wave/root/source-key identities take the
maximum bound across source uses. Maximum nominal FIR cutoff at the bound is
about0.900319 of mixer Nyquist, including loop/tuning rounding. This is not a
brick-wall, zero-aliasing or audible-error bound. Existing preparation rejects
shifts over twelve semitones and key overflow without clamping.

The report separately attributes5,202 allocated NOTE calls, no held/starting
preemption,2,866 nonzero-envelope release reuses and115 slot choices different
from the plain baseline to the exact standalone ROM. Four extremely soft
mappings remain zero in grouped and unpacked controls, with six observed native
calls; filtering adds none. Prepared-storage clipping is1,097 of903,042 points.
The scan does not remeasure native playback or add manual acceptance. Storage
counts are not time-weighted playback or an audible-error bound. Tail reuse,
clipping, extreme-soft-note loss and PCM8/ADSR/tempo quantization remain. The
user reported the requested listening/effects/three-encounter checks passed;
comparative filtered/unfiltered preference was not separately reported. No
independently timed recording, full gameplay trace, linked play or rematch is
inferred.

A separate AJITO filtered experiment studies the existing four long aliases,
changing singleton expression/volume and the tighter voice budget. It remains
outside this scan and requires a new exact-ROM checklist.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v29
```

Use a fresh directory. ROMs, original assets and local outputs stay outside
Git. Historical artifacts and coverage remain immutable.
