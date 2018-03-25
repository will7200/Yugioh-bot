import base64
import concurrent.futures
import logging
import os
import subprocess
import sys
import win32gui

import cv2
import deprecation
import numpy as np
from skimage.measure import compare_ssim

from bot import clean_version
from bot.common import loop_scan, mask_image
from bot.providers import trainer_matches as tm
from bot.providers.duellinks import DuelLinksInfo, DuelError
from bot.providers.nox.predefined import NoxPredefined
from bot.providers.provider import Provider
from bot.shared import *


class Nox(Provider):
    NotPath = None
    _debug = False

    def __init__(self, scheduler, config, run_time):
        super(Nox, self).__init__(scheduler, config, run_time)
        self.predefined = NoxPredefined(self._config, nox_current_version)
        self.NoxPath = os.path.join(self._config.get('nox', 'location'), 'Nox.exe')

    def swipe_time(self, x1, y1, x2, y2, time_amount):
        command = "bin\\adb.exe shell input swipe %d %d %d %d %d" % (
            x1, y1, x2, y2, time_amount)
        self.do_system_call(command)

    def swipe_right(self, time_sleep=0):
        self.swipe(0, 500, 100, 500)
        self.wait_for_ui(2)

    def swipe(self, x1, y1, x2, y2):
        command = "bin\\adb.exe shell input swipe %d %d %d %d " % (x1, y1, x2, y2)
        self.do_system_call(command)

    def take_png_screenshot(self):
        while True:
            try:
                command = "bin\\adb.exe shell \"screencap -p | busybox base64\""
                pcommand = os.popen(command)
                png_screenshot_data = pcommand.read()
                png_screenshot_data = base64.b64decode(png_screenshot_data)
                pcommand.close()
                break
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("[!] Failed to get screen")
        return png_screenshot_data

    def tap(self, x, y):
        self.root.debug("Tapping at location ({},{})".format(int(x), int(y)))
        command = "bin\\adb.exe shell input tap %d %d" % (int(x), int(y))
        if self._debug:
            # Helper to debug taps
            input("waiting for confirmation press enter")
        self.do_system_call(command)

    def key_escape(self):
        command = "bin\\adb.exe shell input keyevent 4"
        self.do_system_call(command)

    root = logging.getLogger("bot.provider.Nox")

    @staticmethod
    def __str__():
        return "Nox"

    def wait_for(self, word, try_scanning=False):
        self.root.info("WAITING FOR {} BUTTON TO APPEAR".format(word))
        ok = ''
        while ok != word and not self.run_time.stop:
            # root.debug("waiting for {}".format(word))
            img = self.get_img_from_screen_shot()
            img = img[745:770, 210:270]
            try:
                if try_scanning:
                    self.scan_for_ok(LOW_CORR)
                ok = self.img_to_string(img, alphabet)
            except:
                self.wait_for_ui(1)
                continue
            if ok == word:
                break
            self.wait_for_ui(2)

    def __is_initial_screen__(self, *args, **kwargs):
        original = cv2.imread(os.path.join(self.assets, "start_screen.png"))
        against = self.get_img_from_screen_shot()
        # convert the images to grayscale
        original = mask_image([127], [255], cv2.cvtColor(original, cv2.COLOR_BGR2GRAY), True)
        against = mask_image([127], [255], cv2.cvtColor(against, cv2.COLOR_BGR2GRAY), True)
        (score, diff) = compare_ssim(original, against, full=True)
        if score > .9:
            return True
        return False

    def __start_app__(self):
        command = "bin\\adb.exe shell monkey -p jp.konami.duellinks -c android.intent.category.LAUNCHER 1"
        self.do_system_call(command)

    def pass_through_initial_screen(self, already_started=False):
        self.__start_app__()
        if not already_started:
            self.root.info("Passing Through Start Screen")
        else:
            self.root.info("Checking for Start Screen")
            try:
                is_home_screen = self.__generic_wait_for__('DuelLinks Landing Page', lambda x: x is True,
                                                           self.__is_initial_screen__, timeout=4, throw=False)
            except concurrent.futures.TimeoutError:
                is_home_screen = False
            if not is_home_screen:
                return
        self.__generic_wait_for__('DuelLinks Landing Page', lambda x: x is True,
                                  self.__is_initial_screen__, timeout=20)
        self.tapnsleep(self.predefined.yugioh_initiate_link, 2)
        timeout = 45
        if self.scan_for_download():
            timeout = 480
        self.__generic_wait_for__('Notifications Page', lambda x: x is True, self.wait_for_notifications,
                                  timeout=timeout)
        self.wait_for_notifications()

    def wait_for_notifications(self, *args, **kwargs):
        self.scan_for_close()
        self.wait_for_ui(1)
        self.scan_for_ok()
        self.wait_for_ui(3)
        t = self.compare_with_back_button(corr=5)
        return t

    def scan_for_download(self, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("Looking for Download Button, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 0)
        location = os.path.join(self.assets, "download_button.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def scan_for_close(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 400, 500)
        location = os.path.join(self.assets, "close.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def method_name(self):
        super(Nox, self).method_name()

    def start_process(self):
        try:
            self.root.info("Starting Nox...")
            process = subprocess.Popen([self.NoxPath], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            self.root.critical("Nox executable not found")
            raise e
        except:
            self.root.error("The program can't run Nox")
            raise NotImplementedError

    def is_process_running(self):
        try:
            if win32gui.FindWindow(None, "Nox") or win32gui.FindWindow(None, "NoxPlayer"):
                return True
        except:
            return False

    def compare_with_cancel_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CANCEL BUTTON, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 240, 0)
        location = os.path.join(self.assets, "cancel_button.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def compare_with_back_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 150, 720)
        location = os.path.join(self.assets, "back__.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def click_auto_duel(self):
        self.root.debug("AUTO-DUEL FOUND CLICKING")
        self.wait_for_ui(.1)
        self.tap(356, 85)

    @deprecation.deprecated(deprecated_in="0.5.0", removed_in="0.6.0", current_version=clean_version,
                            details="Battle Modes are now defined separate from the provider")
    def battle(self, info=None, check_battle=False):
        "The main battle mode"
        if check_battle:
            self.wait_for_auto_duel()
            self.click_auto_duel()
        self.wait_for('OK')
        if info:
            info.status = "Battle Ended"
            self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                info.x, info.y, info.page, info.status
            ))

        self.wait_for_ui(.5)
        self.tap(*self.predefined.button_duel)
        self.wait_for('NEXT', True)
        self.tapnsleep(self.predefined.button_duel, .5)
        self.wait_for('NEXT', True)
        self.wait_for_ui(.3)
        self.tap(*self.predefined.button_duel)
        self.wait_for_white_bottom(True)
        self.wait_for_ui(.5)
        self.tapnsleep(self.predefined.button_duel, .1)
        dialog = True
        while dialog:
            dialog = self.check_if_battle(self.get_img_from_screen_shot())
            if dialog:
                self.tap(*self.predefined.button_duel)
        self.wait_for_ui(.5)
        self.scan_for_ok(LOW_CORR)
        self.wait_for_ui(.1)
        self.scan_for_ok(LOW_CORR)
        # battle_calls = self.run_time.battle_calls
        # for section in ["beforeStart", "afterStart", "beforeEnd", "afterEnd"]:
        #    for value in battle_calls.get(section):
        #        pass
        #         self.root.debug(value)

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
                command = "taskkill /im Nox.exe /f"
                CREATE_NO_WINDOW = 0x08000000
                subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)
        except:
            self.root.error("The program could not be killed")

    def scan_for_ok(self, corr=HIGH_CORR, info=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format('OK', corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 50)
        location = os.path.join(self.assets, "ok_box.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def scan(self):
        for x, y, current_page in self.possible_battle_points():
            self.compare_with_back_button(info=None)
            self.wait_for_ui(1)
            self.tapnsleep((x, y), .5)
            img1 = self.get_img_from_screen_shot()
            battle = self.check_if_battle(img1)
            self.wait_for_ui(2.5)
            dl_info = DuelLinksInfo(x, y, current_page, "Starting Battle")
            version = 0
            if battle:
                self.tapnsleep(self.predefined.dialog_ok, 2.5)
                try:
                    battle, version = self.verify_battle()
                except DuelError:
                    self.tapnsleep(self.predefined.dialog_ok, 2.5)
                    battle, version = self.verify_battle()
            if battle:
                self.current_battle = True
                self.root.info(battlemode % (x, y, current_page, "Starting Battle"))
                self.scan_for_ok(LOW_CORR)
                self.battle_mode(battle, version, dl_info)
                self.current_battle = False
            else:
                self.wait_for_ui(2)
                self.special_events(dl_info)
                dl_info.status = "failure/Back-Button"
                loop_scan(self.compare_with_back_button, **{'info': dl_info})
                dl_info.status = "failure/Close-Button"
                loop_scan(self.scan_for_close, **{'info': dl_info})
                dl_info.status = "success/Gift"
                loop_scan(self.scan_for_ok, **{'info': dl_info})
            self.wait_for_ui(2)
