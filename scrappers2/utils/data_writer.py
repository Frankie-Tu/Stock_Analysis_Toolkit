from scrappers2.utils.logger import Logger
from scrappers2.utils.system_spec import SystemSpec

import os
import sys
from time import strftime


class DataWriter:
    def __init__(self, logger=Logger(__name__, start_time=strftime("%Y-%m-%d %H.%M.%S"))):
        self._logger = logger
        self._separator = SystemSpec().get_separator()

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
