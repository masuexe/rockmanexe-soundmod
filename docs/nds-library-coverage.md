# Star Force music coverage

This ledger tracks the complete requested music catalog across the three pinned
Japanese source archives. It separates available library entries from remaining
work. A registered entry does not establish acceptance of every exported ROM.

| Family | SSEQ slots | With notes | Library entries | Missing SSEQ | STRM music |
| --- | ---: | ---: | ---: | ---: | ---: |
| ssr1 | 38 | 35 | 27 | 8 | 2 |
| ssr2 | 43 | 40 | 11 | 29 | 1 |
| ssr3 | 51 | 47 | 16 | 31 | 1 |

The complete inventory has132 SSEQ slots and four nonempty STRM files. Five
SSEQ slots are empty. Five execute no notes in the bounded source trace. All
122 SSEQ entries with notes, including short cues, and all four streams remain
in scope. The library offers54 of126 music items with content. It still lacks
68 SSEQ entries and four streams. This is not completion of the full goal.

The source files also have three `SEQARC_SE` archives. All their named entries
have the `SE` prefix. These sound-effect archives are listed separately from
the background-music catalog. No effect is silently counted as an imported song.

## Remaining work

Seventeen missing sequences already have a historical packed variant. They
still need source-specific reference, native, integration and manual evidence.
The other51 missing sequences had capacity blockers in the v38 audit. Those
results are historical leads; current conversion support must be verified.
The four STRM files need a separate stream decoding/playback path. The present
SSEQ converter does not import them.

| Stream | Name | Source bytes | State |
| --- | --- | ---: | --- |
| ssr1:strm:0 | STRM_BGM01TITLE | 1878620 | Decoder/playback research |
| ssr1:strm:1 | STRM_BGM35STAFFROLL | 4188468 | Decoder/playback research |
| ssr2:strm:0 | STRM_TITLE | 1708320 | Decoder/playback research |
| ssr3:strm:0 | STRM_TITLE | 1627444 | Decoder/playback research |

## Complete SSEQ ledger

These classifications come from a fresh read of the pinned originals. Note
counts are bounded trace evidence, not a recording of every possible game state.
The v38 status is retained as historical packing evidence only.

| Source | Sequence | Library or remaining category | v38 packing status |
| --- | --- | --- | --- |
| ssr1:0 | BGM00DUMMY | silent_sequence | silent_sequence |
| ssr1:1 | (empty) | empty_slot | empty_slot |
| ssr1:2 | BGM02FMPLANET | sf1-fmplanet-delay | packed_delayed_lfo_approximation |
| ssr1:3 | BGM03HOMETOWN | sf1-hometown-depth | packed_envelope_live_depth_lfo_approximation |
| ssr1:4 | BGM04ROOM | sf1-room-antialias | packed_standard |
| ssr1:5 | BGM05LABO | sf1-labo-antialias | packed_standard |
| ssr1:6 | BGM06SCHOOL | sf1-school-antialias | packed_standard |
| ssr1:7 | BGM07GOWAIINCHO | sf1-gowaiincho-delay | packed_delayed_lfo_approximation |
| ssr1:8 | BGM08YUMENOSHIMA | existing_packing_needs_validation | packed_lfo_approximation |
| ssr1:9 | BGM09SATELLITE | sf1-satellite-upward-antialias | packed_standard |
| ssr1:10 | BGM10DEMPA | existing_packing_needs_validation | packed_delayed_lfo_approximation |
| ssr1:11 | BGM11DEMPAJIKEN | sf1-dempajiken-antialias | packed_standard |
| ssr1:12 | BGM12TRUCK | existing_packing_needs_validation | packed_delayed_lfo_approximation |
| ssr1:13 | BGM13PLANETARIUM | sf1-planetarium-delay | packed_delayed_lfo_approximation |
| ssr1:14 | BGM14SCHOOLDENNO | conversion_capacity_research | capacity_blocked |
| ssr1:15 | BGM15GOWADENNO | existing_packing_needs_validation | packed_lfo_approximation |
| ssr1:16 | BGM16ANTENNA | sf1-antenna-antialias | packed_standard |
| ssr1:17 | BGM17LAST | sf1-last-antialias | packed_standard |
| ssr1:18 | BGM18URA | sf1-ura-upward-antialias | packed_standard |
| ssr1:19 | BGM19KAKUSHI | existing_packing_needs_validation | packed_lfo_approximation |
| ssr1:20 | BGM20HOKORA | sf1-hokora-mixed-delay | packed_mixed_min_depth_lfo_approximation |
| ssr1:21 | BGM21COMICAL | sf1-comical-antialias | packed_standard |
| ssr1:22 | BGM22JIKEN | sf1-jiken-antialias | packed_standard |
| ssr1:23 | BGM23KINCHO | sf1-kincho-antialias | packed_standard |
| ssr1:24 | BGM24KANDO | sf1-kando-antialias | packed_standard |
| ssr1:25 | BGM25SETSUNAI | sf1-setsunai-antialias | packed_standard |
| ssr1:26 | BGM26HENKAN | sf1-henkan-antialias | packed_finite_standard |
| ssr1:27 | BGM27BATTLE | sf1-battle-lfo | packed_lfo_approximation |
| ssr1:28 | BGM28BOSS | sf1-boss-toggle | packed_live_toggle_lfo_approximation |
| ssr1:29 | BGM29LASTBOSS | existing_packing_needs_validation | packed_delayed_lfo_approximation |
| ssr1:30 | BGM30WIN | sf1-win-antialias | packed_standard |
| ssr1:31 | BGM31WIN2 | sf1-win2-antialias | packed_finite_standard |
| ssr1:32 | BGM32LOSE | sf1-lose-depth-min | packed_envelope_live_depth_minimum_lfo_approximation |
| ssr1:33 | BGM33GAMEOVER | sf1-gameover-antialias | packed_standard |
| ssr1:34 | BGM34BOSSMAE | sf1-bossmae-antialias | packed_standard |
| ssr1:35 | (empty) | empty_slot | empty_slot |
| ssr1:36 | BGM36SABISHI | sf1-sabishi-variable-late-envelope | packed_variable_late_fitted_lfo_approximation |
| ssr1:37 | BGM37MISORA | conversion_capacity_research | capacity_blocked |
| ssr2:0 | BGM_DUMMY | silent_sequence | silent_sequence |
| ssr2:1 | BGM_TEKI | existing_packing_needs_validation | packed_delayed_lfo_approximation |
| ssr2:2 | BGM_BURAI | existing_packing_needs_validation | packed_envelope_delayed_lfo_approximation |
| ssr2:3 | BGM_HOMETOWN | conversion_capacity_research | capacity_blocked |
| ssr2:4 | BGM_ROOM | existing_packing_needs_validation | packed_standard |
| ssr2:5 | BGM_SKI | existing_packing_needs_validation | packed_envelope_delayed_lfo_approximation |
| ssr2:6 | BGM_MIZUUMI | sf2-mizuumi-variable-tempo | packed_variable_tempo_lfo_approximation |
| ssr2:7 | BGM_NEWTOKYO | conversion_capacity_research | capacity_blocked |
| ssr2:8 | BGM_NAZCA | conversion_capacity_research | capacity_blocked |
| ssr2:9 | BGM_KODAI | silent_sequence | silent_sequence |
| ssr2:10 | BGM_DEMPA | conversion_capacity_research | capacity_blocked |
| ssr2:11 | BGM_DEMPAJIKEN | sf2-dempajiken-antialias-envelope | packed_envelope_approximation |
| ssr2:12 | BGM_OBAKE | conversion_capacity_research | capacity_blocked |
| ssr2:13 | BGM_YUKIOTOKO | conversion_capacity_research | capacity_blocked |
| ssr2:14 | BGM_FRIEND | existing_packing_needs_validation | packed_envelope_lfo_approximation |
| ssr2:15 | BGM_NESSIE | sf2-nessie-envelope | packed_envelope_lfo_approximation |
| ssr2:16 | BGM_KAICYOU | sf2-kaicyou-toggle | packed_envelope_live_toggle_lfo_approximation |
| ssr2:17 | BGM_SOUDOU | conversion_capacity_research | capacity_blocked |
| ssr2:18 | BGM_MU | conversion_capacity_research | capacity_blocked |
| ssr2:19 | BGM_KAKUSHI | conversion_capacity_research | capacity_blocked |
| ssr2:20 | BGM_HOKORA | sf2-hokora-merged-antialias | packed_known_nine_track_merge |
| ssr2:21 | BGM_COMICAL | existing_packing_needs_validation | packed_standard |
| ssr2:22 | BGM_JIKEN | conversion_capacity_research | capacity_blocked |
| ssr2:23 | BGM_KINCHO | conversion_capacity_research | capacity_blocked |
| ssr2:24 | BGM_KANDO | existing_packing_needs_validation | packed_standard |
| ssr2:25 | BGM_SETSUNAI | conversion_capacity_research | capacity_blocked |
| ssr2:26 | BGM_HENKAN | sf2-henkan-antialias | packed_finite_standard |
| ssr2:27 | BGM_BATTLE | sf2-battle-delay | packed_delayed_lfo_approximation |
| ssr2:28 | BGM_BOSS | conversion_capacity_research | capacity_blocked |
| ssr2:29 | BGM_LASTBOSS | conversion_capacity_research | capacity_blocked |
| ssr2:30 | BGM_WIN | sf2-win-antialias | packed_standard |
| ssr2:31 | BGM_WIN2 | sf2-win2-release-antialias | packed_finite_release_snapshots |
| ssr2:32 | BGM_LOSE | sf2-lose-mixed-depth-min | packed_mixed_envelope_live_depth_minimum_lfo_approximation |
| ssr2:33 | BGM_GAMEOVER | existing_packing_needs_validation | packed_standard |
| ssr2:34 | BGM_BOSSMAE | conversion_capacity_research | capacity_blocked |
| ssr2:35 | BGM_SKYWAVE | conversion_capacity_research | capacity_blocked |
| ssr2:36 | BGM_SABISHI | existing_packing_needs_validation | packed_variable_late_fitted_lfo_approximation |
| ssr2:37 | BGM_VS | sf2-vs-late-depth | packed_late_live_depth_lfo_approximation |
| ssr2:38 | BGM_WIFI | existing_packing_needs_validation | packed_envelope_delayed_lfo_approximation |
| ssr2:39 | BGM_HERO | silent_sequence | silent_sequence |
| ssr2:40 | BGM_NEW01 | conversion_capacity_research | capacity_blocked |
| ssr2:41 | BGM_FANFARE | conversion_capacity_research | capacity_blocked |
| ssr2:42 | BGM_BGM_CREDIT | conversion_capacity_research | capacity_blocked |
| ssr3:0 | BGM_DUMMY | silent_sequence | silent_sequence |
| ssr3:1 | BGM_HOMETOWN | conversion_capacity_research | capacity_blocked |
| ssr3:2 | BGM_ROOM | room-antialias | packed_standard |
| ssr3:3 | BGM_SPIKA | conversion_capacity_research | capacity_blocked |
| ssr3:4 | BGM_STUDIO | sf3-studio-upward-antialias | packed_known_fifteen_track_merge |
| ssr3:5 | BGM_OKINAWA | conversion_capacity_research | capacity_blocked |
| ssr3:6 | BGM_WAXA | conversion_capacity_research | capacity_blocked |
| ssr3:7 | BGM_AJITO | sf3-ajito-upward-antialias | packed_known_fourteen_track_merge |
| ssr3:8 | BGM_SCHOOL | conversion_capacity_research | capacity_blocked |
| ssr3:9 | BGM_DEMPA | conversion_capacity_research | capacity_blocked |
| ssr3:10 | BGM_HOKORA | sf3-hokora-antialias-envelope | packed_envelope_approximation |
| ssr3:11 | BGM_COSMO | conversion_capacity_research | capacity_blocked |
| ssr3:12 | BGM_NOISE | conversion_capacity_research | capacity_blocked |
| ssr3:13 | BGM_KAKUSHI | conversion_capacity_research | capacity_blocked |
| ssr3:14 | BGM_DEN_ROCKET | conversion_capacity_research | capacity_blocked |
| ssr3:15 | BGM_DEN_LIVE | conversion_capacity_research | capacity_blocked |
| ssr3:16 | BGM_DEN_KANKYO | conversion_capacity_research | capacity_blocked |
| ssr3:17 | BGM_DEN_WAXA | conversion_capacity_research | capacity_blocked |
| ssr3:18 | BGM_DEN_BURAI | conversion_capacity_research | capacity_blocked |
| ssr3:19 | BGM_DEN_CRIM | conversion_capacity_research | capacity_blocked |
| ssr3:20 | BGM_DEN_LAST | conversion_capacity_research | capacity_blocked |
| ssr3:21 | BGM_DEALER | conversion_capacity_research | capacity_blocked |
| ssr3:22 | BGM_JACK_QUEEN | conversion_capacity_research | capacity_blocked |
| ssr3:23 | BGM_NOISE_B | conversion_capacity_research | capacity_blocked |
| ssr3:24 | BGM_BURAI | existing_packing_needs_validation | packed_envelope_delayed_lfo_approximation |
| ssr3:25 | BGM_JIKEN | conversion_capacity_research | capacity_blocked |
| ssr3:26 | BGM_DEMPAJIKEN | sf3-dempajiken-merged-antialias | packed_known_eleven_track_merge |
| ssr3:27 | BGM_BOSSMAE | sf3-bossmae-merged-antialias | packed_known_twelve_track_merge |
| ssr3:28 | BGM_COMICAL | sf3-comical-antialias | packed_standard |
| ssr3:29 | BGM_FRIEND | sf3-friend-envelope | packed_envelope_lfo_approximation |
| ssr3:30 | BGM_KINCHO | sf3-kincho-upward-antialias | packed_known_ten_track_merge |
| ssr3:31 | BGM_KANDO | kando-antialias | packed_standard |
| ssr3:32 | BGM_SETSUNAI | conversion_capacity_research | capacity_blocked |
| ssr3:33 | BGM_SABISHI | sf3-sabishi-variable-late-envelope | packed_variable_late_fitted_lfo_approximation |
| ssr3:34 | BGM_REASON | conversion_capacity_research | capacity_blocked |
| ssr3:35 | BGM_BATTLE | sf3-battle-merged-antialias | packed_standard |
| ssr3:36 | BGM_BOSS | conversion_capacity_research | capacity_blocked |
| ssr3:37 | BGM_LASTBOSS | conversion_capacity_research | capacity_blocked |
| ssr3:38 | BGM_WIN | conversion_capacity_research | capacity_blocked |
| ssr3:39 | BGM_WIN2 | sf3-win2-antialias | packed_finite_standard |
| ssr3:40 | BGM_GAMEOVER | sf3-gameover-antialias | packed_standard |
| ssr3:41 | BGM_VS | conversion_capacity_research | capacity_blocked |
| ssr3:42 | BGM_LOSE | sf3-lose-depth-min | packed_live_depth_minimum_lfo_approximation |
| ssr3:43 | BGM_SHOP | conversion_capacity_research | capacity_blocked |
| ssr3:44 | (empty) | empty_slot | empty_slot |
| ssr3:45 | BGM_OMEGABOSS | conversion_capacity_research | capacity_blocked |
| ssr3:46 | (empty) | empty_slot | empty_slot |
| ssr3:47 | BGM_CHANGE | sf3-change-upward-antialias | packed_known_thirteen_track_merge |
| ssr3:48 | BGM_CREDIT | conversion_capacity_research | capacity_blocked |
| ssr3:49 | (empty) | empty_slot | empty_slot |
| ssr3:50 | BGM_DEN_WAXA2 | conversion_capacity_research | capacity_blocked |

Evidence: `out/nds-research/nds-manager-library-v14/source-coverage.json`.
SDAT hashes, stream file hashes and effect archive counts are recorded locally.
Original assets remain outside Git. The inventory adds no manual acceptance.
