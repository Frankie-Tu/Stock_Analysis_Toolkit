from scrappers2.utils.system_spec import SystemSpec
from scrappers2.utils.logger import Logger

import json
import os
from time import strftime
import sys


class ConfigReader:
    def __init__(self, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self._logger = Logger(name=__name__, start_time=start_time).get_logger()
        file_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        separator = SystemSpec().get_separator()
        self.configurations = file_root + separator + "config" + separator + "application_configurations.json"

    def get_configurations(self):
        try:
            with open(self.configurations) as file:
                self._logger.info("reading configurations from {}".format(self.configurations))
                data = json.load(file)
                return data
        except FileNotFoundError:
            self._logger.exception("configuration file: {} not found !".format(self.configurations))
            sys.exit(2)


if __name__ == "__main__":
    print(ConfigReader().get_configurations())