import os
import unittest
import bot.utils.data as data


class Data_Test(unittest.TestCase):
    """Tests for `data.py`."""

    def test_set_data_file(self):
        """tests if the path is set correctly"""
        path_to_set = "C:\\test\\random\\place\\run.json"
        data.set_data_file(path_to_set)
        self.assertTrue(path_to_set == data.data_file)


if __name__ == '__main__':
    unittest.main()
