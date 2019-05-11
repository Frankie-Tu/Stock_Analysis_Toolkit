from Scrappers.yf_core import YFStatistics as yf
from Scrappers.yf_core import YFSummary as yfs
from Scrappers.yf_core import YFStatement as yfst
from collections import OrderedDict
import pandas
import pdb
import sys
import getpass


class ScrapperApp:

    """
    Central control of Scrapper  application
    """

    def __init__(self, stock_ticker_list, storelocation="D:\Yahoo Finance\Stock Data\\",
                 foldername='test_folder', filesave=False, comprehensive=False):
        self.stock_ticker_list = stock_ticker_list
        self.storelocation = storelocation
        self.foldername = foldername
        self.filesave = filesave
        self.comprehensive = comprehensive
        self.ranking = None
        self.score = None
        self.my_system = sys.platform

        if self.my_system == 'linux':
            self.separator = "/"
        elif self.my_system == 'win32':
            self.separator = "\\"

    def scrapper_start(self):
        myclass = yf.YFStatistics(self.stock_ticker_list, store_location=self.storelocation,
                                  folder_name=self.foldername, file_save=self.filesave)
        myclass.statistics_scrap()
        myclass.downsize()
        myclass.scoring()
        trailing_pe_list = myclass.df.iloc[0, :]
        implied_peg = OrderedDict()
        self.ranking = myclass.scoring_df
        self.score = myclass.scoring_dict

        myclass2 = yfs.YFSummary(self.stock_ticker_list, store_location=self.storelocation,
                                 folder_name=self.foldername, filesave=self.filesave)
        myclass2.summary_scrap()

        # whether comprehensive analysis, comprehensive means including statement analysis
        if self.comprehensive:
            cagr_all = yfst.statements(self.stock_ticker_list, folder_name=self.foldername,
                                       file_save=self.filesave, store_location=self.storelocation)

            cagr = cagr_all[0]
            cagr_compare = cagr_all[1]
            cagr_list = list(cagr.columns)
            for ticker in cagr.columns:
                if trailing_pe_list[ticker] == 'N/A' or cagr.iloc[0, cagr_list.index(ticker)] == 'N/A':
                    implied_peg[ticker] = 0
                else:
                    implied_peg[ticker] = float(trailing_pe_list[ticker]) / cagr.iloc[0, cagr_list.index(ticker)] / 100

            if self.filesave:
                cagr_compare.to_csv(self.storelocation + self.foldername + self.separator + 'CAGR_COMPARE.csv')

        else:
            for ticker in self.ranking.columns:
                implied_peg[ticker] = 0

        # print result
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
        mystring = ''
        ignored_item_string = ''
        for key, value in zip(self.score.keys(), self.score.values()):
            col = int(list(myclass2.dataframe.iloc[5:7, :].columns).index(key))
            mystring += (key + ' Score: ' + str(round(value, 2)) +
                         ' Trailing PE: ' + trailing_pe_list[key] +
                         ' Implied PEG: ' + str(implied_peg[key]) + '  Potential: ' +
                         str(myclass2.dataframe.iloc[5:7, :].iloc[0, col]) +
                         '  Price Percentile: ' +
                         str(myclass2.dataframe.iloc[5:7, :].iloc[1, col]) + '\n')

        if myclass.ignored_stats:
            for item in myclass.ignored_stats:
                ignored_item_string += item + ', \n'

            ignored_item_string += ' has been ignored from the calculation of scores! \n' + ''
            print(ignored_item_string)

        print(mystring)
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

        # Store result
        result_col = ["Score", "Trailing PE", "Implied PEG", "Potential", "Price Percentile"]
        result_tickers = list(myclass2.dataframe.columns)
        result_dict = OrderedDict()

        # Creating result dictionary
        for item in result_tickers:
            result_dict[item] = [round(self.score[item], 2)]

        # Appending result dictionary
        for item in result_tickers:
            col = int(list(myclass2.dataframe.iloc[5:7, :].columns).index(item))
            result_dict[item].append(trailing_pe_list[item])                        # Trailing PE
            result_dict[item].append(implied_peg[item])                             # implied_PEG
            result_dict[item].append(myclass2.dataframe.iloc[5:7, :].iloc[0, col])  # potential
            result_dict[item].append(myclass2.dataframe.iloc[5:7, :].iloc[1, col])  # Price percentile

        if self.filesave:
            result_table = pandas.DataFrame(result_dict,result_col,result_tickers).transpose()
            result_table.to_csv(self.storelocation + self.foldername + self.separator + 'Score_Summary.csv')


if __name__ == '__main__':
    my_system = sys.platform

    user_input = input("Please select the ticker you wish you analyze: ")

    user_input = user_input.replace(' ', '').split(sep=",")

    my_user = getpass.getuser()

    if my_system == "linux" or my_system == "darwin":
        store_location = "/home/" + my_user + "/stock_data/"
    elif my_system == "win32":
        store_location = "D:\Yahoo Finance\Stock Data\\"

    mymain = ScrapperApp(user_input, foldername='Retail', comprehensive=True,
                         filesave=True, storelocation=store_location)
    mymain.scrapper_start()