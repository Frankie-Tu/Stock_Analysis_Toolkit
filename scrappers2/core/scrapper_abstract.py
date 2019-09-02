from scrappers2.utils.logger import Logger
from scrappers2.utils.system_spec import SystemSpec

import requests
import os
import sys
from bs4 import BeautifulSoup as Soup
from abc import ABC, abstractmethod
from threading import Lock
from time import strftime


class ScrapperAbstract(ABC):
    """
    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param start_time: strftime => start time of the application for log timestamp
    :param logger_name : String => default __name__
    """

    def __init__(self, tickers, store_location, folder_name='test_folder', file_save=False,
                 start_time=strftime("%Y-%m-%d %H.%M.%S"), logger_name=__name__):
        self._tickers = tickers
        self._store_location = store_location
        self._folder_name = folder_name
        self._file_save = file_save
        self._separator = SystemSpec.get_separator()
        self._logger = Logger(name=logger_name, start_time=start_time).get_logger()
        self._lock = Lock()

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

    def csv_writer(self, main_dir, sub, file_name, dataframe_, *dataframes):
        """
        Used to write dataframe to csv file on hard drive

        :param main_dir: root directory
        :param sub: sub structure
        :param file_name: name of the csv
        :param dataframe_: dataframe to be written to hard drive
        :param dataframes: other dataframes to be appended
        :return: None
        """
        full_path = main_dir + self._separator + sub

        # if path doesn't exist, create
        if not os.path.exists(full_path):
            self._logger.info("Os path: {} does not exist, creating one now".format(full_path))
            try:
                os.makedirs(full_path)
            except PermissionError:
                self._logger.exception("Please check if you have permission to {}".format(full_path))
                sys.exit(1)

        if len(dataframes) == 0:
            try:
                self._logger.info("Saving dataframe to path {}".format(full_path + self._separator + file_name))
                dataframe_.to_csv(full_path + self._separator + file_name)
            except IOError:
                self._logger.error("{} is in use! Result not saved.".format(full_path + self._separator + file_name))
        else: # multiple dfs passed in, appending mode
            try:
                with open(full_path + self._separator + file_name, mode='w') as file:
                    self._logger.info("Saving dataframe to path {}".format(full_path + self._separator + file_name))
                    dataframe_.to_csv(file)

                for df in dataframes:
                    with open(full_path + self._separator + file_name, mode='a') as file:
                        file.write("\n")
                        self._logger.info("Appending dataframe to path {}".format(full_path + self._separator + file_name))
                        df.to_csv(file, header=True)

            except IOError:
                self._logger.error("{} is in use! Result not saved.".format(full_path + self._separator + file_name))

    @abstractmethod
    def data_parser(self, ticker):
        pass

    @abstractmethod
    def run(self):
        pass



