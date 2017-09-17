import time
import os
import traceback
import datetime
import sys
import threading
import configparser
import bot.utils as utils
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from bot.data import setDatafile, writeDatefile, readDatefile, data_object
from bot.yugioh import tapnsleep, SetupLogger, compareWithBackButton, DL_Bot
from bot.shared import defaults_config, home_location, defaultlocations

#sys.stdout = open(os.path.dirname(os.path.realpath(__file__))+'\\file1.txt', 'a')
Config = configparser.SafeConfigParser(defaults=defaults_config)
Config.read("config.ini")
root_dir = Config.get("locations", "home")
if root_dir != home_location:
    defaultlocations.newRoot(root_dir)
    Config = configparser.SafeConfigParser(defaults=defaultlocations.getdict())
    Config.read("config.ini")
log_dir = Config.get("locations", "log")
data_file = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "run_at.json")
level = Config.get("logger", "level")
root = SetupLogger(log_dir, level, stream=Config.getboolean(
    "logger", "stream"), includeap=Config.getboolean("logger", "includeapischeduler"))
setDatafile(data_file)
sched = BlockingScheduler()

eventLock = threading.Lock()


class WatchFile(PatternMatchingEventHandler):
    runnable = True
    thread = None

    def on_moved(self, event):
        super(WatchFile, self).on_moved(event)
        root.debug("File %s was just moved" % event.src_path)

    def on_created(self, event):
        super(WatchFile, self).on_created(event)
        root.debug("File %s was just created" % event.src_path)

    def on_deleted(self, event):
        super(WatchFile, self).on_deleted(event)
        root.debug("File %s was just deleted" % event.src_path)

    def on_modified(self, event):
        super(WatchFile, self).on_modified(event)
        root.debug("File %s was just modified" % event.src_path)
        if self.runnable:
            self.lock()
            self.check_runat()
            self.check_stop()
            self.scheduleunlock()

    def lock(self):
        eventLock.acquire()
        self.runnable = False
        eventLock.release()

    def unlock(self):
        eventLock.acquire()
        self.runnable = True
        eventLock.release()

    def scheduleunlock(self):
        when = datetime.datetime.now() + datetime.timedelta(seconds=4)
        sched.add_job(self.unlock, trigger='date', id='unlock_file at %s' % (
            when.isoformat()), run_date=when)

    def check_runat(self):
        next_run_at = readDatefile()
        if 'runnow' in next_run_at and next_run_at['runnow'] is True:
            root.debug("Forcing run now")
            if self.thread is None:
                sched.remove_all_jobs()
                sched.add_job(main, id='cron_main_force')
            else:
                root.debug("Thread is currently running")
            next_run_at['runnow'] = False
            writeDatefile(next_run_at)

    def check_stop(self):
        data = readDatefile()
        if self.thread is None:
            data.stop = False
            writeDatefile(data)
            return
        if 'stop' in data and data['stop'] is True:
            for x in threading.enumerate():
                if x == self.thread:
                    x.do_run = False
            root.debug("Emitting stop event")
            data.stop = False
            writeDatefile(data)
        elif 'stop' in data and data['stop'] is False:
            root.debug("Emitting resume event")

    def current_thread(self, thread):
        self.thread = thread


event_handler = WatchFile(patterns=[data_file])


def main():
    data = readDatefile()
    data.last_run_at = datetime.datetime.now()
    writeDatefile(data)
    try:
        if not utils.IsNoxRunning():
            utils.StartNoxProcess(os.path.join(
                Config.get('bot', 'noxlocation'), 'Nox.exe'))
            time.sleep(30)
            tapnsleep((25, 550), 10)
            tapnsleep((240, 540), 45)
        compareWithBackButton()
        bot = DL_Bot(sched)
        bot.Auto(event_handler.current_thread)
        if Config.getboolean("bot", "killnoxondone"):
            utils.KillNoxProcess()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
    data.next_run_at = datetime.datetime.now() + datetime.timedelta(hours=4)
    d = data.next_run_at
    writeDatefile(data)
    sched.add_job(main, trigger='date', id='cron_main_at_%s' %
                  (d.isoformat()), run_date=data.next_run_at)


def start():
    sched.start()


executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
sched.configure(executors=executors)
if __name__ == "__main__":
    t = threading.Thread(target=start, args=())
    t.start()
    next_run_at = readDatefile('next_run_at')
    if Config.getboolean("bot", "startonstartup"):
        next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
    elif next_run_at == None:
        next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
    elif datetime.datetime.now() > next_run_at:
        next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
    else:
        nextAt = next_run_at - datetime.datetime.now()
        next_run_at = datetime.datetime.now(
        ) + datetime.timedelta(seconds=nextAt.total_seconds())
    sched.add_job(main, trigger='date', id='cron_main_at_%s' %
                  (next_run_at.isoformat()), run_date=next_run_at)
    root.info("Tracking %s" % (data_file))
    root.info('Next run at %s' % (next_run_at.isoformat()))
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(
        os.path.realpath(__file__)), recursive=True)
    observer.start()
    t.join()
    #r = input("Get Some Input")
    sched.shutdown()
    observer.stop()
    sys.exit(0)
