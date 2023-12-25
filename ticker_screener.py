from lazy_scrapper.controller.selenium import ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException 
import time

class TickerScreener(ChromeDriver):
    def __init__(self):
        self.url = "https://ca.finance.yahoo.com/screener/"
        super().__init__(self.url)

    def processing(self):        
        # waiting for user login
        while True:
            try:
                if self.driver.find_element(By.ID, "uh-profile").text == "FRA":
                    break
            except NoSuchElementException:
                print("waiting for user login....")
                time.sleep(5)
        
        industries = list(map(lambda x: x.text, self.driver.find_element(By.ID, "screener-landing-user-defined").find_elements(By.TAG_NAME, "a")[1:]))
        
        # clicking through the screeners
        for industry in industries:
            self.driver.find_element(By.LINK_TEXT, industry).click()
            time.sleep(5)
            self.driver.back()
            time.sleep(2)
        

if __name__ == "__main__":
    TickerScreener()