# NDS compatibility audit v33: accepted KINCHO upward antialias

The filtered scanner adds only accepted SF3 KINCHO under
`known_sf3_kincho_upward_antialias`: family `ssr3`, slot30, capacity eight,
exactly IDs0–7/14/15, all looping, no fitted attack or active modulation.
`SF3_KINCHO_GROUPS` and both explicit merged-filter/upward-preparation flags
are used. Existing grouping/control, fixed-volume, held-pan, alias/release,
one-octave/key, unsupported-effect, sample-budget and model guards remain.
There is no group search or fitted retry for the pinned route.

All seven originals and three pinned SDATs verify before and after132 slots.
Only filtered `ssr3:30` changes status. ROM/BPS match the exact
[accepted standalone experiment](nds-sf3-kincho-upward-antialias-research.md):

- ROM CRC32: `A988A6B9`.
- ROM SHA-256: `ae6243cff652dc8c028a2ed7d42ebdf38ba001218adec3cbf08231b65260ad01`.
- BPS SHA-256: `87a5c223a77cb9c5c09d341b968a363b632413573c84d6cd6ad37d2380a59a6b`.

All71 prior primary and34 prior filtered ROM/BPS pairs retain bytes, routes,
gains and exact-manual flags. Primary totals stay71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered totals rise34→35 packed and16→17
exact accepted, with18 pending and87 blocked (53 capacity,34 conversion).
Unique accepted source sequences stay41. Acceptance does not transfer by name.

All465 tests pass without skips, including six scanner cases for pinned
identity/structure/groups, both flags, retained conversion/model guards,
headroom/packing, exact acceptance, metadata scopes and report accounting.
Validation checks exact accepted ROM/BPS and manifests, prior packed outputs,
input/source/scanner pins, deterministic reports, actual JavaScript filters
and recursive v10–v32 archive identities. The merged filter selects six
variants and upward preparation four; other structure filters keep counts.

Conversion recomputes108 prepared waves:94 at shift0 and14 at shift2, with
1,086,559 stored PCM8 bytes. Shared physical wave/root/source-key maxima remain
bounded, and the independently checked nominal FIR cutoff at the bound is
about0.9002463 of mixer Nyquist including loop/tuning rounding. This is not a
brick-wall, zero-aliasing or audible-error bound. Conservative preparation can
reduce unbent bandwidth. Prepared storage clamps10,592 points, not a measure
of time-weighted playback or runtime mixer clipping.

The report attributes1,194 allocated NOTE calls, zero rejections and no
held/starting preemptions to the exact standalone ROM. It records477
nonzero-envelope release reuses against476 in a fresh read-only plain-ROM
baseline, with175 different slot choices. The validator checks saved window
metrics and the fresh baseline, including byte identity with the accepted
plain ROM/build/conversion. No zero-velocity NOTE call is observed in that
window. The older plain capture remains immutable and is not substituted for
the fresh matching observation window.

The audit adds no native measurement or manual acceptance. The user reported
the standalone listening/effects/three-encounter checks passed. Comparative
timbre preference, independent timing, full gameplay traces, linked play and
rematch were not separately reported. Ten-voice tails, conservative filtering,
PCM8/clipping and volume/ADSR/tempo quantization remain explicit.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v33
```

Use a fresh directory. ROMs, game assets and local outputs stay outside Git.
Historical artifacts and coverage remain immutable.
