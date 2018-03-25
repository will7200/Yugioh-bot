from unittest import TestCase

import os
from watchdog.observers import Observer

from bot import last_record
from bot.utils.data import read_data_file, write_data_file, set_data_file
from bot.utils.watcher import WatchFile


class TestWatchFile(TestCase):
    """Tests for `watcher.py`."""
    watcher = None
    data_file = r"D:\Sync\OneDrive\Yu-gi-oh_bot\run_at.json"
    data = None

    def setUp(self):
        set_data_file(self.data_file)
        write_data_file({}, self.data_file)
        self.watcher = WatchFile(patterns=[self.data_file])

        def nothing_important(_):
            pass

        self.watcher.event_notification = nothing_important
        self.observer = Observer()
        self.observer.schedule(self.watcher, r"D:\Sync\OneDrive\Yu-gi-oh_bot", recursive=False)
        self.observer.start()
        self.data = read_data_file()
        self.data['test'] = 'yes'
        write_data_file(self.data, self.data_file)

    def test_notify_event(self):
        write_data_file(self.data)
        records = [str(last_record.get_record(x)) for x in range(0, 5)]
        self.assertTrue("FileModifiedEvent" in ' '.join(records), "expecting a file modification event")

    def tearDown(self):
        self.observer.stop()
        os.remove(self.data_file)
