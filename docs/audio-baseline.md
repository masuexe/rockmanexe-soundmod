# EXE4.5 / EXEGP initial audio table analysis

Status: structural scanning and local checksums verified. Playback disassembly and runtime findings are tracked separately in [playback validation](audio-playback.md). BGM/SFX classifications remain unverified.

## Baselines and reproduction

Run `scripts/scan_audio.py` using the command in the README. The generated `manifest.json` records complete SHA-256 hashes, sizes, input paths, patch hashes, and checksum results. Addresses apply to these specific inputs and cannot be transferred directly to EXE6 or another revision.

Original EXE4.5: 8,388,608 bytes, CRC32 `A646601B`, SHA-256:

```text
588a77da006fb0dca0c8addbcc316d7bd4b1c3a42db24750bcfe17b170ac5ef8
```

Both BPS patches require this source CRC32. The PvP output is 8,579,364 bytes with CRC32 `D1240E4B`; the Soundmod output is 25,165,824 bytes with CRC32 `D0020C1F`. Source, target, and patch checksums all pass.

## Structural rules and evidence

The parser uses [pret/pokeemerald's m4a_internal.h](https://github.com/pret/pokeemerald/blob/master/include/gba/m4a_internal.h) as a structural reference: eight-byte table entries, four initial header bytes, a tone-bank pointer, and an array of track pointers. This establishes a hypothesis, not proof that EXE uses identical engine semantics. The two halfword entry fields remain raw in the inventory rather than inheriting the reference game's meanings.

Nonempty headers must have 1–16 tracks, a zero block-count byte, and in-ROM tone-bank and track pointers. Both halfword table fields must be at most 31. Empty headers have four initial zero bytes; bytes five through eight are preserved as a raw field. Both four-byte alignment phases are scanned for runs of at least 16 valid entries, including at least four nonempty entries.

EXEGP's empty header at file offset `0x160BA8` begins `00 00 00 00 00 00 00 40`, unlike EXE4.5's all-zero empty header. Requiring eight zero bytes incorrectly fragments the EXEGP table and misses entries. The current rule handles this difference.

## Candidate tables

| Input | Table file offset | ROM address | Entries | Nonempty entries |
|---|---|---|---:|---:|
| Original EXE4.5 | `0x135214` | `0x08135214` | 499 | 352 |
| EXE4.5 PvP | `0x135214` | `0x08135214` | 499 | 364 |
| EXE4.5 Soundmod | `0x135214` | `0x08135214` | 499 | 404 |
| EXE4.5 Soundmod, additional candidate | `0x1135214` | `0x09135214` | 499 | 352 |
| EXEGP | `0x160658` | `0x08160658` | 170 | 86 |

Within each table, nonempty entries reference distinct headers. This does not prove that their musical content is distinct.

The EXE4.5 main-table pointer occurs at file offsets `0xEE36C`, `0xEE3A0`, `0xEE3EC`, `0xEE440`, and `0xEE474`. The EXEGP pointer occurs at `0x2FFC`, `0x3028`, `0x4C3E4`, `0x4C418`, `0x4C464`, `0x4C4B8`, and `0x4C4EC`. The initial scanner records raw byte matches; code-reference verification belongs to the playback investigation.

No occurrence of the additional Soundmod candidate's start pointer was found. It is not included in the main catalog total, but absence of a literal does not prove it is unused. The actual table selection needs code verification.

## Patch conflicts and additions

PvP changes 12 empty entries at table indices 69–80 into nonempty entries. Soundmod changes 52 empty entries into nonempty entries at:

```text
0–8, 10–13, 15–23, 28–29, 32–39, 69–88
```

BGM/SFX labels require separate evidence. See the playback record for verification of how indices are used by the engine.

Within the original ROM, 59 bytes are changed differently by both patches, at `0x13543C–0x13549B`. They cover the pointers and raw fields of entries 69–80. The extensions also overlap in `[0x800000, 0x82E924)`, totaling 190,756 bytes. Sequential patching or byte-priority selection is insufficient: transplantation must handle resource addresses and audio IDs.

`comparisons.json` contains complete conflict ranges and before/after entries. Extension space has no original data for a common baseline, so overlap size and differing-byte counts are reported separately. Matching bytes alone do not prove resource compatibility.

## What the inventory establishes

The reports identify input versions, correctly decoded patches, and addresses and entries matching the structural hypothesis. The first 16 bytes of each track are retained for manual inspection. Track instructions are not decoded, so these prefixes do not establish duration, complete resource boundaries, or equivalent musical content.

A tone-bank pointer is not a complete dependency list. Nested tones, samples, branch targets, and track loops still need decoding. The current inventory must not be used directly as a relocation plan. Playback references and representative runtime entries should be checked before dependency decoding and single-track transplantation.
