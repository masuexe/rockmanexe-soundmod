# SF3 DEN_LIVE sixteen-track capability experiment

This opt-in experiment preserves all16 source tracks of `ssr3:15 BGM_DEN_LIVE`
without merging their schedules. It tests a larger native MPlay track allocation
before expanding the production library. The manager still registers54 songs;
this experiment is not a new manager entry. All122 sounding SSEQ items and four
STRM items remain in the catalog goal.

## Allocation and conversion

The original Japanese EXE6 MPlay implementation supports up to16 tracks, but its
BGM player is configured for eight. All31 effect players retain their original
track counts and pointers. An explicit capacity option is admitted only for the
two fingerprint-pinned Japanese originals; ordinary exports keep their original
capacity. Imports must fit both their supplied dependency report and the actual
reparsed ROM header. An understated report cannot admit a16-track song into the
ordinary eight-track player.

The experimental BGM pool occupies `0x0203FA00..0x0203FF00`:16 records of80 bytes.
The battle clear at ROM offset`0x71E0` jumps to an appended56-byte Thumb stub.
It clears `0x0203CDA8..0x0203FA00` and `0x0203FF00..0x02040000`, then resumes at
`0x080071EA`. This preserves the music pool and the original clearing of the
upper256-byte workspace. The capacity patch changes only ten clear-hook bytes
and five BGM configuration bytes in the original prefix, in addition to the
ordinary audio/scene hooks declared in the manifest.

The Japanese sprite-cache limits remain `0x0203E000` and `0x02033000`. A lower
apparent RAM gap was rejected because the original Japanese save code accesses
it. The US reverse-engineered layout supplied research leads, not interchangeable
addresses. Static inspection, original-ROM boot traces and controlled clearing
tests support this candidate allocation; they do not prove that every gameplay
path leaves it unused. Actual battle transitions are a required manual check.

The named source route uses16 singleton groups, the existing fitted attack,
36 PCM waves and the established+3.5dB policy. No mixer, resampler or envelope
algorithm changes. Sixteen tracks still share ten PCM channels. In the observed
two-loop native schedule,5441 NOTE calls include24 rejected notes,24 preemptions
of held/starting voices and3011 release-tail reuses. These are retained listening
limits. Source-authored priority does not establish musical importance or prove
that an omitted note is inaudible.

## Reproduction and automatic evidence

```sh
python3 scripts/build_nds_experiment.py \
  --source /home/harp/projects/nds/roms/ssr3b.nds \
  --base ../roms/exe6.gba --song sf3-den-live-sixteen-track \
  --event 1 --event 21 --event scene:communication \
  --out out/sf3-den-live-sixteen-track
```

Use a new output directory. Replacing the base with`exe6f.gba` builds Falzar.
Both final ROMs are8971820 bytes:

| Target | CRC32 | SHA-256 |
| --- | --- | --- |
| Gregar | `30DD33D8` | `82b9bb66719c92f3684526ff065586c9369ffe409ad8fc49f88edda77c634749` |
| Falzar | `0B9EC3A9` | `0b232fc6a7a67074e339392aa402552c47494e732270d457ac400eca2385d3a4` |

Title1, ordinary virus21 and the separate communication scene select the same
song at slot474. Other events retain native music. Both exact final ROMs pass
BPS reconstruction and the following local native checks:

- Natural title/frontend playback runs9572 frames to clock19270. All16 active
  tracks match cursor, wait, key, velocity, status and tone models at325
  checkpoints through two common periods; all36 waves appear. All31 effect
  players initialize with original configurations.
- Read-only NOTE tracing observes every expected call and checks allocated
  gate, key, velocity, priority, ADSR, wave and owner. Allocation losses above
  are observed behavior, not excluded from the pass criterion.
- Controlled clearing preserves all1280 music bytes, clears both surrounding
  spans and returns to the original continuation.
- Three controlled lifecycle cycles restore native songs, restart16 tracks,
  enter/reenter ordinary and communication hooks, and stop. Effects100/129
  are observed on PSG and133 on PCM in separate test windows. Injected PC/LR,
  arguments and a disposable scene descriptor make this helper-call evidence;
  it does not establish actual battle, map or linked-session behavior.
- Six-second real SDL full-mix captures are nonzero, with peaks12018 Gregar
  and12017 Falzar. These short captures do not establish complete-song fidelity.

The source SDAT, converted blob and conversion report exactly match the earlier
RAM-research inputs. Its180-second independent software DS reference therefore
remains applicable:6193 matched source notes and36 exact decoded waves. This is
source/conversion evidence; the final ROMs have their own native observations.
The software reference is not a hardware recording or a subjective comparison.

A fresh public CLI build reproduces all eight Gregar artifacts byte for byte.
Repacking the54 existing converted banks with the default eight-track setting
reproduces the earlier Falzar pool exactly:25646828 bytes, CRC32`A6A1313A`,
SHA-256`cf3e3f3c9a7aeea57663f6953550635fe9acffaa693fb3744311deb06028a0fa`.
This reuses checked converted banks; it does not claim a fresh54-song conversion
or cache-hit audit. All36 relocated PCM resources match their generated headers
and payloads in both final experimental ROMs.

Five new tests cover capacity policy, both original prefixes, conflicts,
source-specific reproduction and the understated-report rejection. All562
Python tests pass without skips, as do the three JavaScript suites. The final
Gregar BPS was copied to`C:\trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`;
destination SHA-256 matches
`ebf9037619b9eecd40733936a925879c61d671bc71dd06d8773a1dad6ff2018d`.
The final local validation summary records the exact artifacts and coverage.
Source assets and generated ROMs remain outside Git.

## Manual status

The user reports “可以，没问题” for exact Gregar ROM`30DD33D8` after the
requested checklist. This is user-reported acceptance; durations and gameplay
were not independently timed or observed. The requested checks are
180 seconds at title for later layers and two common loop joins;90 seconds in
virus battle with chips/Buster and three battle-map-battle cycles; and90 seconds
in communication with effects, exit and reentry. Assess missing notes, balance,
seams, restoration and a fresh start on reentry. Falzar manual coverage and
linked-session stability are not inferred from this delivery.

After acceptance, the next work is to integrate suitable validated candidates
in bounded manager batches and address the remaining modulation/envelope and
stream limits. This one capability experiment does not complete the126 items.
