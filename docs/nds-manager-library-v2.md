# NDS manager library v2: eight registered songs

This batch appends three previously accepted standalone configurations to the
manager library. The source converter, sample preparation, native mixer,
relocator, realtime implementation and project schema are unchanged.

| Slot | Source | Song / selector | Gain | Playback |
| --- | --- | --- | ---: | --- |
| 8959 | SF1 | ROOM / `sf1-room-antialias` | +3.5dB | Looping, six tracks |
| 8960 | SF2 | HENKAN / `sf2-henkan-antialias` | +3.5dB | Finite, four tracks |
| 8961 | SF3 | KANDO / `kando-antialias` | +3.5dB | Looping, seven tracks |

The original five tuples and slots8954–8958 remain intact. The NDS slot base is
now explicitly8954, with a guard rejecting overlapping future GBA donor ranges.
The finite flag is checked against the conversion result. SF1 HENKAN keeps its
separate0dB setting; SF2 HENKAN uses its accepted+3.5dB setting and separate bank.
The API exposes the registered library count and the page displays it dynamically,
so source selection does not change the advertised supported subset.

All eight freshly generated blobs match their standalone accepted bytes;
conversion and dependency JSON values match too. Prior DS reference, filtering
and per-song native evidence is reused under those identities. No new original
DS render, timbre comparison or cross-source acceptance transfer is claimed.

## Compatibility and checks

A saved v1 project loads and exports with the same keys, pools and original
song IDs. The enlarged table changes its ROM/BPS bytes; it is not accepted
merely because its project is compatible. New source/configuration keys append
without renaming existing entries or changing the project schema.

A fresh537-case Python suite without skips and both JavaScript suites pass.
Tests pin the original five tuples, check all eight names/slots and both finite
flags, retain mixed GBA/NDS selection and saved names, and exercise previews,
source disabling/reload and selected-only export. DOM checks verify the dynamic
count. The original compiler/relocator/native sources and v10–v38 archives retain
their identities.

Actual agbplay starts produce nonzero stereo for all eight songs. Real localhost
HTTP checks read the eight-entry library, upload a renamed original, save/export
and download the exact final ROM/BPS. Real mGBA previews cover all three added
songs; the12-second SF2 HENKAN capture has four seconds of zero PCM at its end,
and cached previews leave saved pools unchanged.

The exact Gregar export contains SF1 ROOM at title and SF3 KANDO for ordinary
virus and communication battle requests. A controlled native probe follows7610
ordinary frames between queue/scene/effect calls. It covers at least two complete
common periods for both songs, all80/84 prepared waves, three cross-family
switch/native-restore/restart cycles, effects100/129 and queued stop. Current
music owners are checked against each bank, and native restoration/stop clears
imported tails. It does not measure all NOTE allocations or establish actual
battle/results/map transitions, linked play or rematches.

A fresh review-server load/conversion/export and a separate HTTP export reproduce
the same final ROM/BPS. Falzar additionally passes an eight-song load, actual
export/BPS reconstruction and three3-second new-song previews; full loops,
finite completion, effects/lifecycle and manual Falzar acceptance are not
established by those short clips.

Existing ten-voice,10512Hz/PCM8, sample filtering, volume/envelope/tempo and
per-song allocation/tail limits remain. KANDO's original DS reference exceeds
the native voice budget; source event preservation is not full timbre or
voice-allocation equivalence. The fixed library remains a supported subset,
not general NDS import or whole-archive compatibility.

## Exact-ROM and workflow acceptance

Earlier standalone and v1 manager acceptance was not transferred. The requested
manual checks covered the eight-song roster and three added previews, project
save/reload/export, at least20 seconds of title ROOM and45 seconds of battle
KANDO across its first repeat, chip/Buster effects and three battle→map→battle
cycles. No new three-minute per-song fidelity comparison was requested. Only
these two imported songs are in the delivered gameplay ROM; previewing SF2
HENKAN does not establish its gameplay acceptance in another manager export.

- ROM CRC32: `85108329`; size9552856 bytes.
- ROM SHA-256: `6f06a99eb7463d3534107f8524172afd363f99d73b0aa61eb8643ca03ad6288e`.
- BPS SHA-256: `3114ad079a6a7e61156cb3598deaccef1684eace257e2b93bbfaf5a781122e3f`.
- Local folder: `out/nds-research/nds-manager-library-exe6-v2/`.
- Windows delivery: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

Research receipts remain under `out/nds-research/nds-manager-library-v2/`.
ROMs, source assets and local research outputs stay outside Git.

On 2026-10-25, the user reported “测试无问题” for this exact Gregar ROM and
the requested eight-song manager preview/save/reload/export workflow, title
20-second and battle45-second first-repeat listening, effects and three
encounter cycles. These are user-reported passes, not independent timing or
gameplay recordings. No new three-minute fidelity review, SF2 HENKAN gameplay
in another export, arbitrary pools, linked play, rematches or manual Falzar
acceptance is inferred. Acceptance remains specific to the fingerprint above.
