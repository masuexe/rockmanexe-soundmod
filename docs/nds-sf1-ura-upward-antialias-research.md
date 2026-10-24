# SF1 URA: filtered long notes across the common loop cut

`sf1-ura-upward-antialias` applies the existing singleton upward/future-use
filtering modes to source18 `BGM18URA`. It adds no shared converter, runtime
mixer or native NOTE-handler changes. Eight tracks preserve278 mappings,
nine long-note aliases, five cross-cut intervals and the bank-context split
at tick791. The common entry is864 with period1536.

## Source and preparation

Japanese `ssr1d.nds`, SDAT667, SHA-256
`2b162eced95dadba3362316e0eb49b95b2990014a7fcb119fb9d21c1b01c1fd7`.
All seven local source variants retain pinned identities. A fresh180-second
independent software DS reference matches1846 notes, ten raw waves and source
controls/envelopes. Reference peak13322 and coarse100ms maximum13 voices are
software evidence, not hardware audio or a native polyphony bound.

Each prepared wave/root/source-key uses the maximum pitch after its earliest
use on each contributing track, including every subsequent control and the
entire recurring body. Release tails have no assumed cutoff at gate-off.
An independent raw-action reconstruction verifies all22 identities and shared
uses. Twenty waves prepare with no key shift, one with eight semitones and
one with twelve. Unlike the expired-intro case in SATELLITE, URA retains all
whole-track bounds: its genuine recurring/cross-cut bends still matter.
No bound reduction is forced. The one-octave/key127 guards remain.

All PCM, tuning, loop headers, tone roots/pan/ADSR and relocated waves are
checked. Total PCM8 storage is175256 values;31 clamp (7 negative/24 positive),
with unclamped range approximately−131.137…130.465. This is offline storage
clipping, not native mixer clipping or an audible-error bound. Maximum nominal
cutoff at the pitch ceiling is0.9001439760809073 of mixer Nyquist, not a
brick-wall or zero-alias guarantee. ROM append204148 bytes. Gain remains+3.5dB
with ten PCM voices at10512Hz; LFO, merged, finite and fitted-envelope modes
remain disabled.

## Original native playback and carry evidence

Natural frontend playback covers2637 frames to clock3937, two common periods
and all22 waves, without register/RAM injection, header redirection or restart.
The original NOTE observer covers2647 frames to3952:456/456 calls allocate,
zero rejection or held/starting preemption. Identities, clocks, outcomes and
all slots match the same-source plain reference; both reuse15 nonzero-envelope
release tails. All7772 playback commands match apart from relocated GOTO
pointers, with equal relative targets. Every allocated gate/key/velocity/
priority and105880 BEND/BENDR/TUNE/PAN/VOL byte comparisons pass.

Five actual held intervals are checked across entry864 and first GOTO2400,
then through their individual EOTs, for ten complete carry observations:

| Source track | Source key | Alias | Start relative to cut | EOT relative to cut |
| --- | --- | --- | --- | --- |
| 3 | 60 | 127 | −73 | 556 |
| 4 | 48 | 127 | −96 | 672 |
| 5 | 50 | 126 | −96 | 288 |
| 5 | 62 | 123 | −96 | 288 |
| 7 | 96 | 127 | −96 | 672 |

All five use distinct slots. Held ownership, wave, alias and TIE gate0 persist
through each cut to EOT. The first saved post-EOT states require release/inactive
flags or an observed later allocation of that slot. Source3/7 alias127 retains
different waves and owners through the original compatible-bank split.
The full sequence observer reaches second GOTO3936; later EOTs beyond that
window are not claimed by this carry diagnostic.

Held source3/7 channels reach498/762 pitch units, with175/772 consecutive
positive-pitch/frequency-direction changes retaining allocation/owner/wave/key.
Source2 PAN10/20 and source6 PAN110 have1212 stable channel observations:
804 left-extreme (median−0.8824),408 right-extreme (median+0.8000), including
definition pan and explicit starting/release/changing-pan/low-volume exclusions.
These are bounded channel checks, not absolute-frequency or whole-mix alignment
proofs. Clocks match `1 + floor((frame-1)*112/75)` with anchored residual below
one tick. Source112 tempo maps to native112; emulated phase is not wall or
hardware timing.

Controlled effects100/129, continuation, queued stop and three restoration/
restart cycles pass through disposable PC/LR/argument injection. Actual chip
gameplay, linked play and rematches remain manual scope. The30-second SDL preview
peaks at11547; it nominally contains the first join near0:27. Actual loop
execution is established separately by original native observations.

## Regression and historical reference

Eleven focused cases pass in prototype and after exact root migration: two new
URA cases, seven future-bound safety cases and two SATELLITE regression cases.
Removing the new branch/family entry restores the whole accepted SATELLITE-v2
builder AST. Shared converter/libraries and all prior tests are byte-identical
to that fresh518-case suite. Its518-test/72-pair recompilation evidence is
explicitly reused, not a fresh520-test run or73-song recompilation. Fresh73-pair
integrity checks reconstruct every recorded ROM from BPS/base. Formal CLI
reproduces all eight native-tested outputs byte for byte. Recursive v10–v37
archives and historical counts remain unchanged.

Initial setup failures are retained locally: the copied frontend input-library
path kept a version2 suffix and failed the required keypad check; an upward
checker was invoked before its source-only helper generation completed. Correct
paths/order preserve all assertions and change no ROM. Neither failure is
counted as passing evidence.

The recreated plain ROM/BPS match the previously accepted
[URA experiment](nds-ura-research.md) byte for byte: CRC `B4EE17B9`, ROM SHA-256
`bedd1fdf1703a521f23b01a0e6896dd840d3ccc826e93e6585cf4162ea7c9be3`.
The identity receipt pins its prior acceptance. This is no new manual session
or acceptance transfer to the different filtered ROM. Ten-voice tails and
PCM8/filter/volume/ADSR/tempo approximations remain.

## Accepted exact filtered ROM and test patch

- ROM CRC32: `12733B04`; size8592756 bytes.
- ROM SHA-256: `77489fb6db396e58712f26b4fc48eef4c6f8a7fd017fa12ff49e4017c1f30308`.
- BPS SHA-256: `47f45a8b55a5e0cf56bacf920a789df218775dc20fe6acaaabd7086373bcf0da`.
- Local folder: `out/nds-research/sf1-ura-upward-antialias-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

On 2026-10-25, the user reported “测试无问题” for this exact filtered ROM and
the three requested checks: at least three minutes listening including sustained
notes/tails and joins near0:27/0:44, repeated chip/Buster effects, and three
battle→map→battle cycles with map restoration and fresh starts. ROM, BPS and
delivered-copy fingerprints were verified at acceptance. These are user reports,
not independently observed/timed checks. Linked play, rematches, broader gameplay
and comparative timbre preference remain unestablished. No acceptance transfers
to another source or ROM. Transport remains separately recorded.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr1d.nds --base ../roms/exe6.gba \
  --song sf1-ura-upward-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf1-ura-upward-antialias-exe6-v1
```

Use a fresh directory. ROMs, source assets and local research outputs stay out of Git.
