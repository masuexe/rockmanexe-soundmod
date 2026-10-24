# SF2 HENKAN: filtered shared sample and finite long notes

This experiment adds `sf2-henkan-antialias`, using the existing singleton FIR
and explicit finite mode for SF2 sequence26 `BGM_HENKAN`. No shared converter,
native NOTE handler or runtime mixer changes. Four source-key50 notes retain
468-tick gates and starts0/0/12/12. Track-local alias127/TIE/EOT handling shares
one prepared wave while preserving distinct owners and END468/468/480/480.

## Source and packed data

All seven local source variants retain their pinned identities. The selected
source is Japanese `ssr2d.nds`, SDAT975, SHA-256
`eb092e07ab410a3c81db491f0feb905f6259b891fb0b3cedfccaeca78ddc4ab4`.
A fresh20-second independent software DS reference matches all four finite
notes, the decoded sample, control and envelope evidence. Its peak is21239
and coarse100ms observations reach four voices. This is software reference
evidence, not hardware audio or native polyphony proof.

The single nonlooped source sample has97280 decoded values. Per-key FIR produces
46356 PCM8 values, retaining a zero-extended filter tail and compensated tuning.
All prepared PCM, wave headers, alias tone, source root50, definition pan64,
ADSR and relocated data are checked. Resampling step is2.1002399165368195;
23 stored points clamp (8 negative/15 positive), with unclamped range about
−132.706…134.257. This is offline storage clipping, not native mixer clipping
or an audible-error bound. The blob is49832 bytes; complete ROM append53636.
Merged filtering, upward-bend, LFO, envelope fitting and finite release snapshots
remain disabled. Gain is+3.5dB, ten PCM channels at10512Hz.

## Native playback and shared ownership

Natural frontend playback covers299 frames to clock481, the one wave and all
four EOT/FINE ends, with PCM sampled every frame and no register/RAM injection,
header redirection or clock restart. All four original TIE calls allocate;
there is no rejection, held/starting preemption or release-tail reuse. All81
compiled commands match the same-source plain control exactly, with no GOTO.
All four gates/keys/velocities/priorities and5890 active-window native
BEND/BENDR/TUNE/PAN/VOL bytes match the source/compiled models.

Saved channel observations find255 frames with four distinct owners/slots
simultaneously using the same wave and alias127, from clock13 through423.
All four channels retain TIE gate0 and the expected owner, key and wave.
There are1052 held/nonstarting stereo observations,263 per source track:

| Source track | PAN | Median channel balance |
| --- | --- | --- |
| 0 | 114 | +0.7957 |
| 1 | 14 | −0.7935 |
| 2 | 127 | +1.0000 |
| 3 | 0 | −1.0000 |

The source definition pan is neutral64. These are bounded saved channel-volume
checks, not whole-mix waveform alignment. The nonlooped sample naturally exhausts
before EOT; every track has empty observations before its source END. No claim
is made that a held voice lasts the complete468-tick gate, or that EOT produces
an observed release tail. The compiled and naturally executed EOT/FINE schedule
is checked separately. Active clocks follow
`1 + floor((frame-1)*121/75)` with anchored residual below one tick. Tempo120
maps to native121; emulated phase is not hardware/wall timing.

A separate1200-observation natural root-callback probe settles at clock482,
records901 empty imported-channel states after completion and requires the
final600 states inactive, empty and clock-stable. Its clock is recorded
separately from frontend481. The20-second SDL preview peaks at20489; its final
10 seconds contain zero PCM. Controlled effects100/129, continuation, queued
stop and three restoration/restart cycles pass with disposable emulator
PC/LR/argument injection. Actual chip gameplay, linked play and rematches
remain separate manual scope. A copied stop-report song label was corrected;
the original label/report are retained, with native captures and ROM unchanged.

## Regression and historical reference

Twenty-two focused cases pass in prototype and after exact root migration,
covering all eleven selector additions since the frozen SCHOOL baseline.
Removing this branch/family entry restores the accepted SF3 GAMEOVER builder
AST. Removing all eleven additions restores the frozen487-test builder AST;
other baseline libraries/tests remain byte-identical. Family, capacity, finite
opt-in, gates, alias/EOT, controls and prefix/BPS bounds retain explicit guards.

The prior487-test no-skip suite and58 accepted/two historical control rebuild
record are reused under that source/AST isolation, not a fresh509-test suite.
Fresh integrity checks reconstruct71 archived ROMs from their BPS/base pairs;
they do not recompile those songs. Formal CLI reproduces all eight native-tested
outputs byte for byte; recursive v10–v37 archives and historical counts stay
unchanged. PCM8/filter/volume/ADSR/tempo limitations remain.

The newly rebuilt plain ROM and BPS match the previously accepted
[SF2 HENKAN finite experiment](nds-sf2-henkan-research.md) byte for byte:
ROM CRC `F43FB736`, SHA-256
`4a67c5e057d16d106fc505712d0519714bea423b4908b2c13fec5a7b1b982286`.
`prior-accepted-identity.json` pins that prior manual record and exact artifact
identity. This establishes the historical plain reference; it is no new manual
session or acceptance of the different filtered ROM. Comparative timbre
preference remains unreported.

## Accepted exact filtered ROM and test patch

- ROM CRC32: `93E960A6`; size8442244 bytes.
- ROM SHA-256: `a44759352eb3db41e705ffac7581567ff00f38b8b6d1c7d8d117431bb7f087f3`.
- BPS SHA-256: `dcca2eb3a18f8f1bfeb081bf4c4e14c6308804f103b423a65f65bc5c2dfe4b07`.
- Local folder: `out/nds-research/sf2-henkan-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

`patch-delivery.json` records transport verification separately from acceptance.
On 2026-10-24, the user reported “测试无问题” for this exact filtered ROM and
the requested roughly five-second cue/tail/stereo, ten-second silent no-replay
wait, chip/Buster effects during/after the cue and three battle→map→battle
cycles with restored map music and fresh cue starts/ends. ROM, BPS and test-copy
fingerprints were verified at acceptance. These are user reports, not
independently observed/timed checks. Linked play, rematches, broader gameplay,
looping and comparative preference remain unestablished. No acceptance
transfers to other source families.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-henkan-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-henkan-antialias-exe6-v1
```

Use a fresh output directory. ROMs, source assets and research outputs stay out of Git.
