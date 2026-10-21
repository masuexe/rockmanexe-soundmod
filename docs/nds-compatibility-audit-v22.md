# NDS compatibility audit v22: accepted ten-track KINCHO grouping

The scanner adds only the accepted SF3 KINCHO grouping. Source tracks 2/4/6
share one native track; the remaining seven sources remain independent. The
route requires family `ssr3`, slot 30, capacity eight, exactly source IDs 0–7/14/15,
all tracks looping, no fitted envelope and no active modulation. All existing
shared-control, fixed-volume, held-note-pan and conversion guards remain.
The standalone selector and scanner share `SF3_KINCHO_GROUPS`; all eight
accepted standalone outputs remain byte-identical after the constant refactor.
No general grouping search or new modulation/fitting capability is enabled.

## Results

All seven registered original ROM variants and three pinned SDATs verify before
and after scanning all 132 SSEQ slots. Only `ssr3:30 BGM_KINCHO` changes primary
conversion status. Its ROM/BPS match the
[accepted standalone experiment](nds-sf3-kincho-ten-track-research.md):

- ROM SHA-256: `611a189d5888eba848bf77777f105ed91cf5402238640cc9254a018fdeb37917`.
- BPS SHA-256: `668f8d77a44aecc2f68325d5c06259d0aae3bc4dd763c986efeb28b1c4671135`.

Primary packing rises from 65 to 66, with 31 exact accepted primary variants
and 36 unique source sequences having an exact accepted version. Primary
pending remains 35. All 65 old primary and 29 filtered ROM/BPS pairs keep their
bytes, routes, gains and manual-match flags. The remaining 56 primary blockers
all exceed eight tracks under the current explicit route policy. Filtered
counts remain 29 packed, eleven exact accepted, eighteen pending and 93 blocked;
filtered KINCHO remains capacity-blocked. Different variants do not inherit
acceptance by song name.

## Verification and limits

All 368 regression tests pass. Six new scanner cases cover exact source IDs,
identity/structure restrictions, plain explicit flags, retained converter guards,
headroom/packing behavior, visible model failures, separate policy export and
exclusive summary accounting. Report checks verify old packed identities,
accepted ROM/BPS/manifests, original inputs, source/scanner hashes, deterministic
rendering, actual JavaScript filters and unchanged archived v10–v21 identities.
The ten-track filter selects KINCHO alone; the nine-track filter still selects
SF2 HOKORA alone. Both contribute once to the standard summary column.

Batch success adds conversion, packing, patch and report evidence. It adds no
native playback or manual acceptance. The exact standalone KINCHO record retains
the user's listening/effects/three-encounter checklist pass and its limits; no
independent timing, full gameplay trace, linked-play/rematch result or comparative
preference is inferred. Ten-voice mixing, release tails, PCM8, ADSR and tempo
quantization remain separate from sequence-track grouping.

## Continuing investigation

The next separate candidate is SF3 DEMPAJIKEN (ASCII `BGM_DEMPAJIKEN`), eleven
source tracks into eight using two equal-volume groups: 2/4/6 and 5/8. A source
track with incompatible expression stays independent; its controls are not
flattened. This source also needs a long-note alias and explicit release checks.
It remains outside batch grouping and needs independent source/native evidence
and a new exact-ROM manual check. Native voice-budget rejections must remain
visible in that experiment rather than be treated as missing source events.

```sh
python3 scripts/audit_nds_compatibility.py \
  --source-dir /home/harp/projects/nds/roms --base ../roms/exe6.gba \
  --antialias-variants --out out/nds-research/compatibility-audit-v22
```

Use a fresh directory. ROMs, source game assets and ignored local research
outputs remain outside Git. Local logs, source/archive hashes and independent
verification helpers retain provenance; historical audit counts are immutable.
