# Communication battle music pool

For the pinned Japanese and English PvP 0.6.0 ROMs, the communication battle startup path requests **music ID 98**. In the current manager, edit **Music event #98** to select its pool. This is a song-ID rule and applies to every scene that requests ID 98; it is not an exclusive communication-scene hook.

## Manager workflow

1. Check the desired original music ROM sources and click **Load tracks**.
2. Under **When to play**, choose **Music event #98**.
3. Click **Clear pool** to remove its previous tracks, then check the desired tracks in the library. If original EXE4.5 music should participate, include those entries too.
4. Save the project if desired and click **Build & export patch**.
5. Run the exported `unified.gba`, or apply `unified.bps` to the original EXE4.5 ROM, and test communication battles.

The title and other numbered pools are independent. Checkbox edits automatically use selector shift zero; each song start selects one entry from the pool using the existing selector byte. Repeated selections are possible, and a finite song does not automatically advance. Up to 255 entries are supported.

If an emulator's battle-music mute feature suppresses the game music call, disable that option when testing. For example, [Trill's EXE4.5 primary hook](https://github.com/HCTOrganization/trill/blob/81bbcf16f845518a53bb3399766ae1792e7d50a0/trill-pvp/src/game/exe45/primary.rs) skips the battle music call when `disable_bgm` is true.

## Evidence and limits

ROM profile: PvP CRC32 `D1240E4B`, SHA-256 `2d921fe7775f3a5825a24cc07d821a73dffac576991f02b99cd23222f99e3278`.

The communication startup code at `0x0804479A` passes **descriptor index 99**, not music ID 99, to the descriptor lookup at `0x08008192`. That lookup uses base `0x080C7598` and a 12-byte stride. Descriptor 99 resides at `0x080C7A3C`:

```text
20 00 64 62 47 03 1F 00 52 7A 0C 08
```

Its music byte at offset 3 is `0x62`, decimal **98**. The communication routine passes this descriptor to `0x08004E2C`, which stores the pointer in the subsystem control structure at offset 44. Battle initialization at `0x08006A38` copies it to the battle structure at offset 60.

The battle-start music path selects the descriptor's music byte, or an override for battle mode values at least 70. For mode 71, the override byte at `0x080079CC + 1` is also `0x62`. The request is made at `0x0800796C` through the music wrapper at `0x0800053C`. The [Trill EXE4.5 offsets](https://github.com/HCTOrganization/trill/blob/81bbcf16f845518a53bb3399766ae1792e7d50a0/trill-pvp/src/game/exe45/offsets.rs) independently identify `0x0800796C` as the battle-start music call.

A controlled mGBA check set the descriptor pointer to descriptor 99 and the battle mode to 71, then executed the native selection branch from `0x08007954` to `0x0800796C`. Register `r0` was **98** at the call. This check explicitly injected state and did not perform a complete two-peer communication battle. The earlier selector tests cover dispatch, player initialization, and register preservation; multiplayer behavior remains a separate gameplay test.

Disassemblies and the controlled execution transcript are retained under `out/communication-bgm-research/`. This record avoids confusing communication descriptor index 99 with the actual music event 98.

## English target confirmation

The supplied `bn45_us_pvp_0.6.0.bps` also starts from original EXE4.5 CRC32 `A646601B`. Its descriptor lookup, descriptor-99 music byte, and battle-start selection code match the Japanese target. Music event 98 therefore remains the communication pool. English target dispatch/ABI probes and natural imported playback also pass; see [English target validation](english-pvp.md).

## EXE GP communication battles

Choose **Rockman EXE Battle Chip GP (JP)** as the target and click **Load tracks**. Under **When to play**, select **Communication battles (music #12–14)**. Click **Clear pool**, check the tracks you want to participate, then save and export. Apply `unified.bps` to the supported original `exegp.gba`, or run `unified.gba` directly. The title pool remains independent.

This group writes ordinary pools for IDs **12, 13, and 14**. GP's native communication battle code chooses among those three before requesting playback, so configuring only one would leave two native choices unchanged. The group synchronizes checkbox edits, clearing, and adding visible tracks. If the three existing pools differ, the UI shows the first pool and explains that an edit will apply it to all three. Merely selecting the group does not change any pool. The numbered events remain available for individual editing.

IDs 12–14 also appear in single-player battle paths. Changing this group changes every request for these IDs, including those battles. An exclusively communication-only scene hook would require a separate adapter extension. The existing random selector chooses one pool entry on each music start; repeats are possible.

Older GP projects containing only a customized title pool gain the other 15 native music events when the catalog is loaded. Existing tracks, duplicate entries (weights), and selector shifts are retained. Added events initially contain only their original native song. Save the project to persist the expansion.

### GP selection evidence

Supported target CRC32: `9217FB18`; SHA-256: `6c3ac853d06b0fa70d9ac5a0705841ddb4f0e06cd246894e60bcb1cf824ef025`.

The main menu dispatcher at `0x08035BAC` uses table `0x082A9094`; slot 7 points to communication handler `0x08047F5D`. Its substate dispatcher at `0x08047F5C` uses table `0x082AE618`. Substate 7 points to `0x08048975`. Its first selection branch calls the game RNG at `0x0803FDC8`, masks to 16 bits, takes the remainder modulo 3 via `0x0804DBF0`, adds 12, and requests music through `0x08049FE4` at `0x080489D8`. That wrapper reaches the M4A entry at `0x0804C3BC`. The subsequent communication lifecycle includes the native link reset helper at `0x0804A114`, which updates the link state at `0x02002EE0` and calls `0x08000F28`.

Single-player call sites include explicit requests for ID 12 at `0x08039C56`, ID 13 at `0x08039C40`, and ID 14 at `0x08039C70`. These demonstrate why the group is described as shared battle music.

Controlled mGBA execution entered the native modulo/add branch with RNG inputs 0, 1, and 2 and confirmed requests 12, 13, and 14. A GP export mapping all three to `exe1:0` and `exe4:0` passed nine dispatch/header checks at controlled scheduler ticks, native status-query checks with an explicitly injected nonzero player status (including an unconfigured title query that must return zero), and BPS reconstruction. This injected branch state and did **not** perform a complete two-peer communication battle. Runtime reports and disassemblies are retained under `out/gp-link-research/`. Browser workflow checks cover group edits, distinct initial pools, title isolation, and save/reload.
