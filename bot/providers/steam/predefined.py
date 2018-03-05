import os as os
from enum import Enum
from inspect import getframeinfo, currentframe

import cv2
import numpy as _np

from bot.providers.predefined import Predefined
from bot.shared import nox_current_version, tupletodict

duel_variant_v = {
    'v1'         : (800, 800),
    'v2-duel'    : (640, 800),
    'v2-autoduel': (970, 800)
}


class SteamAreas(Enum):
    MAINAREA = 1
    CARDINFO = 2
    LOG = 3


class SteamPredefined(Predefined):
    files_need = [
        os.path.join("steam", "auto_duel_on.png"),
        os.path.join("steam", "auto_duel_off.png"),
        os.path.join("steam", "new_duel_variant.png")
    ]
    files_needed_for_comparision = [
    ]

    dataset = 'steam'
    
    def __init__(self, *args, **kwargs):
        super(SteamPredefined, self).__init__(*args, **kwargs)

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

    def relative_area(self, x, y, height, width, area):
        area = self.get_area(area)
        xrel, yrel = area.get('top'), area.get('left')
        return tupletodict(x + xrel, y + yrel, height, width)

    @staticmethod
    def duel_variant_version(value):
        return duel_variant_v.get(value, None)

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
        return tupletodict(107, 945, 115, 40)

    @property
    def duel_variant(self):
        return tupletodict(780, 460, 60, 680)

    @property
    def auto_duel_location_pre(self):
        """This location points to the autoduel button before the battle starts"""
        return tupletodict(790, 840, 40, 260)

    @property
    def duel_location_pre(self):
        """This location points to the duel button before the battle starts"""
        return tupletodict(790, 480, 40, 260)

    @property
    def dialog_ok(self):
        return 150, 800

    @property
    def ok_button_duel(self):
        """This specifies the location of the ok button for duels"""
        return tupletodict(855, 720, 50, 180)

    @property
    def button_duel(self):
        """Specifies the location of the button to click"""
        return 800, 870

    @property
    def resolution(self):
        return 1600, 900

    @property
    def street_replay(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def street_replay_location(self):
        """Indicates what page the street replay icon is located"""
        return 2

    @property
    def auto_duel_button(self):
        """Autoduel button during battle"""
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
        """Backlisted areas"""
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
        """Steam has button to move to right page"""
        return self.relative(655, 430, SteamAreas.MAINAREA)

    @property
    def move_left_button(self):
        """Steam has button to move to left page"""
        return self.relative(0, 430, SteamAreas.MAINAREA)

    @property
    def duelist_name_area(self):
        return self.relative_area(660, 5, 35, 150, SteamAreas.MAINAREA)
