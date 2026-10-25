# On-demand NDS conversion and persistent caching

Loading the manager catalog now validates original ROM/SDAT fingerprints and
lists the registered songs without converting audio. Saving a project also
performs no conversion. First preview/export prepares only the NDS songs it
needs; every selected original must remain available and unchanged.

Generated conversions persist under `<data-dir>/nds-cache/`. Restarting the
manager reuses checked entries. Deleting this generated cache is safe: requested
songs will be rebuilt. A read-only/full cache does not prevent valid exports.
The eight-song roster at cache introduction, stable IDs, gains and project
schema were unchanged by that optimization. Later library additions are recorded
in the manager library guide.

## Validation and invalidation

Cache identity includes original ROM and SDAT fingerprints, target base/profile,
registered selector/index/gain, finite flag, track count and ten-channel setting.
A toolchain fingerprint snapshots the conversion dependency closure, all JSON
configuration, Python implementation/version, platform, machine and libc at
module import. Local imports are followed transitively, including function-local
and optional branches. Converter/analysis/target roots are mandatory; missing
roots or invalid Python fail closed. Manager, UI and registry-only edits do not
change this key. Audio dependencies or configuration changes still invalidate it.
Per-song selector/index/gain/finite/track-count changes remain identity changes.
Restart the server after updating Python source; an existing server continues
using its loaded release. The [cache scope update](nds-cache-scope-v2.md) records
the new policy, one-time upgrade and exact-output checks.

Entries use bounded JSON/base64, not executable serialization. A payload digest,
compiled-container fingerprint and configuration checks protect integrity.
Dependency reports are reparsed from compiled bytes, preserving native Python
note tuples that JSON alone would change. JSON canonicalization also normalizes
numeric keys before sorting and hashing. Truncated, malformed, mismatched or
invalid entries are treated as misses and rebuilt through the existing converter;
converter/headroom/timing failures propagate instead of becoming cache hits.

Writes use a unique sibling temporary file, fsync and atomic replacement.
Interrupted temporary files are not read as entries. Memory reuse is protected
by a lock; build snapshots are private so concurrent preview/export preparation
cannot mutate the loaded catalog. Only prepared sources get generated-resource
fingerprints in export metadata. ROM/BPS and parsed conversion provenance remain
unchanged; catalog/manifest metadata can omit unprepared resource fingerprints.

Play now shows elapsed preparation time while waiting, with a first-use/local-
cache hint for NDS songs. It does not estimate completion percentages. Timers
stop on playback, Stop, error and request replacement. Slow preparation happens
outside the manager state lock. State and Stop
requests remain responsive. Stop, a newer preview or a source revision change
prevents a stale request from starting playback. An already requested conversion
may finish and populate the cache after cancellation; cancellation is not a
mid-converter CPU interrupt. Playback still uses the converted GBA song.

Generated PCM caches and `.nds` inputs are ignored by Git, including cache
folders within custom data directories. No source ROM is modified.

## Verification

A fresh 546-case Python suite without skips and both JavaScript suites pass.
New cases cover memory/disk reuse, native dependency types, numeric JSON keys,
corrupt entries, invalid containers/configurations, source/target/toolchain/gain
key changes, atomic-write failure and converter rejection. Manager tests require
zero conversions on catalog load, exactly two on a two-song export, and disk
reuse after restart. Changed original bytes still reject even with a cache.
Thread tests cover state responsiveness, Stop, superseding requests and source
selection changes without stale playback.

The previous eager manager/catalog from commit `ea13061` is compared against
cold lazy, restarted disk and repaired-cache exports. Three project cases
include the accepted ROOM/KANDO project, an all-eight-song pool and a finite
pair. All ROM/BPS pairs are byte-identical to the previous implementation. A
truncated ROOM entry triggers exactly one rebuild while KANDO uses disk cache,
and reproduces the accepted ROM/BPS again. Falzar is checked with the same
cache directory: Gregar entries cannot satisfy Falzar requests, and cold and
restarted Falzar exports match its previous automatically verified bytes.

One local measurement with all three NDS families selected, under concurrent
regression work, recorded 86.76 seconds for the eager eight-song load, 0.18 seconds
for lazy loading and 0.20 seconds after restart. The restarted manager used eight
disk entries with zero conversions across the comparison projects. These are
one-run timings on this machine, with OS caches not cleared; they are not a
universal performance guarantee. First use still pays the needed conversion cost.

Actual localhost HTTP checks load all eight entries with zero conversion, query
state and cancel while a first-use conversion is deliberately paused, then
initialize real realtime audio. A real 12-second finite preview ends with four
seconds of zero PCM and retains project pools. UI/worklet checks also pass.
No converter, relocator, native/realtime implementation or archived v10–v38
report is changed by this optimization.

## Existing acceptance, not a new listening claim

The accepted Gregar ROM remains CRC32 `85108329`, SHA-256
`6f06a99eb7463d3534107f8524172afd363f99d73b0aa61eb8643ca03ad6288e`.
Its BPS remains SHA-256
`3114ad079a6a7e61156cb3598deaccef1684eace257e2b93bbfaf5a781122e3f`.
Exact equality permits reuse of that ROM's existing native measurements and
user-reported listening/gameplay scope. No new listening delivery or manual
pass is recorded; the existing Windows test patch is retained and checked.

The all-eight and finite-pair comparison builds are automatic regression
artifacts, not newly accepted gameplay configurations. Likewise Falzar equality
does not establish manual Falzar acceptance. Prior ten-voice, PCM8/filter,
volume/envelope/tempo and per-song voice/tail limitations remain. Performance,
cache and cancellation behavior is automatically verified, not newly reported
as tested by the user.

Local evidence is under `out/nds-research/nds-lazy-cache-v1/`; generated game
assets remain outside Git.

On 2026-10-25, the user reported no anomaly in the cache-version manager and
confirmed its eight-entry roster. This is manager workflow feedback, without
additional listening/gameplay coverage or a new ROM acceptance claim.
