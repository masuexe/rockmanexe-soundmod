# NDS compatibility audit v35: accepted BATTLE merged antialias

The filtered scanner adds only accepted SF3 BATTLE under
`known_sf3_battle_merged_antialias`: family `ssr3`, slot35, capacity eight,
exactly IDs0–7/9/14/15, all looping, no fitted attack or active modulation.
`BATTLE_GROUPS` and existing explicit merged filtering are used. Upward
preparation remains disabled. Original fixed-volume ratios, grouping/control,
held-pan, alias/release, unsupported-effect, sample-budget and model guards
remain; no group search or fitted retry is added.

All seven originals and three pinned SDATs verify before and after132 slots.
Only filtered `ssr3:35` changes status. ROM/BPS match the
[accepted standalone experiment](nds-sf3-battle-merged-antialias-research.md):

- ROM CRC32: `89634045`.
- ROM SHA-256: `1490032534e505fc145877c291f99dd1c80fa789b5db7fa4325be24cb4ac3c33`.
- BPS SHA-256: `d9199e6ad3079bb54f3ca1e116db71bd7326fb227586e2df6875615fff4d1984`.

All71 prior primary and36 prior filtered ROM/BPS pairs retain bytes, routes,
gains and exact-manual flags. Primary totals stay71 packed,36 exact accepted,
35 pending and51 capacity-blocked. Filtered totals rise36→37 packed and18→19
exact accepted, with18 pending and85 blocked (51 capacity,34 conversion).
Unique accepted source sequences stay41. Matching remains version-specific.

All481 tests pass without skips, including six scanner cases for pinned
identity/structure/groups, explicit flags, retained model/conversion failures,
headroom/packing, exact acceptance, attributed limits and report accounting.
Validation checks accepted ROM/BPS and manifests, prior packed identities,
input/source/scanner pins, deterministic reports, actual JavaScript filters
and recursive v10–v34 archive identities. The merged-filter selector selects
eight variants; upward preparation stays at four. Other structure filters
retain their counts.

Conversion recomputes170 prepared waves and1,054,239 PCM8 bytes, maximum source
step about9.443. Prepared storage clamps10,009 points. These storage counts
are not time-weighted playback, native mixer clipping or an audible-error
bound. Existing FIR, sample-budget and source-step guards remain.

The report attributes4,877 allocated NOTE calls, zero rejections,23 held/
starting preemptions and3,331 nonzero-envelope release reuses to the exact
standalone ROM. All slots and all preemption clocks/displaced source/note/
key/gate identities match a fresh read-only exact accepted plain-ROM capture.
Eight original long-alias uses remain held and release independently; both
aliases overlap in561 saved snapshots. The validator checks saved metrics,
identity proof, exact-ROM alias proof and the fresh baseline, including byte
identity with the accepted original plain ROM/build/conversion. It does not
substitute an older capture or infer unrestricted polyphony/lossless tails.
No zero-velocity NOTE call is observed in this window.

The audit adds no native measurement or manual acceptance. The user reported
the standalone listening/effects/three-encounter checks passed. Comparative
timbre preference, independent timing, full gameplay traces, linked play and
rematch were not separately reported. Existing preemptions, ten-voice tails,
conservative filtering, PCM8/clipping and volume/ADSR/tempo limits remain.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v35
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
Historical artifacts and coverage remain immutable.
