from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.config_reader import ConfigReader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.logger import Logger

import logging
from collections import OrderedDict
import pandas as pd
import scipy.stats as ss
from threading import Lock
import sys
import pdb
from typing import Union


class YFStatistics(ScrapperAbstract):
    """
    Scrap data from Statistics Tab off Yahoo Finance for the given array of stock symbols passed in

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param logger: Logger => by default uses global logger from main
    :return None
    """

    def __init__(self, args, store_location, folder_name, file_save, logger=logging.getLogger("global")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name, file_save=file_save, logger=logger)
        self._application_logic = self._application_logic.get("statistics")
        self._dataframe = None  # Place holder, original df
        self._df_downsized = None  # Place holder, downsized df
        self._target_list = None  # Place holder, name of the items being targeted as important
        self._short_date = None  # Place holder, short float dates
        self._scoring_df = None  # Place holder, listing score for each category for all tickers
        self._scoring_dict = None  # place holder, total score for each ticker stored in dictionary
        self._ignored_stats = OrderedDict()  # place holder, showing all the stats that were ignored in the calculation
        self._lock = Lock()
    
    def parse_rows(self, body: str) -> Union[list[str], list[str]]:
        columns = []
        values = []
        
        rows = body.find_all("tr")

        for row in rows:
            col , val =  row.find_all("td")
            columns.append(col.span.text)
            values.append(val.text)

        return columns, values

    def data_parser(self, ticker):
        """
        parse html to dataframe

        :param ticker: stock ticker symbol
        :return: None
        """

        result_dict = OrderedDict()
        
        url = "https://ca.finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
        
        try:
            # fetch data
            self._logger.info("Sending requests for {}...".format(ticker))
            res = self.requester(url).body
            cols, vals = self.parse_rows(res)
            
            for col, val in zip(cols, vals):
                result_dict[col] = val

        except IndexError:
            self._logger.exception("{}: returned html not in expected format".format(ticker))
            raise IndexError

        if len(result_dict) != 60:
            self._logger.error("expected number of columns: 60, actual number of columns: {}".format(len(result_dict)))
            sys.exit(1)

        # Temp list
        col = []
        val = []

        for colnames, value in zip(result_dict.keys(), result_dict.values()):
            col.append(colnames)
            val.append(value)

        self._logger.info("{}: Converting string to numeric values...".format(ticker))
        # Convert all numbers to base of 1, 1M = 1,000,000, 1k = 1,000, 5% = 0.05
        for item in result_dict.values():

            try:
                # Making sure we are not altering date values
                if item[0:3] not in ('Mar', 'May'):
                    for characters in item:
                        if characters in ('B', 'M', 'k', '%'):
                            index = val.index(item)
                            val[index] = val[index].replace(characters, '')
                            if characters == 'B':
                                val[index] = str(float(val[index].replace(',', '')) * 1000000000)
                            elif characters == 'k':
                                val[index] = str(float(val[index].replace(',', '')) * 1000)
                            elif characters == 'M':
                                val[index] = str(float(val[index].replace(',', '')) * 1000000)
                            elif characters == '%':
                                val[index] = str(float(val[index].replace(',', '')) / 100)
            except Exception:
                self._logger.exception("item {} caused an exception during conversion!".format(item))

        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        # if self._dataframe already exists, append only
        if isinstance(None, type(self._dataframe)):
            self._dataframe = pd.DataFrame(val, col, columns=[ticker])
        else:
            self._dataframe[ticker] = val

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    def run(self):

        # parsing data for multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name,
                                                self._application_logic.get("file_names").get("data_stats"), self._dataframe)

        # populating self.short_date list to be used in downsize method
        self._short_date = []

        for x, y in zip([44, 45, 48], [13, 12, 13]):
            self._short_date.append(list(self._dataframe.index)[x][y:])

        self.__downsize()
        self.__scoring()

    def __downsize(self):
        """
        This method downsizes the dataset to retain only the most important items and save as abstract-data.csv if self.file_save is true

        :return: None
        """
        # Class Attributes that are important to keep
        important_item = self._application_logic.get("important_item")
        important_item.extend(['Shares Short ' + self._short_date[0],
                               'Short Ratio ' + self._short_date[1],
                               'Shares Short ' + self._short_date[2]])

        self._df_downsized = self._dataframe.filter(important_item, axis=0)

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name,
                                                self._application_logic.get("file_names").get("data_stats_abstract"), self._df_downsized)

    def __target_rows(self, value_list):
        """
        determine which rows contain N/A and should be excluded during scoring

        :param value_list: list[String] => list of column names being targeted
        :return: None
        """

        na_list = list(filter(lambda x: 'N/A' in list(self._df_downsized.loc[x, :].values), value_list))

        self._target_list = list(filter(lambda x: x not in na_list, value_list))

        if na_list:
            for item in na_list:
                self._ignored_stats[item] = list(self._df_downsized.loc[item].where(lambda x: x == "N/A").dropna().index)

    def __scoring(self):
        """
        This method calculates final score for each stock based on
        ranking of stocks in each of the categories
        """

        final_score = OrderedDict()

        # create scorecard, initialize
        for item in self._tickers:
            final_score[item] = 0

        category_rank = OrderedDict()

        # all values lower the better
        low_values = self._application_logic.get("low_values")

        # all values higher the better
        high_values = self._application_logic.get("high_values")

        # Secondary Fundamentals
        secondary_values = self._application_logic.get("secondary_values")

        all_values = low_values + high_values + secondary_values

        multiplier = self._application_logic.get("multiplier")

        self.__target_rows(low_values)

        # rank items being targeted and without N/A fields
        for value in self._target_list:
            scoreboard = ss.rankdata(self._df_downsized.loc[value, :].astype(float), method='dense')
            # Append to ranking table
            category_rank[value] = scoreboard
            for item, num in zip(list(self._df_downsized.columns), range(len(self._df_downsized.columns))):
                final_score[item] = (final_score[item] + len(self._df_downsized.columns) - scoreboard[num] + 1) * \
                               multiplier[value]

        self.__target_rows(high_values)

        for value in self._target_list:
            scoreboard = ss.rankdata(self._df_downsized.loc[value, :].astype(float), method='dense')
            category_rank[value] = scoreboard

            # invert ranking
            category_rank[value] = len(self._df_downsized.columns) + 1 - category_rank[value]

            for item, num in zip(list(self._df_downsized.columns), range(len(self._df_downsized.columns))):
                final_score[item] = (final_score[item] + scoreboard[num]) * multiplier[value]

        # Secondary fundamentals, check if value positive
        self.__target_rows(secondary_values)

        for value in self._target_list:
            for item, num in zip(list(self._df_downsized.columns), list(self._df_downsized.loc[value, :].values)):
                # add one point if the number positive, minus one point if negative
                if float(num) >= 0:
                    final_score[item] = final_score[item] + 1
                else:
                    final_score[item] = final_score[item] - 1

        self._scoring_df = pd.DataFrame(category_rank, index=self._df_downsized.columns).transpose()

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, self._application_logic.get("file_names").get("ranking_info"),
                                                self._scoring_df, self._df_downsized.loc[all_values, :])
        self._scoring_dict = OrderedDict(sorted(final_score.items(), key=lambda x: x[1], reverse=True))

    def get_score(self):
        return self._scoring_dict

    def get_ranking(self):
        return self._scoring_df

    def get_downsized_df(self):
        return self._df_downsized

    def get_ignored_stats(self):
        return self._ignored_stats


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=',')
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")["group1"]

    YFStatistics(user_input, store_location=general_conf.get("store_location"),
                 folder_name=config.get("statistics").get("folder_name"), file_save=general_conf.get("file_save"), logger=Logger("statistics").create_logger()).run()