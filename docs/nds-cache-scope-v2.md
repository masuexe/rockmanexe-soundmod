# NDS cache scope and visible preparation time

The previous cache key hashed every Python script and JSON configuration file.
Appending existing song registrations therefore invalidated unrelated prepared
audio, producing repeated first-use waits after each library update. One local
Gregar KANDO measurement took12.87 seconds without cache, versus0.24 seconds
from disk and0.16 seconds for an immediate repeat. These are one-run local
measurements, not a universal timing guarantee or user-side trace.

## New key boundary

The key now fingerprints the transitive local Python imports of the conversion,
analysis and target-validation roots, plus JSON configuration and the existing
Python/platform identity. AST traversal includes imports inside functions and
optional branches; cycles are deduplicated. A versioned dependency policy keeps
old and new key domains distinct. Audio code/configuration changes still miss.

Manager/UI/registry-only changes are outside that closure. Every requested
original ROM/SDAT and target must still match pinned fingerprints. Selector,
sequence index, gain, finite flag, track count and ten-channel configuration
remain part of each song's identity. Changing one of those cannot reuse its old
entry. Registry expansion can preserve prepared audio while the enlarged final
ROM table still changes exported fingerprints and needs its own acceptance.
Adding new converter behavior or editing a conversion dependency remains a
conservative whole-toolchain invalidation.

Existing legacy entries are retained but are not automatically relabelled or
trusted under the new key. This first policy upgrade requires preparation once;
seventeen fresh Falzar entries were compared against prior compiled blob and
conversion/dependency values before being prepared for the current workspace.
Generated entries are appended to the usual `out/manager/nds-cache/`, without
changing user project/config files or legacy entries. Other data directories,
source revisions or targets may still need their own first preparation.

## Waiting feedback

Play now reports real elapsed seconds during preparation and explains first-use
NDS waiting and later cache reuse. No completion percentage or precise finish
estimate is invented. The timer is cleared on playback, Stop, errors and stale
requests, including simultaneous replacements. This display change does not
change the player, mixer, converted audio or exported ROM.

Cold conversion itself still takes seconds. This update avoids unnecessary
reconversion after registration/UI edits; it does not accelerate the FIR DSP.
Record mGBA preview still includes game startup and the selected clip duration.
Updating Python requires a server restart; a page reload alone does not replace
a running server's loaded cache policy. The updated usual manager is started at
`http://127.0.0.1:8765/` with saved Falzar settings and all seventeen entries
prepared. An isolated prepared review server is also at
`http://127.0.0.1:8781/`. Cache preparation preserves user project files.

## Verification and evidence boundary

Local evidence is under `out/nds-research/nds-cache-scope-v2/`. Checks compare
cold and restarted-disk exports for both Japanese EXE6 targets against previous
bytes, exercise all seventeen prepared Falzar realtime starts, and use cloned
production source edits to prove real cache reuse across registry/manager/web
changes and a cache miss after a transitive DSP change. Unit cases also cover
optional imports, cycles, configuration/environment invalidation and invalid or
missing conversion roots.

Three JavaScript suites cover manager workflows/loading text, actual client
elapsed notifications and timer cleanup, and worklet buffering/drain. A full
Python attempt was interrupted at a session transition after473 progress markers,
without a final result; that log is retained separately and is not a pass. The
replacement full run freezes all final Python/JavaScript/native/config inputs.
The initial review-server helper had an argument-count error before serving;
its corrected run is recorded separately, with no ROM or production-source
change. The failed local log is retained. After the session transition, seventeen
derived realtime preview-input files failed their filename/content fingerprint
check (truncated to8MiB). Only those invalid generated research files were
removed and regenerated; the successful new realtime starts use complete files.
Source ROMs, conversion caches and exported baselines retained their identities.
The failed restart log and affected-file hashes remain separate evidence.

The exact accepted Gregar ROM remains CRC32 `D1A5CB1F`, SHA-256
`f1721a7ce5fe6f0fb295a8bb9761bcc2f309e17cd1e8cf050e51265278e5ea80`.
Its BPS remains SHA-256
`0e3fd85d781297e576c37eca16ec88a81504313708b83071baa6809c1a3e8c5e`.
Only that fingerprint reuses the existing user-reported checks. No new listening
pass or delivery is recorded; the Windows patch is retained and checked.
Falzar byte equality is automatic evidence, without inferred manual Falzar
acceptance. Previous voice/filter/PCM8/envelope/tempo and per-song limits remain.

A fresh550-case Python suite without skips and all three JavaScript suites
pass against final frozen inputs. Both target cold/restarted exports match
previous ROM/BPS bytes. Seventeen prepared Falzar realtime starts use zero
conversions and17 disk hits; one local run records 0.145–0.310 seconds to first audio.
These timings include local build/player startup with OS caches not cleared,
not a general latency guarantee. Seventeen entries were appended and verified
in the usual cache directory, preserving all prior entries and user JSON files.
The updated usual manager restores the saved Falzar settings and reads all17
entries without conversion; refreshing its page uses the new elapsed display.
Recursive v10–v38 file sets/hashes and the existing Windows test patch retain
their identities. No new listening or gameplay acceptance is recorded.
