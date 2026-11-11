# SF1 STRM title capability experiment

This experiment adds a separate bounded STRM path, starting with Star Force1's
`STRM_BGM01TITLE`. It does not register streams in the 54-song manager or change
the existing SSEQ decoder, resampler, native mixer, relocator or cache policy.
All126 content items remain in the full-catalog goal.

## Conversion

`nds_stream.py` checks the standard header, HEAD/DATA layout, block/sample counts,
loop, codec, stereo layout and bounded zero padding before decoding. Predictor
and index restart for each channel block. Low nibbles decode first, the predictor
is not output as a sample, unused final nibbles are trimmed, and NDS saturation
uses -32767..32767. All four original streams match full independent vgmstream
PCM16 references; no STRM game audio is stored in Git.

Each channel goes through the unchanged Blackman-windowed sinc filter to
10512Hz PCM8. The title produces two748361-byte channels with a69791-sample
prefix and678570-sample loop. Three filtered left-channel values clamp at PCM8
limits; the right channel has zero clamped values. No normalization hides this.
The loop includes the existing filter guard and integer-period tuning.

The MPlay bank has separate left/right PCM tones. Two simultaneous TIE commands
start at tick0 with hard left/right pan and an immediate sustained envelope.
The sequence waits indefinitely without retriggering either sample; the PCM
headers preserve intro plus loop. The export enables ten PCM voices and uses
music priority20, leaving capacity for effects without a new mixer.

The initial gain policy is explicit: metadata volume70 multiplied by+3.5dB,
rounded to native VOL105. This is an experimental linear policy, not verified
DS player/master gain or fade emulation. Native integer pitch rounding and the
existing mixer/sample-rate approximation remain. Listening must assess volume,
filtering, stereo image and seams; PCM16 reference equality alone proves none
of those converted/native qualities.

The current one-million-output-sample resampler bound remains unchanged.
SF1 STAFFROLL exceeds it and still requires a longer-sample or segmented route.
Only looped stereo ADPCM with the checked512-byte full-block layout is admitted;
other formats fail explicitly. This is not universal STRM support.

## Build and verification

Use the original Japanese ROMs already pinned by the project:

```sh
python3 scripts/build_nds_stream_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds \
  --base ../roms/exe6.gba --output out/sf1-strm-title
```

The output directory must be new. The command emits ROM/BPS, converted blob,
conversion/dependency reports, catalog and build manifest. Source ROM and SDAT
identities are verified before exporting. Stream fields are labelled STRM in
the manifest rather than claiming an SSEQ index. Source assets remain local.

Seven focused tests cover block predictor reset, stereo ordering, odd final
nibbles, symmetric NDS saturation, invalid layouts/counts/indexes, bounded zero
padding, gain headroom and two-TIE/loop/pan structure. They use generated fixtures.
The actual four-stream PCM comparisons and single-title native results are
separate ignored local research evidence.

The final Gregar ROM CRC32 is `20069322`, size9890980 bytes; SHA-256
`ac7baa7cb8989e4b3ec4c8f8098ce08408e63070fbc51c184441f88561ee9137`.
Title1, ordinary virus21 and communication scene65534 all select this stream
at slot474. Other pools keep native music. The manager's accepted54-song ROM
is a separate artifact and receives no changed acceptance from this experiment.

Exact relocated PCM headers/payloads match the generated blob. BPS reconstruction
passes, with no relocator audio adjustment. A fresh public CLI build reproduces
all seven artifacts byte for byte. A six-second real mGBA stereo preview is
nonzero, with peak18906/32768; this is startup evidence, not full-song fidelity.

Natural title playback passes12500 frames with12496 settled stereo observations.
Both channels retain equal sample counters/fractional phase and independent waves,
with no TIE retrigger or slot change. Both cross PCM joins at frames4253,8109
and11965. Remaining-count plus sample position equals748361 throughout. The
measured native integer frequency is10511Hz versus stored10511.993Hz, a
-0.164-cent rounding difference; the measured loop period is64.560 seconds.

A separate2550-frame controlled run checks effects100/129, three native-map
restores and stream restarts, communication scene entry/reentry, and queued stop.
Every imported-music frame retains exactly two owned channels. No imported
channels remain after native restoration or stop. This uses controlled helper
calls and does not prove actual gameplay or linked sessions.

A fresh557-test full Python suite passes without skips, including the seven new
STRM cases. This is a new full run, not reuse of the earlier550-case evidence.
The exact BPS was atomically copied to
`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps` after automated checks passed;
the destination SHA-256 matches `1097d19a80dd8482dd6b9681b4fb5cf407526111677d38adb64156830f32a626`.
The user reports “可以，没问题” for the requested checks on this exact ROM.
This records user-reported acceptance; the durations and gameplay were not
independently timed or observed. Acceptance covers this Gregar experiment only.

Requested manual checks are title playback for210 seconds including all three
joins; virus battle for90 seconds with chips/Buster and three battle-map-battle
cycles; and communication playback for90 seconds with effects and restoration.
Assess volume, stereo, seams and fresh intro after restart. These are user checks,
not claims established by the automated harness.

## Evidence boundaries

Ignored `out/nds-research/sf1-strm-title-exe6-v1/` holds exact fingerprints,
full-reference comparisons, packing/reproduction results and native transcripts.
Early local harness failures remain distinct: a wrong synthetic index mutation,
strict rejection of valid SDAT padding, use of the SSEQ-only file reader, a numeric
communication trigger instead of the scene name, JSON list/tuple mismatches in
prepared dependency reuse, and an old manager slot in the controlled helper.
These were not manual ROM failures. The final build is reproduced independently.

Natural playback and controlled queue/scene/effect calls are separate evidence.
The latter inject PC/LR/arguments and disposable scene RAM; they cannot establish
actual battle/map gameplay, linked play or rematches. No previous SSEQ listening
acceptance transfers to this stream or ROM. The stream's two sustained voices
also require effects tests: a stolen voice could remain absent until restart.
