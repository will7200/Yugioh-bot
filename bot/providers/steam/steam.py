import logging
from ctypes import windll
from inspect import getframeinfo, currentframe

import os
import subprocess

import cv2
import numpy as np
import win32gui

import time

import win32ui
from skimage.measure import compare_ssim

from bot.providers import trainer_matches as tm
from bot.providers.steam.predefined import SteamPredefined, duel_variant_v
from bot.providers.provider import Provider
from bot.providers.shared import *
from providers.common import loop_scan, mask_image, crop_image
from providers.duellinks import DuelLinksInfo


class Steam(Provider):
    SteamPath = None
    _debug = False
    root = logging.getLogger("bot.provider.Steam")
    win_handle = 0

    @staticmethod
    def __str__():
        return "Steam"

    def __init__(self, scheduler, config, run_time):
        super(Steam, self).__init__(scheduler, config, run_time)
        self.predefined = SteamPredefined(self._config, nox_current_version)
        self.SteamPath = os.path.join(self._config.get('steam', 'location'), 'Steam.exe')

    def __is_initial_screen__(self, *args, **kwargs):
        ### TODO Change Picture
        original = cv2.imread(os.path.join(self.assets, "start_screen.png"))
        against = self.get_img_from_screen_shot()
        # convert the images to grayscale
        original = mask_image([127], [255], cv2.cvtColor(original, cv2.COLOR_BGR2GRAY), True)
        against = mask_image([127], [255], cv2.cvtColor(against, cv2.COLOR_BGR2GRAY), True)
        (score, diff) = compare_ssim(original, against, full=True)
        if score > .9:
            return True
        return False

    def battle(self, info=None, check_battle=None):
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
        ## TODO Change Image Coordinates
        img = np.array(img)
        img = img[750:800, 0:400]
        blue_min = np.array([250, 250, 250], np.uint8)
        blue_max = np.array([255, 255, 255], np.uint8)
        amount = cv2.inRange(img, blue_min, blue_max)
        if cv2.countNonZero(amount) > (50 * 200):
            return True
        return False

    def check_battle_is_running(self):
        super(Steam, self).check_battle_is_running()

    def click_auto_duel(self):
        ## TODO Change Coordinates
        self.root.debug("AUTO-DUEL FOUND CLICKING")
        self.wait_for_ui(.1)
        self.tap(356, 85)

    def compare_with_back_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 150, 720)  ## TODO Change Cuttoff parameters
        location = os.path.join(self.assets, "back__.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def determine_autoduel_status(self, img):
        super(Steam, self).determine_autoduel_status()

    def is_process_running(self):
        try:
            self.win_handle = win32gui.FindWindow(None, self.predefined.window_name)
            if self.win_handle:
                return True
        except:
            return False

    def key_escape(self):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    def kill_process(self):
        try:
            if self.is_process_running():
                command = "taskkill /im {} /f".format(self.predefined.window_exe_name)
                CREATE_NO_WINDOW = 0x08000000
                subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)
        except:
            self.root.error("The program could not be killed")

    def method_name(self):
        super(Steam, self).method_name()

    def pass_through_initial_screen(self):
        self.root.info("Passing Through Start Screen")
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

    def start_process(self):
        try:
            self.root.info("Starting Steam...")
            process = subprocess.Popen([self.SteamPath, self.predefined.steam_url_start], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            time.sleep(1)
            self.is_process_running()
        except FileNotFoundError as e:
            self.root.critical("Steam executable not found")
            raise e
        except:
            self.root.error("The program can't run Nox")
            raise NotImplementedError

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

    def scan_for_word(self, word, corr=HIGH_CORR, log=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format(word, corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 50)  ## TODO Change Cuttoff parameters
        location = os.path.join(self.assets, "ok_box.png")
        return self.__wrapper_kmeans_result(t, location, corr, log)

    def scan_for_close(self, corr=HIGH_CORR, log=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 400, 500)  ## TODO Change Cuttoff parameters
        location = os.path.join(self.assets, "close.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def scan_for_download(self, corr=HIGH_CORR, info=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("Looking for Download Button, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img, 480, 0)  ## TODO Change Cuttoff parameters
        location = os.path.join(self.assets, "download_button.png")
        return self.__wrapper_kmeans_result(t, location, corr, info)

    def swipe_right(self, time_sleep=0):
        pass

    def swipe_time(self, x1, y1, x2, y2, time_amount):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    def swipe(self, x1, y1, x2, y2):
        raise NotImplementedError("Function {} has not been implemented".format(getframeinfo(currentframe())[2]))

    def take_png_screenshot(self):
        if not self.win_handle:
            raise Exception("Win handle is not valid for Steam")
        # Crops the image from the desktop
        left, top, right, bottom = win32gui.GetWindowRect(self.win_handle)
        width = right - left
        height = bottom - top
        hwnd_dc = win32gui.GetWindowDC(self.win_handle)
        # Get a bitmap
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bit_map = win32ui.CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bit_map)
        result = windll.user32.PrintWindow(self.win_handle, save_dc.GetSafeHdc(), 0x00000002)
        if result != 1:
            raise Exception("Failed to Steam screen")
        bmp_info = save_bit_map.GetInfo()
        bmp_raw = save_bit_map.GetBitmapBits(False)
        img = np.array(bmp_raw, np.uint8).reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)
        # Clean Up
        win32gui.DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.win_handle, hwnd_dc)
        return img


    def tap(self, x, y):
        self.root.debug("Tapping at location ({},{})".format(x, y))
        # command = "bin\\adb.exe shell input tap %d %d" % (x, y)
        if self._debug:
            # Helper to debug taps
            input("waiting for confirmation press enter")
        self.do_system_call(command)

    def verify_battle(self):
        try_times = 3
        version = 0
        self.root.info("Verifying battle")
        while True:
            try_times -= 1
            img = self.get_img_from_screen_shot()
            if self.predefined.determine_duel_variant(img):
                pointer = duel_variant_v['v2-autoduel']
                ## TODO Change Duel Coordinates
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

    def wait_for_notifications(self, *args, **kwargs):
        self.scan_for_close()
        self.wait_for_ui(1)
        self.scan_for_word(word='ok')
        self.wait_for_ui(3)
        t = self.compare_with_back_button(corr=5)
        return t
