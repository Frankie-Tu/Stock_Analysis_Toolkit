from scrappers2.core.yf_statement import YFStatement
from scrappers2.core.yf_summary import YFSummary
from scrappers2.core.yf_statistics import YFStatistics
from scrappers2.core.analysis.cagr import CAGR
from scrappers2.utils.multi_threader import MultiThreader
from scrappers2.utils.config_reader import ConfigReader

from collections import OrderedDict
from time import strftime
import pandas
import sys
from pdb import set_trace


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
        self.start_time = strftime("%Y-%m-%d %H.%M.%S")

    @staticmethod
    def parallel_runner(class__):
        class__.run()

    def scrapper_start(self):
        implied_peg = OrderedDict()

        statistics = YFStatistics(self.tickers, self.store_location, self.folder_name, self.file_save, self.start_time)
        summary = YFSummary(self.tickers, self.store_location, self.folder_name, self.file_save, self.start_time)
        MultiThreader.run_thread_pool([statistics, summary], self.parallel_runner, 2)

        ranking = statistics.get_ranking()
        score = statistics.get_score()
        trailing_pe_list = statistics.get_downsized_df().iloc[0, :]

        if self.comprehensive:
            statement = YFStatement(self.tickers, self.store_location, self.folder_name, self.file_save, statement_type="IS", start_time=self.start_time)
            statement.run()
            cagr, cagr_compare = CAGR(statements=statement.get_statement(), statement_type="IS",start_time=self.start_time).run()
        else:
            for ticker in ranking.columns:
                implied_peg[ticker] = 0


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=",")
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")

    ScrapperApp(user_input, store_location=general_conf.get("store_location"),
                folder_name=general_conf.get("folder_name"),
                file_save=general_conf.get("file_save"), comprehensive=True).scrapper_start()
