from scrappers.utils.system_spec import SystemSpec
from scrappers.utils.config_reader import ConfigReader

import logging
import requests
from bs4 import BeautifulSoup as Soup
from abc import ABC, abstractmethod
from threading import Lock


class ScrapperAbstract(ABC):
    """
    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param logger: Logger => by default uses global logger from main
    """

    def __init__(self, tickers, store_location, folder_name='test_folder', file_save=False, logger=logging.getLogger("global")):
        self._tickers = tickers
        self._store_location = store_location
        self._folder_name = folder_name
        self._file_save = file_save
        self._separator = SystemSpec.get_separator()
        self._logger = logger
        self._lock = Lock()
        self._application_logic = ConfigReader(file="application_logic.json").get_configurations()

    def requester(self, url):
        """
        :param url: web url to be requested
        :return: parsed html
        """
        self._logger.info("Sending request to url: {}".format(url))

        try:
            r = requests.get(url, timeout=0.5)

            while r.status_code != 200:
                self._logger.error("Attempt failed with status code: {}. Retrying...".format(r.status_code))
                r = requests.get(url, timeout=0.5)
        except requests.exceptions.Timeout:
            self._logger.error("Attempt timed out for url: {}, retrying now...".format(url))
            return self.requester(url)

        return Soup(r.text, 'html.parser')

    @abstractmethod
    def data_parser(self, ticker):
        pass

    @abstractmethod
    def run(self):
        pass



