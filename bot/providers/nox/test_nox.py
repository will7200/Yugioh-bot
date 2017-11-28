from unittest import TestCase

import os

from bot.providers import Nox
from bot.utils.common import default_config


class TestNox(TestCase):
    provider = None

    def setUp(self):
        os.environ['LOG_CFG'] = r'D:\Sync\OneDrive\Yu-gi-oh_bot\config.ini'
        self.provider = Nox(None, default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), None)

    def test_provider(self):
        with self.assertRaises(AssertionError) as context:
            provider = Nox(None, default_config(r'D:\Sync\OneDrive\Fake'), None)
        self.assertTrue('Missing File' in str(context.exception))

    def test_start_process(self):
        with self.assertRaises(FileNotFoundError) as context:
            self.provider.NoxPath = 'C:\\Nox\\Not\\Here'
            self.provider.start_process()

    def test_is_process_running(self):
        self.fail()

    def test_kill_process(self):
        self.fail()
