import requests
from bs4 import BeautifulSoup as Soup
from collections import OrderedDict
import pandas as pd
import numpy as np
import pdb
import os
import math
import sys
import getpass


class YFStatement:
    """
    Note: Scrap data from Financial Tab

    Please input a stock ticker you wish to scrap.
    This Class scraps data off Yahoo Finance for
    the ticker selected.

    Storelocation, foldername and file type are not optional \n
    storelocation example: F:\\\\Yahoo Finance\\\\Stock Data\\\ \\\ \n
    foldername: type = str \n
    filesave: type = boolean
    """
    def __init__(self, ticker, store_location, folder_name, file_save):
        self.ticker = ticker
        self.store_location = store_location
        self.folder_name = folder_name
        self.file_save = file_save
        self.statement_type = {'IS': 'financials',
                               'BS': 'balance-sheet',
                               'CF': 'cash-flow'}
        self.raw_data = None  # Place holder,
        self.statement = None   # Place holder,
        self.statement_growth = None  # Place holder,
        self.my_system = sys.platform

        if self.my_system == 'linux' or self.my_system == 'darwin':
            self.separator = "/"
        elif self.my_system == 'win32':
            self.separator = "\\"

    def downloader(self, statement):
        """
        returns statement with raw data without adjustments \n
        Note: \n
            Statement type: \n
            'Balance Sheet', \n
            'Income Statement', \n
            'Cash Flow'
        """
        # converts "-" to 0 and str to float, eg '123,456.789' to '123456.789'
        def convert(value2):
            if value2 == '-':
                return 0
            else:
                return float(value2.replace(',', ''))

        self.statement = statement.upper()
        url = "https://ca.finance.yahoo.com/quote/" + self.ticker + \
              "/" + self.statement_type[statement.upper()] + "?p=" + self.ticker

        r = requests.get(url, timeout=1)

        while r.status_code != 200:
            r = requests.get(url, timeout=1)

        my_soup = Soup(r.text, 'html.parser')
        all_html = my_soup.find_all('table', {'class': 'Lh(1.7) W(100%) M(0)'})[0].\
            find_all(True, {'class': ['Bdbw(1px) Bdbc($c-fuji-grey-c) Bdbs(s) H(36px)', 'Bdbw(0px)! H(36px)']})

        td_list = [tr.find_all("td")for tr in all_html]

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

        self.raw_data = pd.DataFrame(result_list, index=row_names, columns=date_list)

    def growth_calculation(self):
        """
        Note: \n
            help calculating yoy growth for each item on the statement
            Only call this function after the downloader method has already been called
        """
        item_name_list = list(self.raw_data.index)
        percentage_list_result = []

        for r in range(self.raw_data.shape[0]):
            percentage_list = []

            # loop to calculate YOY growth rate
            for item in [-3, -2, -1]:
                # if num2 is negative and num 1 none zero
                if self.raw_data.iloc[r, item] < 0 and self.raw_data.iloc[r, item - 1] != 0:
                    num2 = self.raw_data.iloc[r, item - 1]
                    num1 = self.raw_data.iloc[r, item]
                    percentage_list.append((num2 - num1)/np.abs(num1))
                # if num2 is positive and num1 none zero
                elif self.raw_data.iloc[r, item] > 0 and self.raw_data.iloc[r, item - 1] != 0:
                    num2 = self.raw_data.iloc[r, item - 1]
                    num1 = self.raw_data.iloc[r, item]
                    percentage_list.append((num2 - num1) / num1)
                # case where num1 or num2 is zero, append 0
                else:
                    percentage_list.append(0)
            percentage_list = percentage_list[::-1]

            # CAGR
            beg_year_value = self.raw_data.iloc[r, 3]
            end_year_value = self.raw_data.iloc[r, 0]
            # When this is the case, we do -(result)
            if beg_year_value < 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = -(math.pow(end_year_value/beg_year_value, 1/3)-1)
                elif end_year_value / beg_year_value < 0:
                    cagr = -(-math.pow(abs(end_year_value/beg_year_value), 1/3)-1)
            # when ths is the case, we do (result)
            elif beg_year_value > 0 and end_year_value != 0:
                if end_year_value / beg_year_value > 0:
                    cagr = math.pow(end_year_value/beg_year_value, 1/3)-1
                elif end_year_value / beg_year_value < 0:
                    cagr = -math.pow(abs(end_year_value / beg_year_value), 1 / 3) - 1

            else:
                cagr = 0

            percentage_list.append(cagr)
            percentage_list_result.append(percentage_list)

        dates = list(self.raw_data.columns)[2::-1]
        dates.append('CAGR')

        self.statement_growth = pd.DataFrame(percentage_list_result, index=item_name_list, columns=dates)

        if self.file_save:
            try:
                if not os.path.exists(self.store_location + self.folder_name + self.separator + self.statement):
                    os.makedirs(self.store_location + self.folder_name + self.separator + self.statement)

                with open(self.store_location + self.folder_name + self.separator + self.statement +
                          self.separator + self.statement + '_G_' +
                          self.ticker + '.csv', mode='w') as file:
                    file.write(self.statement + '\n')
                    self.raw_data.to_csv(file)

                with open(self.store_location + self.folder_name + self.separator + self.statement +
                          self.separator + self.statement + '_G_' +
                          self.ticker + '.csv', mode='a') as file:
                    file.write("%" + "\n")
                    self.statement_growth.to_csv(file)

            except IOError:
                print("Please close your file!!!")


def statements(arg, store_location,
               folder_name, file_save):
    """
    designed to iterate items from args entered through Class Statement_Scrap
    """
    cagr_dict = OrderedDict()
    cagr_dict2 = OrderedDict()
    cagr_dict2_index = ['Total Revenue', 'Gross Profit', 'Net Income From Continuing Ops',
                        'Net Income Applicable To Common Shares']

    for items in arg:
        local_list = []
        local_list2 = []
        income_ss = YFStatement(items, store_location, folder_name,
                                file_save)
        income_ss.downloader('IS')
        income_ss.growth_calculation()

        # Append avg cagr to list
        local_list.append((income_ss.statement_growth.iloc[15, 3] + income_ss.statement_growth.iloc[22, 3])/2)

        # CAGR for income to compare with different tickers
        local_list2.append(income_ss.statement_growth.iloc[0, 3])
        local_list2.append(income_ss.statement_growth.iloc[2, 3])
        local_list2.append(income_ss.statement_growth.iloc[15, 3])
        local_list2.append(income_ss.statement_growth.iloc[22, 3])

        cagr_dict[items] = local_list
        cagr_dict2[items] = local_list2

    cagr_df = pd.DataFrame(cagr_dict)  # bottom lines CAGR
    cagr_df2 = pd.DataFrame(cagr_dict2, index=cagr_dict2_index)
    return cagr_df, cagr_df2


if __name__ == '__main__':
    # checking system spec
    my_system = sys.platform

    user_input = input("Please select the ticker you wish you analyze: ")
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
        if user_input2 in ('IS','BS','CF'):
            break

    user_input = user_input.replace(' ','').split(sep=',')

    my_user = getpass.getuser()

    if my_system == "linux" or my_system == "darwin":
        store_location = "/home/" + my_user + "/stock_data/"
    elif my_system == "win32":
        store_location = "D:\Yahoo Finance\Stock Data\\"

    for item in user_input:
        income_s = YFStatement(item, store_location=store_location, folder_name='test',
                               file_save=False)
        income_s.downloader(user_input2)
        income_s.growth_calculation()

        print("----------------------------------------" + item + "----------------------------------------")
        print(income_s.raw_data)
        print("\n")
        print(income_s.statement_growth)