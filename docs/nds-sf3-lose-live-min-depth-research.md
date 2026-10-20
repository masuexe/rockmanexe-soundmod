# SF3 LOSE with the accepted live/weak-depth route

This standalone experiment converts SF3 `BGM_LOSE` (SSEQ 42), following the
accepted [SF1 LOSE experiment](nds-sf1-lose-live-min-depth-research.md).
Artifact: `out/nds-research/sf3-lose-depth-min-exe6-v1/`.
On 2026-10-20 the user reported “没有问题” after the requested listening,
effects and three-encounter lifecycle checklist, accepting this exact ROM. No
timed recording or completion trace was supplied; two-peer play and rematch
were not separately reported, and no comparative listening preference is inferred.

- ROM SHA-256: `cdd4cd3c85d7ee962a6df87ec4c52f7ff34752f59b3d36dd275c401371e104c2`.
- BPS SHA-256: `bc518d6315cd0ec3f9dabeea221b2d8ea377c6247c513d20cd3e9a0591a9e16b`.

## Scope and source differences

The only implementation change adds CLI choice `sf3-lose-depth-min`, using
the existing looping singleton, fixed-delay, live positive-depth and explicit
minimum-depth flags. Converter, LFO model, native driver, manager, mixer and
allocation policy are unchanged. The shared builder keeps SF1's explicit
fitted-attack flag and leaves it off for SF3, whose source attacks are all 127.
The accepted SF1 ROM/BPS rebuild byte-identically after this builder refactor.

SF1 and SF3 have different SSEQ bytes, executed traces and source wave sets;
acceptance does not transfer by song name. SF3 retains source track IDs
`[0,1,2,5,6,7,15]`, fourteen source/prepared PCM waves and fifty native tone
slots. Its latest source loop entry is 308, versus SF1's 864; after the existing
warmup, compiled common entry/period are 1076/768. Jumps at 1844/2612 occur
near 20.1/28.5 seconds, then repeat about every 8.4 seconds. The export contains
998 mapped notes through its encoded intro/body and appends 233,052 bytes.
Title, ordinary virus battle and communication triggers select slot 474.
Gain stays +3.5 dB, with ten PCM channels at 10,512 Hz and no offline filtering.

The depth/speed/delay configurations retain the accepted route: positive
40/60/100 depth changes with fixed speed 31/delay 48, a depth-60/delay-96
track, and weak depth 3/speed 28/delay 14 tracks. Weak depths map to MOD 1
under the existing 9.375-cent all-phase bound and roughly 3.20-cent isolated
RMS error. The ten/five-cent policy applies to quantization below native
resolution, not to deeper shared-phase modulation. Fixed tempo 115,
initial activation/order guards and excluded modes are unchanged.

## Independent reference

The existing pinned SSEQPlayer renderer runs the original SF3 source for
60 seconds. All 3,003 notes, fourteen PCM16 wave decodes, 283 ordinary controls
and 95 depth controls match. There are 36,171 checked sine updates and 115,268
counter updates, including 79,097 waits and 1,884 zero-phase activations.
All 1,035 positive UpdateMod transitions preserve phase/count; 161 carry
nonzero state. The separate source-only checker verifies note-on ADSR and
per-voice envelopes, including that every attack is instant.

`out/nds-research/sf3-lose-depth-min-research-v1/` retains the pinned SF1/SF3
source comparison and the independent source checker. This is software DS
execution/synthesis, not a DS emulator or hardware recording.

## Native execution and fidelity limits

Natural title playback passes 1,705 frames through clock 2613: intro, two
complete common cycles, all seven tracks and all fourteen prepared samples.
There is no game RAM/register injection, retained-song mode, clock restart,
header redirection or frontend input.

The accepted allocation-aware observer independently follows unchanged EXE6
NOTE handler entry, selected-channel reset branch and exit. Its 1,706 frames
reach clock 2615, checking all 1,420 calls, all scheduled note identities and
11,942 native track LFO states through both jumps. Of these note calls, 1,361
allocate and 59 are rejected by the ten-channel policy: 43 on target track 5
(source 7) and sixteen on target 6 (source 15). Reload-only LFODL behavior and
allocation-dependent note resets are checked without altering the ROM or
forcing allocation. A fabricated successful allocation at tick 404 fails the
negative control at clock 405.

These rejections are observed budget differences, not evidence of identical
DS/GBA polyphony or inaudibility. Source execution reaches sixteen allocated
voices. The requested manual checklist included dense accompaniment and echoes;
the user reported no issues without a separate timed recording or event trace.

Sparse source IDs are mapped explicitly in the optional reference diagnostic.
Sequence-clock/latest-timer comparisons with allocated DS voices have weak
track RMS differences about 1.76/2.56 cents, maximum 6.25. Deeper tracks show
about 24.62–31.70-cent RMS differences and maxima up to 78.125 cents. Shared
track phase/count, overlapping-note resets, triangle versus DS sine, PCM8,
ADSR quantization and voice allocation remain fidelity limits. These values
are diagnostic alignments, not sample alignment or a whole-song error bound.

Packed checks verify all 998 mappings, fifty tone slots and fourteen raw PCM8
payloads/headers, source roots, pan and quantized instant-attack envelopes.
Controlled effects, dispatch, queued stop, native restoration and three restart
cycles pass. Those helper injections do not establish actual gameplay,
results/map transitions, linked play or rematches.

All 294 regression tests pass. The directly related accepted SF1 LOSE ROM/BPS
remain identical; no converter or native-runtime change needs reacceptance of
other songs. Archived v10–v15 reports and counts remain unchanged. The builder
reproduces the exact new ROM/BPS and serialized conversion metadata.
`validation-summary.json` records automated coverage and exact-ROM user-reported
manual acceptance separately.

## Final listening/gameplay check

The actual 30-second mGBA preview peaks at 20,208 and includes both initial
common jumps. `comparison/listen.html` compares it with software DS synthesis
using whole-clip normalization. This provides no manual listening preference
or gameplay acceptance.

The final requested checklist for this exact ROM was:

1. Listen in virus battle for at least three minutes. Check dense accompaniment,
   echoes and long-note vibrato, and joins near 20/29 seconds, for unnatural
   thinning, distortion, muddiness, restarts, hangs or crackles.
2. Repeatedly use chips and the Buster; check effects/music coexistence.
3. Return to the map and begin another battle, for three encounters total;
   check native map music restoration and a fresh imported start each time.

`manual-testing.json` records user-reported acceptance for the exact
fingerprints above. Completed source and documentation follow the standing
commit/push workflow. The new standalone choice is not yet in the batch
scanner; v15's 56 primary/29 filtered counts remain the archived snapshot.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds --base ../roms/exe6.gba \
  --song sf3-lose-depth-min --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf3-lose-depth-min-exe6-v1
```

Use fresh directories for reproduction. The existing reference renderer,
`validate_song.py` and `validate_nds_experiment.py` provide source/natural/helper
checks. Local `validate-allocated-lfo.py`, `check-allocation-evidence.py` and
`check-packed-tones.py` retain the stricter allocation and resource evidence.
ROMs, original game assets and local research outputs remain outside Git.
