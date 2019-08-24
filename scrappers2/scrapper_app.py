from scrappers2.core import yf_statement, yf_summary, yf_statistics
from scrappers2.utils.multi_threader import MultiThreader
from collections import OrderedDict
import pandas
import sys


class ScrapperApp:
    """
    Central control of Scrapper application

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param comprehensive: Boolean => whether to perform statement analysis
    """

    def __init__(self, tickers, store_location, folder_name, file_save, comprehensive):
        self.tickers = tickers
        self.store_location = store_location
        self.folder_name = folder_name
        self.file_save = file_save
        self.comprehensive = comprehensive

    @staticmethod
    def parallel_runner(class__):
        class__.run()

    def scrapper_start(self):
        c1 = yf_statistics.YFStatistics(self.tickers, self.store_location, self.folder_name, self.file_save)
        c2 = yf_summary.YFSummary(self.tickers, self.store_location, self.folder_name, self.file_save)
        MultiThreader.run_thread_pool([c1, c2], self.parallel_runner, 2)




if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=",")

    ScrapperApp(user_input, store_location="/Users/frankietu/repos/Stock_Analysis_Toolkit/tests", folder_name='test',
                file_save=True, comprehensive=True).scrapper_start()
