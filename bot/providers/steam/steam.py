import logging
import os
import subprocess
import time
import win32api

import deprecation
import win32con
import win32gui
import win32ui
from ctypes import windll
from inspect import getframeinfo, currentframe

import cv2
import numpy as np
from skimage.measure import compare_ssim
from win32con import SM_CXSCREEN, SM_CYSCREEN

from bot import clean_version
from bot.providers import BotSetupError
from bot.providers import trainer_matches as tm
from bot.common import loop_scan, mask_image, crop_image, bot_assertion
from bot.providers.duellinks import DuelLinksInfo
from bot.providers.provider import Provider
from bot.shared import *
from bot.providers.steam.predefined import SteamPredefined, SteamAreas


class Steam(Provider):
    SteamPath = None
    _debug = False
    root = logging.getLogger("bot.provider.Steam")
    win_handle = 0

    @staticmethod
    def __str__():
        return "Steam"

    def __init__(self, scheduler, config, run_time, run_checks=True):
        super(Steam, self).__init__(scheduler, config, run_time)
        self.predefined = SteamPredefined(self._config, nox_current_version)
        self.SteamPath = os.path.join(self._config.get('steam', 'location'), 'Steam.exe')
        if run_checks:
            if not self.is_process_running():
                self.start_process()
                time.sleep(2)
            self.ensure_resolutions_matches()

    def __is_initial_screen__(self, *args, **kwargs):
        original = cv2.imread(os.path.join(self.assets, "home_page_steam.png"))
        against = self.get_img_from_screen_shot()
        # convert the images to grayscale
        original = mask_image([127], [255], cv2.cvtColor(original, cv2.COLOR_BGR2GRAY), True)
        against = mask_image([127], [255], cv2.cvtColor(against, cv2.COLOR_BGR2GRAY), True)
        (score, diff) = compare_ssim(original, against, full=True)
        if score > .9:
            return True
        return False

    @deprecation.deprecated(deprecated_in="0.5.0", removed_in="0.6.0", current_version=clean_version,
                            details="Battle Modes are now defined separate from the provider")
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

    def check_if_battle(self, img):
        img = np.array(img)
        img = crop_image(img, **self.predefined.page_area)
        blue_min = np.array([250, 250, 250], np.uint8)
        blue_max = np.array([255, 255, 255], np.uint8)
        amount = cv2.inRange(img, blue_min, blue_max)
        if cv2.countNonZero(amount) > (50 * 200):
            return True
        return False

    def check_battle_is_running(self):
        super(Steam, self).check_battle_is_running()

    def click_auto_duel(self):
        self.root.debug("AUTO-DUEL FOUND CLICKING")
        self.wait_for_ui(.1)
        self.tap(*self.predefined.auto_duel_button)

    def compare_with_cancel_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
        self.root.debug("LOOKING FOR CANCEL BUTTON, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.BoundingTrainer(img, bounding_area=self.predefined.main_area)
        location = os.path.join(self.assets, "cancel_button.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def compare_with_back_button(self, corr=HIGH_CORR, info=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        area = self.predefined.main_area
        area['width'] = 200
        area['top'] = 300
        t = tm.BoundingTrainer(img, bounding_area=area)
        location = os.path.join(self.assets, "back__.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def determine_autoduel_status(self, img):
        super(Steam, self).determine_autoduel_status()

    def ensure_resolutions_matches(self, img=None):
        if img is None:
            img = self.get_img_from_screen_shot()
        height, width, _ = img.shape
        height, width = height - 29, width - 6
        pre_width, pre_height = self.predefined.resolution
        bot_assertion(width == pre_width and height == pre_height, BotSetupError,
                      "Unmatched resolution of {}-{} expected {}-{}".format(width, height, pre_width, pre_height))

    def is_process_running(self):
        try:
            self.win_handle = win32gui.FindWindow(None, self.predefined.window_name)
        except:
            return False
        if self.win_handle:
            return True
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

    def pass_through_initial_screen(self, already_started=False):
        self.root.info("Passing Through Start Screen")
        if not self.__is_initial_screen__():
            return
        if self.__is_initial_screen__():
            self.__generic_wait_for__('DuelLinks Landing Page', lambda x: x is True,
                                      self.__is_initial_screen__, timeout=20)
        self.tapnsleep(self.predefined.yugioh_initiate_link, 3)
        timeout = 45
        if self.scan_for_download():
            timeout = 480
        self.__generic_wait_for__('Notifications Page', lambda x: x is True, self.wait_for_notifications,
                                  timeout=timeout)
        self.wait_for_notifications()

    def possible_battle_points(self):
        if self.run_time.stop:
            self.root.info("Received Stopping signal")
            return
        img = self.get_img_from_screen_shot()
        area = self.predefined.main_area
        area['height'] = 800
        t = tm.BoundingTrainer(img, bounding_area=area)
        t.capture_white_circles()
        current_page = self.get_current_page(img)
        logging.debug("Current-Page {}".format(current_page))
        for x, y in t.circlePoints:
            if self.run_time.stop:
                self.root.info("Received Stopping signal")
                break
            yield x, y, current_page

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
            self.root.error("The program can't run Steam")
            raise NotImplementedError

    def scan(self):
        for x, y, current_page in self.possible_battle_points():
            self.compare_with_back_button(info=None)
            self.wait_for_ui(1)
            self.tapnsleep((x, y), .5)
            img1 = self.get_img_from_screen_shot()
            battle = self.check_if_battle(img1)
            self.wait_for_ui(2)
            dl_info = DuelLinksInfo(x, y, current_page, "Starting Battle")
            version = 0
            if battle:
                self.tapnsleep(self.predefined.dialog_ok, 2.5, True)
                battle, version = self.verify_battle()
            if battle:
                self.current_battle = True
                self.root.info(battlemode % (x, y, current_page, "Starting Battle"))
                self.scan_for_ok(LOW_CORR)
                self.battle_mode(battle, version, dl_info)
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
                loop_scan(self.scan_for_ok, **{'info': dl_info})
            self.wait_for_ui(2)

    def scan_for_ok(self, corr=HIGH_CORR, info=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format('OK', corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        area = self.predefined.main_area
        area['width'] = 400
        t = tm.BoundingTrainer(img, bounding_area=area)
        location = os.path.join(self.assets, "ok_box.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def scan_for_close(self, corr=HIGH_CORR, info=None, img=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
        if img is None:
            img = self.get_img_from_screen_shot()
        area = self.predefined.main_area
        area['width'] = 400
        t = tm.BoundingTrainer(img, bounding_area=area)
        location = os.path.join(self.assets, "close.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def scan_for_download(self, corr=HIGH_CORR, info=None):
        corrword = look_up_translation_correlation(corr)
        self.root.debug("Looking for Download Button, {} CORRERLATION".format(corrword))
        img = self.get_img_from_screen_shot()
        t = tm.BoundingTrainer(img, 500, 300, 600, 300)
        location = os.path.join(self.assets, "download_button.png")
        return self.__wrapper_kmeans_result__(t, location, corr, info)

    def swipe_right(self, time_sleep=1):
        self.tap(*self.predefined.move_right_button)
        self.wait_for_ui(time_sleep)

    def swipe_left(self, time_sleep=1):
        self.tap(*self.predefined.move_left_button)
        self.wait_for_ui(time_sleep)

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
        img_str = cv2.imencode('.jpg', img)[1].tostring()
        return img_str

    def __calculate_absolute_coordinates__(self, x, y):
        width, height = win32api.GetSystemMetrics(SM_CXSCREEN), win32api.GetSystemMetrics(SM_CYSCREEN)
        x = (x * 65536)
        y = (y * 65536)
        return int(x / width), int(y / height)

    def tap_relative(self, x, y, area=SteamAreas.MAINAREA, time_sleep=0):
        area = self.predefined.get_area(area)
        xrel, yrel = area.get('left'), area.get('top')
        self.tap(x + xrel, y + yrel)
        if time_sleep > 0:
            self.wait_for_ui(time_sleep)

    def tapnsleep(self, point, time_sleep, relative=False):
        x, y = point
        if relative:
            self.tap_relative(x, y, SteamAreas.MAINAREA)
        else:
            self.tap(x, y)
        self.wait_for_ui(time_sleep)

    def tap(self, x, y):
        if self.run_time.stop:
            return
        x, y = int(x), int(y)
        self.root.debug("Tapping at location ({},{})".format(x, y))
        if self._debug:
            # Helper to debug taps
            input("waiting for confirmation press enter")
        ox, oy = win32api.GetCursorPos()
        curr_window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(self.win_handle, win32con.SW_RESTORE)
        x, y = int(x), int(y)
        cx, cy = win32gui.ClientToScreen(self.win_handle, (x, y))
        x, y = self.__calculate_absolute_coordinates__(cx, cy)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                             x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(20 / 1000)
        win32api.SetCursorPos((ox, oy))
        win32gui.SetActiveWindow(curr_window)

    def wait_for(self, word, try_scanning=False):
        self.root.info("WAITING FOR {} BUTTON TO APPEAR".format(word))
        ok = ''
        word = word.lower()
        while ok != word and not self.run_time.stop:
            img = self.get_img_from_screen_shot()
            img = crop_image(img, **self.predefined.ok_button_duel)
            try:
                if try_scanning:
                    self.scan_for_ok(LOW_CORR)
                ok = self.img_to_string(img, alphabet).lower()
            except:
                self.wait_for_ui(1)
                continue
            if ok == word:
                break
            self.wait_for_ui(2)

    def wait_for_notifications(self, *args, **kwargs):
        self.scan_for_close()
        self.wait_for_ui(1)
        self.scan_for_ok()
        self.wait_for_ui(3)
        t = self.compare_with_back_button(corr=5)
        return t
