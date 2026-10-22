# SF3 AJITO: fourteen sources, four long aliases and independent dynamics

This separate experiment imports verified Japanese SF3 `ssr3b`, sequence7
`BGM_AJITO`, into Japanese EXE6 Gregar through selector
`sf3-ajito-fourteen-track`. Groups are
`[[0,4,6,7,8,11,14],[1],[2],[3],[5],[9],[10],[15]]`: fourteen sources become
eight native tracks. It retains the existing plain merged converter, ten PCM
voices, 10512 Hz and +3.5 dB gain. There is no new converter/native-driver
capability. Archived v25 still marks AJITO capacity-blocked; no generic batch
grouping search is added.

## Source schedules and resources

The seven-source group has fixed volumes 100/100/90/90/100/90/60, normalized
to group volume100 through the existing velocity-ratio mapping. Shared
expression/effective-pitch and held-note-pan guards remain. Sources with
changing or incompatible controls stay independent, including source9's
expression and source15's changing volume70/80. Per-note pan stays in tones
for merged parts; singleton controls retain their original time course.

All 2,472 mapped source note tuples and multiplicity match an unpacked
fourteen-track singleton control, which is not packed or runnable on the
eight-track target. There are 534 ratio-scaled mappings; unscaled velocities
match the control. Every target velocity remains nonzero, with minimum1 and
maximum absolute linear-velocity rounding error about 0.46594. This is not
a perceived-loudness or waveform error bound. All eight compiled tracks pass
two-cycle note/gate/timing comparisons under unchanged guards.

The source SDAT SHA-256 remains
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
The pinned independent 180-second software DS reference matches 4,477 notes,
27 unique decoded waves, source tempo/depth controls, 4,477 ADSR note-on
snapshots and 422,065 per-voice timer updates. All attacks are instant; no
fitting, active LFO or offline filtering is enabled. This is software synthesis,
not DS hardware capture. All 2,472 packed mappings, 303 keyed tone slots across
voice contexts and 33 prepared waves match source-derived pan, ADSR, roots,
raw PCM8 and relocated wave headers/data. Separate tuned uses remain separate.

## Long natural playback and controls

The common entry is 4032 ticks, period5472, joins9504/14976. Tempo115 maps to
MPlay115, about 91.979 source versus 91.582 native ticks/second: entry around
0:44, jumps around 1:44 and 2:44. Natural frontend playback uses verified
Start input at frames180–190, reaches clock14977 in 9,768 frames and covers
two common cycles plus all 33 waves. There is no register/RAM injection,
forced repeat, header redirect or clock restart. Original NOTE handler bytes
remain identical to the pinned base.

Read-only NOTE entry/allocation/exit observation reaches clock14992 in 9,778
frames. All 3,964 scheduled NOTE calls allocate, with exact wave, owner, key,
ADSR, initial gate, velocity and source-derived priority. All fourteen sources
are represented. Actual player clocks stay within 1.467 ticks of the theoretical
fixed-tempo frame rate across this entire window, inside a two-tick bound.
This is an emulated-frame timing check, not a wall-clock or hardware recording.

Source2 keys55/58/59 use aliases127/126/125; source10 key61 uses alias127 on
its separate native track. All fifteen observed long-note uses remain held
through their gate windows and release afterwards. All source waves used by
these aliases are looped. Their tracks are singletons, so same-group sibling
EOT isolation is not relevant here. No long-note carry across the common loop
boundary is required.

Saved native BEND/BENDR/TUNE/PAN/VOL bytes pass 391,120 comparisons against
compiled commands. Computed pitch matches source effective units, and
singleton pan matches source controls. Source9 retains thirteen distinct
native VOL values through its expression changes; source15 retains native
VOL23/30 for its two volume levels. These state checks do not establish DS
waveform or absolute-frequency equivalence. The merged group has at least
two gated members in 7,178 frames, identified by actual slot allocations and
validated owner/wave without assuming all source waves are distinct.

All 435 source8 initial stereo snapshots retain left/center/right contrast:
188 at pan25, 29 at pan64 and 218 at pan102, with median signed balances
-0.600/+0.018/+0.607. This is channel-volume contrast, not sample alignment
or a whole-song pan-error bound.

## Recorded voice-budget limits and diagnostics

Read-only snapshots immediately before the original chosen-channel unlink
call show fourteen held/starting-channel preemptions: source15 is displaced
six times, source14 six times and source11 twice. The observations cluster
around 0:12, 0:55–0:58, 1:12, 1:55–1:58 and 2:12. There are also 1,544 reuses
of release-flagged channels with nonzero envelope, which can shorten tails.
All new NOTE calls allocating does not establish complete original polyphony;
counts and flags are not a measured audible-error bound. Source events and
priorities remain intact and the native voice count is not raised. The final
manual checklist asks whether these limits and volume-ratio quantization are
acceptable.

Initial saved-log parsers rejected incomplete snapshot counts because three
memory commands were echoed by the terminal: one each for 48-byte preallocation,
64-byte allocated-note and 640-byte track-frame reads. Runtime memory reads
already ignore non-hex command echoes. Analysis now removes only an exact
echoed command immediately after its identical logged command; all memory hex,
the original transcript and the ROM remain unchanged. All 3,964 note snapshots
and 9,778 frame blocks are then counted and compared. No field or timing
comparison is waived. The initial diagnostic failures and normalization scope
are recorded separately in local validation notes.

Controlled effects100/129, music continuation, queued stop and three native-
restore/restart helper cycles pass. Helper calls inject PC/LR/arguments into a
disposable emulator and do not establish real battle/map transitions, linked
play or rematches. The thirty-second preview peaks at15547 and covers neither
the common entry nor either GOTO; full natural sequence checks are separate.
The normalized DS/native comparison is not sample-aligned. PCM8, ordinary
volume/ADSR/tempo quantization, possible tail-shortening and simultaneous
allocation-order differences remain fidelity limits.

## Regression and accepted exact ROM

All 398 prospective-source tests pass without skips, including the new
fourteen-source schedule/velocity/alias and independent-dynamics assertions.
Root migration matches frozen tested hashes and both focused root cases pass.
All 46 accepted and two unaccepted control ROM/BPS pairs rebuild identically.
The production CLI reproduces all eight native-tested outputs byte for byte.
Archived v10–v25 recursive file/path identities remain unchanged; historical
source-pin validators are not rerun against subsequently changed source.

- ROM CRC32: `40560A05`; size 8,882,940 bytes.
- ROM SHA-256: `e7e3331fa5d3c12f75a3719db59a7ae78862439e85a3e091de23966fd09149c1`.
- BPS SHA-256: `fb89025a998c2da15e7f32cf2a216b177a2b03df053d37143f42fe9adb9da7db`.
- Local folder: `out/nds-research/sf3-ajito-fourteen-track-exe6-v1/`.

On 2026-10-22 the user reported passing the exact-ROM listening/effects/three-encounter checklist: listen
in a virus battle for at least three minutes, including the dense passages,
long notes, expression/volume, stereo, tails and joins around 1:44/2:44; repeat
chip/Buster effects; and complete three battle→map→battle encounters, checking
native-map music restore and a fresh imported start. The measured native preemptions, tail reuse and velocity-ratio quantization
remain recorded. No independently timed recording or full gameplay trace was
supplied; linked play, rematches and comparative preference are not inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-ajito-fourteen-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-ajito-fourteen-track-exe6-v1
```

Use a fresh directory. ROMs, original assets, captures, hashes and local research
outputs stay outside Git. Manual acceptance binds only this exact ROM.
