from scrappers.core.yf_statement import YFStatement
from scrappers.utils.logger import Logger
from scrappers.utils.config_reader import ConfigReader

from collections import OrderedDict
from time import strftime
import pandas as pd


class CAGR:
    """
    :param args: list[String] => list of ticker names
    :param statement_type: type of statement => IS, BS, CF
    :param start_time: strftime => start time of the application for log timestamp
    """
    def __init__(self, statements, statement_type, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        self.statements = statements
        self.statement_type = statement_type
        self.start_time = start_time
        self._logger = Logger(__name__, start_time=start_time)
        self._application_logic = ConfigReader(file="application_logic.json").get_configurations().get("cagr")

    def __income_statement(self):
        cagr_avg_dict = OrderedDict()
        cagr_dict = OrderedDict()
        average_income_columns = self._application_logic.get("average_net_income")
        all_income_columns = self._application_logic.get("all_income")

        for ticker in self.statements.keys():

            statement = self.statements.get(ticker).filter(average_income_columns, axis=0)

            # CAGR for net income to compare with different tickers
            statement = self.statements.get(ticker).filter(all_income_columns, axis=0)

            # append average cagr to list
            cagr_avg_dict[ticker] = (statement.iloc[0, 3] + statement.iloc[1, 3])/2
            cagr_dict[ticker] = list(statement.iloc[:, 3])

        return cagr_avg_dict, pd.DataFrame(cagr_dict, index=all_income_columns)

    def __cash_flow(self):
        print("cash_flow")

    def __balance_sheet(self):
        print("balance_sheet")

    def run(self):
        cases = {
            "IS": self.__income_statement,
            "CF": self.__cash_flow,
            "BS": self.__balance_sheet
        }
        return cases.get(self.statement_type)()
