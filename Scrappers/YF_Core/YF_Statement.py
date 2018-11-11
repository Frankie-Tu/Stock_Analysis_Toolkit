import requests
from bs4 import BeautifulSoup as Soup
from collections import OrderedDict
import pandas as pd
import numpy as np
import pdb
import os
import math
import sys


class StatementScrap:
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
    def __init__(self, ticker, storelocation, foldername, filesave):
        self.ticker = ticker
        self.storelocation = storelocation
        self.foldername = foldername
        self.filesave = filesave
        self.statement_type = {'IS': 'financials',
                               'BS': 'balance-sheet',
                               'CF': 'cash-flow'}
        self.raw_data = None  # Place holder,
        self.statement = None   # Place holder,
        self.statement_growth = None  # Place holder,
        self.my_system = sys.platform

        if self.my_system == 'linux':
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
        self.statement = statement.upper()
        url = "https://ca.finance.yahoo.com/quote/" + self.ticker + \
              "/" + self.statement_type[statement.upper()] + "?p=" + self.ticker

        r = requests.get(url)
        my_soup = Soup(r.text, 'html.parser')
        all_html = my_soup.find_all('table', {'class': 'Lh(1.7) W(100%) M(0)'})[0].\
            find_all(True, {'class': ['Bdbw(1px) Bdbc($c-fuji-grey-c) Bdbs(s) H(36px)', 'Bdbw(0px)! H(36px)']})

        td_list = [tr.find_all("td")for tr in all_html]

        # Date extraction
        date_list = [date.text for date in td_list[0]][1:]

        # Grab item name and its corresponding values from each year and assign into Ordered Dictionary
        item_dict = OrderedDict()
        for td in td_list[1:]:
            item1 = td[0].text
            item_dict[item1] = [item2.text for item2 in td[1:]]

        # # Excluding those heading when searching in the item_dict

        row_names = []

        # Values from the income Statement
        result_list = []

        for item in item_dict.keys():
            # Skips headings, item_dict[headings] is empty
            if item_dict[item]:
                # Data Cleaning, converting any '-' in list item_dict[item] to 0
                # Take out ',' and convert str to float
                for value in item_dict[item]:
                    if value == '-':
                        item_dict[item][item_dict[item].index(value)] = 0
                    else:
                        indexnum = item_dict[item].index(value)
                        item_dict[item][indexnum] = float(item_dict[item][indexnum].replace(',', ''))

                result_list.append(item_dict[item])
                row_names.append(item)

        self.raw_data = pd.DataFrame(result_list, index=row_names, columns=date_list)

    def growth_calculation(self):
        """
        Note: \n
            help calculating yoy growth for each item on the statement
            Only call this function after the downloader method has already been called
            Dataframe_in: pandas.dataframe
        """
        itemname_list = list(self.raw_data.index)
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

        self.statement_growth = pd.DataFrame(percentage_list_result, index=itemname_list, columns=dates)

        if self.filesave:
            try:
                if not os.path.exists(self.storelocation + self.foldername + self.separator + self.statement):
                    os.makedirs(self.storelocation + self.foldername + self.separator + self.statement)

                with open(self.storelocation + self.foldername + self.separator + self.statement +
                          self.separator + self.statement + '_G_' +
                          self.ticker + '.csv', mode='w') as file:
                    file.write(self.statement + '\n')
                    self.raw_data.to_csv(file)

                with open(self.storelocation + self.foldername + self.separator + self.statement +
                          self.separator + self.statement + '_G_' +
                          self.ticker + '.csv', mode='a') as file:
                    file.write("%" + "\n")
                    self.statement_growth.to_csv(file)

            except IOError:
                print("Please close your freaking file!!!")


def statements(arg, storelocation,
               foldername, filesave):
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
        income_ss = StatementScrap(items, storelocation, foldername,
                                   filesave)
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

    if my_system == "linux":
        store_location = "/home/frankietu/Stock_data/"
    elif my_system == "win32":
        store_location = "D:\Yahoo Finance\Stock Data\\"

    for item in user_input:
        income_s = StatementScrap(item, storelocation=store_location, foldername='test',
                                  filesave=True)
        income_s.downloader(user_input2)
        income_s.growth_calculation()

        print("----------------------------------------" + item + "----------------------------------------")
        print(income_s.raw_data)
        print("\n")
        print(income_s.statement_growth)