# Japanese EXE6 soundmod targets

The manager supports both original Japanese EXE6 revisions in `../roms/`:

| Game to modify | Original ROM | CRC32 |
| --- | --- | --- |
| Rockman EXE 6 Gregar (JP) | `exe6.gba` | `6285918A` |
| Rockman EXE 6 Falzar (JP) | `exe6f.gba` | `2DFB603E` |

Choose the matching target, select the original music ROM sources you need, and click **Load tracks**. No gameplay pre-patch is required. Configure **Title screen** or **Communication battles (shared music #21)**, clear its existing pool if needed, then select tracks and export. Run `unified.gba` directly, or apply `unified.bps` to the **original ROM of that exact variant**. A Gregar BPS cannot be applied to Falzar or an English BN6 ROM.

Each variant exposes all 37 native music IDs, 1–37, while preserving its complete 474-entry native audio table. Native music keys are `native-exe6:*`; donor IDs such as `exe6:*` and `exe6f:*` retain their existing meanings and slot assignments. Donor and native copies may both appear when the target game is also checked as a source. Only selected donor tracks are included in an export.

The native music player has eight tracks. Music exceeding that capacity is disabled for these targets; for example, the nine-track `exegp:5` remains unavailable. The mixer uses 10,512 Hz, so the verified EXE1/EXE4 fixed-step drums need no rate conversion on EXE6. Realtime playback and optional mGBA recordings use the existing shared preview implementations.

Saved projects are separate: `project-exe6.json` for Gregar and `project-exe6f.json` for Falzar. GP/ChipControl and EXE4.5 projects are retained separately. All targets share music-source choices and assigned track names. Existing music imports/configuration are not automatically copied between different games or EXE6 variants.

```bash
python3 scripts/manage_sound.py --target exe6
python3 scripts/manage_sound.py --target exe6f
```

English BN6 ROMs remain music sources. Their target layouts and any gameplay pre-patch combinations are not enabled by this change.

## Communication battle music

Both Japanese variants use music ID **21** for communication battles. The communication settings generator selects one of 164 battlefield descriptors; every descriptor has byte 2 equal to `0x15` (21). The native round startup either reads that byte or explicitly selects 21 when battle flag bit 3 is set. It requests music at `0x08009406` through `0x080005D4`.

This is an ID rule, not an exclusively communication-scene hook: other scenes requesting 21 use the same configured pool. Each native music start selects one pool entry. The game retains its suppression of repeated requests for the same current music ID. Finite tracks do not automatically advance, and repeated selections are possible.

An emulator or network tool that suppresses the game's BGM call also suppresses this pool. The [Trill primary hook](https://github.com/HCTOrganization/trill/blob/81bbcf16f845518a53bb3399766ae1792e7d50a0/trill-pvp/src/game/bn6/primary.rs) provides such an option; disable it when testing game-driven music.

## Verified layouts

| Field (file offset unless stated) | Gregar | Falzar |
| --- | --- | --- |
| Original song table | `0x164E0C` | `0x1632D0` |
| Player table | `0x164C8C` | `0x163150` |
| Start-by-ID entry | `0x15B338` | `0x1597FC` |
| MPlayStart core | `0x15BB18` | `0x159FDC` |
| Initial SoundMode literal | `0x59C` | `0x59C` |
| Communication descriptor table | `0xB4B18` | `0xB32B8` |
| Read-only selector (RAM address) | `0x0200A210`, 16 bits | `0x0200A210`, 16 bits |

The original SoundMode precondition is `0x0093040D`. Five stock audio-table literals are relocated in each variant. Resource allocation, bank/sample relocation, pool dispatch, BPS generation, and native prefix/table checks are shared with the existing targets. Only layout parameters differ. The selector reads the game's 16-bit frame counter and applies the existing xorshift32 mixer; it consumes no game RNG calls and allocates no RAM. Native queue wrappers and their register/Toolkit restoration remain unchanged. GP's additional status-query hook is not installed in EXE6.

Gregar SHA-256: `fa6808a5c63c2cc09430ec7ad74c6e02f4f35928448e6ff5f8dbdec0795160cf`.

Falzar SHA-256: `21300170c404371da5cd0c327c3959c0981cf0af6e6bb9189fec4010fc6258a4`.

## Evidence and limits

Both variants naturally started title ID 1 and played imported `exe1:0` in nonzero three-second mGBA full-mix recordings. Original title, music ID 21, and representative effects 100 and 129 passed playback/player/header checks. Controlled communication-branch execution covered descriptor and forced-21 paths, selector ticks selecting both `exe1:0` and `exe4:0`, an unchanged 32-bit word around the 16-bit counter, Toolkit preservation through the native queue, and queued stopping of imported music. These probes injected registers, RAM state, and PC; they did not establish a complete two-peer battle.

Tests additionally cover strict revision identity, all 37 native events, the eight-track limit, native prefix/table preservation, both variants' original-ROM BPS reconstruction, independent saved projects, and the existing target regression cases. UI fixture checks cover both variants, event labels, title isolation, and correct patch application ROMs. Full gameplay, longer audible comparisons, and complete hardware/network communication battles remain gameplay tests.

Reports, disassemblies, sample ROM/BPS pairs, and a reusable controlled probe script are in `out/exe6-target-research/`. The layout and communication records can also support the sibling reverse-engineering project. Reference sources are local in `../references/exe6f` (commit `fcdbb4734c1aca27c703a4af095a3ba7f4824798`) and `../references/trill` (commit `81bbcf16f845518a53bb3399766ae1792e7d50a0`); the [Trill offsets](https://github.com/HCTOrganization/trill/blob/81bbcf16f845518a53bb3399766ae1792e7d50a0/trill-pvp/src/game/bn6/offsets.rs) independently identify the Japanese communication music call, and the [Falzar disassembly](https://github.com/dism-exe/exe6f) pins its source ROM revision.
