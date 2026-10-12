# Local sound manager

The manager combines the verified EXE4.5 PvP base, all 52 Soundmod additions, and 15 compatible EXEGP songs. It provides file selection, catalog filters, editable names, short audio previews, playback pools, saved projects, and BPS/ROM export. All processing stays on the local machine.

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

The default input files are:

| Input | Default location |
|---|---|
| Original EXE4.5 ROM | `roms/exe45.gba` |
| PvP patch | `references/exe45_pvp_0.6.0.bps` |
| Soundmod patch | `references/exe45_soundmod.bps` |
| EXEGP donor ROM | `roms/exegp.gba` |

The interface can replace each file. Both BPS patches are independently decoded against the original ROM in memory. Supported source fingerprints are pinned to [the verified baseline profiles](audio-playback.md); other revisions are rejected. Loading arbitrary GBA games is not supported.

## Choose and export

1. Select the four inputs and click **Load tracks**. Defaults are preloaded when present.
2. Browse the 115 available music-player candidates. Search by stable ID or assigned name and filter by source. Enable the other-audio option to see all 637 entries, including reserved effects, empty entries, and the incompatible nine-voice EXEGP entry. Those entries cannot be selected.
3. Click a row to generate a preview or save a name. Source IDs are retained because verified song titles are not embedded in the ROM catalog.
4. Choose **When to play** and check tracks for that event. The title screen and the five original Soundmod triggers are configured by default. Other events are shown by numeric ID because their gameplay contexts have not been verified. Imported projects may configure other native music triggers supported by the builder.
5. Optionally apply the selected pool to every configured event. Every pool needs at least one track before saving or exporting.
6. Click **Build & export patch** and download `unified.bps`. Apply it directly to the original EXE4.5 ROM, not to an already patched PvP ROM. `unified.gba`, `project.json`, and `catalog.csv` can also be downloaded.

Unedited default pools preserve repeated entries and selector shifts. Checking tracks, clearing a pool, adding visible tracks, or applying a pool to all events resets that pool's shift to zero. Checkbox edits collapse duplicate entries into one entry per selected track. This allows all currently available tracks to remain reachable from the existing 8-bit selector. Weighted pools can still be imported through project JSON. Selection uses Soundmod's existing selector byte; uniform randomness is not established. A finite song does not cause automatic playlist advancement.

Names and the saved project persist in `out/manager/track-names.json` and `out/manager/project.json`. **Save project** persists the current configuration; exporting also saves it and writes a downloadable project with names. Use **Import project** to restore such a JSON file after loading the catalog. Names are metadata and are not embedded in the ROM. Each build gets its own output directory; source files are never overwritten. `--data-dir PATH` changes the local state/output directory.

All 67 eligible foreign songs are packed by the existing builder, even when a pool selects fewer songs. Export checks BPS source, target, and patch checksums and decodes the new patch to confirm that it reproduces the output ROM byte-for-byte.

## Audio previews

Previews currently require **Linux**, a C compiler named `cc`, SDL2 development headers, and the mGBA SDL executable. The installed/tested executable is `/usr/games/mgba`, version 0.10.2. An alternative executable can be supplied with `--mgba PATH`; compatibility with other debugger versions is not established.

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

The Python suite passes 44 tests, including manager input rejection, project/name persistence, invalid-project atomicity, preview cache/isolation, HTTP token/origin/path handling, default export fingerprint, and BPS reconstruction. Run:

```bash
python3 -m unittest discover -s tests -v
node tests/test_manager_ui.mjs
```

The Node check uses a lightweight DOM/API fixture to exercise catalog loading, unavailable rows, pool edits, names, preview links, export links, and project saves. It does not replace a real browser layout or end-to-end HTTP test. The execution sandbox prohibits listening sockets and Chromium's required socket operations, so a live server/browser smoke test could not be completed here. The HTTP handler is tested using in-memory requests.

Actual mGBA capture succeeded for EXEGP entry 1 and Soundmod entry 3: each produced a nonzero 3-second, 44.1 kHz stereo signed 16-bit WAV. The manager's default export matches reference SHA-256 `e20a5763e40d3510b200c9fd1a67597eb384d290007e3e38e3b40e5a621b5854`, the ROM the user reported sounded correct. Human feedback does not establish exhaustive listening coverage of all 115 candidates.
