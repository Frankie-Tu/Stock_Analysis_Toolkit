from selenium.webdriver.common.by import By
import re
import time

from scrappers.web.yf_web_abstract import YfWebAbstract


class PortfolioAnalyzer(YfWebAbstract):
    def __init__(self):
        self.portfolio_sectors = {}
        super().__init__("https://ca.finance.yahoo.com/portfolios")
    
    def get_sector(self, ticker):
        
        #click on ticker
        self.find_element(By.LINK_TEXT, ticker).click()
        self.find_element(By.LINK_TEXT, "Profile").click()
        
        time.sleep(2)
        
        if "Fund Overview" not in list(map(lambda x: x.text, self.find_elements(By.TAG_NAME, "h3"))):
        
            # find the sector
            sector = self.find_element(By.CSS_SELECTOR, "p.D\(ib\).Va\(t\)").text
            sector = re.findall("Sector\(s\): (.*)\nIndustry", sector)

            if sector:
                sector = sector[0]
                if sector in self.portfolio_sectors.keys():
                    self.portfolio_sectors[sector].append(ticker)
                else:
                    self.portfolio_sectors[sector] = [ticker]
        
        self.driver.back()
        self.driver.back()
        
    def processing(self):
        self.pending_login()
        
        self.find_element(By.LINK_TEXT, "My Holdings").click()
        my_holdings = self.get_tickers()
        
        for ticker in my_holdings:
            self.get_sector(ticker)
        
        print(self.portfolio_sectors)
        
if __name__ == "__main__":
    PortfolioAnalyzer()