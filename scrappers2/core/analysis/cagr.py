from scrappers2.core.yf_statement import YFStatement
from scrappers2.utils.logger import Logger

from collections import OrderedDict
from time import strftime


class CAGR:
    """
    :param args: list[String] => list of ticker names
    :param statement_type: type of statement => IS, BS, CF
    :param start_time: strftime => start time of the application for log timestamp
    """
    def __init__(self, args, statement_type, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self.args = args
        self.statement_type = statement_type
        self.start_time = start_time
        self._logger = Logger(__name__, start_time=start_time)

    def run(self):
        pass
