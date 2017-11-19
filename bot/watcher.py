import logging

import datetime
import threading

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

class WatchFile(PatternMatchingEventHandler):
    runnable = True
    thread = None
    sched = None
    eventLock = threading.Lock()
    root = logging.getLogger("bot")

    def __init__(self, scheduler, *args, *kwargs):
        self.sched = scheduler

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
        if self.runnable:
            self.lock()
            self.check_runat()
            self.check_stop()
            self.scheduleunlock()

    def lock(self):
        self.eventLock.acquire()
        self.runnable = False
        self.eventLock.release()

    def unlock(self):
        self.eventLock.acquire()
        self.runnable = True
        self.eventLock.release()

    def scheduleunlock(self):
        when = datetime.datetime.now() + datetime.timedelta(seconds=4)
        self.sched.add_job(self.unlock, trigger='date', id='unlock_file at %s' % (
            when.isoformat()), run_date=when)

    def check_runat(self):
        next_run_at = read_data_file()
        if 'runnow' in next_run_at and next_run_at['runnow'] is True:
            self.root.debug("Forcing run now")
            if self.thread is None:
                self.sched.remove_all_jobs()
                self.sched.add_job(main, id='cron_main_force')
            else:
                self.root.debug("Thread is currently running")
            next_run_at['runnow'] = False
            write_data_file(next_run_at)

    def check_stop(self):
        data = read_data_file()
        if self.thread is None:
            data.stop = False
            write_data_file(data)
            return
        if 'stop' in data and data['stop'] is True:
            for x in threading.enumerate():
                if x == self.thread:
                    x.do_run = False
            self.root.debug("Emitting stop event")
            data.stop = False
            write_data_file(data)
        elif 'stop' in data and data['stop'] is False:
            self.root.debug("Emitting resume event")