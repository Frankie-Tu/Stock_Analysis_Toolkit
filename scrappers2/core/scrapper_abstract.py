import requests
from bs4 import BeautifulSoup as Soup

import os
import scipy.stats as ss
import pdb
import sys
import getpass
from abc import ABC, abstractmethod
from scrappers2.utils.logger import Logger
from scrappers2.utils.system_spec import SystemSpec


class ScrapperAbstract(ABC):
    """
    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    """

    def __init__(self, tickers, store_location, folder_name='test_folder', file_save=False):
        self._tickers = tickers
        self._store_location = store_location
        self._folder_name = folder_name
        self._file_save = file_save
        self._separator = SystemSpec.get_separator()
        self._logger = Logger(name=__name__).get_logger()

    def requester(self, url):
        """
        :param url: web url to be requested
        :return: parsed html
        """
        self._logger.info("Sending request to url: {}".format(url))
        r = requests.get(url, timeout=1)

        while r.status_code != 200:
            self._logger.error("Attempt failed with status code: {}. Retrying...".format(r.status_code))
            r = requests.get(url, timeout=1)

        return Soup(r.text, 'html.parser')

    def csv_writer(self, main_dir, sub, file_name, dataframe_):
        """
        Used to write dataframe to csv file on hard drive

        :param main_dir: root directory
        :param sub: sub structure, or file name
        :param dataframe_: dataframe to be written to hard drive
        :return: None
        """
        full_path = main_dir + self._separator + sub

        try:
            # if path doesn't exist, create
            if not os.path.exists(full_path):
                self._logger.info("Os path: {} does not exist, creating one now".format(full_path))
                os.makedirs(full_path)

            self._logger.info("Writing dataframe to path {}".format(full_path + self._separator + file_name))
            dataframe_.to_csv(full_path + self._separator + file_name)
        except IOError:
            self._logger.exception("Please close your file!!!")

    @abstractmethod
    def data_parser(self):
        pass




