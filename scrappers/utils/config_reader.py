from scrappers.utils.system_spec import SystemSpec
from scrappers.utils.logger import Logger

import json
import os
from time import strftime
import sys


class ConfigReader:
    """
    read user configurations

    :param start_time: strftime => start time of the application for log timestamp
    :param file: string => name of the configuration file in config/
    """
    def __init__(self, start_time=strftime("%Y-%m-%d %H.%M.%S"), file="application_configurations.json"):
        self._logger = Logger(name=__name__, start_time=start_time).create_logger()
        file_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        separator = SystemSpec().get_separator()
        self.configurations = file_root + separator + "config" + separator + file

    def get_configurations(self):
        try:
            with open(self.configurations) as file:
                self._logger.debug("reading configurations from {}".format(self.configurations))
                data = json.load(file)
                return data
        except FileNotFoundError:
            self._logger.exception("configuration file: {} not found !".format(self.configurations))
            sys.exit(2)


if __name__ == "__main__":
    print(ConfigReader().get_configurations())