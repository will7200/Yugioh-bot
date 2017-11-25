import base64
import time
import logging
import numpy as np
import cv2

import win32gui

import os

from bot.providers.shared import *
from bot.providers.provider import Provider
from bot.providers.common import loop_scan
from bot.providers.duellinks import DuelLinksInfo
from bot.providers import trainer_matches as tm

class Nox(Provider):

    def setUp(self):
        pass
    def swipe_time(self, x1, y1, x2, y2, time):
        Command = "bin\\adb.exe shell input swipe %d %d %d %d %d" % (
            x1, y1, x2, y2, time)
        os.system(Command)

    def swipe_right(self, time_sleep=0):
        pass

    def swipe(self, x1, y1, x2, y2):
        Command = "bin\\adb.exe shell input swipe %d %d %d %d " % (x1, y1, x2, y2)
        os.system(Command)

    def take_png_screenshot(self):
        while True:
            try:
                Command = "bin\\adb.exe shell \"screencap -p | busybox base64\""
                PngScreenshotData = os.popen(Command).read()
                PngScreenshotData = base64.b64decode(PngScreenshotData)
                break
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("[!] Failed to get screen")
        return PngScreenshotData

    def tap(self, x, y):
        self.root.debug("Tapping at location ({},{})".format(x, y))
        Command = "bin\\adb.exe shell input tap %d %d" % (x, y)
        os.system(Command)

    def key_escape(self):
        Command = "bin\\adb.exe shell input keyevent 4"
        os.system(Command)

    root = logging.getLogger("bot.provider.Nox")

    @staticmethod
    def __str__():
        return "Nox"

    def wait_for(self, word, try_scanning=False):
        pass

    def pass_through_initial_screen(self):
        pass

    def verify_battle(self):
        pass

    def scan_for_close(self, corr=HIGH_CORR, log=None):
        pass

    def method_name(self):
        pass

    def start_process(self):
        try:
            self.root.info("Starting Nox...")
            process = os.subprocess.Popen(self.NoxPath, shell=True, stdout=subprocess.PIPE)
        except:
            self.root.error("The program can't run Nox")

    def is_process_running(self):
        try:
            if win32gui.FindWindow(None, "Nox"):
                return True
        except:
            return False

    def compare_with_back_button(self, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 150, 720)
        location = os.path.join(self.assets, "back__.png")
        self.root.debug(location)
        if t.getMatches(location, corr):
            x, y = t.kmeans.cluster_centers_[0]
            if info:
                self.root.debug("NPC Battle Mode,Points: (%d,%d) at location: (%d), message: %s".format(
                    info.x, info.y, info.page, info.status
                ))
            self.tap(x, y)
            return True
        return False

    def get_current_page(self, img):
        pass

    def click_auto_duel(self):
        pass

    def battle(self, CheckBattle=None, info=None):
        pass

    def check_if_battle(self, img):
        img = np.array(img)
        img = img[750:800, 0:400]
        BLUE_MIN = np.array([250, 250, 250], np.uint8)
        BLUE_MAX = np.array([255, 255, 255], np.uint8)
        amount = cv2.inRange(img, BLUE_MIN, BLUE_MAX)
        if cv2.countNonZero(amount) > (50 * 200):
            return True
        return False

    def determine_autoduel_status(self):
        pass

    def check_battle_is_running(self):
        pass

    def kill_process(self):
        try:
            if self.is_process_running():
                os.system("taskkill /im Nox.exe /f")
        except:
            self.root.error("The program could not be killed")

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
                dl_info.status = "failure/closeButton"
                loop_scan(self.scan_for_close, **{'info': dl_info})
                dl_info.status = "success/Gift"
                loop_scan(self.scan_for_word, **{'word': 'ok', 'info': dl_info})
            time.sleep(2)
