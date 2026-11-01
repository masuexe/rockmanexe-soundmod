# NDS manager library v9: thirty-nine registered songs

This batch appends two independently accepted SF2 configurations. The first37
entries, slots8954–8990, gain, track counts and finite flags stay fixed. It
changes registry data and count/roster fixtures only; converter, mixer, native
driver, relocator, realtime/cache, browser runtime and project schema are unchanged.

| Slot | Song | Selector | Tracks | Gain | Playback |
| --- | --- | --- | ---: | ---: | --- |
| 8991 | SF2 MIZUUMI | `sf2-mizuumi-variable-tempo` | 8 | +3.5dB | Loops |
| 8992 | SF2 NESSIE | `sf2-nessie-envelope` | 8 | +3.5dB | Loops |

[MIZUUMI](nds-sf2-mizuumi-variable-tempo-research.md) uses the accepted explicit
variable-tempo native pitch-LFO approximation. Its six tempos80/85/90/100/110/120
retain LFOS compensation and held-note phase continuity without combining other
live-modulation modes. [NESSIE](nds-nessie-research.md) retains the accepted fitted
attacks90/100/127, one alias for264/312-tick gates and native pitch LFO. Both keep original
PCM preparation; this batch does not add filtering to modulation modes.

## Source and cache verification

Fresh Falzar preparations exactly match each accepted compiled blob and parsed
dependency report. MIZUUMI's conversion report matches strictly. NESSIE's older
report lacks only empty `long_note_loop_carries`/`voice_context_splits` fields
and eight `gate_checked_until_ticks` diagnostics, pinned to17736 for track0 and
17712 for tracks1–7. Removing those ten additions restores exact report equality;
no operative report difference is permitted. The original failed strict-report
preflight stays recorded separately from the successful reconciliation. Eight
negative report mutations across both candidates are rejected.

All39 manager blobs/dependencies match their own accepted standalone artifacts;
36 reports match strictly and three use explicit legacy diagnostic/wording
reconciliation (the prior BATTLE/KAICYOU cases plus NESSIE). Accepted ROM/manual
fingerprints and BPS reconstruction are verified. Independent source/DS and
per-song native evidence is reused under these identities, without a new DS
render, source scan or retroactive expansion of old acceptance scopes.

The toolchain identity remains unchanged. All37 existing Falzar cache entries
hit disk with zero conversions. Metadata load performs no conversion. New
configurations are prepared separately, then all39 configurations use normal
manager load/preview/export paths. Old target/cache-directory/revision boundaries
remain. A v8 saved project retains song keys, slots and pools; expanding the
table to8993 changes ROM bytes, so prior exact-ROM acceptance does not transfer.

## Regression and integration

Fresh34-case manager/cache/lazy-preview/realtime regression and three JavaScript
suites pass without skips. The prior550-case full suite is reused under exact
unchanged audio/runtime/config/test source identities, except the registry and
two roster/count fixtures. Removing SONGS/TRACK_COUNTS restores the prior whole
catalog AST. This is not a fresh550-case full-suite run.

All39 real agbplay starts produce nonzero stereo. A separate Falzar39-song pool
packs22,839,804 bytes and checks distinct headers/tone banks, original per-song
PCM sets, safe exact-content
resource sharing, BPS reconstruction and the32MiB bound. Packing does not establish
every random runtime selection or manual acceptance. Real HTTP checks cover39
catalog entries, byte-equal Falzar export and three-second mGBA previews for both
additions; cache reuse preserves project pools. No new manual Falzar gameplay
acceptance is inferred.

## Retained sound and coverage limits

Native triangle LFO versus DS sine, shared phase/note resets, ADSR approximation,
original PCM aliasing, PCM8, ten voices,10512Hz and tempo/frequency rounding remain.
NESSIE's slower onset timing/curve and release differences retain the standalone
fit bounds. MIZUUMI's DS source reaches sixteen voices in sampled observations;
successful allocation does not prove equal polyphony or unshortened tails.

NESSIE's older standalone instrumented evidence is bounded before its compiled
loop. New composite loop/lifecycle observations are separate evidence and do not
retroactively turn that old record into a complete envelope/LFO/NOTE trace.
MIZUUMI's prior variable-tempo/LFO comparisons retain their exact scope. No new
full NOTE-allocation, waveform-fidelity or zero-preemption proof is claimed.
Other songs retain all previous limits, including AJITO's fourteen held/starting
preemptions, STUDIO soft-note quantization, CHANGE's four preemptions and SF3
DEMPAJIKEN's three rejected NOTE calls in prior bounded standalone traces.

## Exact delivery and requested review

- Gregar ROM CRC32: `4C9805E9`; size9234944 bytes.
- ROM SHA-256: `cac6ba099e96dd42bbcc5fdfda2ee71541be4f77c2207bfdf03060477d4d427d`.
- BPS SHA-256: `9ef601f61960d508a98a1f12a048e74db758a74c4044fe771bd71d41c13ebf20`.
- Prepared39-song Falzar manager: `http://127.0.0.1:8786/`.

The Gregar patch selects MIZUUMI for title and NESSIE for ordinary virus and
communication battle requests; other pools retain native music. Requested manual
checks:39-song roster/two previews, save/reload/export; title MIZUUMI at least180
seconds with tempo transitions near12 and48–51 seconds and joins near107/158;
virus NESSIE at least240 seconds with slower onsets near30 seconds and joins near
131/177/223; chip/Buster effects and three battle→map→battle cycles.
The user reports the requested checks passed; comparative DS fidelity, arbitrary exports/roles,
linked play/rematches and manual Falzar gameplay remain separate.

The final validated BPS overwrites `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`
with byte/SHA-256 equality recorded in the delivery record. Delivery is transport
evidence only. Local records are in `out/nds-research/nds-manager-library-v9/`
and `out/nds-research/nds-manager-library-exe6-v9/`; ROMs/assets/caches stay out of Git.
Archived v10–v38 identities remain unchanged.

## Remaining source investigation

A metadata inventory finds15 additional unregistered source sequences with at
least one accepted standalone record. This is a shortlist for future review,
not15 newly verified manager songs. Alternative plain/filtered SATELLITE records
count as one sequence; the filtered revision's limited missing-accent acceptance
must not be expanded by the inventory. Each future batch still needs exact
configuration/audio/report identity and scope review. Most remaining routes
use native modulation or envelope approximations. This batch registers only
MIZUUMI/NESSIE and adds no new conversion capability.

## Final native verification

The exact composite passes22,410 ordinary frames between controlled calls.
MIZUUMI reaches clock15,464, beyond common entry5424 plus two4800-tick periods;
NESSIE reaches18,580, beyond entry8496 plus two4608-tick periods. All24/29 waves
are observed under the currently active music tracks. Twelve exact-content waves
are shared safely between banks, so coverage uses both wave identity and track
ownership. Both eight-track looping headers retain statusFF in checked windows.

Effects100/129, three controlled native-restore/title/battle/communication-restart
cycles and queued stop pass; no imported tails persist after native restoration.
The fixture uses PC/LR/argument and disposable scene-RAM injection, with normal
frames between calls. It does not establish actual battles, maps, linked play
or rematches, inspect all NOTE allocations, revalidate every LFO/envelope step
or cover NESSIE's third join near223 seconds. The requested four-minute battle
listening covers that later window separately. User-reported acceptance is
recorded below.

## Exact-ROM user acceptance

The user reported “测试没有问题” in response to all three requested checks for
ROM4C9805E9. ROM, BPS and the Windows test copy were verified again when recording
acceptance. The39-song roster and two added previews, save/reload/export, title
MIZUUMI for at least180 seconds and virus-battle NESSIE for at least240 seconds
including the requested tempo/onset/loop windows, chips/Buster and three
battle→map→battle cycles with native restoration and fresh starts are recorded
as user-reported passes.

These are user reports, not independently timed or observed checks. They do
not establish comparative DS fidelity, zero-note-loss, arbitrary exports/roles,
linked play/rematches or manual Falzar gameplay. Original PCM, native triangle
LFO/shared phase, envelope/tempo quantization, voice-budget and all previous
per-song limits remain. Fresh34-case focused regression and reused550-case
full-suite evidence stay separately identified. Acceptance recording changes
documentation only; source tests were not rerun for this step.
