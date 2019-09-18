from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.core.analysis.growth_analysis import YoYGrowth
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.config_reader import ConfigReader

import pandas as pd
from collections import OrderedDict
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
        self._growth_statements = OrderedDict()
        self._raw_statements = OrderedDict()

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
        statement_growth = YoYGrowth.growth_calculation(raw_data)

        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, ticker + "_" + self._statement + ".csv", raw_data, statement_growth)

        self._raw_statements[ticker] = raw_data
        self._growth_statements[ticker] = statement_growth

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    def run(self):
        # parsing data from multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

    def get_statement(self, type, *tickers):
        """

        :param type: growth , raw
        :param tickers: (optional) => stock symbol
        :return:
        """

        type_mapping = {
            "growth": self._growth_statements,
            "raw": self._raw_statements
        }

        if len(tickers) == 0:
            return type_mapping.get(type)
        else:
            return_dict = OrderedDict()
            for ticker in tickers:
                return_dict[ticker] = type_mapping.get(type).get(ticker)
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
