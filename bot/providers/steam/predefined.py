import os as os
from inspect import getframeinfo, currentframe

import cv2
import deprecation
import numpy as _np

from bot import clean_verison
from bot.providers.duellinks import Predefined
from bot.providers.shared import nox_current_version

duel_variant_v = {

}


# TODO HP Implement Steam Predifined
class SteamPredefined(Predefined):
    files_need = [
    ]
    files_needed_for_comparision = [
    ]

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
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def autoduel(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def duel_variant(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def street_replay(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    @property
    def street_replay_location(self):
        return 2

    @property
    def page_area(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    def generate_autoduel_stats(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    def generate_duel_button_stats(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))
