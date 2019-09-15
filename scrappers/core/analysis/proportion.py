from scrappers.utils.logger import Logger
from scrappers.utils.config_reader import ConfigReader

from collections import OrderedDict
from time import strftime
import pandas as pd


class Proportion:
    """
        computing financial statement proportions such as the percentage of asset that is current vs fixed,
        percentage of asset owned by equity holders after all liabilities are paid off etc.

        :param statements: dict[ticker: String, : Statement: Dataframe]
        :param statement_type: type of statement => IS, BS, CF
        :param start_time: strftime => start time of the application for log timestamp
    """

    def __init__(self, statements, statement_type, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self.statements = statements
        self.statement_type = statement_type
        self.start_time = start_time
        self._logger = Logger(__name__, start_time=start_time)
        self._application_logic = ConfigReader(file="application_logic.json").get_configurations().get("proportion")

        pass

    def __income_statement(self):
        # TODO: add proportion calculation for income statement
        pass

    def __cash_flow(self):
        # TODO: add proportion calculation for cash flow statement
        pass

    def __balance_sheet(self):
        # TODO: add proportion calculation for balance statement
        pass

    def run(self):
        cases = {
            "IS": self.__income_statement,
            "CF": self.__cash_flow,
            "BS": self.__balance_sheet
        }
        return cases.get(self.statement_type)()