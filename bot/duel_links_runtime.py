import asyncio
import concurrent
import inspect
import os
import pathlib

import datetime
import threading
import traceback
from abc import abstractmethod

import sys

from bot import logger
from bot.debug_helpers import calling_function
from bot.debug_helpers.helpers_decorators import async_calling_function

from bot.utils.data import read_json_file, write_data_file
from bot.utils.watcher import SyncWithFile


class DuelLinkRunTimeOptions(object):
    # TODO HP all setters persist to file
    _last_run_at = datetime.datetime.fromtimestamp(0)

    @property
    def last_run_at(self):
        return self._last_run_at

    @last_run_at.setter
    def last_run_at(self, value):
        if not isinstance(value, datetime.datetime):
            self.runtime_error_options("last_run_at", datetime.datetime, type(value))
            return
        if self._last_run_at == value:
            return
        self._last_run_at = value
        frame = inspect.currentframe()
        logger.info("Value {} modified to {}".format(inspect.getframeinfo(frame).function, value))
        self.timeout_dump()

    _next_run_at = datetime.datetime.fromtimestamp(0)

    @property
    def next_run_at(self):
        return self._next_run_at

    @next_run_at.setter
    def next_run_at(self, value):
        if not isinstance(value, datetime.datetime):
            self.runtime_error_options("next_run_at", datetime.datetime, type(value))
            return
        if self._next_run_at == value:
            return
        self._next_run_at = value
        # IMPLEMENTATION: Notify Scheduler of next run
        frame = inspect.currentframe()
        logger.info("Value {} modified to {}".format(inspect.getframeinfo(frame).function, value))
        self.timeout_dump()

    _run_now = False

    @property
    def run_now(self):
        return self._run_now

    @run_now.setter
    def run_now(self, value):
        if not isinstance(value, bool):
            self.runtime_error_options("run_now", bool, type(value))
            return
        if self._run_now == value:
            return
        self._run_now = value
        # IMPLEMENTATION: Notify Scheduler to Run Now
        frame = inspect.currentframe()
        logger.info("Value {} modified".format(inspect.getframeinfo(frame).function))
        self.timeout_dump()

    _stop = False

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, stop):
        if not isinstance(stop, bool):
            self.runtime_error_options("stop", bool, type(stop))
            return
        if self._stop == stop:
            return
        self._stop = stop
        frame = inspect.currentframe()
        logger.info("Value {} modified".format(inspect.getframeinfo(frame).function))
        self.timeout_dump()
        # IMPLEMENTATION: Notify Scheduler to Stop Now

    @abstractmethod
    def runtime_error_options(self, option, expecting_type, got_type):
        raise NotImplementedError("runtime_error_options not implemented")

    @abstractmethod
    def timeout_dump(self):
        raise NotImplementedError("timeout_dump not implemented")


class DuelLinkRunTime(DuelLinkRunTimeOptions):
    _file = None
    _unknown_options = []
    _scheduler = None
    _config = None
    _watcher = None
    _timeout_dump = None
    _executor = None
    _task = None
    _provider = None
    _loop = None

    def __init__(self, config, scheduler):
        self._config = config
        self._file = config.get('bot', 'runTimePersistence')
        self._scheduler = scheduler

        self.setUp()
        logger.debug("Watching {} for runTime Options".format(self._file))
        self._watcher = SyncWithFile(self._file, True)
        self._watcher.settings_modified = self.settings_modified
        self.dump()
        # scheduler.add_job(self.dump, 'interval', minutes=1)

    def setUp(self):
        self._loop = asyncio.get_event_loop()
        self._task = asyncio.Task(self.periodic())
        if os.path.dirname(self._file) == "":
            self._file = os.path.join(os.getcwd(), self._file)
        pathlib.Path(os.path.dirname(self._file)).mkdir(parents=True, exist_ok=True)

    def get_provider(self):
        return self._provider

    def set_provider(self, provider):
        self._provider = provider

    def looper(self):
        try:
            self._loop.run_until_complete(self._task)
        except asyncio.CancelledError:
            pass

    def settings_modified(self, events):
        # logger.debug(events)
        self.update()

    def update(self):
        self._unknown_options = []
        tmp_data = read_json_file(self._file)
        if tmp_data is None:
            self.dump()
            return
        for key, value, in tmp_data.items():
            if key.startswith('_'):
                continue
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self._unknown_options.append(key)
        if len(self._unknown_options) > 0:
            logger.debug("Unknown options were passed in [{}]".format(','.join(self._unknown_options)))

    def dump_options(self):
        tmpdict = {}
        for attribute in [a for a in dir(self) if not a.startswith('__') \
                and not a.startswith('_') \
                and not inspect.ismethod(getattr(self, a))
        and not inspect.isfunction(getattr(self, a))]:
            # print(attribute, type(getattr(self,attribute)))
            tmpdict[attribute] = getattr(self, attribute)
        return tmpdict

    @async_calling_function(2)
    def dump(self):
        # TODO signal observer to turn off and then turn on again
        self._watcher.stop_observer()
        tmpdict = self.dump_options()
        logger.debug("Dump Getting Called", tmpdict)
        write_data_file(tmpdict, self._file)
        self._watcher.start_observer()

    def timeout_dump(self):
        if isinstance(self._timeout_dump, asyncio.TimerHandle):
            self._timeout_dump.cancel()
        self._timeout_dump = self._loop.call_later(5, self.dump)
        logger.debug("Timeout dump Scheduled")

    @staticmethod
    def runtime_error(message):
        logger.error(
            "Runtime error: {}".format(message)
        )

    def runtime_error_options(self, option, expecting_type, got_type):
        mess = "option {} has wrong type associated with it. Fix it, no events will be notified.".format(option)
        self.runtime_error(mess)
        mess = "option {} expecting {} but got {}".format(option, expecting_type, got_type)
        self.runtime_error(mess)

    def schedule_next_run(self):
        pass

    def main(self):
        def schedule_shutdown():
            self._scheduler.shutdown()

        def thread_shutdown():
            self.shutdown()
            schedule_shutdown()
            print('done')

        def in_main():
            self.last_run_at = datetime.datetime.now()
            provider = self.get_provider()
            try:
                if not provider.is_process_running():
                    provider.start_process()
                    provider.wait_for_ui(30)
                    provider.pass_through_initial_screen()
                provider.compare_with_back_button()
                logger.info("main event")
                provider.auto()
            except NotImplementedError as ee:
                logger.error(ee)
                logger.fatal("Provider does not have method correctly implemented cannot continue")
                tt = threading.Thread(target=thread_shutdown, args=())
                tt.start()  # (schedule_shutdown, args=(), id='shutdown')
                return
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(traceback.format_exc())
            self.next_run_at = datetime.datetime.now() + datetime.timedelta(hours=4)
            self._scheduler.add_job(in_main, trigger='date', id='cron_main_at_{}'.format(self.next_run_at.isoformat()),
                                    run_date=self.next_run_at)

        self._scheduler.add_job(self.looper, args=(), id="looper")
        if self._config.getboolean("bot", "startBotOnStartUp"):
            self.next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        elif self.next_run_at == datetime.datetime.fromtimestamp(0):
            self.next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        elif datetime.datetime.now() > self.next_run_at:
            self.next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        else:
            next_at = self.next_run_at - datetime.datetime.now()
            self.next_run_at = datetime.datetime.now(
            ) + datetime.timedelta(seconds=next_at.total_seconds())
        self._scheduler.add_job(in_main, trigger='date', id='cron_main_at_%s' %
                                                            (self.next_run_at.isoformat()), run_date=self.next_run_at)
        logger.info("Tracking %s" % (self._file))
        logger.info('Next run at %s' % (self.next_run_at.isoformat()))

    @asyncio.coroutine
    def periodic(self):
        while True:
            yield from asyncio.sleep(1)

    _shutdown = False
    def shutdown(self):
        self._shutdown = True
        self._task.cancel()

    def __del__(self):
        self.dump()
