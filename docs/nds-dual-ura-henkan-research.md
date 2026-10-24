# Two NDS scores in one EXE6 ROM: title URA, battle HENKAN

The additive `build_nds_dual_experiment.py` exporter packs two registered,
checked NDS conversions into one ROM using the existing catalog relocator and
native hooks. Each converted blob has a distinct source namespace even when
both come from the same original NDS ROM. This avoids treating unrelated
blob-relative tone/wave offsets as a shared bank. One music player switches
between the scores; manager integration is outside this research exporter.

The example plan is `examples/nds-dual-ura-henkan.json`:

| Request | Song | Imported slot | Gain |
| --- | --- | --- | --- |
| Title1 | SF1 URA, filtered future-use bound | 474 | +3.5dB |
| Virus battle21 | SF1 HENKAN, finite upward filtering | 475 | 0dB |
| Communication scene | URA | 474 | +3.5dB |
| Other native music requests | Original GBA songs | Preserved native entries | Original |

HENKAN deliberately finishes after roughly six seconds and stays silent until
another music request. This is the same accepted finite-cue behavior in a new
two-bank routing experiment. All474 original table entries and undeclared base
prefix bytes remain intact. Table count becomes476; append317968 bytes; ten
PCM voices at10512Hz remain unchanged.

## Unchanged song content and separate banks

Both roles use verified Japanese `ssr1d.nds`, with registered selectors
`sf1-ura-upward-antialias` and `sf1-henkan-antialias`. The common converter
retains original-ROM/SDAT, gain/headroom, grouping and sample-budget checks.
Per-role source SDAT, converted MPlay blob and dependency JSON are byte-identical
to the accepted standalone versions. Conversion JSON values are equal; battle
gain serializes as integer0 from the JSON plan versus float0.0 from the earlier
standalone CLI. An initial literal JSON-byte check rejected that representation
difference; numeric equality and all actual audio bytes pass. No waveform or
ROM correction was made to satisfy that check.

The relocated songs have distinct headers, tone banks and disjoint wave sets
of22 and two samples. Every compiled track's command/tick/key/control sequence
matches its source report, with normal pointer relocation. BPS reconstruction
and full-prefix preservation pass. No source converter, relocator, hook or
native mixer code changed. Standalone acceptance establishes source history;
it does not accept the new composite-ROM routing.

Both unchanged conversions are rechecked against independently pinned software
DS captures: URA1846 notes and HENKAN four notes. Captures are reused, not new
renders or whole-composite playback proof. The original source/blob/dependency
identity receipts and prior manual-record hashes remain separate.

## Exact-ROM native playback and switches

Read-only natural title observation uses the actual composite manifest and ROM:
2637 frames through clock3937, two URA common periods and all22 waves, with no
register/RAM edits, header redirection or clock restart. The30-second title
preview peaks at11547, matching the standalone peak without normalization.

A clearly marked title-only validation view contains the **same composite ROM
bytes**, with genuine slot474 source metadata for the existing reference/runtime
checker. It claims title-source coverage. Its runtime additionally verifies
the actual ordinary battle dispatch to475, communication dispatch to474,
native restoration, effects100/129, queued stop and three controlled restart
cycles. No fabricated title route to battle is used.

A second controlled probe follows4460 normal frame commands between original
queue/scene/effect calls. It starts naturally at title and first switches while
URA has seven live channels at clock971. Across three full cycles it checks:

- Original virus descriptor/flag0 selects HENKAN475 and resets its clock.
- After sound initialization, the four-track active mask and all four live
  waves belong to HENKAN; current music owners use that bank.
- The cue finishes and freezes clock556. Each cycle includes600 consecutive
  inactive/empty imported-channel observations, with no stale URA tails.
- Effects100/129 during playback and after completion preserve the music header;
  post-END effects do not restart the short cue.
- Native requests2/3/2 restore GBA music, then title and communication requests
  restart URA474. Repeated scene requests restart it again.
- Queued stop resets the music indicator and clears imported tails.

These calls use disposable emulator PC/LR/argument injection and synthetic
descriptor RAM, with Toolkit/stack guards and restoration. They are not actual
battle/results/map or linked-gameplay traces. Physical menu-key simulation is
used during warmup, with unchanged keypad assertions.

Initial test fixtures wrongly treated player byte8 as the current header track
count, then expected an active mask before the first sound update. Correct
checks use actual ROM header counts and post-update masks, retaining exact
header/clock/marker/wave/owner/idle guards. A local text-edit syntax failure
stopped before capture. Failed sources/logs are retained separately; no failed
run is counted as a pass and the composite ROM stayed unchanged.

## Regression scope

Two new tests pass: bounded plan/schema/routing guards and a real same-source
dual build checking distinct banks/waves, both routes, original entries/prefix
and BPS reconstruction. Every prior525-suite Python source is byte-identical;
only the new standalone exporter and test module are added. Thus the prior
525-case/74-recompile evidence is explicitly reused, not a fresh527-case run
or75-song recompilation. Fresh75-pair integrity checks reconstruct the recorded
historical ROMs from their patches. All12 outputs of two fresh public CLI builds
are byte-identical. Recursive v10–v37 archives/counts stay unchanged.

Global ten-voice, PCM8/filter/volume/ADSR/tempo and release-tail limits remain.
This experiment changes routing/resource coexistence and requests separate
exact-ROM manual acceptance; earlier standalone checks do not transfer.

## Accepted exact composite ROM and patch

- ROM CRC32: `87CBD9C4`; size8706576 bytes.
- ROM SHA-256: `c19c41a343fc3e8003e5be06fd2ec8aaa5dfeeedd3c2a9272456cb033d6a37d7`.
- BPS SHA-256: `11d6c977af7cb1553dfa4a5cd75c7065e983e44d721653ebf4aa04b9daa41316`.
- Local folder: `out/nds-research/nds-dual-ura-henkan-exe6-v1/`.
- Windows test destination: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`.

The requested manual checks were: title is URA, virus battle changes to HENKAN and naturally
stops near six seconds, with at least10 seconds silent and no persistent old
music; chip/Buster effects during and after the cue; three battle→map→battle
cycles with restored native map music and fresh HENKAN starts. Communication,
if separately tested, should select URA; linked play/rematches are not inferred
from the other checks. No new three-minute source-fidelity listening is requested.

On 2026-10-25, the user reported “测试无问题” for the exact composite ROM
above and the three requested role/finite-stop/effects/encounter checks. These
are user-reported checks, not independent timing or gameplay recordings. The
optional communication check, linked play, rematches, broader gameplay and
comparative timbre preference were not separately reported. Acceptance is
recorded for this composite fingerprint only.

```sh
python3 scripts/build_nds_dual_experiment.py \
  --base ../roms/exe6.gba --plan examples/nds-dual-ura-henkan.json \
  --out out/nds-research/nds-dual-ura-henkan-exe6-v1
```

Use a fresh directory. ROMs, source assets and local research outputs stay out of Git.
