import requests
from bs4 import BeautifulSoup as Soup
from collections import OrderedDict
import pandas as pd
import os
import scipy.stats as ss
import pdb
import sys
import getpass


class YFStatistics:
    """
    Note: Scraps data from Statistics Tab

    Please input a list array of stock tickers you wish to scrap.
    This Class scraps data off Yahoo Finance for the
    tickers selected.

    Storelocation, foldername, filesave are ont optional arguments \n
    storelocation example: F:\\\Yahoo Finance\\\Stock Data\\\ \\\ \n
    foldername: type = str \n
    filesave: type = boolean
    """

    def __init__(self, args, store_location="D:\Yahoo Finance\Stock Data\\",
                 folder_name='test_folder', file_save=False):
        self.args = args
        self.store_location = store_location
        self.folder_name = folder_name
        self.file_save = file_save
        self.dataframe = None   # Place holder, all stats
        self.df = None          # Place holder, downsized df
        self.target_list = None  # Place holder, row item targets
        self.short_date = None  # Place holder, short float dates
        self.scoring_df = None  # Place holder, listing each every single score for each category for all tickers
        self.scoring_dict = None  # place holder, total score for each ticker stored in dictionary
        self.ignored_stats = []  # place holder, showing all the stats that were ignored in the calculation
        self.my_system = sys.platform

        if self.my_system == 'linux' or self.my_system == 'darwin':
            self.separator = "/"
        elif self.my_system == 'win32':
            self.separator = "\\"

    def statistics_scrap(self):
        """
        Note:
        This method is used by StatisticsScrap Class to start the web
        scrapping process from Statistics tab on Yahoo Finance.
        Do not pass in any parameter to this Method!!
        """
        for items in self.args:

            # Parameters used for html classes
            ticker = items
            url = "https://ca.finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
            statistics_class = 'Mstart(a) Mend(a)'
            statistics_section_class = 'Mb(10px) Pend(20px) smartphone_Pend(0px)'
            statistics_section_class2 = 'Pstart(20px) smartphone_Pstart(0px)'
            td_class = 'Fz(s) Fw(500) Ta(end)'
            table_class = 'table-qsp-stats Mt(10px)'

            def iteration_function(data):
                """
                :param data:
                This is a local function that iterates through <td> within <tr>.
                Used only within statistics_scrap method
                """

                # Temporary list
                mylist = []
                for item in data:
                    mylist.extend(item.find_all('tr'))

                # Dumping results into result dictionary. Both key and value.
                for item, num in zip(mylist, mylist):
                    result_dict[item.span.text] = num.find_all('td', {'class': td_class})[0].text

            # Fetch data
            print("Sending requests for " + items + '...')
            r = requests.get(url)

            while r.status_code != 200:
                r = requests.get(url)

            my_soup = Soup(r.text, 'html.parser')
            all_html = my_soup.find_all('div', {'class': statistics_class})

            # result dictionary initialize:
            result_dict = OrderedDict()

            # Valuation Measures:
            print('Computing Valuation Measures...')
            valuation_measures = all_html[0].find_all('div', {'class': statistics_section_class})[0].find_all("tr")

            for item,num in zip(valuation_measures, valuation_measures):
                result_dict[item.span.text] = num.find_all('td', {'class': td_class})[0].text

            # Financial Highlights:
            print("Computing Financial Highlights...")
            financial_highlights = all_html[0].find_all('div', {'class': statistics_section_class})[1].find_all('table', {'class': table_class})

            iteration_function(financial_highlights)

            # Trading Information:
            print("Computing Trading Information...")
            trading_information = all_html[0].find_all('div', {'class': statistics_section_class2})[0].find_all('table', {'class': table_class})

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
                                val[index] = str(float(val[index].replace(',', ''))*1000000000)
                            elif characters == 'k':
                                val[index] = str(float(val[index].replace(',', ''))*1000)
                            elif characters == 'M':
                                val[index] = str(float(val[index].replace(',', ''))*1000000)
                            elif characters == '%':
                                val[index] = str(float(val[index].replace(',', ''))/100)

            # test to see if dataframe dict exists, if it doesn't create dictionary, else append.
            if isinstance(None, type(self.dataframe)):
                self.dataframe = pd.DataFrame(val, col, columns=[ticker])
            else:
                self.dataframe[ticker] = val

        # Check if User wants to save result to the hard drive
        if self.file_save:
            try:
                # if path doesn't exist, create
                if not os.path.exists(self.store_location + self.folder_name):
                    os.makedirs(self.store_location + self.folder_name)

                self.dataframe.to_csv(self.store_location + self.folder_name +
                                      self.separator + 'Statistics_data.csv')
            except IOError:
                print("Please close your freaking file!!!")

        # populating self.short_date list to be used in downsize method
        self.short_date = []

        for x, y in zip([44, 45, 48], [13, 12, 13]):
            self.short_date.append(list(self.dataframe.index)[x][y:])

    def downsize(self):
        """
        :param: pd.Dataframe
        :return: pd.Dataframe (self.df)

        This is a method used within the StatisticsScrap Class
        with no additional parameters required.

        Purpose: This downsize the data set to more important
        fundamentals and save as abstract-data.csv
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
                          'Shares Short ' + self.short_date[0],
                          'Short Ratio ' + self.short_date[1],
                          'Shares Short ' + self.short_date[2],
                          'Forward Annual Dividend Yield',
                          'Trailing Annual Dividend Yield',
                          "Payout Ratio"
                          ]

        # Append row index from self.dataframe to mylist if they are deemed important by important_item list.
        mylist = []

        for item in list(self.dataframe.index):
            if item in important_item:
                mylist.append(list(self.dataframe.index).index(item))

        # load data from self.dataframe to self.df to be exported where the fundamental deemed as important
        self.df = self.dataframe.iloc[mylist, :]

        # Check if the User wants to save the result to the hard drive
        if self.file_save:
            try:
                self.df.to_csv(self.store_location + self.folder_name + self.separator + 'Statistics_data_abstract.csv')
            except IOError:
                print('Close your freaking file!!!')

    def target_rows(self, value_list):
        """
        :param value_list:
        :return: target_list:

        Note: This method is not meant to be called directly by the user.
        By default, this method is called within method scoring(self)
        """
        NA_list = []
        for value in value_list:
            for i in list(self.df.iloc[value, :].values):
                if i == 'N/A':
                    NA_list.append(value)
                    break    # break out i loop and continue to next value
                else:
                    pass

        self.target_list = []
        for i in value_list:
            if i not in NA_list:
                self.target_list.append(i)

        for item in NA_list:
            self.ignored_stats.append(list(self.df.index)[item])

    def scoring(self):
        """
        This method returns the final score for each stock based on
        ranking of stocks in each of the categories
        """

        # Stock tickers
        stocks = list(self.df.columns)
        # create scorecard, initialize
        for item in stocks:
            try:
                mydict
            except:
                mydict = OrderedDict()
                mydict[item] = 0
            else:
                mydict[item] = 0

        mydict2 = OrderedDict()

        # find all row lower the better
        low_value = [num for num in range(5)]
        low_value.append(16)

        # find all rows where higher the better
        high_value = [num for num in range(5, 9)]
        high_value.extend([10, 14, 17, 33, 34])

        # Secondary Fundamentals
        secondary_value = [num for num in range(11, 14)]

        # All important Fundamentals:
        all_value = low_value + high_value + secondary_value

        # Primary fundamental statistics in high_value & low_value list.
        '''
        low value: Trailing P/E , Forward P/E, PEG, Price/Sales, Price/Book, Total Debt/Equity
        high value: Profit Margin, Operating Margin, ROA, ROE, Quarterly Rev Growth, Quarterly Earning Growth,
                    Current Ratio, Forward Annual Div Yield, Trailing Annual Dividend Yield
        '''
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

        self.target_rows(low_value)

        # Appending Score to mydict
        for value in self.target_list:
            scoreboard = ss.rankdata(self.df.iloc[value, :].astype(float), method='dense')
            # Append to ranking table
            mydict2[self.df.index[value]] = scoreboard
            multiplier_lookup = self.df.index[value]
            for item, num in zip(list(self.df.columns), range(len(self.df.columns))):
                mydict[item] = (mydict[item] + len(self.df.columns) - scoreboard[num] + 1) * \
                               multiplier[multiplier_lookup]

        self.target_rows(high_value)

        for value in self.target_list:
            scoreboard = ss.rankdata(self.df.iloc[value, :].astype(float), method='dense')
            mydict2[self.df.index[value]] = scoreboard

            # invert ranking
            mydict2[self.df.index[value]] = len(self.df.columns) + 1 - mydict2[self.df.index[value]]

            multiplier_lookup = self.df.index[value]
            for item, num in zip(list(self.df.columns), range(len(self.df.columns))):
                mydict[item] = (mydict[item] + scoreboard[num]) * multiplier[multiplier_lookup]

        # Secondary fundamentals, check if value positive
        self.target_rows(secondary_value)

        for value in self.target_list:
            for item, num in zip(list(self.df.columns), list(self.df.iloc[value, :].values)):
                if float(num) >= 0:
                    mydict[item] = mydict[item] + 0.33
                else:
                    mydict[item] = mydict[item] - 0.25

        self.scoring_df = pd.DataFrame(mydict2, index=self.df.columns).transpose()

        if self.file_save:
            try:
                # if path doesn't exist, create
                if not os.path.exists(self.store_location + self.folder_name):
                    os.makedirs(self.store_location + self.folder_name)

                with open(self.store_location + self.folder_name + self.separator +
                          'Ranking_information.csv', mode='w') as file:
                    file.write('Ranking Info' + '\n')
                    self.scoring_df.to_csv(file)
            except IOError:
                print("Please close your freaking file!!!")

            with open(self.store_location + self.folder_name + self.separator +
                      'Ranking_information.csv', mode='a') as file:
                file.write('\n'+'Raw Data' + '\n')
                self.df.iloc[all_value, :].to_csv(file, header=True)

        self.scoring_dict = OrderedDict(sorted(mydict.items(), key=lambda x: x[1], reverse=True))


if __name__ == "__main__":
    # checking system spec
    my_system = sys.platform

    user_input = input("Please select the ticker you wish you analyze: ")

    user_input = user_input.replace(' ', '').split(sep=',')

    my_user = getpass.getuser()

    if my_system == "linux" or my_system == "darwin":
        store_location = "/home/" + my_user + "/stock_data/"
    elif my_system == "win32":
        store_location = "D:\Yahoo Finance\Stock Data\\"

    myclass = YFStatistics(user_input, store_location=store_location, folder_name='test',
                           file_save=False)
    myclass.statistics_scrap()
    myclass.downsize()
    myclass.scoring()

