import os
import time
from abc import abstractmethod
from datetime import datetime

import cv2
import numpy as np

from bot.utils.data import load_dict_from_hdf5, save_dict_to_hdf5
from .shared import *


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


class Predefined(object):
    _config = None
    dataset = None
    version = None
    assets = None

    def __init__(self, config, version):
        self._config = config
        self.cache_file = config.get('locations', 'cache_file')
        self.dataset = self.__class__.__name__
        self.assets = config.get('locations', 'assets')
        self.version = version
        self.get_cache()
        self.check_cache()

    _cache = None
    _last_read = datetime.fromtimestamp(0)

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        self._last_read = datetime.now()
        self._cache = value

    def check_cache(self):
        pass

    def get_cache(self):
        if not os.path.exists(self.cache_file):
            self.generate()
        if self.cache is None:
            self.cache = load_dict_from_hdf5(self.cache_file)
            """
            self.cache = h5py.File(self.cache_file)
            if self.dataset in self.cache.keys():
                df = self.cache.get(self.dataset)
                version = df.get('version', 0)
                if version == 0 or version != self.version:
                    self.generate()
                    self.cache = h5py.File(self.cache_file)
                """

    _duel_varient = None

    @property
    def duel_variant(self):
        raise NotImplementedError("Class {} did not implement duel variant property".format(self.__class__.__name__))

    _auto_duel = None

    @property
    def autoduel(self):
        raise NotImplementedError("Class {} did not implement auto duel property".format(self.__class__.__name__))

    # TODO: IMPLEMENT METHOD TO DETERMINE THE ACCURACY OR THE LIKELHOOD THAT THIS IS AN AUTODUEL BUTTON


    def determine_autoduel_status(self, img):
        vals = self.cache.get(self.dataset)
        autodueloff = vals['auto_duel_off']
        autoduelon = vals['auto_duel_on']
        current = self.get_image_stats(img, **self.autoduel)
        dist1 = np.linalg.norm(current - autoduelon)
        dist2 = np.linalg.norm(current - autodueloff)
        if dist1 < dist2:
            return True
        return False

    def determine_duel_variant(self, img):
        vals = self.cache.get(self.dataset)
        ver_duel_variant = vals['duel_variant']
        edges = cv2.Canny(img, 240, 255)
        current = Predefined.get_image_stats(edges, **self.duel_variant)
        dist1 = np.linalg.norm(current - ver_duel_variant)
        if dist1 <= 5:
            return True
        return False

    @staticmethod
    def get_image_stats(img, left=0, top=0, width=0, height=0):
        crop_img = img[top:(top + height), left:(left + width)]
        (means, stds) = cv2.meanStdDev(crop_img)
        stats = np.concatenate([means, stds]).flatten()
        return stats

    def write_hdf5(self, data, dataset):
        data = {dataset: data}
        save_dict_to_hdf5(data, self.cache_file, mode='a')

    @abstractmethod
    def generate(self):
        raise NotImplementedError("Class {} did not implement generate".format(self.__class__.__name__))


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
        self.sleep_factor = value

    def wait_for_ui(self, amount):
        time.sleep(amount * self.sleep_factor)

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
    def compare_with_back_button(self, corr=HIGH_CORR, info=None):
        raise NotImplementedError("compare_with_back_button not implemented")

    @abstractmethod
    def scan_for_word(self, word, corr=HIGH_CORR, log=None):
        raise NotImplementedError("scan_for_work not implemented")

    @abstractmethod
    def scan_for_close(self, corr=HIGH_CORR, log=None):
        raise NotImplementedError("scan_for_close not implemented")

    @abstractmethod
    def get_current_page(self, img):
        raise NotImplementedError("get_current_image not implemented")

    @abstractmethod
    def click_auto_duel(self):
        raise NotImplementedError("click_auto_duel not implemented")

    @abstractmethod
    def determine_autoduel_status(self):
        raise NotImplementedError("determine_autoduel_status not implemented")

    @abstractmethod
    def battle(self, check_battle=None, info=None):
        raise NotImplementedError("battle not implemented")

    @abstractmethod
    def check_if_battle(self, img):
        raise NotImplementedError("check_if_battle not implemented")

    @abstractmethod
    def verify_battle(self):
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
