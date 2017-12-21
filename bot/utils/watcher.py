import logging
import os
import time
from abc import abstractmethod

import watchdog
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class WatchFile(PatternMatchingEventHandler):
    root = logging.getLogger("bot.watcher")

    def on_moved(self, event):
        super(WatchFile, self).on_moved(event)
        self.root.debug("File %s was just moved" % event.src_path)

    def on_created(self, event):
        super(WatchFile, self).on_created(event)
        self.root.debug("File %s was just created" % event.src_path)

    def on_deleted(self, event):
        super(WatchFile, self).on_deleted(event)
        self.root.debug("File %s was just deleted" % event.src_path)

    def on_modified(self, event):
        super(WatchFile, self).on_modified(event)
        self.root.debug("File %s was just modified" % event.src_path)

    def on_any_event(self, event):
        super(WatchFile, self).on_modified(event)
        self.notify_event(event)

    def notify_event(self, event):
        self.root.debug(str(event))
        self.event_notification(event)

    @abstractmethod
    def event_notification(self, event):
        raise NotImplementedError("event notification not ready")


class SyncWithFile(WatchFile):
    _observer = None

    def __init__(self, file, auto_start=False):
        self.watcher = WatchFile(patterns=[file])
        self.watcher.event_notification = self.event_notification
        self.file_observing = file
        if auto_start:
            self.start_observer()

    @property
    def observer(self):
        return self._observer

    @observer.setter
    def observer(self, observer):
        self._observer = observer

    _file_observing = None

    @property
    def file_observing(self):
        return self._file_observing

    @file_observing.setter
    def file_observing(self, value):
        self._file_observing = value

    def event_notification(self, event):
        """ HANDLES ROUTING OF WATCHDOG EVENT TYPES, SOME EDITORS MOVE TO TEMP FILES TO WRITE"""
        # TODO LP Investigate other possible file modifications
        if isinstance(event, watchdog.events.FileModifiedEvent):
            self.settings_modified(event)
        elif isinstance(event, watchdog.events.FileMovedEvent):
            if event.dest_path == self.file_observing:
                self.settings_modified(event)
        else:
            self.root.debug("Event type {} is not handled".format(type(event)))

    @abstractmethod
    def settings_modified(self, events):
        raise NotImplementedError("settings_modified not implemented")

    def start_observer(self):
        self.observer = Observer()
        self.observer.schedule(self.watcher, os.path.dirname(self.file_observing), recursive=False)
        self.observer.start()

    def stop_observer(self):
        if 'stop' in dir(self.observer):
            self.observer.stop()


if __name__ == "__main__":
    data_file = r"D:\Sync\OneDrive\Yu-gi-oh_bot\run_at.json"
    syncer = SyncWithFile(data_file, auto_start=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        syncer.stop_observer()
    syncer.observer.join()
