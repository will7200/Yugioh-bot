import base64
import logging
import os
import sys
import win32gui

import cv2
import numpy as np

from bot.providers import trainer_matches as tm
from bot.providers.common import loop_scan, crop_image, mask_image
from bot.providers.duellinks import DuelLinksInfo
from bot.providers.nox.predefined import NoxPredefined, duel_variant_v
from bot.providers.provider import Provider
from bot.providers.shared import *


class Nox(Provider):
    def setUp(self):
        super(Nox, self).setUp()
        self.predefined = NoxPredefined(self._config, nox_current_version)

    def swipe_time(self, x1, y1, x2, y2, time_amount):
        command = "bin\\adb.exe shell input swipe %d %d %d %d %d" % (
            x1, y1, x2, y2, time_amount)
        os.system(command)

    def swipe_right(self, time_sleep=0):
        self.swipe(0, 500, 100, 500)
        self.wait_for_ui(2)

    def swipe(self, x1, y1, x2, y2):
        command = "bin\\adb.exe shell input swipe %d %d %d %d " % (x1, y1, x2, y2)
        os.system(command)

    def take_png_screenshot(self):
        while True:
            try:
                command = "bin\\adb.exe shell \"screencap -p | busybox base64\""
                png_screenshot_data = os.popen(command).read()
                png_screenshot_data = base64.b64decode(png_screenshot_data)
                break
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("[!] Failed to get screen")
        return png_screenshot_data

    def tap(self, x, y):
        self.root.debug("Tapping at location ({},{})".format(x, y))
        command = "bin\\adb.exe shell input tap %d %d" % (x, y)
        os.system(command)

    def key_escape(self):
        command = "bin\\adb.exe shell input keyevent 4"
        os.system(command)

    root = logging.getLogger("bot.provider.Nox")

    @staticmethod
    def __str__():
        return "Nox"

    def wait_for(self, word, try_scanning=False):
        self.root.info("WAITING FOR {} BUTTON TO APPEAR".format(word))
        ok = ''
        while ok != word:
            # root.debug("waiting for {}".format(word))
            img = self.get_img_from_screen_shot()
            img = img[745:770, 210:270]
            try:
                if try_scanning:
                    self.scan_for_word('ok', LOW_CORR)
                ok = self.img_to_string(img,
                                        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
            except:
                self.wait_for_ui(1)
                continue
            if ok == word:
                break
            self.wait_for_ui(2)

    def pass_through_initial_screen(self):
        super(Nox, self).pass_through_initial_screen()

    def verify_battle(self):
        try_times = 3
        version = 0
        while True:
            try_times -= 1
            img = self.get_img_from_screen_shot()
            if self.predefined.determine_duel_variant(img):
                pointer = duel_variant_v['v2-autoduel']
                img = img[680:710, 300:420]
                version = 2
                break
            else:
                if try_times == 0:
                    pointer = duel_variant_v['v1']
                    img = img[680:710, 210:265]
                    version = 1

        # img = img[680:710, 90:150] new version duel
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ok = self.img_to_string(img,
                                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz").lower()
        if version == 1:
            if ok.startswith("due") or ok == "duel":
                return (pointer, version)
        if version == 2:
            if ok.startswith("auto") or 'auto' in ok:
                return (pointer, version)
        return None

    def scan_for_close(self, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 500)
        location = os.path.join(self.assets, "close.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def method_name(self):
        super(Nox, self).method_name()

    def start_process(self):
        try:
            self.root.info("Starting Nox...")
            process = os.subprocess.Popen(self.NoxPath, shell=True, stdout=os.subprocess.PIPE)
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
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def __wrapper_kmeans_result(self, trainer, location, corr, info=None):
        if trainer.getMatches(location, corr):
            x, y = trainer.kmeans.cluster_centers_[0]
            if info:
                self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                    info.x, info.y, info.page, info.status
                ))
            self.tap(x, y)
            return True
        return False

    def get_current_page(self, img):
        left = 0
        top = 775
        width = 480
        height = 25
        area = crop_image(img, left, top, width, height)
        area = mask_image([254, 254, 254], [255, 255, 255], area)
        height, width = area.shape
        current_page = 0
        for x in range(4):
            box = crop_image(area, (x * width / 4), 0, ((x + 1) * width / 4), height)
            height1, width1 = box.shape
            if (height1 * width1 - cv2.countNonZero(box)) > 0:
                current_page = x
        return current_page + 1

    def click_auto_duel(self):
        self.root.debug("AUTO-DUEL FOUND CLICKING")
        self.wait_for_ui(.1)
        self.tap(356, 85)

    def battle(self, info=None):
        "The main battle mode"
        self.wait_for('OK')
        if info:
            info.status = "Battle Ended"
            self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                info.x, info.y, info.page, info.status
            ))

        self.wait_for_ui(.5)
        self.tap(230, 750)
        self.wait_for('NEXT', True)
        self.tapnsleep((230, 750), .5)
        self.wait_for('NEXT')
        self.wait_for_ui(.3)
        self.tap(230, 750)
        self.wait_for_white_bottom(True)
        self.wait_for_ui(.5)
        self.tapnsleep((230, 750), .1)
        dialog = True
        while dialog:
            dialog = self.check_if_battle(self.get_img_from_screen_shot())
            if dialog:
                self.tap(230, 750)
        self.wait_for_ui(.5)
        self.scan_for_word('ok', LOW_CORR)
        self.wait_for_ui(.1)
        self.scan_for_word('ok', LOW_CORR)
        battle_calls = self.run_time.battle_calls
        for section in ["beforeStart", "afterStart", "beforeEnd", "afterEnd"]:
            for value in battle_calls.get(section):
                self.root.debug(value)


    def check_if_battle(self, img):
        img = np.array(img)
        img = img[750:800, 0:400]
        blue_min = np.array([250, 250, 250], np.uint8)
        blue_max = np.array([255, 255, 255], np.uint8)
        amount = cv2.inRange(img, blue_min, blue_max)
        if cv2.countNonZero(amount) > (50 * 200):
            return True
        return False

    def determine_autoduel_status(self):
        super(Nox, self).determine_autoduel_status()

    def check_battle_is_running(self):
        super(Nox, self).check_battle_is_running()

    def kill_process(self):
        try:
            if self.is_process_running():
                os.system("taskkill /im Nox.exe /f")
        except:
            self.root.error("The program could not be killed")

    def scan_for_word(self, word, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format(word, corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 50)
        location = os.path.join(self.assets, "ok_box.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def scan(self):
        for x, y, current_page in self.possible_battle_points():
            self.compare_with_back_button(info=None)
            self.wait_for_ui(1)
            self.tapnsleep((x, y), .5)
            img1 = self.get_img_from_screen_shot()
            battle = self.check_if_battle(img1)
            self.wait_for_ui(2.5)
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
                self.battle(dl_info)
            else:
                self.wait_for_ui(2)
                loop_scan(self.compare_with_back_button, **{'info': dl_info})
                dl_info.status = "failure/closeButton"
                loop_scan(self.scan_for_close, **{'info': dl_info})
                dl_info.status = "success/Gift"
                loop_scan(self.scan_for_word, **{'word': 'ok', 'info': dl_info})
            self.wait_for_ui(2)
