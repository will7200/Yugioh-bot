import time
from abc import abstractmethod

import asyncio

from bot.shared import *


class Event(object):
    _name = None
    _args = []
    _kwargs = {}

    def __init__(self, func, *args, **kwargs):
        self._name = func
        self._args = args
        self._kwargs = kwargs

    @property
    def func(self):
        return self._name

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs


class DuelLinksInfo(object):
    _x = None
    _y = None
    _page = None
    _status = None
    _name = None

    def __init__(self, x, y, page, status):
        self._x = x
        self._y = y
        self._page = page
        self._status = status

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def page(self):
        return self._page

    @property
    def status(self):
        return self._status

    @property
    def name(self):
        return self._name

    @x.setter
    def x(self, value):
        self._x = value

    @y.setter
    def y(self, value):
        self._y = value

    @page.setter
    def page(self, value):
        self._page = value

    @status.setter
    def status(self, value):
        self._status = value

    @name.setter
    def name(self, value):
        self._name = value


class EventExecutor(object):
    def __init__(self):
        pass

    def do_event(self, _event):
        exists = getattr(self, _event.name, False)
        if exists:
            func = getattr(self, _event.name)
            if not callable(func):
                return False
            func(**_event.args)
            return True
        return False


class DuelLinks(object):
    _thread = None

    @property
    def current_thread(self):
        return self._thread

    @current_thread.setter
    def current_thread(self, thread):
        self.register_thread(thread)

    def register_thread(self, thread):
        self._thread = thread

    _auto_duel_box = None

    @property
    def auto_duel_box(self):
        "Determines the location of where the auto duel button is"
        return self._auto_duel_box

    _current_run = 0

    @property
    def current_run(self):
        return self._current_run

    @current_run.setter
    def current_run(self, run):
        self._current_run = run

    _sleep_factor = 1

    @property
    def sleep_factor(self):
        return self._sleep_factor

    @sleep_factor.setter
    def sleep_factor(self, value):
        self._sleep_factor = value

    def wait_for_ui(self, amount):
        time.sleep(amount * self.sleep_factor)

    async def async_wait_for_ui(self, amount):
        await asyncio.sleep(amount * self.sleep_factor)

    @abstractmethod
    def auto(self):
        raise NotImplementedError("auto not implemented")

    @abstractmethod
    def debug_battle(self):
        "Helps to debug when battle it not going right"
        raise NotImplementedError("debug_battle not implemented")

    @abstractmethod
    def check_battle_is_running(self):
        raise NotImplementedError("check_battle_is_running not implemented")

    @abstractmethod
    def check_battle(self):
        raise NotImplementedError("check_battle not implemented")

    @abstractmethod
    def scan(self):
        raise NotImplementedError("scan not implemented")

    @abstractmethod
    def method_name(self):
        raise NotImplementedError("method_name not implemented")

    @abstractmethod
    def compare_with_cancel_button(self, corr=HIGH_CORR, info=None, img=None):
        raise NotImplementedError("compare_with_cancel_button not implemented")

    @abstractmethod
    def compare_with_back_button(self, corr=HIGH_CORR, info=None, img=None):
        raise NotImplementedError("compare_with_back_button not implemented")

    @abstractmethod
    def scan_for_ok(self, corr=HIGH_CORR, info=None, img=None):
        raise NotImplementedError("scan_for_ok not implemented")

    @abstractmethod
    def scan_for_close(self, corr=HIGH_CORR, info=None, img=None):
        raise NotImplementedError("scan_for_close not implemented")

    @abstractmethod
    def get_current_page(self, img):
        raise NotImplementedError("get_current_image not implemented")

    @abstractmethod
    def click_auto_duel(self):
        raise NotImplementedError("click_auto_duel not implemented")

    @abstractmethod
    def determine_autoduel_status(self, img):
        raise NotImplementedError("determine_autoduel_status not implemented")

    @abstractmethod
    def battle(self, info=None, check_battle=None):
        raise NotImplementedError("battle not implemented")

    @abstractmethod
    def check_if_battle(self, img):
        raise NotImplementedError("check_if_battle not implemented")

    @abstractmethod
    def verify_battle(self, img=None, log=True):
        raise NotImplementedError("verify_battle not implemented")

    @abstractmethod
    def pass_through_initial_screen(self):
        raise NotImplementedError("pass_through_initial_screen not implemented")

    @abstractmethod
    def wait_for(self, word, try_scanning=False):
        raise NotImplementedError("wait_for not implemented")

    @abstractmethod
    def wait_for_auto_duel(self):
        raise NotImplementedError("wait_for_auto_duel not implemented")

    @abstractmethod
    def wait_for_white_bottom(self):
        raise NotImplementedError("wait for white bottom not implemented")


class DuelError(Exception):
    """Exception raised for errors in the in duel Links"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
