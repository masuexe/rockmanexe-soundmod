# SF1 HENKAN: finite filtering with a tiny upward echo detune

`sf1-henkan-antialias` explicitly combines singleton filtering, upward pitch
preparation, future-use bounds and finite source mode. This extends the former
loop-only upward guard only when future-use mode is also explicit. Other
finite/upward combinations retain their rejection; merged tracks, native LFO,
fitted envelopes, release snapshots and mixed finite/loop sources remain
excluded. The native mixer/NOTE handler are unchanged.

The source is Japanese `ssr1d.nds`, SDAT667, sequence26 `BGM26HENKAN`. All seven
local source variants retain pinned identities. A fresh20-second software DS
reference matches all four finite notes, both decoded waves and controls/
envelopes. Reference peak19260 and coarse maximum four voices are software
evidence, not hardware audio or a native polyphony bound.

## Exact finite score, gain and pitch

Four source-key48 notes retain534-tick gates, starts0/0/20/20 and per-track
END534/534/554/554. Native TIE alias127 and individual EOT-before-FINE ordering
are preserved, with no GOTO or invented repeat. The two prepared waves are
shared by source0/2 and source1/3. Primary tracks have pitch0; the later echoes
retain positive pitch1 unit (one64th semitone). Future-use bounds union every
subsequent source control through END across shared identities. Both waves
prepare at key49 with bound1, including first uses0/20; no tiny detune is rounded
away. One-octave/key127 and nominal cutoff guards remain.

The gain is explicitly **0dB**, matching the prior accepted plain HENKAN.
Default+3.5dB still fails native VOL headroom and is tested as a rejection.
No gain is silently clipped or normalized. Source tempo120 maps to native121.
The roughly six-second cue plays once, then stays silent until another request.

All prepared PCM, tuning, wave headers, roots, tone pan/ADSR and relocation are
checked. Total storage108998 PCM8 values; three clamp (two negative/one positive),
with unclamped range approximately−131.844…130.621. These are offline storage
values, not native mixer clipping or an audible-error bound. Maximum nominal
cutoff at the upward bound is0.850253924705601 of mixer Nyquist, not a brick-wall
or zero-alias guarantee. ROM append117832 bytes; ten PCM channels at10512Hz.

## Original native observations

Natural frontend and original NOTE probes cover345 frames to clock555, all
four EOT/FINE ends and both waves, without register/RAM injection, header
redirection or restart. Four of four TIE calls allocate, with no rejection,
preemption or release-tail reuse. All identities/clocks/slots and85 compiled
commands match the recreated plain reference. All gates/keys/velocities/
priorities and6750 active-window control-byte comparisons pass. Active clocks
follow `1 + floor((frame-1)*121/75)` with anchored residual below one tick;
emulated phase is not wall or hardware timing.

315 saved observations have four distinct owners/slots sharing two waves.
Both echo/base pairs retain the same wave/key/TIE gate, TUNE+1 on the echoes
and higher actual frequency words. The measured offset is1.5696476612 cents
against target1.5625, within the0.05-cent diagnostic tolerance. Fixed source
PAN16/112/0/127 has1310 held/nonstarting channel observations, with median
balances−0.7522/+0.7719/−1/+1. This is bounded channel-volume/frequency evidence,
not DS waveform or whole-mix alignment proof.

The nonlooped samples naturally exhaust just before their source gates; no
full-gate held-voice or observed EOT-release-tail claim is made. A separate
1200-observation root-callback probe freezes clock556, observes855 empty
imported-channel states after completion and requires the final600 inactive,
empty and clock-stable. Its clock is recorded separately from frontend555.
The20-second SDL capture peaks at12480; the final10 seconds are zero PCM.
Controlled effects100/129, continuation, queued stop and three restoration
cycles pass through disposable PC/LR/argument injection. Actual gameplay,
linked play and rematches remain separate manual scope.

## Fresh regression and historical identity

The complete525-case suite passes with zero skips, including five new tests
for finite opt-in/exclusions, exact FINE and tiny TUNE, looping/over-END rejection,
shared-wave later detune and the actual HENKAN gain/schedule/prefix/BPS case.
All74 historical ROM/BPS variants are freshly recompiled at their original
settings and remain byte-identical; this is not integrity-only reconstruction
or reused coverage. Their two historical unaccepted controls remain unaccepted.
Formal CLI reproduces all eight native-tested files exactly. Recursive v10–v37
archives and historical counts remain unchanged.

A local helper-generation quoting error prevented some initial native checkers
from being created. Their failed invocations stopped before capture and are
retained separately; corrected generation changes no ROM. These failures are
not passing evidence.

The recreated plain ROM/BPS match the previously accepted
[SF1 HENKAN finite cue](nds-henkan-research.md) byte for byte: CRC `5266B13B`,
ROM SHA-256 `2460891b9371ea374aa4934ed8c723307bb9b47907c26e9056128e9da1dedaba`.
The receipt pins that prior manual record. This is no new manual session or
acceptance transfer to the different filtered ROM. PCM8/filter/volume/ADSR/
tempo and ten-voice tail approximations remain.

## Accepted exact filtered ROM and test patch

- ROM CRC32: `1B230522`; size8506440 bytes.
- ROM SHA-256: `331891b75eb1555b2ef01cca1b8e10c7fe127bf7e63a9f8bb140b36d5767ebbe`.
- BPS SHA-256: `20e58ec9d73eb517f22ee1449f49d4db95b457b45068fb8d6dc6fea6cd8dadf7`.
- Local folder: `out/nds-research/sf1-henkan-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

On 2026-10-25, the user reported “测试无问题” for this exact filtered ROM and
the requested complete six-second cue/stereo/tail, ten-second silent no-replay
wait, chip/Buster effects during/after playback and three battle→map→battle
cycles with restored map music and fresh cue starts/ends. ROM, BPS and delivered
copy fingerprints were verified at acceptance. These are user reports, not
independently timed/observed checks. No three-minute loop, linked play, rematches,
broader gameplay or comparative timbre preference is established. No acceptance
transfers to another source/ROM. Transport remains separately recorded.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-henkan-antialias --song-gain-db 0 \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-henkan-antialias-exe6-v1
```

Use a fresh directory. ROMs, source assets and local research outputs stay out of Git.
