# EXEGP song 1: dependencies and experimental PvP transplantation

Status: supported sequence closure, donor sustained execution, resource relocation, BPS reconstruction, and transplanted sustained execution verified. This is a single-song experiment. Full Soundmod integration, an automatic in-game selection hook, multiplayer validation, and a listening review are not complete.

## Sequence and dependencies

Donor: the verified EXEGP ROM (`9217FB18`), audio table file offset `0x160658`, ID 1, header address `0x081BF480`, tone-bank address `0x0815F828`.

The dependency analyzer follows running commands, pattern calls/returns, waits, notes, ties, and supported control commands. Reference encodings come from [MPlayDef.s](https://github.com/pret/pokeemerald/blob/master/sound/MPlayDef.s); pattern/note handling is checked against [m4a_1.s](https://github.com/pret/pokeemerald/blob/master/src/m4a_1.s). Tone and sample layouts use [m4a_internal.h](https://github.com/pret/pokeemerald/blob/master/include/gba/m4a_internal.h). Actual EXEGP behavior is validated separately in mGBA, rather than assumed from another game.

The selected song contains:

- Seven tracks, occupying 1,649 sequence bytes.
- Six top-level voices, numbered 0–5.
- Thirteen reachable tone records: six top-level records and seven drum-map records.
- Nine distinct PCM samples, totaling 105,006 bytes including their 16-byte headers.
- A 36-byte song header and 61 pointer fields requiring relocation.
- 106,847 covered source bytes in total, excluding unrelated bank entries and padding.

Voice 5 is a drum-map tone. It selects child records using note keys 36, 38, 43, 46, 47, 49, and 50. Several records share a PCM sample, and voices 2 and 3 also share a sample. Copying only the sequence or only the top-level bank would therefore be incomplete.

All seven tracks reach `FINE`; this song has no infinite sequence loop. Its longest track ends at sequence tick 1803. Pattern blocks are sometimes encountered inline before later calls reuse them. A `PEND` with an empty pattern stack falls through; treating it as an unconditional track end would omit later music.

Each consumed sequence range, note/voice pair, tone record, sample header/length, resource hash, and pointer site is retained in `dependencies.json`. Unsupported commands, nonzero key shifts, invalid references, unsupported sample encodings, nested composite tones, excessive pattern depth, and zero-time cycles fail analysis rather than producing a relocation-ready claim. This is not yet a complete parser for every song in every EXE ROM.

```bash
python3 scripts/analyze_song.py roms/exegp.gba \
  --table 0x160658 --id 1 --out out/exegp-song1-analysis
```

## Donor sustained execution

The validator boots a disposable EXEGP copy, injects ID 1 at the first naturally reached start-by-ID routine, then lets the game execute normally frame by frame. The game subsequently restarts the same song once; this clock restart is recorded rather than hidden.

For every frame and track, the model is compared with the actual cursor, remaining wait, pattern depth, note key/velocity, running command, completion flag, and copied tone record. Mixer channel sample pointers are checked against the dependency closure. PCM buffers are sampled every 60 frames to establish changing, nonzero mixed data.

The donor run passed 1,690 frames and 11,830 track-state comparisons. All nine samples were observed on mixer channels, 28 distinct nonzero PCM-buffer hashes were recorded, and all tracks ended at player clock 1804.

```bash
python3 scripts/validate_song.py roms/exegp.gba \
  --id 1 --out out/exegp-song1-sustained
```

The dummy SDL backend discards audio. These checks establish sustained sequence/mixer execution, not subjective sound quality or an exported WAV.

## Relocation into PvP

The builder requires the verified EXEGP donor and EXE4.5 PvP 0.6.0 fingerprints. It builds PvP from the original EXE4.5 ROM and its checked BPS patch. The selected target entry must be empty; occupied entries such as PvP ID 69 are rejected.

The experiment uses target ID 0 and EXE4.5 music player 31. Its eight-track capacity accommodates the donor's seven tracks. Both table halfwords are set to 31, following existing EXE4.5 music entries; the donor player index 0 is not copied across games.

Selected resources are appended after the existing PvP image. Top-level and drum banks are allocated as sparse, zero-filled tables preserving the original indices. Used rows are copied and their pointers rewritten. Unused rows do not retain unrelated donor pointers. Track starts, pattern targets, tone-bank links, and sample pointers are all relocated. Shared samples remain shared.

The resulting dependency analysis reproduces the donor's notes and sequence timing. PCM headers and sample payloads compare byte-for-byte with the donor. Existing PvP bytes are unchanged outside the selected eight-byte audio entry and the explicitly declared startup mixer configuration.

ID 0 is provisional: the original Soundmod also adds a track there. A combined Soundmod/PvP/EXEGP catalog must allocate stable IDs and resolve that collision before adopting this experiment's slot assignment.

## Mixer compatibility finding

The donor uses ten PCM mixing channels. EXE4.5's effective startup configuration uses four, independently of the music player's track capacity. The first transplanted run matched all sequence states but exposed only seven of the nine samples on mixer channels.

EXE4.5 initializes the sound library using the literal `0x0093C400` at file offset `0xEE328`, then invokes SoundMode again from `0x080004E0`, using `0x0093040D` at file offset `0x504`. Changing only the library literal is ineffective because the later call restores four channels. This was confirmed by breakpoints at SoundMode (`0x080EE85C`) and by its runtime arguments.

The final experiment changes only the channel field in the effective game-startup literal:

```text
File offset 0x504: 0x0093040D -> 0x00930A0D
Actual changed byte: 0x505, 0x04 -> 0x0A
```

Other SoundMode bits and the library default remain unchanged. The validator observes ten channels after boot. The target still mixes at 176 samples per VBlank (reported rate 10,512), whereas the donor uses 264 (15,768). The relocated encoded samples are identical; mixed output is not claimed to be bit-identical across these configurations.

Increasing the global budget also affects other sounds and mixer work. This experiment has not been tested in PvP multiplayer or benchmarked on hardware. A future manager must account for mixer budgets as well as track capacities.

## Experimental build and verification

```bash
python3 scripts/transplant_song.py \
  --base roms/exe45.gba \
  --pvp-patch references/exe45_pvp_0.6.0.bps \
  --donor roms/exegp.gba --donor-id 1 --target-id 0 \
  --pcm-channels 10 --out out/pvp-exegp-song1-mixer10

python3 scripts/validate_song.py \
  out/pvp-exegp-song1-mixer10/transplanted.gba \
  --transplant out/pvp-exegp-song1-mixer10/transplant.json \
  --keep-song --out out/pvp-exegp-song1-mixer10-sustained
```

All output directories must be new. The builder exports:

- `transplanted.gba`: PvP plus the single donor song and declared mixer adjustment.
- `transplanted.bps`: applies directly to original EXE4.5 CRC32 `A646601B`, not an already patched PvP image.
- `transplant.json`: provenance, output hash, changed entry/configuration, bank allocations, resource locations, and relocated pointers.
- `source-dependencies.json` and `target-dependencies.json`: before/after dependency analysis.

The appended allocation is 109,780 bytes. The final ROM is 8,689,144 bytes with CRC32 `EC171492` and SHA-256:

```text
6506e9ccf891eee34ca2777bf2efbacd4e435b4c1bb8f71d5d9c2431e6de9b82
```

The exported BPS is 605,483 bytes. Decoding it against the original ROM reproduces the experimental image exactly, with all BPS checksums verified.

The transplanted sustained run passed 1,846 frames and 12,922 track-state comparisons, observed all nine relocated samples, and recorded 30 distinct nonzero PCM-buffer hashes. It reached the same final clock, 1804. One game-driven clock restart was recorded.

`--keep-song` is a controlled debugger intervention. When normal game code tries to start a different header on the selected music player, the validator redirects the header argument to the transplanted song. One such redirection occurred at frame 291. It does not install a permanent hook in the ROM. Therefore the experimental ROM does not automatically choose this new song during normal gameplay; it is currently demonstrated using the validator.

## Artifacts for reverse engineering

`dependencies.json` provides resource boundaries and reference sites suitable for annotations. The sustained `validation.json` and `debugger.txt` provide runtime evidence. `transplant.json` records exactly which source references were mapped to which target locations. These artifacts can be consumed by `rockmanexe-reverse`; its files were not changed.

The follow-up milestone implemented a unified catalog, stable IDs, batch Soundmod/EXEGP relocation, and a permanent start-by-ID selection hook; see [the unified build record](unified-catalog.md). Keep audible preview and mixer requirements in that design; parsing a valid sequence alone does not establish playback compatibility.
