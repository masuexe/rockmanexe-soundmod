# SF3 CHANGE: thirteen sources, fixed-volume ratios and a moving long note

This separate experiment imports verified Japanese SF3 `ssr3b`, sequence 47
`BGM_CHANGE`, into Japanese EXE6 Gregar through selector
`sf3-change-thirteen-track`. Groups are
`[[0],[1],[2],[3],[4,6,7,9,14,15],[5],[8],[13]]`: thirteen sources become eight
native tracks. It retains the existing plain merged converter, ten PCM voices,
10512 Hz and +3.5 dB gain. No converter or native driver/mixer capability is
added. Archived v24 still marks this source capacity-blocked; no batch grouping
search is enabled.

## Source schedules and volume mapping

An equal-fixed-volume-only investigation cannot produce enough compatible
merges. Existing pitch guards reject several otherwise equal-volume pairs,
including grouping source5 with 0/6. Those guards are retained. The selected
six-source group passes shared-expression/effective-pitch and held-note-pan
checks with fixed source volumes 110/100/110/110/80/70 respectively, normalized
to group volume 110 using the existing velocity-ratio formula. Other sources
stay independent; source5 retains its moving pitch/pan controls.

All 855 mapped source note tuples, including multiplicity, match an unpacked
thirteen-track singleton control, which is not runnable in the eight-track
target. There are 161 ratio-scaled mappings; unscaled velocities match the
control. Every mapped velocity is nonzero and equals the existing formula,
with maximum absolute linear-velocity rounding error about 0.48036. This is
not a waveform or perceived-loudness error bound. Ordinary native volume and
ADSR quantization remain. Two identical source4 key59 notes at tick372 are
both retained and executed; dictionary uniqueness is not used to discard one.
All eight compiled tracks pass two-cycle note/gate/timing comparisons.

The source SDAT SHA-256 remains
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
The pinned independent 180-second software DS reference matches 5,070 notes,
twenty unique decoded waves, tempo/depth controls, 5,070 note-on ADSR snapshots
and 386,046 per-voice timer updates. Twenty-five prepared native waves retain
separately tuned uses. All attacks are instant; there is no fitted attack,
active LFO or offline filtering. This is software synthesis, not DS hardware
capture. All 855 packed mappings, 92 keyed tone slots and 25 prepared waves
match source-derived pan, ADSR, tuning, raw PCM8 and relocated loop data.

## Intro-only loop reference validation

Source9 plays six intro notes and then loops through rests. The old reference
check incorrectly required its last note to reach two complete loops. The
validator now handles this exact structure separately: the entire intro note
list must match, duration metadata at the minimum source tick rate must cover
`end_ticks + loop_ticks`, and independent control observations must match
through that window. The normal sounding-loop last-note requirement remains.
Source9 requires 3,456 ticks; the 180-second reference covers it. No source
notes are invented, removed or repeated to satisfy a coverage assertion.

Four tests reject changed/extra/missing intro notes, insufficient duration,
missing/truncated/wrong controls and attempts to use metadata to bypass normal
sounding-loop coverage. The failed original source-check log is retained.
Native observation initially rejected duplicate mapping keys; it now permits
only identical mapping duplicates and checks actual event offsets plus full
source-note multiplicity counters. The failed initial run is retained. No ROM
change is made for either diagnostic correction.

## Original native playback, long notes and stereo

Natural frontend playback uses verified Start input at frames 180–190. It
reaches clock 4393 in 2,891 frames, covering the intro, two common cycles and
all 25 waves, without RAM/register injection, forced repeat, header redirects
or clock restart. NOTE handler bytes remain identical to the pinned base.
Read-only NOTE entry/allocation/exit observation reaches clock 4409 in 2,901
frames. All 1,339 scheduled NOTE calls allocate, with exact wave/owner/key/ADSR,
initial gate, velocity and source-derived priority. All thirteen sources,
including the six intro-only source9 calls, are represented.

Source5 key76 uses native alias127 for its 383-tick TIE/EOT notes. Both observed
uses remain held through their gate windows and release afterwards: source
onsets 1536/3072, ends 1919/3455. There are 244/245 held snapshots and 754/624
released snapshots. Source5 is a singleton, so same-group sibling EOT isolation
is not relevant to this alias. No carry across a loop boundary is needed.

Saved native track BEND/BENDR/TUNE/PAN bytes pass 92,832 comparisons against
the compiled stream, and their computed pitch matches source effective units;
singleton pan matches source controls. The long-note tail sweep has 141 held
snapshots, fifteen effective pitch values, nine pan values and fifteen actual
channel frequency-word values. These are register/state observations, not
absolute-frequency or DS waveform equivalence. An initial diagnostic confused
computed-pitch byte8 with BEND byte14; corrected comparisons also check computed
pitch bytes8/9 against the source. The original capture and ROM are unchanged.

The six-source group has at least two gated members in 1,367 frames. Source
identification uses actual slot allocations and validated owner/wave, without
assuming source waves are distinct. All 107 source6 note-on stereo snapshots
retain opposing directions: pan14 has 56 observations, pan112 six and pan114
45, with median signed balances about -0.810/+0.767/+0.814. This is initial
channel-volume contrast, not a whole-song pan-error bound.

## Recorded ten-voice limitations

Read-only channel snapshots immediately before the original unlink call show
four held/starting-channel preemptions, all in the intro before common entry
1320. At clocks 352/360/372/376 (about 3.9–4.1 seconds), new source6/4 notes
displace source13 key88 once and source14 keys64/71/76 three times. Thus all
new NOTE calls allocating does **not** establish complete original polyphony.
There are also 183 reuses of release-flagged channels with nonzero envelope,
which can shorten tails. Counts and flags are not an audible-error bound.
All source events and priorities remain; the mixer voice count is not raised
to hide these limitations. The manual checklist explicitly asks whether the
intro/overlap, tails and volume-ratio approximation are acceptable.

Tempo 114 maps to MPlay114, about 91.179 source versus 90.786 native ticks per
second. Common entry is 1320, period1536, joins2856/4392: around 0:15 at entry
and 0:31/0:48 at the first two jumps. Controlled effects100/129, continuation,
queued stop and three native-restore/restart helper cycles pass. Helper calls
inject PC/LR/arguments into a disposable emulator and do not establish real
battle/map transitions, linked play or rematches. The thirty-second preview
peaks at 13114 and covers neither GOTO; natural full-loop checks are separate.
The normalized DS/native comparison is not sample-aligned.

## Regression and exact accepted ROM

All 390 prospective-source tests pass without skips, including the new source
integration and intro-only reference cases. Root migration matches all frozen
tested source hashes; six focused root cases pass. All 45 accepted and two
unaccepted control ROM/BPS pairs rebuild identically. The production CLI
reproduces all eight native-tested outputs byte for byte. Archived v10–v24
recursive file/path identities remain unchanged. Old audit validators are
historical and are not rerun against subsequently changed source hashes.

- ROM CRC32: `36A6D87C`; size 8,791,632 bytes.
- ROM SHA-256: `34a58369565907c3713ca92bef337cabf7dd14435fe401fb10ff34387aa36575`.
- BPS SHA-256: `901420858ca8bde5d9ad7222a3ddfae1f791d248fbff9fe27e2ba924fc5a550a`.
- Local folder: `out/nds-research/sf3-change-thirteen-track-exe6-v1/`.

On 2026-10-22 the user reported passing the requested checklist: virus-battle listening for at least three
minutes, especially intro around 0:04, moving long notes/pan, tails and joins
around 0:31/0:48; repeated chip/Buster effects; and three battle→map→battle
encounters with native-map music restored and the import starting afresh.
The measured intro preemptions, release-channel reuse and velocity-ratio
quantization remain recorded. No independently timed recording or full gameplay
trace was supplied; linked play, rematches and comparative preference are not
inferred.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-change-thirteen-track \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-change-thirteen-track-exe6-v1
```

Use a fresh directory. ROMs, original assets, captures, local diagnostic evidence
and hashes remain outside Git. Manual acceptance binds only this exact ROM.
