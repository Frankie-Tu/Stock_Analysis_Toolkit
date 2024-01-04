from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException 
import time

from scrappers.web.yf_web_abstract import YfWebAbstract


class PortfolioAnalyzer(YfWebAbstract):
    def __init__(self):
        super().__init__("https://ca.finance.yahoo.com/portfolios")
        
    def processing(self):
        self.pending_login()
        
        self.find_element(By.LINK_TEXT, "My Holdings").click()
        my_holdings = self.get_tickers()
        print(my_holdings)
        
if __name__ == "__main__":
    PortfolioAnalyzer()