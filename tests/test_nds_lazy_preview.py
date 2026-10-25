"""Slow first-use conversions do not block state/stop or start stale previews."""
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path('scripts').resolve()))
from manager_backend import Manager


class LazyPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = Manager(self.temp.name, preload=False)
        self.key = 'nds-ssr1-18:18'
        self.manager.value = {'entries':[{'key':self.key,'source':'nds-ssr1-18','source_index':18,
                                         'target_index':8954,'playlist_eligible':True,'nds_selector':'fixture'}],
                              'preview_trigger':1,'native_source':'native'}
        self.manager.decoded = (b'',b'',{},None,{})
        self.entered, self.release = threading.Event(), threading.Event()
        self.errors = []

    def tearDown(self):
        self.release.set()
        self.manager.close()
        self.temp.cleanup()

    def worker(self):
        try:
            self.manager.live_preview(self.key)
        except ValueError as error:
            self.errors.append(str(error))

    def build(self, *args):
        self.entered.set()
        if not self.release.wait(3):
            raise AssertionError('Preview fixture release timed out')
        return b'rom', {}, {'target_table_file_offset':0,'table_entry_count':9000}

    def test_stop_cancels_pending_conversion_without_holding_state_lock(self):
        with patch.object(self.manager, '_build_snapshot', side_effect=self.build), patch.object(self.manager.realtime, 'start') as start:
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.assertTrue(self.entered.wait(1))
            self.assertTrue(self.manager.lock.acquire(blocking=False))
            self.manager.lock.release()
            self.assertIsNotNone(self.manager.state()['catalog'])
            self.manager.stop_live_preview()
            self.release.set()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            start.assert_not_called()
            self.assertEqual(self.errors, ['Preview cancelled or sources changed'])

    def test_newer_preview_cannot_be_replaced_by_an_older_slow_request(self):
        calls = 0
        def build(*args):
            nonlocal calls
            calls += 1
            if calls == 1:
                return self.build(*args)
            return b'new rom', {}, {'target_table_file_offset':0,'table_entry_count':9000}
        with patch.object(self.manager, '_build_snapshot', side_effect=build), patch.object(self.manager.realtime, 'start', return_value='new session') as start:
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.assertTrue(self.entered.wait(1))
            self.assertEqual(self.manager.live_preview(self.key), 'new session')
            self.release.set()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(start.call_count, 1)
            self.assertEqual(start.call_args.args[0], b'new rom')
            self.assertEqual(self.errors, ['Preview cancelled or sources changed'])

    def test_source_selection_change_cannot_start_an_old_prepared_song(self):
        self.manager.selected_sources = {'nds-ssr1'}
        self.manager.source_paths['nds-ssr1'] = ('fixture.nds', Path(self.temp.name) / 'fixture.nds')
        with patch.object(self.manager, '_build_snapshot', side_effect=self.build), patch.object(self.manager.realtime, 'start') as start:
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.assertTrue(self.entered.wait(1))
            self.manager.select_sources([])
            self.release.set()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            start.assert_not_called()
            self.assertEqual(self.errors, ['Preview cancelled or sources changed'])
