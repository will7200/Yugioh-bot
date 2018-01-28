from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import asyncio

import os

import cv2

from duel_links_runtime import DuelLinkRunTime
from modes.Battle import VagabondBattle
from providers import Nox
from providers.duellinks import DuelLinksInfo
from utils.common import default_config


class TestVagabondBattle(TestCase):
    def setUp(self):
        os.environ['LOG_CFG'] = r'D:\Sync\OneDrive\Yu-gi-oh_bot\config.ini'
        dlRuntime = DuelLinkRunTime(default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), None, False)
        dlRuntime._disable_dump = True
        self.provider = Nox(None, default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), dlRuntime)
        self.provider.sleep_factor = 0.0
        loop = asyncio.get_event_loop()
        loop.set_default_executor(ThreadPoolExecutor(2))
        self.battler = VagabondBattle(self.provider)

    def test_check_battle(self):
        img = cv2.imread(os.path.join(self.provider.assets, 'new_duel_variant.png'))
        vaga_img = cv2.imread(os.path.join(self.provider.assets, "nox", "vagabond.png"))
        info = DuelLinksInfo(0, 0, 2, "battle mode")
        self.assertTrue(self.battler.check_battle(info, img) is False, "Name is not vagabond")
        self.assertTrue(self.battler.check_battle(info, vaga_img) is True, "Name is vagabond")
        self.assertTrue(info.name == 'vagabond')
