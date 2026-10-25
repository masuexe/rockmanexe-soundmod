# NDS compatibility audit v38: standalone and composite acceptance

The audit can now read the accepted two-song exporter manifest without failing
on a missing standalone `nds_conversion` field. Accepted composite ROMs are
verified against their recorded ROM and BPS fingerprints and listed separately
in JSON and the Markdown summary. They do not supply per-song manual matches
or increase standalone acceptance counts. The standalone-only
`manual_evidence()` interface remains available.

Per-sequence evidence also retains the original `acceptance_scope`, where
recorded. This preserves the SATELLITE revision2 report that its missing third
accent was fixed, without asserting its other listening/gameplay checks passed.
The rejected revision1 remains excluded. Pending and issue records cannot
become acceptance evidence.

## Refreshed existing routes

The v38 scan uses the same conversion routes, groups, gains, capacity guards
and filtering policies as v37. All seven originals and three pinned SDATs are
checked before and after the 132-slot scan. Every conversion/packing attempt,
failure, resource field and generated ROM/BPS fingerprint is compared with v37.
All 71 primary and 37 filtered variants repack identically.

Twelve filtered flags gain exact matches to existing standalone acceptance:
SF1 SCHOOL, DEMPAJIKEN, ANTENNA, COMICAL, JIKEN, KANDO, WIN, GAMEOVER and
BOSSMAE; SF2 HENKAN; SF3 COMICAL and GAMEOVER. Matching remains source-family,
sequence-index and artifact specific. Byte-identical SF2 ROOM/COMICAL/KANDO/
GAMEOVER versions do not inherit SF1 acceptance.

| Existing scanner variants | Packed | Exact accepted | Pending | Blocked |
| --- | ---: | ---: | ---: | ---: |
| Primary | 71 | 36 | 35 | 51 |
| Filtered | 37 | 33 | 4 | 85 |

Filtered exact matches rise from21 to33, pending falls from16 to4, and unique
source sequences with an accepted scanned variant rise from43 to54. Packing
statuses remain unchanged. Eight merged-filter and four upward-preparation
variants remain counted under the existing scanner policies.

The newer standalone SF1 SATELLITE/URA/HENKAN future-use filtering paths are
not enabled by this scanner update. Their accepted records remain related
evidence for slots9/18/26, while the older attempted filtered routes remain
blocked. The standalone documents and exact acceptance scopes continue to
apply; scan failure does not reject those separately built artifacts.

## Composite acceptance

One composite record is separately verified:

- Configuration: `nds-dual-ura-henkan-exe6-v1`.
- ROM CRC32: `87CBD9C4`.
- ROM SHA-256: `c19c41a343fc3e8003e5be06fd2ec8aaa5dfeeedd3c2a9272456cb033d6a37d7`.
- BPS SHA-256: `11d6c977af7cb1553dfa4a5cd75c7065e983e44d721653ebf4aa04b9daa41316`.

Its [original record](nds-dual-ura-henkan-research.md) accepts the requested
title/battle roles, finite stop/no-replay wait, effects and three encounter
cycles as user-reported checks. Optional communication, linked play, rematches
and broader gameplay were not separately reported. No standalone or linked
acceptance is inferred from this composite result.

## Verification and boundaries

Five new tests cover composite isolation, retained partial acceptance scope,
pending/issue exclusion, ROM/manifest/BPS mismatch rejection, invalid roles and
summary counts. A fresh full 532-case Python suite, without skips, and both
existing JavaScript suites pass. This replaces test-evidence reuse for this
scanner change. Conversion and packing functions retain their previous ASTs;
every other existing Python source remains byte-identical.

Batch checks compare exact existing ROM/BPS outputs, current manual records,
JSON/CSV/HTML/Markdown consistency, actual JavaScript filter results, deterministic
report regeneration, source fingerprints and recursive v10–v37 archive hashes.
The composite BPS also reconstructs its accepted ROM. The initial loader
failure is retained in the local research folder, separate from passing runs.

This update adds no converter/native capability, playback capture, listening
or gameplay acceptance. PCM8/filter/volume/ADSR/tempo and ten-voice limits remain.
The Windows test patch stays at the already accepted composite version; no new
listening delivery is made.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v38
```

Use a fresh directory. Local report validation and test evidence are in
`out/nds-research/compatibility-audit-v38-research/`; ROMs, assets and research
outputs remain outside Git.
