# SF3 GAMEOVER singleton filtering and finite completion

This separate experiment imports SF3 `BGM_GAMEOVER` (sequence40) with the
existing singleton FIR and explicit finite mode. It changes no shared converter,
runtime mixer or native NOTE handler. Eight singleton tracks preserve83 notes,
all source controls and per-track END ticks239/287/311/311/335/323/287/335.
These ENDs are one tick earlier than the accepted SF1 cue; its manual acceptance
does not transfer to this source or ROM.

## Source and packing evidence

All seven local game variants retain their pinned identities. SF3 Black Ace and
Red Joker share the verified SDAT; this experiment uses `ssr3b.nds`, file187,
SDAT SHA-256 `bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
A fresh20-second independent software DS execution matches all83 finite notes,
13 raw waves, tempo/depth controls and envelope evidence. Its peak is22367;
coarse100ms observations reach16 voices. This is software reference evidence,
not hardware audio or a native polyphony bound.

The export prepares39 tones/waves and283400 PCM8 values. Per-source-key FIR
output, tuning, loop headers, tone pan, ADSR and relocated data are checked
against the packed ROM. Filtering clamps742 stored values (399 negative,
343 positive); unclamped values span approximately−147.266…153.022. This is
offline storage clipping, not mixer clipping or an audible-error bound.
Maximum resampling step is5.002212389380531. The song blob is297652 bytes;
the complete ROM appends301344 bytes. No merged, upward-bend, LFO, fitted
envelope or finite release-snapshot capability is enabled.

## Native finite-score and stop evidence

Natural frontend observation covers174 frames to clock337, all39 waves and
every track FINE, with PCM observed each frame. It uses no register/RAM
injection, header redirection, forced repeats or clock restart. All83 original
NOTE calls allocate; none is rejected or preempts a held/starting voice. An
unaccepted same-source plain control has identical NOTE identities, clocks,
outcomes and all slot choices; both reuse54 nonzero-envelope release tails.
All441 compiled playback commands match the control exactly, with no GOTO.

Four release-tail reuses have owner0 after the previous source track FINE.
Checks still require release flags, the previous wave/key, an inactive previous
track and a clock beyond its END. No held-voice ownership guard is relaxed.
All83 allocated gates, keys, velocities and source-derived priorities match.
There are6255 BEND/BENDR/TUNE/PAN/VOL byte comparisons within active per-track
windows; inactive cached bytes are outside this comparison.

Source6 stereo checks include definition pan and one stable-pan frame. They
cover93 nonstarting/nonrelease observations:47 at PAN20, median balance−0.7273,
and46 at PAN100, median+0.6396. Changed-pan and starting/release observations
are excluded explicitly. This bounded diagnostic is not whole-mix alignment.
The active clock follows `1 + floor((frame-1)*146/75)` with anchored residual
below one tick. Source tempo145 maps to native146; this is an emulated phase
check, not hardware/wall timing.

A separate1200-observation natural root-callback probe reaches and freezes
clock337, observes981 empty imported-channel states after completion and
requires all final600 states inactive, empty and clock-stable. The15-second
SDL preview peaks at22134 and its final10 seconds contain only zero PCM.
Controlled effects100/129, continuation, queued stop and three restoration
cycles pass using disposable emulator PC/LR/argument injection. Actual chip
gameplay, linked play and rematches remain separate manual scope.

Initial copied SF1 END fixtures expected one extra tick and failed before
native NOTE capture or at the focused exact-END assertion. A frontend invocation
also passed a directory instead of a ROM and failed before capture. Failed
sources/logs are retained locally. Corrected exact SF3 expectations and CLI
arguments change no ROM; failed runs are not passing evidence.

## Regression scope

Twenty focused cases cover the ten selector additions since the frozen SCHOOL
full suite. Removing the new SF3 finite selector restores the whole accepted
COMICAL builder AST. Removing all ten additions restores the frozen487-test
builder AST, with other baseline libraries/tests byte-identical. Both finite
selectors and both source families retain explicit guards.

The487-test no-skip suite and58 accepted/two historical control rebuild record
are reused under that source/AST isolation; this is not a fresh507-test suite.
Fresh integrity checks reconstruct70 archived ROMs from their BPS/base pairs;
they do not recompile those songs. Formal CLI reproduces all eight native-tested
files byte for byte. Recursive v10–v37 archives retain their identities and
their historical counts. Ten-voice tails and filter/PCM8/volume/ADSR/tempo
limitations remain.

## Accepted exact ROM and test patch

- ROM CRC32: `F618E431`; size8689952 bytes.
- ROM SHA-256: `66bc1edf1ef1b7e33de21a710e02134660c70da162adf132b7b934a13c36218b`.
- BPS SHA-256: `c4dc792b53af29227d3540d933a42fa6b54f6549579fc5b8a5f97f742b8c82f8`.
- Local folder: `out/nds-research/sf3-gameover-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

`patch-delivery.json` records transport verification separately from acceptance.
On 2026-10-24, the user reported “测试无问题” for this exact ROM and the three
requested checks: complete roughly three-second cue/tail, at least10 seconds
silent without replay, chip/Buster effects during/after it, and three
battle→map→battle cycles with restored map music and fresh cue starts/ends.
ROM, BPS and delivered test-copy fingerprints were verified at acceptance.
These are user reports, not independently observed/timed checks. Linked play,
rematches, broader gameplay, three-minute looping and comparative preference
remain unestablished. No acceptance transfers to plain control or other families.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-gameover-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-gameover-antialias-exe6-v1
```

Use a fresh output directory. ROMs, source assets and local outputs stay out of Git.
