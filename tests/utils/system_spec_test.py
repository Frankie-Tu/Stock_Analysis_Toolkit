import unittest
import getpass
import sys

from scrappers.utils.system_spec import SystemSpec


class SystemSpecTest(unittest.TestCase):
    def test_get_user(self):
        self.assertEqual(getpass.getuser(), SystemSpec.get_user())

    def test_get_separator(self):
        my_system = sys.platform
        if my_system == 'linux' or my_system == 'darwin':
            sep = "/"
        elif my_system == 'win32':
            sep = "\\"
        self.assertEqual(sep, SystemSpec.get_separator())
