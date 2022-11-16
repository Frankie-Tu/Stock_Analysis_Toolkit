from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.config_reader import ConfigReader
from scrappers.utils.logger import Logger

import logging
from collections import OrderedDict
import pandas as pd
import re


class YFSummary(ScrapperAbstract):
    """
    Scrap data from Summary Tab off Yahoo Finance for the given array of stock symbols passed in

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param logger: Logger => by default uses global logger from main
    :return: None
    """

    def __init__(self, args, store_location, folder_name, file_save, logger=logging.getLogger("global")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name, file_save=file_save,logger=logger)
        self._dataframe = None
    
    def parse_rows(self, body: str):
        columns = []
        values = []
        rows = body.find_all("tr")
        cur_price = body.find(id="quote-header-info").find("fin-streamer").text

        for row in rows:
            col , val =  row.find_all("td")
            columns.append(col.span.text)
            values.append(val.text)
        
        columns.append("Current Price")
        values.append(cur_price)
        
        return columns, values

    def data_parser(self, ticker):
        """
        parse html to dataframe

        :return: None
        """
        result_dict = OrderedDict()

        url = "https://ca.finance.yahoo.com/quote/" + ticker + "?p=" + ticker

        try:
            self._logger.info("{}: Sending requests...".format(ticker))
            res = self.requester(url).body

            cols, vals = self.parse_rows(res)

        except IndexError:
            self._logger.exception("{}: returned html not in expected format".format(ticker))
            raise IndexError

        for col, val in zip(cols, vals):
            result_dict[col] = val

        result_dict['52 Week Low'] = float(result_dict['52 Week Range'].split(" - ")[0].replace(",", ""))
        result_dict['52 Week High'] = float(result_dict['52 Week Range'].split(" - ")[1].replace(",", ""))

        if result_dict["1y Target Est"] == 'N/A':
            result_dict['1y Target Est'] = 0
        else:
            result_dict['1y Target Est'] = float(result_dict["1y Target Est"].replace(',', ''))

        # Based on  estimates provided by analysts and compare that to the current stock price
        self._logger.info('{}: Calculating growth potential and current price percentile'.format(ticker))
        result_dict['Growth Potential'] = float(result_dict['1y Target Est']) / float(result_dict['Current Price']) - 1
        result_dict['52 Week Percentile'] = (float(result_dict['Current Price']) - float(result_dict['52 Week Low'])) / \
                                            (float(result_dict['52 Week High']) - float(result_dict['52 Week Low']))

        # if self._dataframe already exists, append only
        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        if isinstance(None, type(self._dataframe)):
            self._logger.info('Creating dataframe...')
            self._dataframe = pd.DataFrame( result_dict.values(), result_dict.keys(), columns=[ticker])
        else:
            self._logger.info('Appending ' + ticker + ' to dataframe')
            self._dataframe[ticker] = result_dict.values()

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    def run(self):
        # parsing data for multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, "Summary_data.csv", self._dataframe)

    def get_summary(self):
        return self._dataframe


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=',')
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")["group1"]

    YFSummary(user_input, store_location=general_conf.get("store_location"),
                 folder_name=config.get("summary").get("folder_name"), file_save=general_conf.get("file_save"), logger=Logger("summary").create_logger()).run()
