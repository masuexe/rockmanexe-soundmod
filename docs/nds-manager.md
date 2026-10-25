# NDS music in the manager

The manager accepts fingerprint-pinned Japanese Star Force original ROMs as
music sources for Japanese EXE6 Gregar and Falzar. It reuses the existing
registered conversions, GBA resource relocator, playback pools and BPS exporter.
The current library contains seventeen configurations:

| Source | Song | Preparation | Gain | Playback |
| --- | --- | --- | ---: | --- |
| Star Force 1 | URA | Future-use upward filtering | +3.5dB | Loops |
| Star Force 1 | HENKAN | Finite future-use upward filtering | 0dB | Ends near six seconds |
| Star Force 2 | WIN | Filtering | +3.5dB | Loops |
| Star Force 3 | ROOM | Filtering | +3.5dB | Loops |
| Star Force 3 | BATTLE | Existing eleven-to-eight grouping and filtering | +3.5dB | Loops |
| Star Force 1 | ROOM | Filtering | +3.5dB | Loops |
| Star Force 2 | HENKAN | Finite filtering | +3.5dB | Ends naturally |
| Star Force 3 | KANDO | Filtering | +3.5dB | Loops |
| Star Force 1 | SCHOOL | Filtering | +3.5dB | Loops |
| Star Force 2 | WIN2 | Finite release snapshots and filtering | +3.5dB | Ends naturally |
| Star Force 3 | COMICAL | Filtering | +3.5dB | Loops |
| Star Force 1 | COMICAL | Filtering | +3.5dB | Loops |
| Star Force 1 | KANDO | Filtering | +3.5dB | Loops |
| Star Force 2 | DEMPAJIKEN | Fitted envelopes and filtering | +3.5dB | Loops |
| Star Force 2 | HOKORA | Nine-to-eight grouping and filtering | +3.5dB | Loops |
| Star Force 3 | WIN2 | Finite filtering | +3.5dB | Ends naturally |
| Star Force 3 | GAMEOVER | Finite filtering | +3.5dB | Ends naturally |

The [second library batch](nds-manager-library-v2.md) added ROOM/HENKAN/KANDO.
The [third batch](nds-manager-library-v3.md) adds SCHOOL/WIN2/COMICAL; its
delivered ROM6406CA45 has user-reported listening and added-song visibility
acceptance, with individual timing/workflow/gameplay subchecks not separately confirmed.
The [fourth batch](nds-manager-library-v4.md) adds the final six entries;
its exact ROM D1A5CB1F and all three requested workflow/listening/gameplay checks
have user-reported acceptance. Slow preview loading is separately under investigation.
Other songs and other NDS revisions are not offered by this library.
Existing standalone acceptance is source history; it does not accept every
manager-generated ROM. Target-specific and linked-gameplay coverage remains
separate.

## Use

1. Start the manager and choose **Rockman EXE 6 Gregar (JP)** or **Falzar (JP)**.
2. Select the Star Force sources under **Original music ROMs**. Local originals
   in `/home/harp/projects/nds/roms` are discovered automatically. Alternatively,
   use **Add music ROMs** to upload a supported `.nds` file, including a renamed
   original. All seven previously pinned Japanese source revisions are accepted.
3. Click **Load tracks** to validate originals and list the registered songs.
   Audio is prepared only when needed for a preview or export; the first use can
   take longer, and later sessions reuse checked local caches. Choose songs for
   each pool. GBA donors and native music can be used in the same project.
4. Use **Play now** for the converted GBA song through agbplay, or **Record mGBA
   preview** for an audio capture from a separately built target ROM. Neither
   option plays the original DS driver; agbplay's enhanced mixer can differ from
   game playback.
5. Save the project or export its BPS. The patch applies to the original selected
   EXE6 ROM. HENKAN ends naturally; a pool does not automatically advance when a
   finite song finishes.

Source choices, uploaded inputs, project pools and custom names persist in the
manager's local workspace. The exported project keeps stable song keys and names.
Load its source catalog before importing that project on another workspace.
Disabling a source follows the existing reconciliation behavior: unavailable
pool entries are removed and empty pools fall back to native target music.
Switching to another target removes NDS selections; stored source files remain.

## Packing and provenance

NDS slots8954–8961 follow all reserved GBA donor slots. The first five keep
slots8954–8958; the second batch appends8959–8961. Existing IDs and song
keys remain fixed when other sources are deselected. Each converted song has
its own source namespace, including two songs from the same original; relative
wave/tone offsets are never used to merge unrelated banks.

Every selected original is fingerprint checked again when loaded. The converter
also checks the pinned SDAT and existing headroom, grouping, sample and timing
guards. [On-demand conversion and persistent caching](nds-conversion-cache.md)
use original/SDAT/target fingerprints, registered configuration and loaded-toolchain
identity. Cache dependencies are reparsed from checked compiled bytes. Originals
must remain available and unchanged, even on a cache hit. Original game files are
read-only. Source uploads
retain the existing32MiB limit, which includes the seven pinned NDS originals.

Exports pack only songs actually used by pools. `build.json` records selected
conversions under `nds_manager`, with original/SDAT/generated-resource identity
and gain metadata. This field explicitly does not infer manual acceptance.
The compatibility audit records an accepted manager export separately from
standalone per-song matches, retaining its actual pool rules and reported scope.

No converter, native sound driver or mixer implementation changes are required.
Ten PCM voices,10512Hz mixing, PCM8 storage and existing filter, modulation,
envelope and timing approximations continue to apply. Earlier allocation and
release-tail limitations remain relevant to these unchanged song configurations.

## Initial five-song integration verification

The five freshly generated source blobs are byte-identical to their accepted
standalone versions; conversion/dependency JSON values also match. Their prior
software DS reference and detailed native-song evidence is reused under that
identity. No fresh original-DS render or new timbre preference is claimed.

The initial integration passes a fresh536-case Python suite without skips,
the existing audio-worklet suite and expanded manager DOM tests. Actual local
HTTP checks upload a renamed32MiB original, load all three families, save a name
and project, export and download files. Two fresh manager builds reproduce the
same ROM/BPS; an HTTP export under the final source also reproduces them.
Three non-NDS exports for EXE4.5 PvP, GP and EXE6 match the previous committed
manager byte-for-byte across ROM/BPS/project/catalog outputs.

All five converted songs initialize the actual agbplay player and produce
nonzero stereo samples. Real12-second manager mGBA previews play URA and HENKAN;
HENKAN's final four seconds are zero PCM, preview caching works, and saved pools
remain unchanged. These are disposable title-preview ROMs. Falzar additionally
passes an actual manager export/BPS reconstruction and two3-second previews;
its full lifecycle and manual gameplay acceptance are not established here.

The exact Gregar manager export separately passes4460 ordinary emulator frames
between controlled helper calls, including three cross-bank cycles, finite
completion with600 quiet observations per cycle, effects during and after the
cue, native music restoration, title/communication restart and queued stop.
These PC/LR/descriptor-assisted probes are not actual battle/map/linked gameplay.
The converter, relocator, native mixer and realtime implementation are unchanged;
recursive v10–v38 audit archives remain immutable.

Initial research-helper JSON-key/cache and preview-result-path fixture failures
are retained separately. They did not require audio or final-ROM corrections.
An interrupted regression run preceded the final startup-selection guard and
is not counted as a pass. The final full run uses the corrected source.

The exact delivery below has its own user-reported manager-workflow and Gregar
ROM acceptance; earlier standalone and dual-exporter acceptance was not transferred:

- Folder: `out/nds-research/nds-manager-exe6-v1/`.
- ROM CRC32: `8B49FA37`; size8774860 bytes.
- ROM SHA-256: `d11fe648a4840926209a36af14a83381f1762c7aaae5eb35b443c1d0ddbd5271`.
- BPS SHA-256: `0fa0d4f11e444d1fa232be75462e188ccea686bb0bd74d5ee77dcf722b93be29`.
- Test pools: title/communication URA8954, ordinary virus battle HENKAN8955;
  other native music events retain their original selections.

Manual checks cover the five-entry library, Play now, project save/reload/export;
correct title/battle music and at least ten seconds quiet after the finite cue;
chip/Buster effects and three battle→map→battle cycles. No new three-minute
source-fidelity comparison is requested. Actual linked play, arbitrary pool
combinations and manual Falzar acceptance remain separate.

On 2026-10-25, the user reported “测试无问题” after the requested combined
manager workflow and exact-ROM checks. Library/preview/save/reload/export,
finite cue/no-replay wait, effects and three encounter cycles are recorded as
user-reported passes. They were not independently observed or timed. No new
three-minute comparison, all-five-song gameplay/fidelity review, arbitrary pool
combinations, linked play, rematches or manual Falzar acceptance is inferred.
The exact ROM acceptance applies only to the fingerprint above.
