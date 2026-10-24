# SF1 GAMEOVER: finite singleton antialias and natural stopping

This adds only `sf1-gameover-antialias` for verified SF1 SDAT sequence33,
`BGM33GAMEOVER`, using eight singleton tracks and the existing finite export
and FIR modes. The only enabled converter options are `bandlimited_pcm=True`
and `finite_support=True`; converter/native code and their guards are unchanged.
No fitted-envelope, release override, merged/upward/LFO or mixed-score mode is
enabled. This is a roughly three-second cue that ends, rather than a looping
BGM. The experiment still routes title/virus-battle/communication to slot474.

A fresh same-source plain export remains `unaccepted_control` at
`out/nds-research/sf1-gameover-plain-control-v1/`, without manual acceptance.
No acceptance transfers from another game's GAMEOVER or another finite cue.

## Complete finite-source evidence

All83 mappings match the complete raw SSEQ score and the plain control:
identity, gates, velocities, priorities, controls and timing are preserved.
Per-track END ticks are240/288/312/312/336/324/288/336. Every source gate closes
before or at its END. Native analysis has FINE on all eight tracks at those
same ticks, with no GOTO. All439 playback commands are byte-identical to the
plain control; no GOTO relocation normalization is needed. There are no
zero-velocity mappings or long-note aliases. All39 tones and39 prepared waves
retain source root/pan/ADSR and relocated PCM/header data. Resampling
reproduction uses the same DSP implementation, not independent audio validation.

Prepared storage contains283,400 PCM8 points and746 clamps:396 negative,
350 positive; unclamped extrema are about−147.266/+153.029. These are storage
counts, not time-weighted audible error or native mixer clipping. Maximum
source step is about5.0022; appended size301,328 bytes. Filtering, PCM8 clipping
and envelope/volume quantization limits remain explicit.

A fresh independent20-second software DS reference matches all83 notes and13
decoded raw waves, source ADSR and tempo/depth controls, with complete finite
schedule checking. It extends well beyond source END and tail. Peak is17309
and coarse100ms maximum voices16. It is software rendering, not DS hardware.
Source tempo145 maps to native146, about115.973→116.270 ticks/s. Track ends are
approximately2.1–2.9 seconds; tempo quantization remains.

Natural frontend playback reaches clock337 in174 frames, covering the entire
cue and all39 waves. Every-frame PCM observation checks this short cue;
no RAM/register injection, header redirection, forced repeats or clock restarts
are used. Read-only original NOTE observation likewise reaches clock337 in174
frames: all83 calls allocate, with no rejection or held/starting preemption.
Identities, clocks, outcomes and every slot match the plain control; both
reuse54 nonzero-envelope release channels.

All83 allocated channels retain gate/key/velocity/source-derived priority.
There are6,275 saved native BEND/BENDR/TUNE/PAN/VOL byte comparisons during
each finite track's active window. Inactive track bytes are not claimed as
musical control evidence. Source6 stereo retains96 settled observations with
source-note pan20/100:48 left≤20 and48 right≥100, median signed balance about
−0.739/+0.622. Definition pan is included. Starting/release channels are
excluded before held-owner checks. This is not whole-mix waveform alignment.
The frontend/NOTE frame clock matches `1 + floor((frame-1)*146/75)` through
completion, with anchored residual below one tick; no post-stop advancing
clock or hardware/wall timing is asserted.

## Natural END, tails and stopped state

A separate1,200-observation root-callback probe checks each FINE against its
source END. It records early track completion, then an inactive player, a
frozen clock338 and981 empty imported-channel observations after completion.
The final600 observations remain empty with the same clock and inactive status.
No CPU/RAM edits, forced repeat or restart is used. This callback/bootstrap run
reports338; the separate frontend/NOTE runs report337. Their measurements are
retained separately; both finish beyond the final END336 and neither restarts.

The15-second native SDL full-mix recording has peak16729 and its final ten
seconds contain entirely zero PCM. This clip-specific silence measurement is
separate from read-only channel/clock verification and from human listening.
Controlled effects100/129, continuation, queued stop and three restore/restart
cycles also pass in the existing finite-aware helper windows; they do not
establish actual chip gameplay, linked play or rematches.

FINE clears track ownership while a release tail may remain active. Two later
channel reuses have owner0, proven release flags, reached source END, inactive
former tracks, and exact prior keys/wave pointers. The copied loop observer's
owner-retention assumption initially failed in both filtered/plain captures.
A copied stereo check also tested ownership before excluding release channels;
the finite command comparator indexed absent loop-only metadata. All initial
sources/logs are preserved separately. Corrected finite observation rules keep
held-owner/key assertions, stereo thresholds and exact command checking. These
fixture corrections change no ROM, converter or native code and are not
counted as initially passing tests.

## Regression scope and reuse

Sixteen focused cases pass in prototype and after exact migration: two GAMEOVER
cases and fourteen cases for prior additions since the frozen full suite.
New cases cover explicit finite opt-in, family/capacity/mode guards, full score,
per-track FINE/no GOTO, gates before END, BPS reconstruction and prefix bounds.
Formal CLI reproduces all eight native-tested files byte for byte; recursive
v10–v37 archives retain their identities.

Removing the new branch/family entry restores the whole accepted BOSSMAE builder
AST. Removing all eight additions restores the frozen487-test SCHOOL builder
AST; other baseline libraries/tests remain byte-identical. The new branch is
pinned to source33 and exactly the two existing finite/filter options; previous
seven loop branches still require filtering only. Parent/full-suite evidence is
hashed. The487-test no-skip suite and58 accepted/two historical-control rebuild
record are reused, not a fresh503-test run or68-song rebuild. Fresh integrity
checks reconstruct68 archived ROMs from their BPS/base pairs without recompiling
the old songs. Remaining coverage limits are preserved.

## Accepted exact SF1 ROM and delivered test patch

- ROM CRC32: `8816B5DC`; size8,689,936 bytes.
- ROM SHA-256: `8107504d036dda61bb997d5c0c12a08b321529559bd3243f2aec456a71acb9e9`.
- BPS SHA-256: `727cb17b4c3922005e0e5dbde059b7c8593900045881de8417f6cd867c401efd`.
- Local folder: `out/nds-research/sf1-gameover-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

`patch-delivery.json` records copied SHA-256 separately from human acceptance.
`comparison/filter-ab.html` presents unaccepted plain and accepted filtered
native recordings at the same configured gain without extra normalization or
sample alignment. The software DS/native normalized page is separate.
Comparative timbre preference is distinct from functional acceptance.

The user reported the requested exact-SF1-ROM finite-cue checks passed on
2026-10-24: “测试没有问题”. This covers the complete roughly three-second
cue and tail, at least ten seconds after END without spontaneous replay,
chip/Buster effects during and after the cue without abnormal restarts, and
three battle→map→battle encounters restoring native map music and replaying
the cue from its beginning to natural END. No three-minute loop check is
inferred. The Windows-delivered patch hash matched this BPS when acceptance
was recorded. Automated, transport and user reports remain separate.
Comparative timbre preference, independent timing, full gameplay traces, linked
play and rematches were not separately reported. No acceptance is inferred for
the plain control or another family. Recorded voice/filter/PCM8/volume/ADSR/
tempo and regression-coverage limits remain in force.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-gameover-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-gameover-antialias-exe6-v1
```

Use a fresh directory. ROMs, assets and local outputs stay outside Git.
