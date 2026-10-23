# NDS compatibility audit v32: accepted SF2 HOKORA merged antialias

The filtered scanner adds only the accepted SF2 HOKORA configuration under
`known_sf2_hokora_merged_antialias`. It requires family `ssr2`, slot20,
capacity eight, exactly source IDs0–8, all tracks looping, no fitted attack
and no active modulation. `SF2_HOKORA_GROUPS` merges0/4 and keeps the other
seven sources separate. Only the existing explicit merged-filter mode is
enabled; upward-pitch preparation is not enabled for this song. Existing
control/grouping, fixed-volume, held-pan, unsupported-effect, alias/release,
filter-budget and model guards remain. No search or fitted retry is added.

All seven originals and three pinned SDATs verify before and after132 slots.
Only filtered `ssr2:20` changes status. ROM/BPS match the exact
[accepted standalone experiment](nds-sf2-hokora-merged-antialias-research.md):

- ROM CRC32: `02686B1E`.
- ROM SHA-256: `923ead50245fcd3fc0eb18d6689abbac0849be57856a1adbab57bc7f3802b022`.
- BPS SHA-256: `ffc7b70b6b7bb90e988f440d743c97a464a96dc6e16773723e0d31fafd981411`.

All71 prior primary and33 prior filtered ROM/BPS pairs keep bytes, routes,
gains and manual-match flags. Primary totals stay71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered totals rise33→34 packed and15→16
exact accepted, with18 pending and88 blocked (54 capacity,34 conversion).
Unique accepted source sequences remain41. Matching is by exact version,
not by song name.

All457 tests pass without skips, including six new scanner cases for pinned
identity/structure/groups, explicit flags, retained conversion/model failures,
headroom/packing and exact acceptance, attributed limits, and report accounting.
Validation checks manifests and exact accepted ROM/BPS, prior packed identities,
input pins, source/scanner hashes, deterministic JSON/CSV/HTML/summary reports,
actual JavaScript filters and unchanged recursive v10–v31 archive identities.
The merged-filter selector now selects five variants; upward preparation
retains its three variants and prior structure filters keep their counts.

Conversion recomputes81 prepared waves and748,395 PCM8 bytes, maximum source
step about15.363. Storage clipping is1,197 points. These are conversion/storage
counts, not time-weighted playback, runtime mixing or an audible-error bound.
The unchanged FIR, sample-budget and source-step guards remain.

The report explicitly attributes1,555 allocated NOTE calls, zero rejections,
zero held/starting preemptions,384 nonzero-envelope release reuses and354 slot
choices different from the fresh plain-ROM baseline to the exact standalone
ROM. That separate read-only baseline observes385 release reuses and no held
preemptions over the same window. The validator checks saved window metrics,
baseline allocation proof and byte identity with the exact accepted plain
ROM/build/conversion. It does not substitute the older plain capture's shorter
observation window or alter archived artifacts. No zero-velocity NOTE call is
observed in the new window.

The audit adds no native measurement or manual acceptance. The user reported
the standalone listening/effects/three-encounter checks passed. Comparative
timbre preference, independent timing, full gameplay traces, linked play and
rematch were not separately reported. Ten-voice tail reuse, conservative
filtering, PCM8/clipping and volume/ADSR/tempo quantization remain explicit.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v32
```

Use a fresh directory. ROMs, original assets and local outputs remain outside
Git. Historical artifacts and coverage stay immutable.
