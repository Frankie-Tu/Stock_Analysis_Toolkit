import requests
from bs4 import BeautifulSoup as Soup
from collections import OrderedDict
import pandas as pd
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

    def __init__(self, args, store_location, folder_name='test_folder', file_save=False):
        self._args = args
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

    @abstractmethod
    def data_parser(self):
        pass

    @abstractmethod
    def csv_writer(self):
        pass


