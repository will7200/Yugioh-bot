import asyncio
import base64
import logging
import os
import subprocess
import sys
import win32gui

import cv2
import numpy as np
from skimage.measure import compare_ssim

from bot.providers import trainer_matches as tm
from bot.providers.common import loop_scan, crop_image, mask_image
from bot.providers.duellinks import DuelLinksInfo
from bot.providers.nox.predefined import NoxPredefined, duel_variant_v
from bot.providers.provider import Provider
from bot.providers.shared import *


class Nox(Provider):
    NotPath = None
    _debug = False

    def setUp(self):
        super(Nox, self).setUp()
        self.predefined = NoxPredefined(self._config, nox_current_version)
        self.NoxPath = os.path.join(self._config.get('bot', 'noxlocation'), 'Nox.exe')

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
        self.root.debug("Tapping at location ({},{})".format(x, y))
        command = "bin\\adb.exe shell input tap %d %d" % (x, y)
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
                    self.scan_for_word('ok', LOW_CORR)
                ok = self.img_to_string(img,
                                        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
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

    def __generic_wait_for__(self, message, condition_check, fn, *args, **kwargs):
        self.root.info("Waiting for {}".format(message))
        timeout = kwargs.get('timeout', 10)

        async def wait_for(self):
            exceptions_occurred = 0
            while not self.run_time.stop:
                try:
                    condition = fn(*args, **kwargs)
                except Exception as e:
                    print(e)
                    if exceptions_occurred > 5:
                        raise Exception("Maximum exception count occurred")
                    exceptions_occurred += 1
                    await self.async_wait_for_ui(1)
                    continue
                if condition_check(condition):
                    break
                await self.async_wait_for_ui(2)

        async def main(self):
            await wait_for(self)

        loop = asyncio.new_event_loop()
        task = loop.run_until_complete(asyncio.wait_for(main(self), timeout=timeout, loop=loop))
        # loop.run_until_complete(asyncio.wait_for(main(self), timeout=timeout, loop=loop))

    def __start_app__(self):
        command = "bin\\adb.exe shell monkey -p jp.konami.duellinks -c android.intent.category.LAUNCHER 1"
        self.do_system_call(command)

    def pass_through_initial_screen(self):
        self.root.info("Passing Through Start Screen")
        # TODO Check if at home screen
        self.__start_app__()
        self.__generic_wait_for__('DuelLinks Landing Page', lambda x: x is True,
                                  self.__is_initial_screen__, timeout=20)
        self.tapnsleep(self.predefined.yugioh_initiate_link, 2)
        # TODO Check for prompt
        timeout = 45
        if self.scan_for_download():
            timeout = 480
        self.__generic_wait_for__('Notifications Page', lambda x: x is True, self.wait_for_notifications,
                                  timeout=timeout)
        self.wait_for_notifications()

    def wait_for_notifications(self, *args, **kwargs):
        self.scan_for_close()
        self.wait_for_ui(1)
        self.scan_for_word(word='ok')
        self.wait_for_ui(3)
        t = self.compare_with_back_button(corr=5)
        return t

    def scan_for_download(self, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("Looking for Download Button, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 0)
        location = os.path.join(self.assets, "download_button.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def verify_battle(self):
        try_times = 3
        version = 0
        self.root.info("Verifying battle")
        while True:
            try_times -= 1
            img = self.get_img_from_screen_shot()
            if self.predefined.determine_duel_variant(img):
                pointer = duel_variant_v['v2-autoduel']
                img = img[680:710, 300:420]
                version = 2
                break
            elif try_times == 0:
                pointer = duel_variant_v['v1']
                img = img[680:710, 210:265]
                version = 1
                break

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ok = self.img_to_string(img,
                                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz").lower()
        self.root.debug("Duel-Buttons Version {}".format(version))
        if version == 1:
            if ok.startswith("due") or ok == "duel":
                return pointer, version
        if version == 2:
            if ok.startswith("auto") or 'auto' in ok:
                return pointer, version
        self.root.debug("No Auto-Duel button or Button Found")
        return None

    def scan_for_close(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 400, 500)
        location = os.path.join(self.assets, "close.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

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

    def is_street_replay(self):
        img = self.get_img_from_screen_shot()
        street_replay = self.predefined.street_replay
        img = crop_image(img, **street_replay)
        word = self.img_to_string(img, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        if 'street' in word or 'replay' in word.lower():
            return True
        return False

    def compare_with_cancel_button(self, corr=HIGH_CORR, info=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CANCEL BUTTON, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 240, 0)
        location = os.path.join(self.assets, "cancel_button.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def compare_with_back_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 150, 720)
        location = os.path.join(self.assets, "back__.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def __wrapper_kmeans_result(self, trainer, location, corr, info=None):
        if trainer.get_matches(location, corr):
            x, y = trainer.kmeans.cluster_centers_[0]
            if info:
                self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                    info.x, info.y, info.page, info.status
                ))
            self.tap(x, y)
            return True
        return False

    def get_current_page(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        area = crop_image(img, **self.predefined.page_area)
        area = mask_image([254], [255], area)
        height, width = area.shape
        current_page = 0
        for x in range(4):
            box = crop_image(area, (x * width / 4), 0, ((x + 1) * width / 4), height)
            if cv2.countNonZero(box) > 0:
                current_page = x
                break
        return current_page + 1

    def click_auto_duel(self):
        self.root.debug("AUTO-DUEL FOUND CLICKING")
        self.wait_for_ui(.1)
        self.tap(356, 85)

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
                command = "taskkill /im Nox.exe /f"
                CREATE_NO_WINDOW = 0x08000000
                subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)
        except:
            self.root.error("The program could not be killed")

    def scan_for_word(self, word, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format(word, corrword))
        if img is None:
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
            version = 0
            if battle:
                self.tapnsleep((150, 400), 2.5)
                battle, version = self.verify_battle()
            if battle:
                self.current_battle = True
                self.root.info(battlemode % (x, y, current_page, "Starting Battle"))
                self.scan_for_word('ok', LOW_CORR)
                self.tapnsleep(battle, 0)
                if version == 2:
                    self.battle(dl_info)
                else:
                    self.battle(dl_info, check_battle=True)
                self.current_battle = False
            else:
                self.wait_for_ui(2)
                if self.predefined.street_replay_location == current_page \
                        and self.is_street_replay():
                    dl_info.status = "street replay cancelling"
                    self.compare_with_cancel_button(info=dl_info)
                dl_info.status = "failure/Back-Button"
                loop_scan(self.compare_with_back_button, **{'info': dl_info})
                dl_info.status = "failure/Close-Button"
                loop_scan(self.scan_for_close, **{'info': dl_info})
                dl_info.status = "success/Gift"
                loop_scan(self.scan_for_word, **{'word': 'ok', 'info': dl_info})
            self.wait_for_ui(2)
