# SF1 SATELLITE: restore an accent suppressed by an expired pitch bound

In revision1 (CRC `A75BF6AF`), the user reported a clearly missing third note
in a four-note phrase near00:20, in both title and virus battle. That ROM is
**not accepted**. Its2741 successful NOTE allocations and channel-state checks
did not establish that every note was audible in the final mix.

The matching phrase has four primary accents on source3/instrument54 at ticks
2160/2208/2256/2304, keys88/89/91/88, each with velocity105 and a12-tick gate.
The key91 accent near20.4 seconds was heavily attenuated. The whole-track
conservative pitch bound included an earlier intro bend of498 units, preparing
this later key91 wave at key99 even though its future pitch stays zero. This
unnecessary eight-semitone ceiling removed much of that accent's energy.
This is excessive filtering, not a missing NOTE call or a ten-voice rejection.

## Revision2: bound pitch after a sample can first exist

The existing `sf1-satellite-upward-antialias` selector now explicitly enables
`bandlimited_upward_future_support`. It requires singleton upward-filter mode;
finite, fitted-envelope, native-LFO and merged combinations remain excluded by
existing/additional guards. Other selectors retain the default whole-track
bound and their byte-identical outputs.

For each wave/root/source-key identity on each source track, find its earliest
possible NOTE. Bound every control state from there onward **and the entire
recurring body**, then take the maximum across every track sharing the identity.
Earlier recurring bends still count because a later iteration or release tail
can encounter them. Do not trim at gate-off: release tails can continue following
track controls. One-octave/key127 preparation limits, tuning compensation and
nominal cutoff checks remain. Source keys, schedules, pitch controls, bank
allocation and native mixer are unchanged.

Fourteen prepared-wave bounds drop from498 to zero. Of86 waves,82 now shift
by zero semitones, one by eight and three by twelve; the genuine intro bends
remain protected. The key91 accent prepares at91 with bound0 and first use2256.
An independent raw-action reconstruction verifies every first use, subsequent/
recurring control bound, shared identity and prepared wave. Maximum nominal
cutoff at the bound is0.9003767312847538 of mixer Nyquist. This is not a brick-wall
or an audible alias-error guarantee.

## Actual output around the four accents

Diagnostic ROMs zero other waves' PCM payloads while preserving every command,
control, tone, wave header and sample length. Native SDL captures isolate this
voice without deleting notes or changing scheduling. The four attack envelopes
use a15ms RMS window over190ms after each modeled onset, at original gain:

| Native source3 output | Key88 | Key89 | Key91, third accent | Key88 |
| --- | ---: | ---: | ---: | ---: |
| Rejected revision1 | 857 | 821 | 178 | 850 |
| Corrected revision2 | 1317 | 1297 | 1253 | 1324 |
| Prior plain reference | 1576 | 1487 | 1464 | 1579 |

The third accent increases7.024 times and reaches95.1% of the median of the
other three, compared with about21% before. These are diagnostic output-energy
measurements, not human listening acceptance or whole-mix perceptual proof.
No extra gain or normalization is applied. Local `comparison/four-accent-ab.html`
contains equal-level full-mix and isolated clips from18.8–22.6 seconds. Diagnostic
isolated ROMs are not delivered as test patches. NumPy/SciPy are used only in
this local audio analysis; production conversion remains Python stdlib.

## Source and native evidence

Japanese `ssr1d.nds`, SDAT667, SHA-256
`2b162eced95dadba3362316e0eb49b95b2990014a7fcb119fb9d21c1b01c1fd7`.
All seven source variants retain pinned identities. The unchanged, pinned
180-second independent software DS reference is rechecked against revision2:
3775 notes,26 raw waves and source controls/envelopes match. Reference peak15544
and coarse100ms maximum16 voices are software evidence, not hardware audio or
native polyphony proof.

Eight tracks preserve1665 mappings, common entry3840/period5376, twelve alias
identities and the original compatible-bank split at tick791. The track3/key60
and track7/key96 alias127 contexts retain their distinct waves. Natural frontend
playback covers7875 frames through clock14594, two complete common cycles and
all86 waves, without register/RAM injection, header redirection or restart.
The original NOTE observer covers7883 frames through14608:2741/2741 allocations,
including62 TIE uses, zero rejection or held/starting preemption. All identities,
clocks, outcomes, slots and307 nonzero-envelope release reuses match plain.
All15031 playback commands match apart from relocated GOTO pointers.

All2741 allocated gate/key/velocity/priority snapshots and315320 native
BEND/BENDR/TUNE/PAN/VOL comparisons pass. Source3/7 held channels reach498/762
units with76/839 consecutive positive pitch/frequency-direction changes,
retaining owner/wave/key. Source6 PAN10/20/110 has5173 stable observations:
4912 left-extreme (median−0.7255),261 right-extreme (median+0.7576), with definition
pan included and explicit starting/release/change-frame exclusions. These are
bounded channel checks, not absolute-frequency or whole-mix alignment proofs.
Saved clocks follow `1 + floor((frame-1)*139/75)`; emulated phase is not wall or
hardware timing. Effects100/129, continuation, queued stop and three restoration
cycles pass via disposable PC/LR/argument injection; actual gameplay remains
manual scope. The30-second full-mix preview peaks at12983 and precedes the first
GOTO; separate native observations establish actual loop coverage.

Revision2 stores515909 PCM8 values,293 clamped (156 negative/137 positive), with
unclamped range approximately−148.736…140.026. This is offline storage clipping,
not mixer clipping or an audible-error bound. ROM append573820 bytes. Gain
remains+3.5dB, ten PCM channels at10512Hz. Ten-voice tails and PCM8/filter/volume/
ADSR/tempo approximations remain.

## Fresh regression and historical records

Because shared conversion code changed, revision2 runs the complete518-case
suite with zero skips, including seven new cases for expired intro bends,
subsequent release-tail bends, recurring earlier bends, held starting pitch,
mode/key guards, unchanged default behavior and this exact key91 regression.
This replaces coverage reuse for this revision. All72 historical ROM/BPS pairs
are freshly recompiled with their original options and remain byte-identical;
this is not integrity-only patch reconstruction. The two historical unaccepted
controls stay unaccepted. Formal CLI reproduces all eight new native-tested
outputs byte for byte. Recursive v10–v37 archives and historical counts stay
unchanged; no new scanner route or native runtime is introduced.

The recreated plain ROM/BPS retain the prior same-source acceptance:
CRC `25210DFE`, ROM SHA-256
`77ca068cb73ae060b0ce4abb0eede11657d999b149419b21ed224911cbdabd61`.
That identity receipt is no new manual session or acceptance transfer to either
filtered revision. Revision1's partial/interrupted records, short frame-cap run,
reversed track-max fixture and premature reproduction invocation remain local
historical records, not passing evidence. Its exact user-reported issue remains
recorded in `sf1-satellite-upward-antialias-exe6-v1/manual-testing.json`.

## Corrected exact ROM: audible issue resolved by user report

- ROM CRC32: `6B36F61C`; size8962428 bytes.
- ROM SHA-256: `515d406f1a591e39f99306fdf4366eef48bf1e6d8be12ac90d11ca93b234b75b`.
- BPS SHA-256: `9c0fbccec7b93bfb3832c3cb99dcb219e42a477e729b1354009c6de44f16740b`.
- Local folder: `out/nds-research/sf1-satellite-upward-antialias-exe6-v2/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

On 2026-10-25, after delivery of this exact corrected ROM, the user reported
“正常了”, accepting resolution of the missing third accent near00:20. ROM, BPS
and test-copy fingerprints were verified at acceptance. This brief report does
not separately establish listening duration, both-scene retest, chip/Buster
effects or three battle→map→battle cycles. Those broader manual checklist items
are not newly inferred; automatic lifecycle/native observations remain separate.
Linked play, rematches and comparative preference remain unestablished.
Revision1 stays unaccepted. Transport verification remains a separate record.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-satellite-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-satellite-upward-antialias-exe6-v2
```

Use a fresh directory. The current selector reproduces revision2; revision1's
builder/converter are retained locally for historical reproduction. ROMs, assets
and local research outputs stay outside Git.
