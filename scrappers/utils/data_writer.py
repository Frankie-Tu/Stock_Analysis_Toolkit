from scrappers.utils.logger import Logger
from scrappers.utils.system_spec import SystemSpec

import os
import sys
import logging
from time import strftime


class DataWriter:
    def __init__(self, logger=logging.getLogger("global")):
        self._logger = logger
        self._separator = SystemSpec().get_separator()

    def csv_writer(self, main_dir, sub, file_name, *dataframes, **dataframes_dict):
        """
        Used to write dataframe to csv file on hard drive

        :param main_dir: root directory
        :param sub: sub structure
        :param file_name: name of the csv
        :param dataframes: dataframes
        :param dataframes_dict: dict{ticker, dataframe}
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

        if len(dataframes) != 0:
            try:
                self._logger.info("Saving dataframe to path {}".format(full_path + self._separator + file_name))
                with open(full_path + self._separator + file_name, mode='w') as file:
                    for df in dataframes:
                        file.write("\n")
                        df.to_csv(file, header=True, lineterminator='\n')
            except IOError:
                self._logger.error("{} is in use! Result not saved.".format(full_path + self._separator + file_name))
            
            except Exception as e:
                self._logger.exception(e)

        if len(dataframes_dict.keys()) != 0:
            try:
                self._logger.info("Saving dataframe to path {}".format(full_path + self._separator + file_name))
                with open(full_path + self._separator + file_name, mode='w') as file:
                    for ticker in dataframes_dict.keys():
                        file.write("\n{}\n".format(ticker))
                        dataframes_dict.get(ticker).to_csv(file, header=True, line_terminator='\n')
            except IOError:
                self._logger.error("{} is in use! Result not saved.".format(full_path + self._separator + file_name))
