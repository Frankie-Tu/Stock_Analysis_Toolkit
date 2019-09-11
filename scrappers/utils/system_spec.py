import sys
import getpass


class SystemSpec:

    @staticmethod
    def get_user():
        return getpass.getuser()

    @staticmethod
    def get_separator():
        _my_system = sys.platform

        if _my_system == 'linux' or _my_system == 'darwin':
            return "/"
        elif _my_system == 'win32':
            return "\\"
