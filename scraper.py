"""release scraper"""
from package.seleniumhelper import firefox
from publisher_parser import jpop as jpop_parser
from publisher_parser import planet as planet_parser
from publisher_parser import star as star_parser


class WebScraper:
    """class for release scraping"""

    def __init__(self):
        self.driver = firefox()
        self.data = []

    def extract(self, planet=True, planet_old=False, star=True, jpop=True, jpop_news=True):
        """extract"""
        if planet:
            self.data += planet_parser.parse(self.driver, old=planet_old)
        if star:
            self.data += star_parser.parse(self.driver)
        if jpop or jpop_news:
            self.data += jpop_parser.parse(driver=self.driver, news=jpop_news, releases=jpop)
        self.driver.quit()
        return self.data
