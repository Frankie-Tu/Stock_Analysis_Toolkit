from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.core.analysis.growth_analysis import YoYGrowth
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.config_reader import ConfigReader
from scrappers.utils.logger import Logger

import logging
import pandas as pd
from collections import OrderedDict
import re
from pdb import set_trace


class YFStatement(ScrapperAbstract):
    """
    Scrap data from Statement Tab off Yahoo Finance for the given array of stock symbols passed in for the given statement type

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param statement_type: type of statement => IS, BS, CF
    :param logger: Logger => by default uses global logger from main
    """

    def __init__(self, args, store_location, folder_name, file_save, statement_type, logger=logging.getLogger("global")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name,file_save=file_save, logger=logger)
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
            if value2 in ['-', ""]:
                return 0
            else:
                return float(value2.replace(',', ''))

        url = "https://ca.finance.yahoo.com/quote/" + ticker + \
              "/" + self._statement_type[self._statement] + "?p=" + ticker

        try:
            self._logger.info("Sending requests for {}...".format(ticker))
            all_html = self.requester(url).find_all("div", {"class": "M(0) Mb(10px) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})[0]. \
                find_all("div", {"class": ["D(tbr) C($primaryColor)", "D(tbr) fi-row Bgc($hoverBgColor):h"]})

            # Date extraction
            date_list = [date.text for date in all_html[0].find_all("div", {"class": re.compile(
                "^D\(ib\) Fw\(b\) Ta\(end\) Pstart\(6px\) Pend\(4px\) Py\(6px\) Bxz\(bb\) BdB Bdc\(\$seperatorColor\) Miw\(100px\) Miw\(156px\)")})]

            item_dict = OrderedDict()

            # Grab item name and its corresponding values from each year and assign into Ordered Dictionary
            for row in all_html[1:]:
                values = row.find_all("div",
                                      {"class":
                                           re.compile("^D\(tbc\) Ta\(end\) Pstart\(6px\) Pend\(4px\) Bxz\(bb\) Py\(8px\) BdB Bdc\(\$seperatorColor\) Miw\(100px\) Miw\(156px\)")})

                item_dict[row.span.text] = list(map(lambda x: x.text, values))

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
        :param type: growth , raw => growth(yoy%) , raw (raw numbers)
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
        user_input = general_conf.get("symbols")["group1"]

    YFStatement(user_input, store_location=general_conf.get("store_location"),
                folder_name=config.get("statement").get(user_input2).get("folder_name"),
                file_save=general_conf.get("file_save"), statement_type=user_input2, logger=Logger("statement").create_logger()).run()
