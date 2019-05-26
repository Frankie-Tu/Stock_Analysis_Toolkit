import requests
from bs4 import BeautifulSoup as Soup
from collections import OrderedDict
import pandas as pd
import pdb
import os
import scipy.stats as ss
import sys
import getpass


class YFSummary:
    """
    Note: Scrap data from Summary Tab

    Please input a list array of stock tickers you wish to scrap.
    This Class scraps data off Yahoo Finance for
    the tickers selected.

    Storelocation, foldername and file type are not optional \n
    storelocation example: F:\\\Yahoo Finance\\\Stock Data\\\ \\\ \n
    foldername: type = str \n
    filesave: type = boolean
    """

    def __init__(self, args, store_location="D:\Yahoo Finance\Stock Data\\",
                 folder_name='test_folder', filesave=False):
        self.args = args
        self.store_location = store_location
        self.folder_name = folder_name
        self.file_save = filesave
        self.dataframe = None   # Place holder, summary information for tickers
        self.my_system = sys.platform

        if self.my_system == 'linux' or self.my_system == 'darwin':
            self.separator = "/"
        elif self.my_system == 'win32':
            self.separator = "\\"

    def summary_scrap(self):
        """
        Note:
        This method is used by SummaryScrap Class to start the web
        scrapping process from Summary tab on Yahoo Finance.
        Do not pass in any parameter to this Method!!
        """
        for item in self.args:

            ticker = item
            url = "https://ca.finance.yahoo.com/quote/" + ticker + "?p=" + ticker

            # initialize result dictionary
            result_dict = OrderedDict()

            # get 52 week price info
            print('Scrapping 52 week price data for ' + item)
            r = requests.get(url, timeout=1)

            while r.status_code != 200:
                r = requests.get(url, timeout=1)

            my_soup = Soup(r.text, 'html.parser')
            all_html = my_soup.find_all('table', {'class': "W(100%)"})
            fifty2_week_range = all_html[0].find_all('tr', {'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($c-fuji-grey-c) H(36px) '})[5]
            fifty2_week_range_value = fifty2_week_range.find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)'})[0]
            fifty2_week_range_value = fifty2_week_range_value.text.split(sep=' - ')
            fifty2_week_range_low = fifty2_week_range_value[0]
            fifty2_week_range_high = fifty2_week_range_value[1]

            # 1y Target Est
            print('Scrapping 1 year target estimates for ' + item)
            all_html = my_soup.find_all('table', {'class': "W(100%) M(0) Bdcl(c)"})
            one_year_target = all_html[0].find_all('tr', {
                'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($c-fuji-grey-c) H(36px) Bdbw(0)! '})
            one_year_target = one_year_target[0].find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)'})
            one_year_target = one_year_target[0].span.text

            # Stock price. percentage change
            print('Scrapping price info & percentage change for ' + item)
            all_html_2 = my_soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})

            current_price = all_html_2[0].div.span.text

            # Due to the fact that stock can go up or down, as a result of that, fontcolor = red or green
            try:
                change = all_html_2[0].div.find_all('span', {'class': "Trsdu(0.3s) Fw(500) Fz(14px) C($dataGreen)"})[0].text
            except:
                try:
                    change = all_html_2[0].div.find_all('span', {'class': "Trsdu(0.3s) Fw(500) Fz(14px) C($dataRed)"})[0].text
                except:
                    change = all_html_2[0].div.find_all('span', {'class': "Trsdu(0.3s) Fw(500) Fz(14px)"})[0].text

            change = change.split(sep=' ')[1].replace('(', "").replace(')', "")
            change = change.replace('%', '')
            change = str(float(change) / 100)

            # Append result to
            fifty2_week_range_high = fifty2_week_range_high.replace(',', '')
            fifty2_week_range_low = fifty2_week_range_low.replace(',', '')
            current_price = current_price.replace(',', '')

            result_dict['52 Week Low'] = float(fifty2_week_range_low)
            result_dict['52 Week High'] = float(fifty2_week_range_high)
            try:
                result_dict['1y Target Est'] = float(one_year_target)
            except:
                if one_year_target == 'N/A':
                    result_dict['1y Target Est'] = 0
                else:
                    result_dict['1y Target Est'] = one_year_target.replace(',', '')

            result_dict['Change %'] = float(change)
            result_dict['Current Price'] = float(current_price)

            # Based on target
            print('Calculating growth potential and current price percentile ' + item)
            result_dict['Growth Potential'] = float(result_dict['1y Target Est']) / float(result_dict['Current Price']) - 1
            result_dict['52 Week Percentile'] = (float(result_dict['Current Price']) - float(result_dict['52 Week Low'])) / \
                                                (float(result_dict['52 Week High']) - float(result_dict['52 Week Low']))

            col = []
            val = []

            # Transfer info from result_dict to col and val list
            for key, value in zip(result_dict.keys(), result_dict.values()):
                col.append(key)
                val.append(round(value,4))

            # if self.dataframe already exists, append only
            if isinstance(None, type(self.dataframe)):
                print('Creating dataframe...')
                self.dataframe = pd.DataFrame(val, col)
                self.dataframe.columns = [ticker]
            else:
                print('Appending ' + item + ' to dataframe')
                self.dataframe[ticker] = val

        # Check if User wants to save the result to hard drive.
        if self.file_save:
            try:
                if not os.path.exists(self.store_location + self.folder_name):
                    print('Creating path: ' + self.store_location + self.folder_name)
                    os.makedirs(self.store_location + self.folder_name)

                with open(self.store_location + self.folder_name + self.separator + 'Summary_data.csv', mode='w') as file:
                    print('Saving data...')
                    file.write('Summary' + '\n')
                    self.dataframe.to_csv(file)

            except:
                print("Please close your freaking file!!!")


if __name__ == "__main__":
    my_system = sys.platform

    user_input = input("Please select the ticker you wish you analyze: ")

    user_input = user_input.replace(' ', '').split(sep=',')

    my_user = getpass.getuser()

    if my_system == "linux" or my_system == "darwin":
        store_location = "/home/" + my_user + "/stock_data/"
    elif my_system == "win32":
        store_location = "D:\Yahoo Finance\Stock Data\\"

    myclass2 = YFSummary(user_input, store_location=store_location,
                         filesave=False)
    myclass2.summary_scrap()
