import time
import logging
from bot.providers.shared import *
from bot.providers.provider import Provider
from bot.providers.common import loop_scan
from bot.providers.duellinks import DuelLinksInfo


class Nox(Provider):
    root = logging.getLogger("bot.provider.Nox")

    def verify_battle(self):
        pass

    def scan_for_close(self, corr=HIGH_CORR, log=None):
        pass

    def method_name(self):
        pass

    def start_process(self):
        pass

    def is_process_running(self):
        pass

    def compare_with_back_button(self, info=None):
        pass

    def get_current_page(self, img):
        pass

    def click_auto_duel(self):
        pass

    def battle(self, CheckBattle=None, info=None):
        pass

    def check_if_battle(self, img):
        pass

    def determine_autoduel_status(self):
        pass

    def check_battle_is_running(self):
        pass

    def kill_process(self):
        pass

    def scan_for_word(self, word, corr=HIGH_CORR, log=None):
        pass

    def scan(self):
        for x, y, current_page in self.possible_battle_points():
            self.compare_with_back_button(info=None)
            time.sleep(1)
            self.tapnsleep((x, y), .5)
            img1 = self.get_img_from_screen_shot()
            battle = self.check_if_battle(img1)
            time.sleep(2.5)
            dl_info = DuelLinksInfo(x, y, current_page, "Starting Battle")
            if battle:
                self.tapnsleep((150, 400), 2.5)
                battle = self.verify_battle()
            if battle:
                self.current_battle = True
                self.root.info(battlemode % (x, y, current_page, "Starting Battle"))
                self.scan_for_word('ok', LOW_CORR)
                p, v = battle
                self.tapnsleep(p, 0)
                self.battle(self.check_battle, dl_info)
            else:
                time.sleep(2)
                loop_scan(self.compare_with_back_button, **{'info': dl_info})
                dl_info.status("failure/closeButton")
                loop_scan(self.scan_for_close, **{'info': dl_info})
                dl_info.status("success/Gift")
                loop_scan(self.scan_for_word, **{'word': 'ok', 'info': dl_info})
            time.sleep(2)
