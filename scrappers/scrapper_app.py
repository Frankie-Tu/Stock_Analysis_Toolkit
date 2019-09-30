from scrappers.core.yf_statement import YFStatement
from scrappers.core.yf_summary import YFSummary
from scrappers.core.yf_statistics import YFStatistics
from scrappers.core.analysis.growth_analysis import CAGR, YoYGrowth
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.config_reader import ConfigReader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.logger import Logger
from scrappers.core.analysis.proportion import Proportion

from collections import OrderedDict
from time import strftime
from pandas import DataFrame
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

    def __init__(self, tickers, store_location, file_save, comprehensive):
        self.tickers = tickers
        self.store_location = store_location
        self.file_save = file_save
        self.comprehensive = comprehensive
        self.start_time = strftime("%Y-%m-%d %H.%M.%S")
        self.logger = Logger(__name__, start_time=self.start_time).get_logger()
        self.config = ConfigReader("application_configurations.json").get_configurations()

    @staticmethod
    def parallel_runner(class__):
        class__.run()

    def scrapper_start(self):
        implied_peg = OrderedDict()

        statistics = YFStatistics(self.tickers, self.store_location, self.config.get("statistics").get("folder_name"), self.file_save, self.start_time)
        summary = YFSummary(self.tickers, self.store_location, self.config.get("summary").get("folder_name"), self.file_save, self.start_time)
        MultiThreader.run_thread_pool([statistics, summary], self.parallel_runner, 2)

        ranking = statistics.get_ranking()
        score = statistics.get_score()
        ignored_stats = statistics.get_ignored_stats()
        summary_data = summary.get_summary()
        trailing_pe_list = statistics.get_downsized_df().iloc[0, :]

        if self.comprehensive:
            statement = YFStatement(self.tickers, self.store_location, self.config.get("statement").get("IS").get("folder_name"), self.file_save, statement_type="IS", start_time=self.start_time)
            statement.run()
            cagr, cagr_compare = CAGR(statements=statement.get_statement("growth"), statement_type="IS",start_time=self.start_time).run()

            statements = statement.get_statement("raw")
            #Proportion(statements, "IS", self.start_time).run()

            for ticker in self.tickers:
                if trailing_pe_list[ticker] == "N/A" or cagr.get(ticker) == "N/A":
                    implied_peg[ticker] = 0
                else:
                    implied_peg[ticker] = float(trailing_pe_list[ticker]) / cagr.get(ticker) / 100

            if self.file_save:
                DataWriter(self.logger).csv_writer(self.store_location, "", "CAGR_COMPARE.csv", cagr_compare)
        else:
            for ticker in ranking.columns:
                implied_peg[ticker] = 0

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
        summary_dict = OrderedDict()
        summary_columns = ["Score", "Trailing PE", "Implied PEG", "Potential", "Price Percentile"]

        for ticker, value in zip(score.keys(), score.values()):
            ticker_data = [round(value, 2), trailing_pe_list[ticker],
                           implied_peg[ticker], str(summary_data.loc["Growth Potential", ticker]),
                           str(summary_data.loc["52 Week Percentile", ticker])]

            summary_dict[ticker] = ticker_data

        summary_df = DataFrame(summary_dict, index=summary_columns).transpose()

        print(summary_df)

        if ignored_stats:
            print("ignored items:")
            for column in ignored_stats.keys():
                print("{}: {}".format(column, ignored_stats.get(column)))

        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

        if self.file_save:
            DataWriter(self.logger).csv_writer(self.store_location, "", "SCORE_COMPARE.csv", summary_df)


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=",")
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")[0]

    ScrapperApp(user_input, store_location=general_conf.get("store_location"),
                file_save=general_conf.get("file_save"), comprehensive=True).scrapper_start()
