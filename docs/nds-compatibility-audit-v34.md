# NDS compatibility audit v34: accepted DEMPAJIKEN merged antialias

The filtered scanner adds only accepted SF3 DEMPAJIKEN under
`known_sf3_dempajiken_merged_antialias`: family `ssr3`, slot26, capacity eight,
exactly IDs0–8/14/15, all looping, no fitted attack or active modulation.
`SF3_DEMPAJIKEN_GROUPS` and the existing explicit merged-filter flag are used;
upward preparation remains disabled. Grouping/control, fixed-volume, held-pan,
alias/release, unsupported-effect, filter-budget and model guards remain.
No group search or fitted retry is introduced.

All seven originals and three pinned SDATs verify before and after132 slots.
Only filtered `ssr3:26` changes status. ROM/BPS match the
[accepted standalone experiment](nds-sf3-dempajiken-merged-antialias-research.md):

- ROM CRC32: `E0395A10`.
- ROM SHA-256: `5eb54e17c9e4155f975aaab02e8443284f2d49e27336111f42ad7fe39fe03013`.
- BPS SHA-256: `a196b81730d01914eef436dac932e89c60c3c7bcc49e58cb49b2db7fb0a1e50f`.

All71 prior primary and35 prior filtered ROM/BPS pairs retain bytes, routes,
gains and exact-manual flags. Primary totals stay71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered totals rise35→36 packed and17→18
exact accepted, with18 pending and86 blocked (52 capacity,34 conversion).
Unique accepted source sequences stay41. Acceptance does not transfer by name.

All473 tests pass without skips, including six new scanner cases for pinned
identity/structure/groups, explicit filtering, retained model/conversion
failures, headroom/packing, exact acceptance, native-limit attribution and
report accounting. Validation checks accepted ROM/BPS and manifests, prior
packed identities, input/source/scanner pins, deterministic reports, actual
JavaScript filters and recursive v10–v33 archive identities. The merged filter
selects seven variants; upward preparation stays at four. Prior structure
filters keep their counts.

Conversion recomputes96 prepared waves and680,241 PCM8 bytes, maximum source
step about11.881. Prepared storage clamps5,834 points. These are storage counts,
not time-weighted playback, runtime mixer clipping or an audible-error bound.
Existing FIR, sample-budget and source-step guards remain.

The report explicitly attributes999 NOTE calls,996 allocations and three
rejections to the exact standalone ROM. Rejections at696/2424/4152 remain
source14/key64/instrument19. The three held/starting preemptions have the same
clocks and displaced source15/note/key/gate identities as the fresh exact
accepted plain-ROM observation. Nonzero-envelope release reuses rise522→532,
with383 different slot choices. The validator checks saved window metrics,
rejection/preemption identity proof and the fresh baseline, including byte
identity with the original accepted plain ROM/build/conversion. It does not
replace the old shorter capture or imply the allocator preserves every note.
No zero-velocity NOTE call is observed in this window.

The audit adds no native measurement or manual acceptance. The user reported
the standalone listening/effects/three-encounter checks passed. Comparative
timbre preference, independent timing, full gameplay traces, linked play and
rematch were not separately reported. Known accompaniment rejection, observed
preemptions, ten-voice tails, conservative filtering, PCM8/clipping and
volume/ADSR/tempo quantization remain explicit.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v34
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
Historical artifacts and coverage remain immutable.
