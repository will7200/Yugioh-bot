import os as os
from inspect import getframeinfo, currentframe

import cv2
from enum import Enum
import deprecation
import numpy as _np

from bot import clean_version
from bot.providers.duellinks import Predefined
from bot.providers.shared import nox_current_version

duel_variant_v = {
    'v1'         : (800, 800),
    'v2-duel'    : (640, 800),
    'v2-autoduel': (970, 800)
}


class SteamAreas(Enum):
    MAINAREA = 1
    CARDINFO = 2
    LOG = 3


def tupletodict(top, left, height, width):
    return {
        'top'   : top,
        'left'  : left,
        'width' : width,
        'height': height
    }


# TODO HP Implement Steam Predifined
class SteamPredefined(Predefined):
    files_need = [
    ]
    files_needed_for_comparision = [
    ]

    dataset = 'Steam'

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
        self.write_hdf5(save, 'steam')

    def generate_autoduel_stats(self):
        location = self.assets
        autoduelon = os.path.join(location, "steam", "auto_duel_on.png")
        autodueloff = os.path.join(location, "steam", "auto_duel_off.png")
        a = self.get_image_stats(cv2.imread(autodueloff), **self.autoduel)
        b = self.get_image_stats(cv2.imread(autoduelon), **self.autoduel)
        save = {
            'auto_duel_off': a,
            'auto_duel_on' : b
        }
        return save

    def generate_duel_button_stats(self):
        location = self.assets
        new_duel_variant = os.path.join(location, "steam", "new_duel_variant.png")
        im = cv2.imread(new_duel_variant, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(im, 240, 255)
        a = self.get_image_stats(_np.array(edges), **self.duel_variant)
        save = {
            'duel_variant': a
        }
        return save

    def get_area(self, area):
        return {
            SteamAreas.MAINAREA: self.main_area,
            SteamAreas.CARDINFO: self.card_info_area,
            SteamAreas.LOG     : self.log_area
        }[area]

    def relative(self, x, y, area):
        area = self.get_area(area)
        xrel, yrel = area.get('left'), area.get('top')
        return x + xrel, y + yrel

    @property
    def window_name(self):
        return "Yu-Gi-Oh! DUEL LINKS"

    @property
    def window_exe_name(self):
        return "dlpc.exe"

    @property
    def steam_url_start(self):
        return "steam://rungameid/601510"

    @property
    def yugioh_initiate_link(self):
        return 800, 650

    @property
    def autoduel(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def duel_variant(self):
        return {}

    @property
    def auto_duel_location_pre(self):
        return tupletodict(790, 840, 40, 260)

    @property
    def street_replay(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def street_replay_location(self):
        return 2

    @property
    def auto_duel_button(self):
        return self.relative(600, 100, area=SteamAreas.MAINAREA)

    @property
    def page_area(self):
        return {
            'left'  : 464,
            'top'   : 866,
            'width' : 678,
            'height': 50
        }

    _main_area = {}

    @property
    def main_area(self):
        return {
            'left'  : 464,
            'top'   : 25,
            'width' : 678,
            'height': None
        }

    _card_info_area = {}

    @property
    def card_info_area(self):
        return {
            'left'  : 1142,
            'top'   : 25,
            'width' : 1604 - 1142,
            'height': None
        }

    _log_area = {}

    @property
    def log_area(self):
        return {
            'left'  : 0,
            'top'   : 25,
            'width' : 462,
            'height': None
        }

    @property
    def backlist(self):
        return [
            {'left'  : 450,
             'top'   : 415,
             'width' : 62,
             'height': 110},
            {'left'  : 1090,
             'top'   : 425,
             'width' : 62,
             'height': 110}
        ]

    @property
    def move_right_button(self):
        return self.relative(655, 430, SteamAreas.MAINAREA)

    @property
    def move_left_button(self):
        return self.relative(0, 430, SteamAreas.MAINAREA)
