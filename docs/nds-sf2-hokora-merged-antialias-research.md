# SF2 HOKORA: bounded nine-track merged antialias experiment

This experiment applies the existing explicit merged-antialias capability to
accepted SF2 slot20 `BGM_HOKORA`. It retains `SF2_HOKORA_GROUPS`: sources0/4
share one native track, with1/2/3/5/6/7/8 separate. Both merged sources have
fixed volume100 and neutral pan64. No converter or native-engine capability
is added; the builder exposes one pinned selector. Upward-pitch preparation,
LFO, fitted envelopes, finite release and mixed-loop modes are not enabled.
Existing compatibility, sample-budget and unsupported-effect guards remain.

All1,014 source mappings, source controls, timing, priorities and grouping
match the accepted plain conversion. There are no long aliases or loop carries.
An unpacked nine-track control preserves source note/velocity schedules;
another unpacked filtered control matches all81 prepared wave headers and raw
PCM bytes. Those controls cannot run in the eight-track target and reuse the
same DSP implementation. All81 keyed native tones are checked for source
ADSR/root/pan and relocated wave data. All4,360 playback commands are byte
identical to the plain version except relocated GOTO pointer words, whose
relative track targets remain exact.

The unchanged offline filter prepares748,395 PCM8 bytes, maximum source step
about15.363, below the32-step and4MB guards. Maximum stored tuning error is
about0.00044246 cents; this is not a whole-song native frequency-error bound.
Analysis-only instrumentation reproduces every prepared byte and records
1,197 clamped points (645 negative,552 positive), with unclamped values about
−142.960…142.508. These are stored samples, not time-weighted playback or native
mixer clipping. No per-wave normalization or runtime mixer change is introduced.

The pinned independent180-second software DS reference is reused from the
plain HOKORA investigation. Both recursive reference copies and the SDAT are
hashed; the source checker is rerun. It matches4,916 source notes and22 decoded
waves and independently checks source tempo/controls/ADSR. This is no new
renderer run and no DS hardware capture. Source tempo125 maps to native126:
about99.977 source versus100.342 native ticks/s. Existing tempo quantization
remains. Common entry1992 and period1920 put entry near0:20 and first joins
near0:39/0:58.

Natural frontend playback with Start input, without register/RAM injection,
header redirection or forced restart, reaches clock5833 in3,473 frames, covers
two complete cycles and all81 prepared waves. A separate read-only original
NOTE-handler observation reaches clock5849 in3,482 frames:1,555 NOTE calls all
allocate; no held/starting note is preempted. There are384 nonzero-envelope
release-channel reuses. A fresh read-only capture of the exact accepted plain
ROM over the same window has385 such reuses and no held preemptions;354 slot
choices differ. Original source/note identities, clocks and allocation success
match. The old plain artifacts remain unchanged; the fresh baseline is stored
separately. NOTE allocation success alone does not prove preservation of tails
or unrestricted whole-song polyphony.

All1,555 allocated channels retain gate/key/velocity/source-derived priority.
There are139,280 native track-byte comparisons for BEND/BENDR/TUNE/PAN/VOL,
including source-derived singleton volume/expression and pitch/pan. Source2
expression produces24 observed native volume levels15–40. In three held
key76 expression ramps,22 snapshots per ramp show seven channel-volume sums
rising19→39. These confirm actual held-channel changes, not a DS loudness
error bound. Stereo analysis
uses1,361 active source3 channel observations after one stable-pan frame,
excluding changed-pan frames and starting/release channels. Median signed
channel-volume balances are about−0.902 for pan10,0 for pan64 and+0.818 for
pan110. These are diagnostics, not waveform alignment or a full-song stereo
bound. The first NOTE-exit pan fixture incorrectly treated starting-channel
volume bytes as settled; those can retain earlier values. Its failed log is
preserved. The final check uses saved settled-frame observations without
changing source, converter or ROM.

No zero-velocity NOTE call is observed. Maximum emulated frame-clock residual
is1.64 ticks against a two-tick bound; it is not hardware or wall-clock timing.
Controlled helper effects100/129, continuation, queued stop and three native
restore/restart cycles pass using disposable emulator PC/LR/argument injection.
They do not establish actual chip use, linked play, rematches or gameplay.

All451 prospective-source regression tests pass without skips, including two
new builder/family/capacity/filter-guard cases. Root migration matches the
frozen tested source hashes and the two focused cases pass. All52 accepted
and two unaccepted control ROM/BPS pairs rebuild identically. Production CLI
reproduces all eight native-tested outputs byte for byte; recursive v10–v31
archive identities remain unchanged. Automated and user-reported checks are
kept separate.

## Accepted exact ROM

- ROM CRC32: `02686B1E`; size9,172,772 bytes.
- ROM SHA-256: `923ead50245fcd3fc0eb18d6689abbac0849be57856a1adbab57bc7f3802b022`.
- BPS SHA-256: `ffc7b70b6b7bb90e988f440d743c97a464a96dc6e16773723e0d31fafd981411`.
- Local folder: `out/nds-research/sf2-hokora-merged-antialias-exe6-v1/`.

The30-second preview peaks at10239 and covers the common entry, not the first
GOTO. `comparison/merged-filter-ab.html` compares plain/filtered native audio
at the same gain without extra loudness normalization or sample alignment;
the plain version is already a GBA conversion. The normalized software
DS/native page is separate. Comparative timbre preference is distinct from
functional acceptance.

On 2026-10-23, the user reported “没有问题” for this exact ROM, accepting
at least three minutes of virus-battle listening, repeated chip/Buster effects
and three battle→map→battle encounters with native-map restoration and a fresh
imported start. This is user-reported manual acceptance, separate from
automated evidence. Comparative timbre preference, independent timing, a full
manual trace, linked play and rematches were not separately reported.
Ten-voice tail reuse, conservative filtering, PCM8/clipping and volume/ADSR/
tempo quantization remain. Acceptance binds only the fingerprint above.

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr2d.nds --base ../roms/exe6.gba \
  --song sf2-hokora-merged-antialias \
  --event 1 --event 21 --event scene:communication \
  --out out/nds-research/sf2-hokora-merged-antialias-exe6-v1
```

Use a fresh directory. ROMs, game assets, captures and local outputs stay
outside Git.
