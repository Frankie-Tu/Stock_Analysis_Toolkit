from lazy_scrapper.controller.selenium import ChromeDriver
from lazy_scrapper.controller.decor import retry
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException 
import time

class TickerScreener(ChromeDriver):
    def __init__(self, industry=None):
        self.url = "https://ca.finance.yahoo.com/screener/"
        self.industry = industry
        super().__init__(self.url)
    
    @retry
    def get_tickers(self):
        tickers = list(map(lambda x: x.text, self.driver.find_element(By.ID, "screener-results").find_elements(By.CSS_SELECTOR, '[data-test="quoteLink"]')))
        return tickers

    @retry
    def find_element(self, by, value):
        return self.driver.find_element(by,value)
    
    @retry 
    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def processing(self):        
        # waiting for user login
        while True:
            try:
                if self.driver.find_element(By.ID, "uh-profile").text == "FRA":
                    break
            except NoSuchElementException:
                print("waiting for user login....")
                time.sleep(1)
        
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