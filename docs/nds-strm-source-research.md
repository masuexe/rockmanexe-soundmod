# Star Force STRM source research

All four music streams in the pinned source archives have verified offline
ADPCM decoding. They remain outside the 54-song production library. This source
investigation does not establish GBA playback, conversion quality or listening
acceptance and does not change the accepted ROM14D9DEF4 or its delivered patch.

## Source and decoder checks

The original SDAT FAT files supply these streams. All use encoding2 (NDS ADPCM),
two channels and a declared26182Hz rate. All have an enabled loop, including
STAFFROLL. Sample positions below are per channel.

| Source | Music | Samples | Loop start | Duration seconds |
| --- | --- | ---: | ---: | ---: |
| ssr1 file119 | TITLE | 1863836 | 173736 | 71.188 |
| ssr1 file120 | STAFFROLL | 4155636 | 3457448 | 158.721 |
| ssr2 file166 | TITLE | 1694858 | 940816 | 64.734 |
| ssr3 file367 | TITLE | 1614619 | 916432 | 61.669 |

The local bounded header interpretation and every channel block match
[ndspy's STRM parser](https://github.com/RoadrunnerWMC/ndspy/blob/master/ndspy/soundStream.py).
A separate research decoder resets the predictor/index at every channel block,
decodes low nibbles first, omits the predictor as an output sample and trims
unused final nibbles to the declared sample count. It uses NDS saturation
at -32767. This is an offline helper; the existing SSEQ wave decoder is unchanged.

All18,657,898 PCM16 channel samples match the independently built
[vgmstream decoder](https://github.com/vgmstream/vgmstream/blob/6802153425adde134e49394fc653455166d7d2f2/src/coding/ima_decoder.c)
bit for bit. The reference build disables optional external codecs and uses
commit6802153425adde134e49394fc653455166d7d2f2. Its
[STRM metadata reader](https://github.com/vgmstream/vgmstream/blob/6802153425adde134e49394fc653455166d7d2f2/src/meta/nds_strm.c)
also supplies the independent playback loop positions.

For every stream, decoding an intro plus two loop periods exactly matches
one full decoded source followed by its loop suffix. Seeking to the loop start
also exactly matches that suffix. These are software decoder tests, not native
GBA loop or latency measurements.

An initial helper assertion rejected SF2 TITLE's zero file padding after the
aligned last block. The corrected assertion bounds and checks those zeros;
no source asset, PCM algorithm or production file changed for that correction.

## Capacity investigation

The current10512Hz resampler's output-length arithmetic predicts the following
PCM8 storage, including its prefix guard and integer loop period. These are
estimates from the current formula, not rendered or packed results.

| Music | Samples per channel | Stereo PCM8 bytes | Within current one-million-sample bound |
| --- | ---: | ---: | --- |
| ssr1 TITLE | 748361 | 1496722 | Yes |
| ssr1 STAFFROLL | 1668516 | 3337032 | No |
| ssr2 TITLE | 680518 | 1361036 | Yes |
| ssr3 TITLE | 648302 | 1296604 | Yes |

The estimated total is7,491,394 bytes. Adding it directly to the measured
25,646,828-byte 54-song Falzar pool yields33,138,222 bytes before additional
metadata/alignment or resource sharing. This is close to the32MiB ROM limit;
it is not proof that a full stream library export fits. Remaining SSEQ additions
will also require capacity planning. The user goal does not require every song
to be included in one exported ROM, but each chosen pool must fit its target.

The next capability experiment should start with one title stream, preserve
stereo and its intro/loop distinction, filter before downsampling, and verify
native channel ownership, clock drift, loop seams and effects/transitions.
STAFFROLL needs an explicitly bounded longer-sample or segmented path before
registration. No current bound is silently relaxed by this investigation.

## Local evidence

Ignored `out/nds-research/strm-source-v1/` contains source fingerprints,
`metadata.json`, `decoding-validation.json`, `loop-validation.json`,
`capacity-estimate.json`, decoder/build logs and helper fingerprints in
`research-notes.json`. Original assets, decoded audio and reference source/builds
remain outside Git. No new ROM was delivered or manually accepted here.
