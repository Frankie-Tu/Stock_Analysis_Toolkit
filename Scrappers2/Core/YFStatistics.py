from Scrappers2.Core.ScrapperAbstract import ScrapperAbstract


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
        print("data_parser")

    def csv_writer(self):
        print("writer")
