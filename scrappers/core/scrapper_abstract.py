from scrappers.utils.system_spec import SystemSpec
from scrappers.utils.config_reader import ConfigReader

import logging
import requests
from bs4 import BeautifulSoup as Soup
from abc import ABC, abstractmethod
from threading import Lock
from typing import Union


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
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

        try:
            r = requests.get(url, timeout=2, headers=headers)

            while r.status_code != 200:
                self._logger.error("Attempt failed with status code: {}. Retrying...".format(r.status_code))
                r = requests.get(url, timeout=2)
        except requests.exceptions.Timeout:
            self._logger.error("Attempt timed out for url: {}, retrying now...".format(url))
            return self.requester(url)

        return Soup(r.text, 'html.parser')
    
    @abstractmethod
    def parse_rows(self, body: str):
        pass

    @abstractmethod
    def data_parser(self, ticker):
        pass

    @abstractmethod
    def run(self):
        pass



