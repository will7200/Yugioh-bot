import asyncio
import concurrent
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import os

from duel_links_runtime import DuelLinkRunTime
from providers import Steam
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

    def test_battle(self):
        self.fail()

    def test_check_if_battle(self):
        self.fail()

    def test_check_battle_is_running(self):
        self.fail()

    def test_click_auto_duel(self):
        self.fail()

    def test_compare_with_back_button(self):
        self.fail()

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
        self.fail()

    def test_scan_for_close(self):
        self.fail()

    def test_scan_for_download(self):
        self.fail()

    def test_swipe_right(self):
        self.fail()

    def test_swipe_time(self):
        self.fail()

    def test_swipe(self):
        self.fail()

    def test_tap(self):
        self.fail()

    def test_verify_battle(self):
        self.fail()

    def test_wait_for(self):
        self.fail()

    def test_wait_for_notifications(self):
        self.fail()

