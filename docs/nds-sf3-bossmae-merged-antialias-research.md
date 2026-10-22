# SF3 BOSSMAE: offline filtering with merged tracks

This separate experiment combines the accepted SF3 BOSSMAE twelve-to-eight
configuration with the existing per-source-key offline antialias filter.
Selector `sf3-bossmae-merged-antialias` uses Japanese `ssr3b` sequence27 and
`[[0,3,4],[1],[2],[5,7],[8],[9],[13,15],[14]]`, ten PCM voices, 10512 Hz and
+3.5 dB. The native driver/mixer and source schedule remain unchanged.

The new converter flag `merged_bandlimited_support` requires explicit
`bandlimited_pcm`, at least one merged group, entirely looping tracks and no
native LFO, fitted attack, finite/release or mixed-ending mode. It retains
existing shared-expression/effective-pitch, fixed-volume, held-note-pan,
long-alias/release and conversion-model guards. Default filtered conversion
still requires singleton tracks. Upward bends, transpose, modulation,
portamento and sweep remain rejected. In particular, STUDIO's upward bend
prevents this bounded combination; its accepted plain version is unchanged.
No scanner route or automatic grouping search is enabled.

## Source and prepared data

All 974 source mappings, velocities, priorities, timing validations and loop
metadata match the accepted plain grouped control. The three merged groups
have equal source volumes within each group, so they require no additional
volume-ratio quantization. Source7's note-on pan alternates17/110. No long alias
or loop carry is needed. All 3,825 compiled commands are byte-identical to the
plain baseline after normalizing only relocated GOTO pointer words; target
offsets within each track remain exact.

Per-source-key filtering prepares 81 waves instead of sixteen plain tuned
waves, using 513,763 PCM8 bytes. The maximum source step is about7.681, within
the existing bound32 and 4 MB sample budget. Every prepared wave/header is
recomputed from source and checked after relocation, along with all 974 note
mappings and 111 keyed tone slots, source envelopes, roots and note-on pans.
An unpacked twelve-track filtered control independently exercises the grouping
choice: its mapped source-note fields and all 81 filtered waves/headers match.
It uses the same DSP implementation and cannot run in the eight-track target;
it is not an independent DSP or native-playback reference. Existing analytic
DSP tests retain their own passband, alias-rejection, loop, tuning and tail
coverage. Filtering changes sample data, length, tuning and storage; it does
not increase the native voice budget.

Analysis-only instrumentation confirms the unchanged filter clamps4,763 of
513,763 stored output samples (about0.927%, across66 prepared waves) to PCM8
range:1,806 negative and2,957 positive clips. Unclamped values range about
-147.27 to153.02 in PCM8 units. This includes FIR overshoot and endpoint
quantization; counts are prepared storage entries, not time-weighted playback
or an audible distortion bound. The unpacked filtered control has identical
output. No per-wave normalization is added; sample clipping remains an
explicit limit distinct from the runtime mix/preview peak. Manual listening
must assess roughness/distortion as well as reduced aliasing.

The original pinned 180-second independent software DS reference is reused
only after exact SDAT and recursive renderer-output identity checks. Source
SDAT SHA-256 is
`bf986568be3b1b4bd0c7674694cd3b86641a266138df3271989a2f6fea240220`.
The reused reference matches 6,084 notes, sixteen decoded source waves, 6,084
ADSR note-on snapshots and 513,907 per-voice timer updates. All attacks are
instant. The source-only validator is rerun; this is software synthesis, not
a DS hardware capture or a new independent renderer run.

## Native verification and limits

Common entry is1608 ticks, period1920, joins3528/5448. Source tempo153 maps to
MPlay154, about122.372 versus122.640 ticks/second. Natural frontend playback
uses verified Start input at frames180–190 and reaches clock5450 in2,655
frames, covering two common cycles and all81 prepared waves. It uses no
RAM/register injection, forced repeat, header redirect or clock restart.
Original NOTE-handler bytes match the pinned EXE6 base.

Read-only NOTE entry/allocation/exit and pre-unlink observation reaches
clock5464 in2,662 frames. All1,514 scheduled NOTE calls allocate with exact
owner, wave, ADSR, key, gate, velocity and priority; every source is represented.
Allocation clocks, tracks, keys, instruments, success and slots match the plain
baseline across this window. There are no held/starting preemptions, but905
release-flagged channels with nonzero envelope are reused, potentially
shortening tails. These are windowed observations, not a full-song audible-
error bound or complete DS polyphony. Gated overlap is seen in all three
merged groups. All192 source7 allocations retain opposite initial stereo
directions. This is native channel-volume contrast, not a waveform pan bound.

Saved BEND/BENDR/TUNE/PAN/VOL bytes pass106,480 comparisons; source effective
pitch, computed native pitch and singleton pan match. Player-clock residual
stays within2.04 ticks of fixed-tempo emulated frames, within154/75 ticks.
This is not wall-clock/hardware timing. Controlled effects100/129, queued stop,
continuation and three native-restore/restart helper cycles pass using
PC/LR/argument injection into a disposable emulator. They do not establish
real battle/map transitions, linked play or rematches.

The thirty-second native preview peaks at14814 and covers the first common
GOTO around0:29, but not the second around0:45. Full natural checks are separate.
The local `comparison/merged-filter-ab.html` presents plain versus filtered
native recordings at the same configured gain without further normalization.
They are not sample-aligned. The separate normalized DS/native page is also
not a waveform-error metric. Listening determines whether the changed timbre
is useful; reduced aliasing does not establish overall DS fidelity.

## Regression and accepted exact ROM

All416 prospective-source tests pass without skips, including four new
integration/guard cases. Root migration matches the frozen tested hashes and
both unchanged/filtered paths pass the focused four cases. All48 previously
accepted and two unaccepted control ROM/BPS pairs rebuild identically. The
production CLI reproduces all eight native-tested files byte for byte.
Archived v10–v27 recursive file/path identities remain unchanged.

Local setup diagnostics remain in validation notes: the first output directory
was prepared before a CLI requiring a fresh directory, and an initial natural
validator command omitted its positional ROM. Initial negative-test fixtures
assumed an actually compatible grouping was incompatible, and then modified
shared state dictionaries; corrected fixtures create a real mid-song volume
change without shared-state aliasing. An interrupted regression run is not
counted as a pass. A copied prior-rebuild summary count47 was corrected to48
from its fifty verified rows without changing any ROM/BPS comparison. These setup/test corrections do not change the native-tested
ROM. Automated evidence and exact-ROM manual acceptance stay separate.

- ROM CRC32: `0279DBB2`; size8,937,340 bytes.
- ROM SHA-256: `dde49b852f1c45e5d988eb45554fe14c029406b9ee976b1a6da1264250813b7c`.
- BPS SHA-256: `90e92561cf2e8108ed8e71220e5d694cd53f72e17ce3bcc85189a9755ee6dfe3`.
- Local folder: `out/nds-research/sf3-bossmae-merged-antialias-exe6-v1/`.

On 2026-10-22, the user reported “测试没有问题” for this exact ROM and the
requested three-minute virus-battle listening (including timbre/distortion),
repeated chip/Buster effects and three battle→map→battle checks. This is
user-reported acceptance; no independently timed recording, full gameplay
trace, linked play or rematch is inferred. Filtered/unfiltered timbre preference
was not separately reported. Sample clipping, PCM8/ADSR/tempo quantization and
the ten-voice release-tail limit remain. Automated evidence and exact-ROM
manual acceptance stay distinct.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-bossmae-merged-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-bossmae-merged-antialias-exe6-v1
```

Use a fresh directory. ROMs, source assets, captures and local research outputs
stay outside Git. Archived v27 counts and accepted fingerprints remain intact.
