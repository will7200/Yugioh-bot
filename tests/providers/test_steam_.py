import asyncio
import concurrent
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import os

import cv2

from providers import trainer_matches as tm
from duel_links_runtime import DuelLinkRunTime
from providers import Steam
from providers.common import crop_image
from providers.shared import alpha_numeric, alphabet
from utils.common import default_config


class TestSteam(TestCase):
    provider = None
    __debug_pictures__ = False

    images_needed_debug = [
        "street_replay.png",
        "home_page_steam.png"
    ]

    def setUp(self):
        os.environ['LOG_CFG'] = r'D:\Sync\OneDrive\Yu-gi-oh_bot\config.ini'
        dlRuntime = DuelLinkRunTime(default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), None, False)
        self.provider = Steam(None, default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), dlRuntime)
        self.provider.sleep_factor = 0.0
        self.loop = asyncio.get_event_loop()
        self.loop.set_default_executor(ThreadPoolExecutor(2))
        dlRuntime._loop = self.loop
        self.provider.is_process_running()
        os.chdir(r'..\..')

    def test_battle(self):
        self.fail()

    def test_check_if_battle(self):
        location = os.path.join(self.provider.assets, "steam", "steam_pre_battle.png")
        img = cv2.imread(location)
        self.assertTrue(self.provider.check_if_battle(img), "Is Battle")

    def test_check_battle_is_running(self):
        self.fail()

    def test_click_auto_duel(self):
        self.provider.click_auto_duel()

    def test_compare_with_back_button(self):
        img = os.path.join(self.provider.assets, "steam", "steam_back.png")
        t = tm.BoundingTrainer(img, bounding_area=self.provider.predefined.main_area)
        location = os.path.join(self.provider.assets, "back__.png")
        # t.show_area_bounded(self.provider.predefined.main_area, img)
        # t._debug = True
        self.assertTrue(t.get_matches(location, 3) is True, "Expecting a back button")
        # t.compare()

    def test_determine_autoduel_status(self):
        self.fail()

    def test_is_process_running(self):
        self.fail()

    def test_key_escape(self):
        self.fail()

    def test_kill_process(self):
        self.fail()

    def test_method_name(self):
        self.fail()

    def test_pass_through_initial_screen(self):
        self.provider.is_process_running()
        test_function = lambda x: x is False
        with self.assertRaises(Exception) as context:
            self.provider.__generic_wait_for__('DuelLinks Landing Page', test_function,
                                               None)
        self.assertTrue('Maximum exception count' in str(context.exception))
        self.provider.sleep_factor = 0.5
        self.assertTrue(callable(self.provider.__is_initial_screen__))
        with self.assertRaises(concurrent.futures._base.TimeoutError) as context:
            self.provider.__generic_wait_for__('DuelLinks Landing Page', test_function,
                                               self.provider.__is_initial_screen__, timeout=5)

    def test_start_process(self):
        self.fail()

    def test_scan(self):
        self.fail()

    def test_scan_for_word(self):
        img = os.path.join(self.provider.assets, "steam", "steam_back.png")
        t = tm.BoundingTrainer(img, bounding_area=self.provider.predefined.main_area)
        location = os.path.join(self.provider.assets, "back__.png")
        # t.show_area_bounded(self.provider.predefined.main_area, img)
        # t._debug = True
        self.assertTrue(t.get_matches(location, 3) is True, "Expecting a back button")
        # t.compare()

    def test_scan_for_close(self):
        img = os.path.join(self.provider.assets, "steam", "steam_close.png")
        area = self.provider.predefined.main_area
        area['width'] = 400
        t = tm.BoundingTrainer(img, bounding_area=area)
        location = os.path.join(self.provider.assets, "close.png")
        # t.show_area_bounded(self.provider.predefined.main_area, img)
        # t._debug = True
        self.assertTrue(t.get_matches(location, 3) is True, "Expecting a back button")
        img = os.path.join(self.provider.assets, "steam", "steam_ok.png")
        t = tm.BoundingTrainer(img, bounding_area=area)
        location = os.path.join(self.provider.assets, "close.png")
        t.get_matches(location, 3)
        # t.show_area_bounded(self.provider.predefined.main_area, img)
        # t._debug = True
        self.assertTrue(t.get_matches(location, 3) is False, "Is Ok button not close")

    def test_scan_for_ok(self):
        img = os.path.join(self.provider.assets, "steam", "steam_ok.png")
        t = tm.BoundingTrainer(img, bounding_area=self.provider.predefined.main_area)
        location = os.path.join(self.provider.assets, "ok_box.png")
        # t.show_area_bounded(self.provider.predefined.main_area, img)
        # t._debug = True
        self.assertTrue(t.get_matches(location, 3) is True, "Expecting a back button")
        # t.compare()

    def test_scan_for_download(self):
        img = os.path.join(self.provider.assets, "steam", "download_update.png")
        t = tm.BoundingTrainer(img, 500, 300, 600, 300)
        location = os.path.join(self.provider.assets, "download_button.png")
        # t.show_area(500, 300, 600, 300, img)
        self.assertTrue(t.get_matches(location, 3) is True, "Expecting a download button")

    def test_swipe_right(self):
        self.fail()
        # self.provider.swipe_right(0)

    def test_swipe_left(self):
        self.fail()
        # self.provider.swipe_left(0)

    def test_swipe_time(self):
        self.fail()

    def test_swipe(self):
        self.fail()

    def test_tap(self):
        x, y = self.provider.predefined.yugioh_initiate_link
        self.provider.tap(x, y)

    def test_verify_battle(self):
        location = os.path.join(self.provider.assets, "steam", "duel_variant_autoduel.png")
        img = cv2.imread(location)
        points, version = self.provider.verify_battle(img)
        self.assertTrue(version == 2)

    def test_wait_for(self):
        location = os.path.join(self.provider.assets, "steam", "ok_button_duel.png")
        img = cv2.imread(location)
        img = crop_image(img, **self.provider.predefined.ok_button_duel)
        word = self.provider.img_to_string(img, alphabet).lower()
        self.assertTrue(word == 'ok')

    def test_wait_for_notifications(self):
        self.fail()

    def test_battle_icons(self):
        self.provider.is_process_running()
        img = self.provider.get_img_from_screen_shot()
        area = self.provider.predefined.main_area
        area['height'] = 700
        t = tm.BoundingTrainer(img, bounding_area=area)
        t.capture_white_circles()
