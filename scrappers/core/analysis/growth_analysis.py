from scrappers.utils.config_reader import ConfigReader

import logging
from collections import OrderedDict
import pandas as pd
import math
import numpy as np
from pdb import set_trace


class CAGR:
    """
    fetching important cagr items from the statements

    :param statements: dict[ticker: String, Statement: Dataframe]
    :param statement_type: type of statement => IS, BS, CF
    :param logger: Logger => by default uses global logger from main
    """
    def __init__(self, statements, statement_type, logger=logging.getLogger("global")):
        self.statements = statements
        self.statement_type = statement_type
        self._logger = logger
        self._application_logic = ConfigReader(file="application_logic.json").get_configurations().get("cagr")

    def __income_statement(self):
        """
        returns average of net income and dataframe of cagr for net income, profit and revenue

        :return: [{ticker, average cagr}, dataframe}
        """
        cagr_avg_dict = OrderedDict()
        cagr_dict = OrderedDict()
        average_income_columns = self._application_logic.get("average_net_income")
        all_income_columns = self._application_logic.get("all_income")

        for ticker in self.statements.keys():

            statement = self.statements.get(ticker).filter(average_income_columns, axis=0)
            #set_trace()
            cagr_avg_dict[ticker] = (statement["CAGR"].iloc[0] + statement["CAGR"].iloc[1]) / 2

            # CAGR for net income to compare with different tickers
            statement = self.statements.get(ticker).filter(all_income_columns, axis=0)

            # append average cagr to list
            cagr_dict[ticker] = list(statement["CAGR"])

        return cagr_avg_dict, pd.DataFrame(cagr_dict, index=all_income_columns)

    def __cash_flow(self):
        # TODO: add cagr logic for cash flow statement
        pass

    def __balance_sheet(self):
        # TODO: add cagr logic for balance sheet
        pass

    def run(self):
        cases = {
            "IS": self.__income_statement,
            "CF": self.__cash_flow,
            "BS": self.__balance_sheet
        }
        return cases.get(self.statement_type)()


class YoYGrowth:

    @staticmethod
    def growth_calculation(raw_data):
        """
        help calculating yoy growth for each item on the statement.
        computing compounded annual growth rate between reference year and latest year
        Only works with even number of years.
        TODO: add support for odd number of years
        :param raw_data: raw statement data: Pandas.DataFrame
        :return: growth_statement: Pandas.DataFrame
        """
        item_name_list = list(raw_data.index)
        percentage_list_result = []
        num_years = raw_data.shape[1]

        for r in range(raw_data.shape[0]):
            percentage_list = []

            # loop to calculate YOY growth rate. start from 2 to skip ttm
            for year in range(2, num_years):
                # if num2 is negative and num 1 none zero. num1 is base year
                if raw_data.iloc[r, year] < 0 and raw_data.iloc[r, year - 1] != 0:
                    num2 = raw_data.iloc[r, year - 1]
                    num1 = raw_data.iloc[r, year]
                    percentage_list.append((num2 - num1) / np.abs(num1))
                # if num2 is positive and num1 none zero
                elif raw_data.iloc[r, year] > 0 and raw_data.iloc[r, year - 1] != 0:
                    num2 = raw_data.iloc[r, year - 1]
                    num1 = raw_data.iloc[r, year]
                    percentage_list.append((num2 - num1) / num1)
                # case where num1 or num2 is zero, append 0
                else:
                    percentage_list.append(0)
            percentage_list = percentage_list[::-1]

            # CAGR
            beg_year_value = raw_data.iloc[r, 3]
            end_year_value = raw_data.iloc[r, 1]
            # When this is the case, we do -(result)
            if beg_year_value < 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = -(math.pow(end_year_value / beg_year_value, 1 / 2) - 1)
                elif end_year_value / beg_year_value < 0:
                    cagr = -(-math.pow(abs(end_year_value / beg_year_value), 1 / 2) - 1)
            # when ths is the case, we do (result)
            elif beg_year_value > 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = math.pow(end_year_value / beg_year_value, 1 / 2) - 1
                elif end_year_value / beg_year_value < 0:
                    cagr = 0
            else:
                cagr = 0

            percentage_list.append(cagr)
            percentage_list_result.append(percentage_list)

        dates = list(raw_data.columns)[2:][::-1]
        dates.append('CAGR')

        return pd.DataFrame(percentage_list_result, index=item_name_list, columns=dates)
