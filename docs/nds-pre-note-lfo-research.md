# Pitch-LFO setup before the first note: Star Force 1 GOWAIINCHO

This experiment corrects a source-classification and compiler boundary error.
SSEQ 7 `BGM07GOWAIINCHO` initializes track 2 depth at tick 24, but its first
note is at tick 688. It does not enable modulation on an already sounding
voice. The earlier equality guard rejected both setup before the first note
and activation afterward using the same diagnostic. On 2026-10-17 the user
reported no issues after the requested four-minute battle listening and
gameplay checks for this exact ROM.

Artifact: `out/nds-research/sf1-gowaiincho-delay-exe6-v1/`.
CLI song: `sf1-gowaiincho-delay`.

## Corrected boundary and unchanged limits

The fixed-delay compiler now accepts initialization before or at the first
note timestamp, including the existing same-tick note-then-depth order.
Activation after the first note's timestamp remains rejected. Modulation
settings must still remain fixed after activation, except positive depth
changes when the separate live-depth flag is explicitly enabled. This build
does not enable live-depth or envelope fitting modes.

The silent target track can advance its shared triangle after setup, with
no notes to sound it. The first note still emits the existing LFOS reset and
LFODL commands, resetting phase and starting a fresh note-on delay. Source
DS voices only allocate their independent counters when notes start. The
correction changes admissibility and report metadata; emitted commands for
previously accepted inputs are unchanged.

Track 2 uses type 0, speed 25, depth 20, range 1 and delay 10. Source tempo
105 maps to target parameter 105 (83.619 ticks/second). Native LFOS 29/MOD 2
and LFODL 5 approximate the DS sine and delay. Rounded phase displacement
is 47.836 ms versus the DS 52.095 ms wait; total native counter wait is
59.795 ms including the baseline zero-phase tick. The first note occurs
about 8.23 seconds into target playback. Overlapping voices and release
tails still share the target track's phase and delay, reset by newer notes.
PCM8, envelope, tempo, waveform and ten-voice allocation approximations remain.

The pinned Japanese `ssr1d.nds` supplies SDAT file 667, SSEQ file 6, bank 39,
volume 80 and source player 0. All eight tracks and 24 samples are retained,
with 12 voice contexts and 415,760 generated MPlay bytes. Japanese EXE6 Gregar
uses eight-track capacity, ten PCM voices at 10,512 Hz and +3.5 dB imported
gain. Title (1), ordinary virus music (21) and communication scenes select
slot 474. Original entries and prefix bytes outside declared hook/config
ranges are preserved. BPS reconstruction passes; input ROMs are unchanged.

- ROM: 8,808,324 bytes, CRC32 `AB4E8BA6`.
- SHA-256: `531e03794ba6dccb3396c4e88734921ecd10fd381ec2eba5e6f5e4ad36405299`.
- Compiled loop start/period: 7800/4704 ticks. First jumps are approximately
  150 and 206 seconds. Warmup unrolls existing music without adding silence.

## Evidence

The independent 180-second software DS reference covers at least two complete
source loops on every track: 4,742 notes, all 24 decoded PCM16 samples, 65
ordinary controls, four depth controls and 54,632 active sine observations.
Delay checks cover 2,220 waiting updates and 222 observed activations.
The depth-control and first-note traces independently confirm tick 24 setup
before tick 688 sound. The existing pinned `reference-player-depth-v2`
renderer supplies these observations without synthesis changes.

`lfo-window/validation.json` checks 2,400 natural frames through clock 3359,
with all note/track states and track 2's LFO matching actual MPlay RAM.
There are 132 delayed zero-phase snapshots. At clock 688, before executing
the first note, the silent track has phase 56 and no delay; at clock 689
the note has reset phase/value to zero and loaded delay 5, with count 4 after
one tick. These snapshots establish that initialization did not consume the
first sounding note's delay.

The diagnostic sequence-clock comparison has 3,997 allocated-voice
observations, RMS pitch difference 11.96 cents and maximum 26.5625 cents.
It is not waveform alignment or equal source/target voice allocation.
`preview/preview.wav` and `comparison/listen.html` provide 30-second actual
native audio and normalized software-DS/GBA comparison.

`runtime/` checks original effects 100/129, ordinary/synthetic communication
dispatch, music continuation, queued stop, native restoration and three
controlled restart cycles. Debugger helper calls do not establish actual
gameplay. Neither this probe nor the natural title window executes a complete
GBA loop. Complete-loop listening has user-reported acceptance; instrumented
full-loop execution remains uncompleted.

All 194 Python tests pass. New regressions check setup during a rest before
the first note, note-on delay reset, continued rejection of later parameter
changes, actual GOWAIINCHO timing, BPS reconstruction and original-data
preservation. All thirteen earlier accepted ROMs and BPS patches rebuild
byte-identically; fingerprints are in
`out/nds-research/pre-note-lfo-research-v1/accepted-rebuilds.json`.
`validation-summary.json` collects automated results; `manual-testing.json`
records user-reported acceptance for this exact ROM on 2026-10-17. The
requested checks cover four-minute battle listening, the part entering after
about eight seconds, held notes/release tails, loop joins, chips/Buster
coexistence, map restoration and next-encounter restart. No timed recording
or full-loop execution trace was supplied; specific linked play and rematches
were not separately reported. The synthesis approximations and bounded
automated coverage remain unchanged.

The archived v6 audit remains at 43 packed candidates. Future scan policy
text now describes pre-note setup accurately; this experiment does not rerun
the batch or claim other newly accepted songs. Further source inspection
also identifies PLANETARIUM's setup before its first note (0 versus 24),
while BOSS (3840 versus 0) and Star Force 2 KAICYOU (768 versus 48) are
confirmed examples of actual later activation requiring further research.

## Reproduce and listen

```bash
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-gowaiincho-delay --event 1 --event 21 --event scene:communication \
  --out out/nds-gowaiincho-example
mkdir out/nds-gowaiincho-example/reference
out/nds-research/reference-player-depth-v2/nds-reference \
  out/nds-gowaiincho-example/source.sdat 7 180 out/nds-gowaiincho-example/reference
python3 scripts/validate_nds_experiment.py out/nds-gowaiincho-example \
  --reference out/nds-gowaiincho-example/reference --lifecycle \
  --out out/nds-gowaiincho-example/runtime
python3 scripts/validate_nds_lfo.py out/nds-gowaiincho-example --frames 2400 \
  --reference out/nds-gowaiincho-example/reference --out out/nds-gowaiincho-example/lfo-window
```

Use fresh output directories. Listen in battle for four minutes, checking
the part entering after about eight seconds, held notes/release tails and
joins near 150/206 seconds. Use chips and the Buster, finish the battle,
confirm native map music restoration and start another encounter to check
GOWAIINCHO restarts. Title scenes end too early for complete loops.
