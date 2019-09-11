from scrappers.core.scrapper_abstract import ScrapperAbstract
from scrappers.utils.multi_threader import MultiThreader
from scrappers.utils.data_writer import DataWriter
from scrappers.utils.config_reader import ConfigReader

from collections import OrderedDict
import pandas as pd
import re
from time import strftime
from pdb import set_trace

class YFSummary(ScrapperAbstract):
    """
    Note: Scrap data from Summary Tab

    Please input a list array of stock tickers you wish to scrap.
    This Class scraps data off Yahoo Finance for the tickers selected.

    :param args: list[String] => list of ticker names
    :param store_location: String => root directory on hard drive to save output
    :param folder_name: String => folder name to be created in the directory of store_location
    :param file_save: Boolean => whether to save the output
    :param start_time: strftime => start time of the application for log timestamp
    """

    def __init__(self, args, store_location, folder_name, file_save, start_time=strftime("%Y-%m-%d %H.%M.%S")):
        super().__init__(tickers=args, store_location=store_location, folder_name=folder_name,
                         file_save=file_save, start_time=start_time, logger_name=__name__)
        self._dataframe = None

    def data_parser(self, ticker):
        """
        Method is used by YFSummary Class to parse html
        data from Summary tab on Yahoo Finance.

        :return: None
        """
        result_dict = OrderedDict()

        url = "https://ca.finance.yahoo.com/quote/" + ticker + "?p=" + ticker

        try:
            # fetch data
            self._logger.info("{}: Sending requests...".format(ticker))
            my_soup = self.requester(url)
            all_html = my_soup.find_all('table', {'class': "W(100%)"})
            fifty2_week_range = all_html[0].find_all('tr', {'class': re.compile(r'^(Bxz\(bb\) Bdbw\(1px\) Bdbs\(s\) Bdc\(\$c-fuji-grey-c\) H\(36px\)){1}.*')})[5]
            fifty2_week_range_value = fifty2_week_range.find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)'})[0].text.split(sep=' - ')
            fifty2_week_range_low = fifty2_week_range_value[0]
            fifty2_week_range_high = fifty2_week_range_value[1]

            # 1y Target Est
            self._logger.info('{}: Scrapping 1 year target estimates'.format(ticker))
            all_html = my_soup.find_all('table', {'class': "W(100%) M(0) Bdcl(c)"})
            one_year_target = all_html[0].find_all('tr', {'class': re.compile(r'(Bxz\(bb\) Bdbw\(1px\) Bdbs\(s\) Bdc\(\$c-fuji-grey-c\) H\(36px\) Bdbw\(0\)!){1}.*')})[0]\
                .find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)'})[0].span.text

            # Stock price.
            self._logger.info('{}: Scrapping price info & percentage change'.format(ticker))
            all_html_2 = my_soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})

            current_price = all_html_2[0].div.span.text

            # Stock price change
            change = all_html_2[0].div.find_all('span', {'class': re.compile(r"Trsdu\(0.3s\) Fw\(500\) Fz\(14px\)")})[0]\
                .text.split(sep=' ')[1].replace('(', "").replace(')', "").replace('%', '')
            change = str(float(change) / 100)

        except IndexError:
            self._logger.exception("{}: returned html not in expected format".format(ticker))
            raise IndexError

        # Append result
        fifty2_week_range_high, fifty2_week_range_low, current_price = list(map(lambda x: x.replace(',', ''), [fifty2_week_range_high, fifty2_week_range_low, current_price]))

        result_dict['52 Week Low'] = float(fifty2_week_range_low)
        result_dict['52 Week High'] = float(fifty2_week_range_high)

        if one_year_target == 'N/A':
            result_dict['1y Target Est'] = 0
        else:
            result_dict['1y Target Est'] = float(one_year_target.replace(',', ''))

        result_dict['Change %'] = float(change)
        result_dict['Current Price'] = float(current_price)

        # Based on target
        self._logger.info('{}: Calculating growth potential and current price percentile'.format(ticker))
        result_dict['Growth Potential'] = float(result_dict['1y Target Est']) / float(result_dict['Current Price']) - 1
        result_dict['52 Week Percentile'] = (float(result_dict['Current Price']) - float(result_dict['52 Week Low'])) / \
                                            (float(result_dict['52 Week High']) - float(result_dict['52 Week Low']))

        col = []
        val = []

        # Transfer info from result_dict to col and val list
        for key, value in zip(result_dict.keys(), result_dict.values()):
            col.append(key)
            val.append(round(value, 4))

        # if self._dataframe already exists, append only
        self._lock.acquire()
        self._logger.debug("{} locked".format(ticker))

        if isinstance(None, type(self._dataframe)):
            self._logger.info('Creating dataframe...')
            self._dataframe = pd.DataFrame(val, col, columns=[ticker])
        else:
            self._logger.info('Appending ' + ticker + ' to dataframe')
            self._dataframe[ticker] = val

        self._lock.release()
        self._logger.debug("{} unlocked".format(ticker))

    def run(self):
        # parsing data for multiple stock symbols in parallel
        MultiThreader.run_thread_pool(self._tickers, self.data_parser, 15)

        if self._file_save:
            DataWriter(self._logger).csv_writer(self._store_location, self._folder_name, "Summary_data.csv", self._dataframe)

    def get_summary(self):
        return self._dataframe


if __name__ == "__main__":
    user_input = input("Please select the ticker you wish you analyze: ")
    user_input = user_input.replace(' ', '').split(sep=',')
    config = ConfigReader().get_configurations()
    general_conf = config.get("general")

    if user_input == [""]:
        user_input = general_conf.get("symbols")

    YFSummary(user_input, store_location=general_conf.get("store_location"),
                 folder_name=config.get("summary").get("folder_name"), file_save=general_conf.get("file_save")).run()
