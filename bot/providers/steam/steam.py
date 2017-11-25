from .. import Provider
from bot.providers.shared import *


class Steam(Provider):

    @staticmethod
    def __str__():
        return "Steam"

    def verify_battle(self):
        pass

    def scan(self):
        pass

    def wait_for(self, word, try_scanning=False):
        pass

    def check_if_battle(self, img):
        pass

    def is_process_running(self):
        pass

    def determine_autoduel_status(self):
        pass

    def scan_for_word(self, word, corr=HIGH_CORR, log=None):
        pass

    def battle(self, CheckBattle=None, info=None):
        pass

    def click_auto_duel(self):
        pass

    def scan_for_close(self, corr=HIGH_CORR, log=None):
        pass

    def get_current_page(self, img):
        pass

    def compare_with_back_button(self, info=None):
        pass

    def pass_through_initial_screen(self):
        pass

    def check_battle_is_running(self):
        pass

    def start_process(self):
        pass

    def method_name(self):
        pass

    def kill_process(self):
        pass

    def swipe_time(self, x1, y1, x2, y2, time_amount):
        pass

    def key_escape(self):
        pass

    def take_png_screenshot(self):
        pass

    def swipe(self, x1, y1, x2, y2):
        pass

    def tap(self, x, y):
        pass
