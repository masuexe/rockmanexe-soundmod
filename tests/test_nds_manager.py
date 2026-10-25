"""Initial NDS library through real manager load/save/export and preview paths."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from manager_backend import Manager
from nds_catalog import NDS_DIRECTORY, NDS_PROFILES, NDS_SLOT_START, SONGS, identify_nds
from scan_audio import apply_bps, fingerprint
from analyze_song import analyze


def finish(manager, task):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        job = manager.job(task['job_id'])
        if job['status'] != 'running':
            if job['status'] != 'done':
                raise AssertionError(job['message'])
            return job
        time.sleep(.02)
    raise AssertionError('Manager NDS task timed out')


class NdsManagerGuardTests(unittest.TestCase):
    def test_registry_preserves_v1_slots_and_source_specific_configuration(self):
        self.assertEqual(NDS_SLOT_START, 8954)
        self.assertEqual(SONGS[:5], (
            ('ssr1', 18, 'sf1-ura-upward-antialias', 'URA', 3.5, False),
            ('ssr1', 26, 'sf1-henkan-antialias', 'HENKAN', 0, True),
            ('ssr2', 30, 'sf2-win-antialias', 'WIN', 3.5, False),
            ('ssr3', 2, 'room-antialias', 'ROOM', 3.5, False),
            ('ssr3', 35, 'sf3-battle-merged-antialias', 'BATTLE', 3.5, False)))
        self.assertEqual(len({(r[0], r[1]) for r in SONGS}), len(SONGS))
        self.assertEqual(SONGS[5:8], (
            ('ssr1', 4, 'sf1-room-antialias', 'ROOM', 3.5, False),
            ('ssr2', 26, 'sf2-henkan-antialias', 'HENKAN', 3.5, True),
            ('ssr3', 31, 'kando-antialias', 'KANDO', 3.5, False)))
        self.assertEqual(SONGS[8:], (
            ('ssr1', 6, 'sf1-school-antialias', 'SCHOOL', 3.5, False),
            ('ssr2', 31, 'sf2-win2-release-antialias', 'WIN2', 3.5, True),
            ('ssr3', 28, 'sf3-comical-antialias', 'COMICAL', 3.5, False)))

    def test_unknown_rom_and_unsupported_target_leave_state_intact(self):
        with self.assertRaises(ValueError):
            identify_nds(b'unknown revision')
        with tempfile.TemporaryDirectory() as d:
            # A CLI-started EXE6 session may leave sources without a saved target.
            (Path(d) / 'sources.json').write_text(json.dumps({'sources': ['nds-ssr1']}))
            m = Manager(d, preload=False)
            try:
                self.assertEqual(m.selected_sources, set())
                m.source_paths['nds-ssr1'] = ('source.nds', Path(d) / 'source.nds')
                revision = m.revision
                with self.assertRaisesRegex(ValueError, 'EXE6'):
                    m.select_sources(['nds-ssr1'])
                self.assertEqual(m.revision, revision)
                with self.assertRaises(ValueError):
                    m.upload('rom:nds-ssr1', 'bad.nds', b'bad')
                self.assertFalse((Path(d) / 'uploaded-roms').exists())
                self.assertEqual(m.selected_sources, set())
            finally:
                m.close()


@unittest.skipUnless((NDS_DIRECTORY / 'ssr3b.nds').exists()
                     and Path('../roms/exe6.gba').exists(), 'verified local game inputs unavailable')
class NdsManagerIntegrationTests(unittest.TestCase):
    def test_all_families_save_reload_selected_export_and_both_previews(self):
        with tempfile.TemporaryDirectory() as d:
            m = Manager(d, target='exe6')
            try:
                originals = {k: fingerprint(m.source_paths[k][1].read_bytes()) for k in NDS_PROFILES}
                finish(m, m.load(list(NDS_PROFILES) + ['exe1']))
                self.assertEqual(m.nds_cache.stats['conversions'], 0)
                self.assertEqual(m.value['nds_conversions'], [])
                self.assertFalse(any(k.startswith('nds-') for k in m.decoded[2]))
                state = m.state()
                nds = [r for r in state['catalog']['entries'] if r.get('nds_selector')]
                self.assertEqual(len(nds), 11)
                self.assertEqual(state['nds_library_song_count'], 11)
                self.assertEqual([r['target_index'] for r in nds], list(range(NDS_SLOT_START, NDS_SLOT_START + len(SONGS))))
                self.assertEqual([r['name'] for r in nds], ['URA', 'HENKAN', 'WIN', 'ROOM', 'BATTLE', 'ROOM', 'HENKAN', 'KANDO', 'SCHOOL', 'WIN2', 'COMICAL'])
                self.assertEqual([r['key'] for r in nds if r['finite_song']], ['nds-ssr1-26:26', 'nds-ssr2-26:26', 'nds-ssr2-31:31'])
                self.assertTrue(all(o['loaded'] for o in state['source_options'] if o['key'] in NDS_PROFILES))
                title, cue = nds[:2]
                project = copy.deepcopy(state['project'])
                project['pools']['1']['tracks'] = [title['key']]
                project['pools']['21']['tracks'] = [cue['key']]
                project['pools']['scene:communication']['tracks'] = [title['key']]
                project['pools']['2']['tracks'] = ['exe1:0']
                m.name(title['key'], 'My URA')
                job = finish(m, m.export(project))
                out = Path(job['result']['directory'])
                manifest = json.loads((out / 'build.json').read_text())
                rom = (out / 'unified.gba').read_bytes()
                self.assertEqual(apply_bps(m.inputs['base'][1], (out / 'unified.bps').read_bytes())[0], rom)
                self.assertEqual({x['key'] for x in manifest['imports']}, {title['key'], cue['key'], 'exe1:0'})
                self.assertEqual({x['key'] for x in manifest['nds_manager']['songs']}, {title['key'], cue['key']})
                self.assertFalse(manifest['nds_manager']['manual_acceptance_inferred'])
                self.assertEqual(manifest['nds_manager']['library_song_count'], 11)
                waves = [set(s['file_offset'] for s in analyze(rom, manifest['target_table_file_offset'], r['target_index'])['samples']) for r in (title, cue)]
                self.assertFalse(waves[0] & waves[1])
                self.assertEqual([len(w) for w in waves], [22, 2])
                saved = json.loads((out / 'project.json').read_text())
                self.assertEqual(saved['names'][title['key']], 'My URA')
                self.assertEqual(saved['pools'], project['pools'])
                self.assertEqual(m.nds_cache.stats['conversions'], 2)
                # Reload uses cached conversions but revalidates original input identities.
                with patch('nds_conversion_cache.build_experiment', side_effect=AssertionError('Unexpected conversion')):
                    finish(m, m.load(['nds-ssr1']))
                self.assertEqual(m.state()['project']['pools']['21']['tracks'], [cue['key']])
                self.assertEqual(next(r['name'] for r in m.state()['catalog']['entries'] if r['key'] == title['key']), 'My URA')
                with patch.object(m.realtime, 'start', return_value='session') as start:
                    self.assertEqual(m.live_preview(title['key']), 'session')
                    data, table, count, song, rate = start.call_args.args
                    self.assertEqual((count, song, rate), (NDS_SLOT_START + len(SONGS), title['target_index'], 48000))
                    self.assertEqual(len(analyze(data, table, song)['samples']), 22)
                def capture(data, manifest, target, directory, seconds, mgba):
                    self.assertEqual(target, cue['target_index'])
                    self.assertEqual(manifest['nds_manager']['songs'][0]['key'], cue['key'])
                    directory.mkdir()
                    wav = directory / 'preview.wav'
                    wav.write_bytes(b'test preview')
                    return wav, {'seconds': seconds}
                with patch('manager_backend.capture_preview', side_effect=capture):
                    finish(m, m.preview(cue['key'], 3))
                self.assertEqual(originals, {k: fingerprint(m.source_paths[k][1].read_bytes()) for k in NDS_PROFILES})
                other = Manager(d, target='exe6')
                try:
                    self.assertEqual(other.state()['selected_sources'], ['nds-ssr1'])
                    finish(other, other.load())
                    self.assertEqual(other.state()['project']['pools']['21']['tracks'], [cue['key']])
                    self.assertEqual(other.names[title['key']], 'My URA')
                    with patch('nds_conversion_cache.build_experiment', side_effect=AssertionError('Persistent cache missed')):
                        finish(other, other.export(other.state()['project']))
                    self.assertEqual(other.nds_cache.stats['conversions'], 0)
                    self.assertEqual(other.nds_cache.stats['disk_hits'], 2)
                finally:
                    other.close()
                changed = Path(d) / 'externally-changed.nds'
                changed.write_bytes(b'changed after catalog load')
                m.nds_sources['nds-ssr1'] = changed
                with self.assertRaisesRegex(AssertionError, 'source changed'):
                    finish(m, m.export(m.state()['project']))
                m.select_target('exegp')
                self.assertFalse(set(m.state()['selected_sources']) & NDS_PROFILES.keys())
                self.assertFalse(any(o['key'] in NDS_PROFILES for o in m.state()['source_options']))
            finally:
                m.close()

    def test_upload_and_restart_recognize_family_not_uploaded_filename(self):
        with tempfile.TemporaryDirectory() as d:
            m = Manager(d, preload=False, target='exe6')
            raw = (NDS_DIRECTORY / 'ssr1l.nds').read_bytes()
            try:
                state = m.upload('rom', 'renamed.nds', raw)
                self.assertEqual(state['added_source'], 'nds-ssr1')
                self.assertEqual(state['selected_sources'], ['nds-ssr1'])
                self.assertEqual(m.source_paths['nds-ssr1'][1].read_bytes(), raw)
                before = m.revision
                with self.assertRaises(ValueError):
                    m.upload('rom:nds-ssr2', 'wrong-family.nds', raw)
                self.assertEqual(m.revision, before)
            finally:
                m.close()
            other = Manager(d, target='exe6')
            try:
                self.assertEqual(other.state()['selected_sources'], ['nds-ssr1'])
                self.assertEqual(other.source_paths['nds-ssr1'][1].read_bytes(), raw)
            finally:
                other.close()
