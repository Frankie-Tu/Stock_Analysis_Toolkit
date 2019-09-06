from scrappers2.core.scrapper_abstract import ScrapperAbstract
from scrappers2.utils.multi_threader import MultiThreader
from scrappers2.utils.config_reader import ConfigReader
from scrappers2.utils.data_writer import DataWriter

from collections import OrderedDict
import pandas as pd
import scipy.stats as ss
from threading import Lock
from time import strftime
import pdb


class YFStatistics(ScrapperAbstract):
    """
    Scraps data from Statistics Tab.
    Please input a list of stock tickers you wish to scrap.
    This Class scraps data off Yahoo Finance for the
    tickers selected.

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param start_time: strftime => start time of the application for log timestamp
    """

    def __init__(self, args, store_location, folder_name, file_save, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name,
                         file_save=file_save, start_time=start_time, logger_name=__name__)
        self._dataframe = None  # Place holder, all stats
        self._df_downsized = None  # Place holder, downsized df
        self._target_list = None  # Place holder, row item targets
        self._short_date = None  # Place holder, short float dates
        self._scoring_df = None  # Place holder, listing each every single score for each category for all tickers
        self._scoring_dict = None  # place holder, total score for each ticker stored in dictionary
        self._ignored_stats = []  # place holder, showing all the stats that were ignored in the calculation
        self._lock = Lock()

    def data_parser(self, ticker):
        """
        Method is used by YFStatistics Class to parse html
        data from Statistics tab on Yahoo Finance. Supports multi-threaded operation

        :param ticker: stock ticker symbol
        :return: None
        """

        def iteration_function(data, class_name):
            """
            This is a nested function that iterates through <td> within <tr>.
            Used only within YFStatistics.data_parser method to populate result_dict OrderedDict

            :param data: html data
            :param class_name: html class
            :return: None
            """

            # Temporary list
            mylist = []
            for item in data:
                mylist.extend(item.find_all('tr'))

            # Dumping results into result dictionary. Both key and value.
            for item, num in zip(mylist, mylist):
                result_dict[item.span.text] = num.find_all('td', {'class': class_name})[0].text

        result_dict = OrderedDict()
        
        url = "https://ca.finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
        statistics_class = 'Mstart(a) Mend(a)'
        statistics_section_class = 'Mb(10px) Pend(20px) smartphone_Pend(0px)'
        statistics_section_class_val_measure = "Mb(10px) smartphone_Pend(0px) Pend(20px)"
        statistics_section_class2 = 'Pstart(20px) smartphone_Pstart(0px)'
        td_class = 'Fz(s) Fw(500) Ta(end) Pstart(10px) Miw(60px)'
        table_class = 'table-qsp-stats Mt(10px)'

        try:
            # fetch data
            self._logger.info("Sending requests for {}...".format(ticker))
            all_html = self.requester(url).find_all('div', {'class': statistics_class})[0]

            # Valuation Measures:
            self._logger.info("{}: Computing Valuation Measures...".format(ticker))
            valuation_measures = all_html \
                .find_all('div', {'class': statistics_section_class_val_measure})[0] \
                .find_all("tr")

            for item, num in zip(valuation_measures, valuation_measures):
                result_dict[item.span.text] = num \
                    .find_all('td', {'class': td_class})[0].text

            # Financial Highlights:
            self._logger.info("{}: Computing Financial Highlights...".format(ticker))
            financial_highlights = all_html \
                .find_all('div', {'class': statistics_section_class})[0] \
                .find_all('table', {'class': table_class})

            iteration_function(financial_highlights, td_class)

            # Trading Information:
            self._logger.info("{}: Computing Trading Information...".format(ticker))
            trading_information = all_html \
                .find_all('div', {'class': statistics_section_class2})[0] \
                .find_all('table', {'class': table_class})

            iteration_function(trading_information, td_class)

        except IndexError:
            self._logger.exception("{}: returned html not in expected format".format(ticker))
            raise IndexError

        # Temp list
        col = []
        val = []

        # Get all keys into column and values into values from the result dictionary
        for colnames, value in zip(result_dict.keys(), result_dict.values()):
            col.append(colnames)
            val.append(value)

        self._logger.info("{}: Converting string to numeric values...".format(ticker))
        # Convert all numbers to base of 1, 1M = 1,000,000, 1k = 1,000, 5% = 0.05
        for item in result_dict.values():

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

        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        # test to see if dataframe dict exists, if it doesn't create dictionary, else append.
        if isinstance(None, type(self._dataframe)):
            self._dataframe = pd.DataFrame(val, col, columns=[ticker])
        else:
            self._dataframe[ticker] = val

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    def run(self):

        # parsing data for multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

        # write to csv if requested
        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, "Statistics_data.csv", self._dataframe)

        # populating self.short_date list to be used in downsize method
        self._short_date = []

        for x, y in zip([44, 45, 48], [13, 12, 13]):
            self._short_date.append(list(self._dataframe.index)[x][y:])

        self.__downsize()
        self.__scoring()

    def __downsize(self):
        """
        Method used within the YFStatistics Class.

        Purpose: This downsize the dataset to more important
        fundamentals and save as abstract-data.csv

        :return: None
        """
        # Class Attributes that are important to keep
        important_item = ['Trailing P/E',
                          'Forward P/E',
                          'PEG Ratio (5 yr expected)',
                          'Price/Sales',
                          'Price/Book',
                          'Profit Margin',
                          'Operating Margin',
                          'Return on Assets',
                          'Return on Equity',
                          'Revenue Per Share',
                          'Quarterly Revenue Growth',
                          'Gross Profit',
                          'EBITDA',
                          'Net Income Avi to Common',
                          'Quarterly Earnings Growth',
                          'Total Cash Per Share',
                          'Total Debt/Equity',
                          'Current Ratio',
                          'Operating Cash Flow',
                          'Levered Free Cash Flow',
                          'Beta (3Y Monthly)',
                          '52-Week Change',
                          'S&P500 52-Week Change',
                          '52 Week High',
                          '52 Week Low',
                          '50-Day Moving Average',
                          '200-Day Moving Average',
                          'Avg Vol (3 month)',
                          'Avg Vol (10 day)',
                          'Shares Outstanding',
                          'Shares Short ' + self._short_date[0],
                          'Short Ratio ' + self._short_date[1],
                          'Shares Short ' + self._short_date[2],
                          'Forward Annual Dividend Yield',
                          'Trailing Annual Dividend Yield',
                          "Payout Ratio"
                          ]

        # filtering dataframe to find the indices of only the important rows.
        mylist = list(filter(lambda x: x in important_item, self._dataframe.index))
        mylist = list(map(lambda x: list(self._dataframe.index).index(x), mylist))

        # load data from self.dataframe to self.df to be exported where the fundamental deemed as important
        self._df_downsized = self._dataframe.iloc[mylist, :]

        # write to csv if requested
        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, "Statistics_data_abstract.csv", self._df_downsized)

    def __target_rows(self, value_list):
        """
        Method is not meant to be called directly by the user.
        By default, this method is called by method scoring(self)

        Updates self.target_list during every call

        :param value_list: list[String] => list of column names being targeted
        :return: None
        """

        na_list = list(filter(lambda x: 'N/A' in list(self._df_downsized.loc[x, :].values), value_list))

        self._target_list = list(filter(lambda x: x not in na_list, value_list))

        self._ignored_stats.extend(na_list)

    def __scoring(self):
        """
        This method returns the final score for each stock based on
        ranking of stocks in each of the categories
        """

        # create scorecard, initialize
        mydict = OrderedDict()

        for item in self._tickers:
            mydict[item] = 0

        mydict2 = OrderedDict()

        # all values lower the better
        low_values = ["Trailing P/E",
                     "Forward P/E",
                     "PEG Ratio (5 yr expected)",
                     "Price/Sales",
                     "Price/Book",
                     "Total Debt/Equity"]

        # all values higher the better
        high_values = ["Profit Margin",
                      "Operating Margin",
                      "Return on Assets",
                      "Return on Equity",
                      "Quarterly Revenue Growth",
                      "Quarterly Earnings Growth",
                      "Current Ratio",
                      "Forward Annual Dividend Yield",
                      "Trailing Annual Dividend Yield"]

        # Secondary Fundamentals
        secondary_values = ["Gross Profit",
                           "EBITDA",
                           "Net Income Avi to Common"]

        # All important Fundamentals:
        all_values = low_values + high_values + secondary_values

        # Multipliers
        multiplier = {'Trailing P/E': 0,  # 1.3,
                       'Forward P/E': 0,  # 1.1,
                       'PEG Ratio (5 yr expected)': 0,  #1,
                       'Price/Sales': 0.5,
                       'Price/Book': 0.5,
                       'Profit Margin': 1.2,
                       'Operating Margin': 1.2,
                       'Return on Assets': 1,
                       'Return on Equity': 1.1,
                       'Quarterly Revenue Growth': 0.8,
                       'Quarterly Earnings Growth': 1,
                       'Total Debt/Equity': 1.2,
                       'Current Ratio': 1.1,
                       'Forward Annual Dividend Yield': 0.4,
                       'Trailing Annual Dividend Yield': 0.6}

        self.__target_rows(low_values)

        # Appending Score to mydict
        for value in self._target_list:
            scoreboard = ss.rankdata(self._df_downsized.loc[value, :].astype(float), method='dense')
            # Append to ranking table
            mydict2[value] = scoreboard
            multiplier_lookup = value
            for item, num in zip(list(self._df_downsized.columns), range(len(self._df_downsized.columns))):
                mydict[item] = (mydict[item] + len(self._df_downsized.columns) - scoreboard[num] + 1) * \
                               multiplier[multiplier_lookup]

        self.__target_rows(high_values)

        for value in self._target_list:
            scoreboard = ss.rankdata(self._df_downsized.loc[value, :].astype(float), method='dense')
            mydict2[value] = scoreboard

            # invert ranking
            mydict2[value] = len(self._df_downsized.columns) + 1 - mydict2[value]

            multiplier_lookup = value
            for item, num in zip(list(self._df_downsized.columns), range(len(self._df_downsized.columns))):
                mydict[item] = (mydict[item] + scoreboard[num]) * multiplier[multiplier_lookup]

        # Secondary fundamentals, check if value positive
        self.__target_rows(secondary_values)

        for value in self._target_list:
            for item, num in zip(list(self._df_downsized.columns), list(self._df_downsized.loc[value, :].values)):
                if float(num) >= 0:
                    mydict[item] = mydict[item] + 0.33
                else:
                    mydict[item] = mydict[item] - 0.25

        self._scoring_df = pd.DataFrame(mydict2, index=self._df_downsized.columns).transpose()

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, "Ranking_information.csv", self._scoring_df,
                                                self._df_downsized.loc[all_values, :])
        self._scoring_dict = OrderedDict(sorted(mydict.items(), key=lambda x: x[1], reverse=True))

    def get_score(self):
        return self._scoring_dict

    def get_ranking(self):
        return self._scoring_df

    def get_downsized_df(self):
        return self._df_downsized


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=',')
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")

    YFStatistics(user_input, store_location=general_conf.get("store_location"),
                 folder_name=config.get("statistics").get("folder_name"), file_save=general_conf.get("file_save")).run()