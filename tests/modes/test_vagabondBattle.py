from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import asyncio

import os

import cv2

from bot.duel_links_runtime import DuelLinkRunTime
from bot.modes.Battle import VagabondBattle, NPCBattle
from bot.providers import Nox, Steam
from bot.providers.duellinks import DuelLinksInfo
from bot.utils.common import default_config


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
        dlRuntime = DuelLinkRunTime(default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), None, False)
        self.provider_steam = Steam(None, default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), dlRuntime, False)
        self.provider_steam.sleep_factor = 0.0
        self.battler_steam = VagabondBattle(self.provider_steam)
        self.battler_npc_steam = NPCBattle(self.provider_steam)

    def test_check_battle(self):
        img = cv2.imread(os.path.join(self.provider.assets, 'new_duel_variant.png'))
        vaga_img = cv2.imread(os.path.join(self.provider.assets, "nox", "vagabond.png"))
        info = DuelLinksInfo(0, 0, 2, "battle mode")
        self.assertTrue(self.battler.check_battle(info, img) is False, "Name is not vagabond")
        self.assertTrue(self.battler.check_battle(info, vaga_img) is True, "Name is vagabond")
        self.assertTrue(info.name == 'vagabond')
        img = cv2.imread(os.path.join(self.provider_steam.assets, 'steam', 'new_duel_variant.png'))
        self.assertTrue(self.battler_steam.check_battle(info, img) is False, "Name is not vagabond")
        self.assertTrue(self.battler_npc_steam.check_battle(info, img) is True, "NPC battle")
        self.assertTrue(info.name == 'emma')
