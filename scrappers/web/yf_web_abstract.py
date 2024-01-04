from lazy_scrapper.controller.selenium import ChromeDriver
from lazy_scrapper.controller.decor import retry
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException 
import time

class YfWebAbstract(ChromeDriver):
    def __init__(self, url):
        super().__init__(url)
        
    def pending_login(self):
        # waiting for user login
        while True:
            try:
                if self.driver.find_element(By.ID, "uh-profile").text == "FRA":
                    break
            except NoSuchElementException:
                print("waiting for user login....")
                time.sleep(1)
    
    def get_tickers(self):
        return list(map(lambda x: x.text, self.find_elements(By.CSS_SELECTOR, '[data-test="quoteLink"]')))

    @retry
    def find_element(self, by, value):
        return self.driver.find_element(by,value)
    
    @retry 
    def find_elements(self, by, value):
        elems = self.driver.find_elements(by, value)
        
        if elems == []:
            raise Exception("Empty Array of Elements")
        
        return elems
    
    def processing(self):
        return super().processing()
    