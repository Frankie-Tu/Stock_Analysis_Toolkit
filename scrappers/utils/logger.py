import logging
import sys
from time import strftime
from scrappers.utils.system_spec import SystemSpec
import os
from pathlib import Path


class Logger:

    def __init__(self, name, log_level=logging.INFO, log_format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s", file_mode='w', start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self._name = name
        self._log_level = log_level
        self._log_format = log_format
        self._file_mode = file_mode
        self._separator = SystemSpec.get_separator()
        self._start_time = start_time

    def get_logger(self):
        """
        generate logger based on config
        :return: logger: logging.Logger
        """

        handler = logging.StreamHandler(sys.stdout)

        # generate absolute path of ../logs/
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir(os.pardir)
        log_dir = os.getcwd() + self._separator + "logs"

        # if path doesn't exist, create
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = log_dir + self._separator + \
                   "ScrapperApp_{}.log".format(self._start_time)

        logging.basicConfig(filename=log_file,
                            level=self._log_level,
                            format=self._log_format,
                            filemode=self._file_mode)

        logger = logging.getLogger(self._name)
        logger.addHandler(handler)
        logger.debug("Logger created")
        logger.debug("Logger type: {}".format(type(logger)))

        if self._name == "__main__":
            logger.info("Log path: {}, mode: {}".format(log_file, self._file_mode))

        return logger
