from unittest import TestCase

from bot.duel_links_runtime import DuelLinkRunTimeOptions
from bot.utils.data import read_json_file, write_data_file


class TestDuelLinkRunTimeOptions(TestCase):
    def setUp(self):
        file = r'D:\Sync\OneDrive\Yu-gi-oh_bot\run_at_test.json'
        self.runtimeoptions = DuelLinkRunTimeOptions(file)


    def test_update(self):
        self.runtimeoptions.update()
        self.runtimeoptions.run_now = True
        self.runtimeoptions.dump()
        tmp_data = read_json_file(self.runtimeoptions._file)
        runtimedict = self.runtimeoptions.dump_options()
        self.assertTrue(tmp_data == runtimedict, "Expecting them to be the same")
        tmp_data['run_now'] = False
        write_data_file(tmp_data, self.runtimeoptions._file)
        self.runtimeoptions.update()
        runtimedict = self.runtimeoptions.dump_options()
        self.assertTrue(tmp_data == runtimedict, "Expecting them to be the same")

    def test_dump(self):
        self.runtimeoptions.dump()
        tmp_data = read_json_file(self.runtimeoptions._file)
        runtimedict = self.runtimeoptions.dump_options()
        self.assertTrue(tmp_data == runtimedict, "Expecting them to be the same")

    def test_runtimeerrors(self):
        self.runtimeoptions.update()
        self.runtimeoptions.stop = 'Yes'
        self.assertTrue(self.runtimeoptions.stop != 'Yes', 'Cannot change to type string')
        self.runtimeoptions.next_run_at = 'Try'
        self.assertTrue(self.runtimeoptions.next_run_at != 'Try', 'Cannot change from datetime to string')
