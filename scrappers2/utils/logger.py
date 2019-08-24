import logging
import sys
from time import strftime
from scrappers2.utils.system_spec import SystemSpec
import os
from pathlib import Path


class Logger:

    def __init__(self, name, log_level=logging.INFO, log_format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s", file_mode='w', start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self.name = name
        self.log_level = log_level
        self.log_format = log_format
        self.file_mode = file_mode
        self.separator = SystemSpec.get_separator()
        self.start_time = start_time

    def get_logger(self):
        """
        generate logger based on config
        :return: logger: logging.Logger
        """

        handler = logging.StreamHandler(sys.stdout)

        # generate absolute path of ../logs/
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir(os.pardir)
        log_dir = os.getcwd() + self.separator + "logs"

        # if path doesn't exist, create
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = log_dir + self.separator + \
                   "ScrapperApp_{}.log".format(self.start_time)

        logging.basicConfig(filename=log_file,
                            level=self.log_level,
                            format=self.log_format,
                            filemode=self.file_mode)

        logger = logging.getLogger(self.name)
        logger.addHandler(handler)
        logger.info("Logger created")
        logger.debug("Logger type: {}".format(type(logger)))
        logger.info("Log path: {}, mode: {}".format(log_file, self.file_mode))
        return logger
