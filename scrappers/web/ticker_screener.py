from lazy_scrapper.controller.decor import retry
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException 
import time

from scrappers.web.yf_web_abstract import YfWebAbstract


class TickerScreener(YfWebAbstract):
    def __init__(self, industry=None):
        self.url = "https://ca.finance.yahoo.com/screener/"
        self.industry = industry
        super().__init__(self.url)

    def processing(self):
        
        self.pending_login()
        
        industries = list(map(lambda x: x.text, self.driver.find_element(By.ID, "screener-landing-user-defined").find_elements(By.TAG_NAME, "a")[1:]))
        
        if self.industry:
            industries = list(filter(lambda x: x in self.industry, industries))
        
        payload = {}
        
        # clicking through the screeners
        for industry in industries:
            self.find_element(By.LINK_TEXT, industry).click()
            print(f"getting tickers for: {industry}")
            payload[industry]= self.get_tickers()
            self.driver.back()

        print(f"Payload is as follows: {payload}")
        

if __name__ == "__main__":
    sectors_to_screen = ["High Dividend", "Energy"]
    # TickerScreener(sectors_to_screen)
    TickerScreener()