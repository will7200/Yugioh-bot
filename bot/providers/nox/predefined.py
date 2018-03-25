import os as os

import cv2
import deprecation
import numpy as _np

from bot import clean_version
from bot.providers.predefined import Predefined
from bot.shared import nox_current_version, tupletodict

left = 319
top = 79
width = 80
height = 23
auto_duel_box = (left, top, left + width, top + height)

duel_variant_v = {
    'v1'         : (230, 690),
    'v2-duel'    : (120, 690),
    'v2-autoduel': (290, 690)
}


class NoxPredefined(Predefined):
    files_need = [
        "auto_duel_on.png",
        "auto_duel_off.png",
        "new_duel_variant.png"
    ]
    files_needed_for_comparision = [
        "download_button.png"
    ]

    def __init__(self, *args, **kwargs):
        super(NoxPredefined, self).__init__(*args, **kwargs)

    def run_prechecks(self):
        for file in self.files_need:
            assert (os.path.exists(os.path.join(self.assets,
                                                file))), "Missing File for stats generations: if you git cloned this repo you probably have a miss configured home!!!"

    def generate(self):
        self.run_prechecks()
        save = {}
        temp_dict = self.generate_autoduel_stats()
        save = {**save, **temp_dict}
        temp_dict = self.generate_duel_button_stats()
        save = {**save, **temp_dict}
        save['version'] = nox_current_version
        self.write_hdf5(save, self.dataset)

    @deprecation.deprecated(deprecated_in="0.3.1", removed_in="0.5.0", current_version=clean_version,
                            details="App is not opened through ADB Call instead of ui touch event")
    @property
    def yugioh_app_location(self):
        """ Note that if you don't place the app icon on the bottom left corner of a 800x480 nox emulator,
            you will need to change this """
        return 25, 550

    @property
    def yugioh_initiate_link(self):
        return 240, 530

    @property
    def autoduel(self):
        return {
            'left'  : 319,
            'top'   : 79,
            'width' : 80,
            'height': 23,
        }

    @property
    def button_duel(self):
        """Specifies the location of the button to click"""
        return 230, 750

    @property
    def duel_variant(self):
        return {
            'left'  : 210,
            'top'   : 680,
            'width' : 265 - 210,
            'height': 710 - 680
        }

    @property
    def auto_duel_location_pre(self):
        """This location points to the autoduel button before the battle starts"""
        return tupletodict(680, 300, 30, 120)

    @property
    def duel_location_pre(self):
        """This location points to the duel button before the battle starts"""
        return tupletodict(680, 210, 30, 55)

    @property
    def page_area(self):
        return {
            'left'  : 0,
            'top'   : 775,
            'width' : 480,
            'height': 25,
        }

    @property
    def dialog_ok(self):
        return 150, 400

    @property
    def street_replay(self):
        return {
            'left'  : 181,
            'top'   : 283,
            'width' : 311 - 181,
            'height': 307 - 285
        }

    @property
    def quick_rankduel_area(self):
        return tupletodict(307, 110, 25, 260)

    @property
    def duelist_name_area(self):
        return tupletodict(590, 0, 25, 150)

    @staticmethod
    def duel_variant_version(value):
        return duel_variant_v.get(value, None)

    def generate_autoduel_stats(self):
        location = self.assets
        autoduelon = os.path.join(location, "auto_duel_on.png")
        autodueloff = os.path.join(location, "auto_duel_off.png")
        a = self.get_image_stats(cv2.imread(autodueloff), **self.autoduel)
        b = self.get_image_stats(cv2.imread(autoduelon), **self.autoduel)
        save = {
            'auto_duel_off': a,
            'auto_duel_on' : b
        }
        return save

    def generate_duel_button_stats(self):
        location = self.assets
        new_duel_variant = os.path.join(location, "new_duel_variant.png")
        im = cv2.imread(new_duel_variant, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(im, 240, 255)
        a = self.get_image_stats(_np.array(edges), **self.duel_variant)
        save = {
            'duel_variant': a
        }
        return save
