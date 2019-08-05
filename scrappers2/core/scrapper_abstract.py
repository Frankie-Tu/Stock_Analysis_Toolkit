import requests
from bs4 import BeautifulSoup as Soup

import os
import scipy.stats as ss
import pdb
import sys
import getpass
from abc import ABC, abstractmethod


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
        self._my_system = sys.platform

        if self._my_system == 'linux' or self._my_system == 'darwin':
            self._separator = "/"
        elif self._my_system == 'win32':
            self._separator = "\\"

    def requester(self, url):
        """
        :param url: web url to be requested
        :return: parsed html
        """
        r = requests.get(url, timeout=1)

        while r.status_code != 200:
            r = requests.get(url, timeout=1)

        return Soup(r.text, 'html.parser')

    def csv_writer(self, main_dir, sub, dataframe_):
        """
        Used to write dataframe to csv file on hard drive

        :param main_dir: root directory
        :param sub: sub structure, or file name
        :param dataframe_: dataframe to be written to hard drive
        :return: None
        """

        try:
            # if path doesn't exist, create
            if not os.path.exists(main_dir):
                os.makedirs(main_dir)

            dataframe_.to_csv(main_dir + self._separator + sub)
        except IOError:
            print("Please close your file!!!")

    @abstractmethod
    def data_parser(self):
        pass




