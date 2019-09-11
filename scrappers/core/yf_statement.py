from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.config_reader import ConfigReader

import pandas as pd
from collections import OrderedDict
import numpy as np
import math
from time import strftime


class YFStatement(ScrapperAbstract):
    """
    Note: Scrap data from Financial tab

    Please input a list of stock tickers you wish to scrap.
    This class scraps data off Yahoo Finance for the tickers selected

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param statement_type: type of statement => IS, BS, CF
    :param start_time: strftime => start time of the application for log timestamp
    """

    def __init__(self, args, store_location, folder_name, file_save, statement_type, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name,
                         file_save=file_save, start_time=start_time, logger_name=__name__)
        self._statement_type = self._application_logic.get("statement").get("statement_type")
        self._statement = statement_type.upper()
        self._growth_statements = OrderedDict()  # Place holder,

    def data_parser(self, ticker):
        """
        :param ticker: String => stock symbol
        :return: None
        """

        # converts "-" to 0 and str to float, eg '123,456.789' to '123456.789'
        def convert(value2):
            if value2 == '-':
                return 0
            else:
                return float(value2.replace(',', ''))

        url = "https://ca.finance.yahoo.com/quote/" + ticker + \
              "/" + self._statement_type[self._statement] + "?p=" + ticker

        try:
            # fetch data
            self._logger.info("Sending requests for {}...".format(ticker))
            all_html = self.requester(url).find_all('table', {'class': 'Lh(1.7) W(100%) M(0)'})[0].\
                find_all(True, {'class': ['Bdbw(1px) Bdbc($c-fuji-grey-c) Bdbs(s) H(36px)', 'Bdbw(0px)! H(36px)']})

            td_list = [tr.find_all("td") for tr in all_html]

            # Date extraction
            date_list = [date.text for date in td_list[0][1:]]

            # Grab item name and its corresponding values from each year and assign into Ordered Dictionary
            item_dict = OrderedDict()
            for td in td_list[1:]:
                item_dict[td[0].text] = list(map(lambda x: x.text, td[1:]))

            # data cleaning
            row_names = list(filter(lambda x: item_dict[x], item_dict.keys()))
            result_list = []

            for item in row_names:
                result_list.append(list(map(lambda x: convert(x), item_dict[item])))

        except IndexError:
            self._logger.exception("{}: returned html not in expected format".format(ticker))
            raise IndexError

        raw_data = pd.DataFrame(result_list, index=row_names, columns=date_list)
        statement_growth = self.__growth_calculation(raw_data)

        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, ticker + "_" + self._statement + ".csv", raw_data, statement_growth)

        self._growth_statements[ticker] = statement_growth

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    @staticmethod
    def __growth_calculation(raw_data):
        """
        help calculating yoy growth for each item on the statement
        :param raw_data: raw statement data: Pandas.DataFrame
        :return: growth_statement: Pandas.DataFrame
        """
        item_name_list = list(raw_data.index)
        percentage_list_result = []

        for r in range(raw_data.shape[0]):
            percentage_list = []

            # loop to calculate YOY growth rate
            for item in [-3, -2, -1]:
                # if num2 is negative and num 1 none zero
                if raw_data.iloc[r, item] < 0 and raw_data.iloc[r, item - 1] != 0:
                    num2 = raw_data.iloc[r, item - 1]
                    num1 = raw_data.iloc[r, item]
                    percentage_list.append((num2 - num1) / np.abs(num1))
                # if num2 is positive and num1 none zero
                elif raw_data.iloc[r, item] > 0 and raw_data.iloc[r, item - 1] != 0:
                    num2 = raw_data.iloc[r, item - 1]
                    num1 = raw_data.iloc[r, item]
                    percentage_list.append((num2 - num1) / num1)
                # case where num1 or num2 is zero, append 0
                else:
                    percentage_list.append(0)
            percentage_list = percentage_list[::-1]

            # CAGR
            beg_year_value = raw_data.iloc[r, 3]
            end_year_value = raw_data.iloc[r, 0]
            # When this is the case, we do -(result)
            if beg_year_value < 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = -(math.pow(end_year_value / beg_year_value, 1 / 3) - 1)
                elif end_year_value / beg_year_value < 0:
                    cagr = -(-math.pow(abs(end_year_value / beg_year_value), 1 / 3) - 1)
            # when ths is the case, we do (result)
            elif beg_year_value > 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = math.pow(end_year_value / beg_year_value, 1 / 3) - 1
                elif end_year_value / beg_year_value < 0:
                    cagr = -math.pow(abs(end_year_value / beg_year_value), 1 / 3) - 1

            else:
                cagr = 0

            percentage_list.append(cagr)
            percentage_list_result.append(percentage_list)

        dates = list(raw_data.columns)[2::-1]
        dates.append('CAGR')

        return pd.DataFrame(percentage_list_result, index=item_name_list, columns=dates)

    def run(self):
        # parsing data from multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

    def get_statement(self, *tickers):
        if len(tickers) == 0:
            return self._growth_statements
        else:
            return_dict = OrderedDict()
            for ticker in tickers:
                return_dict[ticker] = self._growth_statements.get(ticker)
            return return_dict


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=',')

    while True:
        print(
            """
            =================================================================
            ==                  Income Statement = IS                      ==
            ==                  Balance Sheet = BS                         ==
            ==                  Cash Flow Statement = CF                   ==
            =================================================================
            """)
        user_input2 = input("Statement Type Initial: ").upper()
        if user_input2 in ('IS', 'BS', 'CF'):
            break
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")

    YFStatement(user_input, store_location=general_conf.get("store_location"),
                folder_name=config.get("statement").get(user_input2).get("folder_name"),
                file_save=general_conf.get("file_save"), statement_type=user_input2).run()
