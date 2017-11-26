import os as _os

import cv2
import numpy as _np

from bot.providers.duellinks import Predefined
from bot.providers.shared import nox_current_version

left = 319
top = 79
width = 80
height = 23
auto_duel_box = (left, top, left + width, top + height)

duel_variant_v = {
    'v1': (230, 690),
    'v2-duel': (120, 690),
    'v2-autoduel': (290, 690)
}


class NoxPredefined(Predefined):
    def generate(self):
        save = {}
        temp_dict = self.generate_autoduel_stats()
        save = {**save, **temp_dict}
        temp_dict = self.generate_duel_button_stats()
        save = {**save, **temp_dict}
        save['version'] = nox_current_version
        self.write_hdf5(save, self.dataset)

    @property
    def autoduel(self):
        return {
            'left': 319,
            'top': 79,
            'width': 80,
            'height': 23,
        }

    @property
    def duel_variant(self):
        return {
            'left': 210,
            'top': 680,
            'width': 265 - 210,
            'height': 710 - 680
        }

    def generate_autoduel_stats(self):
        location = self.assets
        autoduelon = _os.path.join(location, "auto_duel_on.png")
        autodueloff = _os.path.join(location, "auto_duel_off.png")
        a = self.get_image_stats(cv2.imread(autodueloff), **self.autoduel)
        b = self.get_image_stats(cv2.imread(autoduelon), **self.autoduel)
        save = {
            'auto_duel_off': a,
            'auto_duel_on': b
        }
        return save

    def generate_duel_button_stats(self):
        location = self.assets
        new_duel_variant = _os.path.join(location, "new_duel_variant.png")
        im = cv2.imread(new_duel_variant, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(im, 240, 255)
        a = self.get_image_stats(_np.array(edges), **self.duel_variant)
        save = {
            'duel_variant': a
        }
        return save
