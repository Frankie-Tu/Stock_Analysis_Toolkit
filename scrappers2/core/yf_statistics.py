from scrappers2.Core.scrapper_abstract import ScrapperAbstract

from collections import OrderedDict
import pandas as pd


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
    """

    def __init__(self, args, store_location, folder_name, file_save):
        super().__init__(args, store_location, folder_name, file_save)
        self._dataframe = None  # Place holder, all stats
        self._df_downsized = None  # Place holder, downsized df
        self._target_list = None  # Place holder, row item targets
        self._short_date = None  # Place holder, short float dates
        self._scoring_df = None  # Place holder, listing each every single score for each category for all tickers
        self._scoring_dict = None  # place holder, total score for each ticker stored in dictionary
        self._ignored_stats = []  # place holder, showing all the stats that were ignored in the calculation

    def data_parser(self):
        """
        Method is used by YFStatistics Class to parse html
        data from Statistics tab on Yahoo Finance.

        :return: None
        """

        def iteration_function(data):
            """
            This is a nested function that iterates through <td> within <tr>.
            Used only within YFStatistics.data_parser method to populate result_dict OrderedDict

            :param data: html data
            :return: None
            """

            # Temporary list
            mylist = []
            for item in data:
                mylist.extend(item.find_all('tr'))

            # Dumping results into result dictionary. Both key and value.
            for item, num in zip(mylist, mylist):
                result_dict[item.span.text] = num.find_all('td', {'class': td_class})[0].text

        for ticker in self._tickers:

            url = "https://ca.finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
            statistics_class = 'Mstart(a) Mend(a)'
            statistics_section_class = 'Mb(10px) Pend(20px) smartphone_Pend(0px)'
            statistics_section_class_val_measure = "Mb(10px) smartphone_Pend(0px) Pend(20px)"
            statistics_section_class2 = 'Pstart(20px) smartphone_Pstart(0px)'
            td_class = 'Fz(s) Fw(500) Ta(end) Pstart(10px) Miw(60px)'
            table_class = 'table-qsp-stats Mt(10px)'

            # result dictionary initialize:
            result_dict = OrderedDict()

            # fetch data
            print("Sending requests for " + ticker + '...')
            all_html = self.requester(url).find_all('div', {'class': statistics_class})[0]

            # Valuation Measures:
            print('Computing Valuation Measures...')
            valuation_measures = all_html \
                .find_all('div', {'class': statistics_section_class_val_measure})[0] \
                .find_all("tr")

            for item, num in zip(valuation_measures, valuation_measures):
                result_dict[item.span.text] = num \
                    .find_all('td', {'class': td_class})[0].text

            # Financial Highlights:
            print("Computing Financial Highlights...")
            financial_highlights = all_html \
                .find_all('div', {'class': statistics_section_class})[0] \
                .find_all('table', {'class': table_class})

            iteration_function(financial_highlights)

            # Trading Information:
            print("Computing Trading Information...")
            trading_information = all_html \
                .find_all('div', {'class': statistics_section_class2})[0] \
                .find_all('table', {'class': table_class})

            iteration_function(trading_information)

            # Temp list
            col = []
            val = []

            # Get all keys into column and values into values from the result dictionary
            for colnames, value in zip(result_dict.keys(), result_dict.values()):
                col.append(colnames)
                val.append(value)

            print("Converting values...")
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

            # test to see if dataframe dict exists, if it doesn't create dictionary, else append.
            if isinstance(None, type(self._dataframe)):
                self._dataframe = pd.DataFrame(val, col, columns=[ticker])
            else:
                self._dataframe[ticker] = val

            # write to csv if requested
            if self._file_save:
                self.csv_writer(self._store_location + self._folder_name, "Statistics_data.csv", self._dataframe)

            # populating self.short_date list to be used in downsize method
            self._short_date = []

            for x, y in zip([44, 45, 48], [13, 12, 13]):
                self._short_date.append(list(self._dataframe.index)[x][y:])