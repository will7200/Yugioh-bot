import os
import unittest
from bot.debug_helpers import calling_function, last_record


class HelpersTest(unittest.TestCase):
    """Tests for `debug helpers folder`."""

    def test_calling_function(self):
        self.fake_calling_function()
        self.assertTrue('fake_calling_function' in last_record.get_record())

    @calling_function
    def call_function(self):
        do_nothing = None
        return

    def fake_calling_function(self):
        self.call_function()
        return


if __name__ == '__main__':
    unittest.main()
