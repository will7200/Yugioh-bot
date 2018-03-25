import os
from abc import abstractmethod
from datetime import datetime

import cv2
import numpy as np

from bot import default_timestamp
from bot.utils.data import load_dict_from_hdf5, save_dict_to_hdf5


class Predefined(object):
    _config = None
    dataset = None
    version = None
    assets = None

    def __init__(self, config, version):
        self._config = config
        self.cache_file = config.get('locations', 'cache_file')
        self.dataset = self.dataset or self.__class__.__name__
        self.assets = config.get('locations', 'assets')
        self.version = version
        self.get_cache()
        self.check_cache()

    _cache = None
    _last_read = datetime.fromtimestamp(default_timestamp)

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
            if self.dataset in self.cache.keys():
                return
            self.generate()

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

    @property
    def street_replay_location(self):
        return 4

    @property
    def quick_rankduel_location(self):
        return 2