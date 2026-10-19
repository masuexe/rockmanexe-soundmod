# Star Force 2 DEMPAJIKEN: filtered envelopes and a carried long note

The candidate is `out/nds-research/sf2-dempajiken-antialias-envelope-exe6-v1/`.
On 2026-10-19 the user reported “没有问题”, accepting this exact
combined-mode ROM after the requested listening/gameplay checklist. This is a cross-game test of
the combination accepted for [SF3 HOKORA](nds-sf3-hokora-antialias-envelope-research.md),
using the [accepted unfiltered DEMPAJIKEN](nds-dempajiken-research.md) as its
baseline. It also tests a long note held across the generated loop jump.

## Configuration and identity

Japanese `ssr2d.nds`, pinned SDAT file 975, SSEQ 11 `BGM_DEMPAJIKEN`, bank 60
retains eight singleton tracks and twelve instrument contexts. Eighteen unique
source waves produced nineteen sample/root entries in the unfiltered version;
the new preparation creates 91 per-key PCM8 waves totaling 671,187 bytes.
All 826 compiled note mappings, source ADSR snapshots, target schedules,
attack fits, tempo, priorities and +3.5 dB gain match the accepted baseline.
Attack 100 still maps to native 74 and instant attack 127 to 255. The native
mixer remains ten channels at 10,512 Hz.

Only the explicit `sf2-dempajiken-antialias-envelope` build choice is added.
The shared converter, FIR, envelope fitting and mixer are unchanged from
HOKORA. Existing guards against filtered native LFO, merged groups, upward
bend, transpose, modulation, portamento and finite-plus-envelope remain.

The ROM is 9,092,900 bytes, CRC32 `4929C90F`, SHA-256
`cb7267bd34c4c1b7ad74548f649d23c981ddc75b3c200e1bc772c0a1698d04d7`.
BPS SHA-256 is
`3f1b580abf1203b38dcdf4919b12340ba32059a225e83215df6ff54cd0e4ec3d`.
Reconstruction is verified. The filtered ROM grows by 363,332 bytes (about
354.8 KiB) relative to the accepted baseline. Maximum source step is about
15.8526 and stored tuning error remains below 0.001 cent. The 5,906 PCM8
clamped values include full-scale quantization and FIR overshoot, rather
than measuring full-mix clipping.

## Source and native checks

The source SDAT is byte-identical to the baseline; its independent 180-second
software DS reference is reused unchanged. Checks match 5,131 notes, 1,183
pan/bend/expression/delay controls and eighteen exact original decoded PCM16
arrays. Envelope validation matches 5,131 note-on snapshots and 472,076
per-voice updates, including 2,240 non-instant attack updates. Original PCM
comparisons validate decoding, not equality of filtered waveforms to DS audio.

Every mapped note's actual packed tone is checked. All 92 voice/key slots
retain the expected source-key pitch, pan and ADSR and point to exactly the
intended prepared waveform bytes. Ninety-one wave headers, lengths, loops,
tuning metadata and nonzero PCM8 are checked separately. One physical
prepared wave can serve both an ordinary key slot and its long-note alias.

Natural title playback checks one complete generated loop without register
injection: 1,650 frames, final clock 3650, all eight track states matched,
all 91 prepared samples observed. The separate 2,400-frame envelope window
reaches clock 5308, with 19,544 allocated-channel observations, 17,553 exact
native envelope steps, 96 gradual-attack states and 7,554 release states.
This covers the first fitted attack class and first loop jump/EOT, rather
than every later envelope instance or a second complete original-song loop.

The common loop starts at tick 1344 with period 2304. Native tempo 166 gives
about 132.197 ticks/second. The first fitted attack is at tick 1536, around
11.62 seconds; these 12-tick notes exercise quick release after a gradual
onset. The first GOTO is at tick 3648, around 27.60 seconds, then every
17.43 seconds: roughly 28, 45, 62, 80, 97, 115, 132, 150 and 167 seconds.

Track 2's source key 86 uses alias 127 for a 239-tick gate. The repeated note
starts at tick 3528 and ends at 3767, carrying from 120 ticks before GOTO to
119 ticks after it. `natural-carry-validation.json` checks the original
arrangement: 108 held-channel observations, slot 7 retained with flags 17
and amplitude 191 across clocks 3648/3650, then release flags 81 and amplitude
175 at clock 3768. The actual first-jump held voice survives and releases on
schedule without another mapped note-on at the jump.

`carry-probe/` adds three native jumps and four EOT cycles with a disposable
single-track sequence using the real filtered bank, alias and gate. No
register/RAM injection is used, but it shortens the score: it does not
establish later full eight-track execution. Static note/gate validation
checks two original periods and extends track 2's final gates through tick
6079. `check-natural-carry.py` reproduces the original first-jump analysis.

Controlled effects 100/129 preserve advancing music; ordinary battle and
synthetic communication dispatch, queued stop, native restoration and three
restart cycles pass. These helper calls inject registers and do not establish
actual linked play or results-screen/map transitions.

The DS renderer reaches sixteen voices in coarse observations, while the
native mixer permits ten. Matching source schedules, packed tone parameters,
envelope steps and first-jump continuity does not establish identical audible
polyphony or timbre. Existing fitting and native synthesis approximations remain.

All 253 regression tests pass. Targeted rebuilds of the accepted unfiltered
DEMPAJIKEN, combined-mode HOKORA and envelope/LFO FRIEND produce byte-identical
ROMs and BPS patches. See `regression-tests.txt` and `prior-regressions.json`.

## Listening and manual acceptance

`comparison/listen.html` embeds thirty-second software DS, accepted unfiltered
envelope and new combined-mode clips, normalized by whole-clip loudness.
The native previews include the first jump and carried note release around
28.5 seconds; the page has a 25-second seek button. The new preview peak is
11,522 versus 13,163 in the baseline recording. Equal gain settings do not
imply equal output amplitude after filtering; normalization masks that raw
difference. The DS reference is software synthesis, not hardware output.

Test this exact ROM in a virus or communication battle for at least three
minutes. Listen for the gradual notes from about 12 seconds, high-note
balance and the long-note continuation/release around 28–29 seconds, followed
by repeated joins around 45, 62 and 80 seconds. Use chips and the Buster,
finish the battle and verify map music resumes, then start at least two more
encounters and verify playback starts from the beginning. `manual-testing.json`
records the user-reported pass for this exact combined-mode ROM. No timed
recording or personal execution trace was supplied; linked play/rematch was
not separately reported. Automated coverage remains one complete original
track loop, a 2,400-frame envelope window, original first-jump carry/EOT and
a separate shortened single-track probe. No comparative preference is inferred.

Reproduce into a new output directory:

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds \
  --base ../roms/exe6.gba --song sf2-dempajiken-antialias-envelope \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-dempajiken-antialias-envelope-exe6-v1
```

The production manager and archived v12 report remain unchanged. This standalone
combined-mode option is separate from the audit's plain filtered route.
