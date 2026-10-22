# SF3 BOSSMAE: twelve sources, three equal-volume groups

This separate experiment imports verified Japanese SF3 `ssr3b`, sequence 27
`BGM_BOSSMAE`, into Japanese EXE6 Gregar through selector
`sf3-bossmae-twelve-track`. Groups are
`[[0,3,4],[1],[2],[5,7],[8],[9],[13,15],[14]]`: twelve sources become eight
native sequence tracks. The existing plain merged converter, ten PCM voices,
10512 Hz and +3.5 dB gain are retained. No native driver/mixer or new conversion
mode is introduced. Archived v23 still marks this source capacity-blocked;
there is no batch search or automatic acceptance of other groupings.

## Source and conversion evidence

Groups 0/3/4, 5/7 and 13/15 have fixed source volumes 100, 90 and 60 respectively.
All retain existing shared-expression/effective-pitch and held-note-pan guards.
Each source's group-volume ratio is one, avoiding extra velocity-ratio
quantization. Distinct note-on pan remains in native tones, including source
7's alternating 17/110. All 974 mapped source note tuples and target velocities
match an unpacked twelve-track singleton control, which is not runnable on
the eight-track target. Source priorities remain distinct where specified.
All eight compiled tracks pass two-cycle note/gate/timing comparisons.
No long-note alias or carry across the common loop is required.

The source SDAT SHA-256 remains
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
The pinned independent 180-second software DS reference matches 6,084 notes,
sixteen decoded waves, tempo/depth controls, 6,084 ADSR note-on snapshots and
513,907 per-voice timer updates. All attacks are instant; there is no fitting,
active modulation or offline filtering. This is software reference synthesis,
not DS hardware capture. All 974 packed note mappings, 111 keyed tone slots
and sixteen prepared waves match source-derived ADSR, roots, note-on pan,
raw PCM8 and relocated loop headers/data.

Tempo 153 maps to MPlay154, about 122.372 source versus 122.640 native ticks
per second. The common entry is 1608 ticks, period 1920, joins 3528/5448:
about 0:13 at entry and 0:29/0:44 at the first two jumps. Ordinary PCM8,
volume/velocity, ADSR and tempo quantization remain fidelity limits.

## Original native playback and voice-budget evidence

Natural frontend playback uses Start at frames 180–190, with KEYINPUT reads
verified. It reaches clock 5450 in 2,655 frames, covering the intro, two common
cycles and all sixteen waves, without RAM/register injection, header redirects,
forced repeat or clock restart. Original NOTE handler bytes remain identical
to the pinned base. Read-only NOTE entry/allocation/exit observation extends
to clock 5464 over 2,662 frames. All 1,514 scheduled NOTE calls allocate;
allocated wave, owner, key, ADSR, initial gate, velocity and source-derived
priority match. All twelve sources are represented.

A second observer adds a breakpoint immediately before the original selected-
channel unlink call, saving its existing flags, envelope and ownership. The
initial observation is retained; adding this read-only breakpoint leaves all
calls, allocation fields, frames and overlap observations identical. No held
or starting channel is displaced in this two-cycle window. There are **905
reuses of release-flagged channels with nonzero envelope**, which can shorten
tails under the ten-voice budget. These are channel-state observations, not
905 proven audible defects or a whole-song error bound. Successful new-note
allocation alone does not establish full voice fidelity. The final manual
checklist explicitly asks about tails and overlapping instruments.

Gated overlap of at least two source members appears in each merged group:
2,368 frames for 0/3/4, 668 for 5/7 and fifteen for 13/15. Identification uses
the latest actual allocation per native slot, validated owner/wave and gated
flags, without assuming source waves are distinct. It does not require all
three members of the first group to be simultaneous. All 192 source-7 initial
channel snapshots retain opposing stereo directions: 102 at pan17 and ninety
at pan110, with median signed balances about -0.833/+0.737. This is stereo
contrast, not sample alignment or a whole-song pan-error bound.

Controlled effects 100/129, music continuation, queued stop and three native-
restore/restart helper cycles pass. These helper calls inject PC/LR/arguments
into a disposable emulator and do not establish real battle/map transitions,
linked play or rematches. The thirty-second native preview peaks at 14638;
it covers the first GOTO around 0:29, but not the second around 0:44. The
normalized software DS/native comparison is not sample-aligned.

## Regression and delivery

All 378 prospective-source tests pass without skips, including the new twelve-
source/three-group integration and source-family/capacity guards. Root migration
matches all frozen tested source hashes, and both focused root cases pass.
All 44 accepted and two unaccepted control ROM/BPS pairs rebuild identically.
The production CLI reproduces all eight native-tested output files byte for
byte. Archived v10–v23 recursive file/path identities remain unchanged.

An initial draft-test invocation loaded the unextended production module and
failed; it is retained separately. Corrected draft loading and root tests pass.
An initial pan helper retained old source/pan constants; those were corrected
to source7, pan17/110 and rechecked against the unchanged saved capture.
A preview-directory alias resolves a comparison invocation path mismatch.
These observer/invocation corrections do not modify the production ROM.

## Exact ROM and user-reported manual acceptance

- ROM CRC32: `053B8A3F`; size 8,645,332 bytes.
- ROM SHA-256: `1ada1a4ed7c64d5279021b69e6ceacc49f14b78a6ee012fe17de1870bdacc935`.
- BPS SHA-256: `a5c52e2dc1a2bf7abf4d4bdd15d94b136b1e9d83ce6d42787a4fdc59a123bdf6`.
- Local folder: `out/nds-research/sf3-bossmae-twelve-track-exe6-v1/`.

On 2026-10-22 the user reported passing the three requested checks: at least three minutes in a
virus battle, checking merged instruments, stereo, tails/overlap and joins
around 0:29/0:44; repeated chip/Buster effects; and three battle→map→battle
encounters with native-map music restored and each import starting afresh.
The recorded native voice-budget/release-channel reuse limit remains. No
independently timed recording or full gameplay trace was supplied; linked play,
rematches and comparative preference are not inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-bossmae-twelve-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-bossmae-twelve-track-exe6-v1
```

Use a fresh output directory. Local captures, diagnostic snapshots, reference
outputs, hashes and logs stay ignored. ROMs and source game assets stay outside
Git; final manual acceptance must bind this exact fingerprint.
