# NDS manager library v3: eleven registered songs

This batch appends three existing standalone configurations to the manager.
The first eight tuples/slots8954–8961, saved keys, gains and project schema
remain intact. The converter, sample preparation, native mixer, relocator,
realtime engine and cache implementation are unchanged.

| Slot | Source | Song / selector | Gain | Playback |
| --- | --- | --- | ---: | --- |
| 8962 | SF1 | SCHOOL / `sf1-school-antialias` | +3.5dB | Looping, seven tracks |
| 8963 | SF2 | WIN2 / `sf2-win2-release-antialias` | +3.5dB | Finite, six tracks |
| 8964 | SF3 | COMICAL / `sf3-comical-antialias` | +3.5dB | Looping, eight tracks |

WIN2 uses its existing explicit finite-release snapshot route. Its SF2 source
track3 release initialization remains120, mapped to native177 rather than the
instrument default237. It ends naturally, without an invented repeat. SCHOOL
and COMICAL use existing singleton filtering. This expands the registered
subset; selecting three NDS originals does not import every archive sequence.

Catalog load performs no conversion. First preview/export prepares only the
requested songs; later sessions reuse validated local entries. Appending the
registry changes the conservative loaded-toolchain cache key, so old entries
are rebuilt on demand under the new release. Old project keys and pools remain
compatible, while table expansion to8965 changes ROM/BPS fingerprints. The
previous accepted ROM85108329 does not accept the new export.

## Evidence and manual scope

Local evidence is generated under `out/nds-research/nds-manager-library-v3/`.
All eleven fresh conversions are compared against exact accepted standalone
blobs, dependency reports and conversion data before prior DS-reference and
per-song native evidence is reused. This identity check is not a fresh DS
render, a new timbre comparison or acceptance of every manager export.

The new Gregar delivery assigns SCHOOL to title and COMICAL to ordinary virus
and communication battle requests. WIN2 is checked through its own manager
preview. The final requested manual checks cover the eleven-song roster,
three added previews, WIN2 ending/no-replay wait, project save/reload/export,
SCHOOL's first loop join, COMICAL's loop join, chip/Buster effects and three
battle→map→battle encounters. Exact fingerprints and automatic results are recorded below.

The final-ROM report below accepts general listening and added-song visibility. Earlier standalone and
manager acceptances remain specific to their own artifacts and reported scope.
Controlled native helper calls do not establish actual battles, maps, results,
linked play or rematches. Short Falzar captures do not establish full loops or
manual Falzar acceptance. The existing ten-voice,10512Hz/PCM8, sample filtering,
volume/envelope/tempo and per-song allocation/release-tail limits remain.

ROMs, source assets, caches and local research outputs stay outside Git.

## Automatic results and exact artifact

All eleven fresh blobs, dependency values and conversion reports match their
accepted standalone counterparts. Their archived ROM fingerprints and BPS
reconstruction also pass. All eleven actual agbplay starts produce nonzero
stereo, without claiming complete-song or fidelity equivalence.

Actual localhost HTTP lists eleven entries with zero load conversions and
exports the exact final ROM/BPS. New SCHOOL/COMICAL short mGBA captures are
nonzero. The12-second WIN2 preview has zero PCM throughout its last four seconds;
cached preview jobs retain project pools. A restarted review manager uses two
disk entries and no conversions to reproduce the final SCHOOL/COMICAL export.
The previous eight-song project retains its IDs and pools, with changed output
bytes from the enlarged table. Falzar separately passes a build/BPS check and
three3-second added-song captures; those clips do not check full finite tails.

The exact Gregar ROM passes12110 normal frames between controlled queue, scene
and effect calls. Title SCHOOL reaches clock14086 after7600 warmup frames,
covering common entry3072 plus two5376-tick periods and all120 waves. First
battle COMICAL reaches clock5375, exceeding entry624 plus two2304-tick periods,
and observes all101 waves. Three cycles check effects100/129, native map requests,
cross-family title/scene restarts, no imported tails after native restoration
and queued stop. Track-owner wave checks use the current bank; no new exhaustive
NOTE-allocation or actual gameplay trace is claimed.

- ROM CRC32: `6406CA45`; size9777504 bytes.
- ROM SHA-256: `6b1ea1514e39fb47ea2084d868ebaeb71e846e7330391f989aa08ccd253368b0`.
- BPS SHA-256: `8eb6bad8aea7d80ba8b34d8a10589f205973048563ffda7041cd63a9e0492614`.
- Exact experiment: `out/nds-research/nds-manager-library-exe6-v3/`.
- Review manager: `http://127.0.0.1:8779/`.
- Manual report: listening without issues and added songs visible; detailed subchecks not separately confirmed.

The initial native-fixture preparation used a relative lookup for a parent
fingerprint recorded as an absolute path. It failed before emulator launch;
resolving both paths corrected the fixture without changing the ROM or runtime
source. The local failure note remains separate from passing native evidence.

A fresh546-case Python regression suite without skips and both JavaScript
suites pass. Runtime changes are limited to the appended registry/count facts;
manager/UI tests pin the eleven-song roster and preserve previous IDs and finite
flags. Frozen regression inputs and recursive v10–v38 file sets/hashes remain
unchanged. The final validated BPS is copied over the requested Windows test
path, with atomic replacement and destination SHA-256/byte equality recorded
in `patch-delivery.json`; transport does not establish manual acceptance.

## User report for the exact delivery

On 2026-10-25, the user reported “测试试听无问题，新加的也可以看见”
after receiving ROM6406CA45. Its ROM/BPS and the Windows test copy were checked
again at recording. This accepts the reported general listening and added-song
visibility scope, without independent listening/timing observations.

The report does not individually confirm the scene/duration of listening,
each added-song preview, WIN2 ending plus ten-second no-replay wait, project
save/reload/export, chip/Buster effects or three battle→map→battle cycles.
Those bundled requested subchecks remain explicitly partial/unreported in the
local manual record. Automatic evidence above stays separate; no broader or
other-ROM/Falzar/linked/rematch acceptance is inferred.
