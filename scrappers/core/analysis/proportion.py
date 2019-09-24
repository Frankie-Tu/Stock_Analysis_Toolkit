from scrappers.utils.logger import Logger
from scrappers.utils.config_reader import ConfigReader
from scrappers.utils.data_writer import DataWriter

from collections import OrderedDict
from time import strftime
import pandas as pd
from pdb import set_trace


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
        self._logger = Logger(__name__, start_time=start_time).get_logger()
        self._application_logic = ConfigReader(file="application_logic.json").get_configurations().get("proportion")

        pass

    def __income_statement(self):
        # TODO: add proportion calculation for income statement

        agg = self._application_logic.get("agg")
        plus = self._application_logic.get("plus")
        minus = self._application_logic.get("minus")
        all_items = []
        all_items.extend(plus.copy())
        all_items.extend(minus.copy())
        statement_abstract = OrderedDict()

        for ticker in self.statements.keys():
            statement = self.statements.get(ticker)
            for row in all_items:
                statement.loc[row] = statement.loc[row] / statement.loc[agg]
            statement.loc[all_items] = statement.loc[all_items].applymap(lambda x: round(x*100, 2))
            statement_abstract[ticker] = statement.loc[all_items]
        # TODO: examine proportion trends for cost and income
        DataWriter(self._logger).csv_writer("/home/frankie/repos/Stock_Analysis_Toolkit/tests", "proportions", "test.csv",
                                            **statement_abstract)

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