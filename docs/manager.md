# Local sound manager

The manager modifies a verified target using music read directly from original EXE/BN ROMs. Supported targets include EXE4.5 JP/English PvP and original EXE GP; see [target selection and GP validation](multi-target.md). Soundmod BPS is no longer a music input. With EXE4.5 as the target, the current shared library has 23 donor ROMs and 787 eligible entries: 48 native PvP entries plus 739 foreign music-player candidates. Original `exe45.gba` is also selectable as a music source, including for GP exports. GP has 16 native music events and a ten-track player; its donor availability can differ. It provides file selection, catalog filters, editable names, realtime audio previews and separate mGBA verification clips, playback pools, saved projects, and BPS/ROM export. All processing stays on the local machine.

## Start

From the repository root:

```bash
python3 scripts/manage_sound.py
```

The browser opens `http://127.0.0.1:8765/`. To open it manually or choose another port:

```bash
python3 scripts/manage_sound.py --no-browser --port 8766
```

Python 3.10 or newer is sufficient for the catalog and export. No third-party Python packages or frontend build tools are required. The HTTP server binds only to `127.0.0.1`; run it in a normal local terminal that permits listening sockets. Stop it with Ctrl+C.

The default base inputs and music source directory are:

| Input | Default location |
|---|---|
| Original EXE4.5 ROM | `../roms/exe45.gba` |
| Original EXE GP target | `../roms/exegp.gba` (no pre-patch) |
| Default Japanese PvP patch | `../patches/exe45_pvp_0.6.0.bps` (fallback: `references/`) |
| Original music ROMs | `../roms/*.gba` matching the configured profiles |

Choose **Game to modify** first. The original target ROM and any required PvP patch can be replaced in the interface. GP uses its original ROM directly; `--target exegp` preselects it. Japanese and English PvP 0.6.0 targets are supported from the same original base; use `--pvp-patch ../patches/bn45_us_pvp_0.6.0.bps` to preload English. See [English target support](english-pvp.md) for fingerprints, preserved resources, and verification. Music sources appear as checkboxes with game names and filenames. Use **Select all** or **Clear selection**, then check only the games you want. Click **Load tracks** to apply the choice. The server lists available files at startup, but reads and analyzes donor ROM bytes only when selected for loading. **Add music ROMs** accepts multiple donor files and checks the added sources; identities are determined by content fingerprint rather than uploaded filename. Uploaded donor copies persist under the local data directory's `uploaded-roms/` folder. The PvP BPS is decoded against original EXE4.5 in memory. Donor profiles are pinned in `config/rom-profiles.json`; unsupported revisions are rejected. The shared directory is `/home/harp/projects/gba/roms` in this workspace. Restart the server after changing files there, or add files through the interface.

Supported local profiles cover Japanese Rockman EXE 1–6, Black/Blue Moon/Team Colonel/Falzar variants, Battle Chip GP, and corresponding English Battle Network/Chip Challenge ROMs. Each source has its own game label and stable key such as `exe1:0`, `bn2:1`, or `exegp:1`. Song titles remain user-assigned metadata. Regional variants are listed separately; this count is not a count of unique compositions.

## Choose and export

1. Select **Game to modify**, supply the original target ROM and any required pre-patch, check the music ROM sources you need, then click **Load tracks**. The source counter distinguishes selected, available, and loaded ROMs. Native target music is always included; clearing every donor source loads only those entries (48 for PvP, 16 for GP).
2. Browse the music-player candidates from checked sources. For EXE4.5 with all 23 donor sources enabled, the current library has 787 available candidates. Search by stable ID or assigned name and filter by source. Enable the other-audio option to see all 8,954 entries when EXE4.5 is selected as a donor, including reserved effects, empty entries, and music exceeding the target player capacity. Existing source IDs remain stable. Ineligible entries cannot be selected. GP donor entry 5 has nine tracks: it is incompatible with EXE4.5 but fits GP.
3. Click a row, then **Play now** for realtime playback or **Stop** to end it. A row change also stops playback. Use the verification section for an mGBA recording, or save an assigned name. Source IDs are retained because verified song titles are not embedded in the ROM catalog.
4. Choose **When to play** and check tracks for that event. EXE4.5 defaults to the title screen and five original Soundmod triggers; GP defaults to its 16 native music events, with title event 1. EXE4.5 communication battle startup uses **Music event #98**; see [the workflow and verification record](communication-battle-music.md). Other numbered events have not been fully mapped to gameplay contexts. Rules replace a music ID wherever it is requested, so a shared ID is not an exclusive scene hook. Imported projects may configure other native music triggers supported by the builder.
5. Optionally apply the selected pool to every configured event. Every pool needs 1–255 entries before saving or exporting.
6. Click **Build & export patch** and download `unified.bps`. Apply it directly to the original selected target ROM. EXE4.5 exports include PvP; GP exports apply to original `exegp.gba`. `unified.gba`, `project.json`, and `catalog.csv` can also be downloaded.

New projects default to native music for the selected target events. When sources are disabled or legacy keys are unavailable, their entries are removed from the current playback pools. Other selections, including repeated entries, remain. A pool with no remaining tracks falls back to its native target trigger song; the manager reports the changes. Pools changed by pruning reset their selector shift to zero. Invalid project structures restore the native defaults. The old project file is kept until you save or export. Names for absent sources are retained on disk but excluded from current project downloads. Imported valid pools preserve repeated entries and selector shifts until edited. Checking tracks, clearing a pool, adding visible tracks, or applying a pool to all events resets that pool's shift to zero. Checkbox edits collapse duplicate entries into one entry per selected track. Every pool is limited to 255 entries so its entries remain reachable from the existing 8-bit selector. Filter by game before using **Add visible tracks**, or choose a smaller subset if the pool exceeds the limit. Weighted pools can still be imported through project JSON. EXE4.5 selection reads its existing RNG1 byte; GP mixes the existing scheduler tick. Uniform randomness is not established. A finite song does not cause automatic playlist advancement.

Source choices persist automatically when applied in `out/manager/sources.json`, including an empty choice. The next server start restores checkboxes without reading unchecked donors. Changing checkboxes marks the choice as pending and disables preview/export until **Load tracks** applies it. Current unsaved pool edits are carried through that reload and pruned as described above. Applying sources also stops live preview and clears recordings cached for the previous input revision.

Names persist in `out/manager/track-names.json`. EXE4.5 projects use `out/manager/project.json`; GP projects use `out/manager/project-exegp.json`. The target choice persists in `out/manager/target.json`. **Save project** persists the current configuration; exporting also saves it and writes a downloadable project with names. Use **Import project** to restore such a JSON file after loading the catalog. Names are metadata and are not embedded in the ROM. Each build gets its own output directory; source files are never overwritten. `--data-dir PATH` changes the local state/output directory.

Only foreign songs referenced by export pools are packed. Catalog IDs use fixed per-profile ranges, including absent ROMs and unavailable entries, so adding or removing donor files does not renumber existing keys. Unselected foreign slots remain empty. The relocator verifies native target preservation and reparses imported notes, timing, termination, and PCM contents. Export checks BPS source, target, and patch checksums and decodes the new patch to confirm that it reproduces the output ROM byte-for-byte.

## Audio previews

**Play now** uses the agbplay MP2K core and a streamed Web Audio player. Build it once with `python3 scripts/build_realtime.py --fetch-deps` in the tested Ubuntu environment. It does not wait for a WAV file and plays looping songs until stopped. See [realtime setup, implementation, and measurements](realtime-preview.md). Source playback uses agbplay's mixer and can sound different from the target game.

The **Verify playback in the exported game** section records short clips using mGBA. These verification captures require **Linux**, a C compiler named `cc`, SDL2 development headers, and the mGBA SDL executable. The installed/tested executable is `/usr/games/mgba`, version 0.10.2. An alternative executable can be supplied with `--mgba PATH`; compatibility with other debugger versions is not established.

The manager builds a disposable ROM that plays exactly the selected song on the title screen. It waits for the expected player/header initialization and captures the actual SDL audio callback using a small temporary `LD_PRELOAD` library. The recording includes Direct Sound PCM and hardware PSG voices. No debugger register injection redirects playback. The disposable emulator has isolated configuration and save files and uses dummy audio/video drivers; listening happens through the browser's WAV player.

Choose a 3-, 12-, or 30-second clip. Generation takes the clip duration plus build/boot time. Successful clips are cached for the current input files and duration. Previewing does not change the configured export pools. Browser autoplay rules may require clicking the audio player's play button when a clip is ready. A naturally finite song can end before the clip finishes; silence after its end is retained.

The title-screen lifecycle remains active. Clips are limited to 30 seconds to stay below the observed attract/demo transition in the tested title runs. These short clips are listening aids, not full-track or gameplay validation. A dedicated lifecycle-free preview player remains future work.

A standalone capture command is also available for a manifest whose title pool selects only the requested target ID:

```bash
python3 scripts/render_preview.py out/unified-v2/unified.gba \
  --manifest out/unified-v2/build.json --id 551 \
  --seconds 12 --out out/title-preview
```

The output directory must be new.

## Verification

The Python suite passes 67 tests, including manager input rejection, project/name persistence, invalid-project atomicity, preview cache/isolation, HTTP token/origin/path handling, original-ROM identity, selected-only packing/loading, source-choice persistence, disabled-source pool pruning, native-only catalogs, and BPS reconstruction. Run:

```bash
python3 -m unittest discover -s tests -v
node tests/test_manager_ui.mjs
node tests/test_audio_worklet.mjs
```

The Node check uses a lightweight DOM/API fixture to exercise catalog loading, unavailable rows, pool edits, names, preview links, export links, and project saves. It does not replace a real browser layout or end-to-end HTTP test. A real Chromium/HTTP smoke test additionally loaded the complete catalog, filtered original game sources, generated EXE1 and EXE6 previews, edited a mixed pool, and downloaded all four exported files without JavaScript errors. Results and a screenshot are in `out/original-browser-validation/`. A further browser check loaded only EXE1 and GP (83 available entries), disabled EXE1 while carrying unsaved pool edits, retained the GP selection (63 entries), exported successfully, and restored the checkboxes on page reload and server restart (with zero donor files loaded until Load tracks). Evidence is under `out/source-selection-browser-validation/`. The HTTP handler is also tested using in-memory requests.

Actual mGBA capture succeeded for original EXE1 entry 0 and EXE6 entry 1 through the browser: each produced a nonzero 3-second, 44.1 kHz stereo signed 16-bit WAV. Earlier EXEGP and Soundmod captures remain historical evidence for the capture mechanism. Default manager projects now use native PvP music and therefore do not reproduce the earlier Soundmod reference ROM.

Donor profiles are based on structural tables and music-player assignments. Conservative dependency analysis rejects unsupported commands and voice initialization patterns. These are transplant candidates, not an exhaustive BGM/SFX or gameplay audit. All 692 eligible foreign entries also passed a batch relocation/reparse and native-preservation check. Representative runtime checks do not establish listening coverage of all 740 candidates. See [original-ROM library evidence](original-rom-library.md).
