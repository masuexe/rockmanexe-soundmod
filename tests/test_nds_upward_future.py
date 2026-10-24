"""Future pitch bounds must protect tails/loops without filtering expired intro bends."""
import sys
import unittest
from pathlib import Path

sys.path[:0] = [str(Path('scripts').resolve()), str(Path('tests').resolve())]
from nds_track_merge import convert_merged_song, upward_pitch_bound_after_first_use
from nds_music import SoundArchive, nds_sdat
from build_nds_experiment import build_experiment, SOURCE_ARCHIVES
from test_nds_upward_antialias import archive, score


def action(tick, bend, bend_range=12):
    return {'ticks': tick, 'state_after': {'bend': bend, 'bend_range': bend_range}}


class FuturePitchBoundsTests(unittest.TestCase):
    def test_expired_intro_does_not_filter_a_later_sample(self):
        track = {'termination': 'loop', 'loop_action': 2,
                 'actions': [action(0, 83), action(9, 0), action(20, 0), action(40, 0)]}
        self.assertEqual(upward_pitch_bound_after_first_use(track, 20), 0)
        self.assertEqual(upward_pitch_bound_after_first_use(track, 0), 498)

    def test_later_bend_is_retained_even_after_note_off(self):
        track = {'termination': 'loop', 'loop_action': 3,
                 'actions': [action(0, 0), action(10, 0), action(100, 83), action(120, 0)]}
        # A note at10 can release before100, but an arbitrarily long tail may remain.
        self.assertEqual(upward_pitch_bound_after_first_use(track, 10), 498)

    def test_earlier_recurring_bend_can_affect_the_next_iteration(self):
        track = {'termination': 'loop', 'loop_action': 1,
                 'actions': [action(0, 0), action(10, 83), action(20, 0), action(40, 0)]}
        self.assertEqual(upward_pitch_bound_after_first_use(track, 20), 498)
        self.assertEqual(upward_pitch_bound_after_first_use(track, 400), 498)

    def test_held_pitch_at_note_start_is_not_omitted(self):
        track = {'termination': 'loop', 'loop_action': 2,
                 'actions': [action(0, 83), action(10, 83), action(30, 0)]}
        self.assertEqual(upward_pitch_bound_after_first_use(track, 10), 498)

    def test_opt_in_and_key_ceiling_remain_required(self):
        with self.assertRaisesRegex(ValueError, 'explicit singleton'):
            convert_merged_song(archive(score()), 0, [(0,)], bandlimited_upward_future_support=True)
        with self.assertRaisesRegex(ValueError, 'explicit singleton'):
            convert_merged_song(archive(score()), 0, [(0, 1)], bandlimited_pcm=True,
                                bandlimited_upward_support=True, bandlimited_upward_future_support=True)
        with self.assertRaisesRegex(ValueError, 'one-octave/key range'):
            convert_merged_song(archive(score(bend=127, key=120)), 0, [(0,)], bandlimited_pcm=True,
                                bandlimited_upward_support=True, bandlimited_upward_future_support=True)

    def test_default_mode_still_uses_the_whole_track_bound(self):
        _, _, old = convert_merged_song(archive(score()), 0, [(0,)], bandlimited_pcm=True,
                                        bandlimited_upward_support=True)
        self.assertNotIn('future_use_pitch_bounds', old['bandlimited_pcm'])
        self.assertNotIn('earliest_use_ticks_by_source_track', old['samples'][0]['resampling'])
        self.assertEqual(old['samples'][0]['resampling']['positive_pitch_bound_units'], 396)

    @unittest.skipUnless(Path('/home/harp/projects/nds/roms/ssr1d.nds').exists()
                         and Path('../roms/exe6.gba').exists(), 'local verified game inputs unavailable')
    def test_satellite_third_accent_uses_its_future_pitch_not_an_expired_intro(self):
        source = Path('/home/harp/projects/nds/roms/ssr1d.nds').read_bytes()
        _, _, _, c, *_ = build_experiment(source, Path('../roms/exe6.gba').read_bytes(),
                                          song='sf1-satellite-upward-antialias')
        a = SoundArchive(nds_sdat(source, SOURCE_ARCHIVES['ssr1']['file_id']))
        bank, ids = a.bank(c['sequence_info']['bank_id'])
        definition = a.note_definition(bank, 54, 91)
        sample = next(s for s in c['samples'] if
                      (s['archive_id'], s['wave_id'], s['root_key'], s['source_key']) ==
                      (ids[definition.archive_slot], definition.wave_id, definition.root_key, 91))
        self.assertTrue(c['bandlimited_pcm']['future_use_pitch_bounds'])
        self.assertEqual(sample['resampling']['positive_pitch_bound_units'], 0)
        self.assertEqual(sample['resampling']['preparation_key'], 91)
        self.assertEqual(sample['resampling']['earliest_use_ticks_by_source_track'], {'3': 2256})
        self.assertEqual([(n['tick'], n['source_key'], n['duration']) for n in c['note_mapping']
                          if n['source_track'] == 3 and 2160 <= n['tick'] <= 2304
                          and n['source_velocity'] == 105],
                         [(2160, 88, 12), (2208, 89, 12), (2256, 91, 12), (2304, 88, 12)])
