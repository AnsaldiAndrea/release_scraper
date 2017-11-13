"""release scraper"""
import pprint
from selenium import webdriver
from lxml import html
from package.seleniumhelper import wait_for_element, wait_for_elements, wait_for_clickable
from package.normal import *

pp = pprint.PrettyPrinter()

MONTH_DICT = {
    'gennaio': 1,
    'febbraio': 2,
    'marzo': 3,
    'aprile': 4,
    'maggio': 5,
    'giugno': 6,
    'luglio': 7,
    'agosto': 8,
    'settembre': 9,
    'ottobre': 10,
    'novembre': 11,
    'dicembre': 12
}

MONTH_NEXT = {
    'Gennaio': 'Febbraio',
    'Febbraio': 'Marzo',
    'Marzo': 'Aprile',
    'Aprile': 'Maggio',
    'Maggio': 'Giugno',
    'Giugno': 'Luglio',
    'Luglio': 'Agosto',
    'Agosto': 'Settembre',
    'Settembre': 'Ottobre',
    'Ottobre': 'Novembre',
    'Novembre': 'Dicembre',
    'Dicembre': 'Gennaio'
}


class WebScraper:
    """class for release scraping"""

    def __init__(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        self.data = []

    def main(self):
        """main"""
        self.planet()
        self.star()
        self.jpop()
        self.driver.quit()
        pp.pprint(self.data)
        print('count = {}'.format(len(self.data)))

    def extract(self):
        """extract"""
        self.planet()
        self.star()
        self.jpop()
        self.driver.quit()
        return self.data

    def planet(self):
        """get planet manga releases"""
        # this week releases
        self.driver.get("http://comics.panini.it/calendario/uscite-questa-settimana/")
        # print('parsing - this week - planet')
        self.parse_planet_manga(self.driver)
        # next week releases
        self.driver.get("http://comics.panini.it/calendario/uscite-prossime-settimane/")
        # print('parsing - next weeks - planet')
        self.parse_planet_manga(self.driver)

    def star(self):
        """get starcomics releases"""
        self.driver.get("https://www.starcomics.com/UsciteMensili.aspx")
        self.parse_starcomics(self.driver)

    def jpop(self):
        """get jpop releases"""
        self.driver.get('http://www.j-pop.it/blog')
        self.parse_jpop_news(self.driver)
        self.driver.get('http://www.j-pop.it/nuovi-prodotti')
        path = self.parse_jpop(self.driver)
        while path:
            self.driver.get(path)
            path = self.parse_jpop(self.driver)

    def parse_planet_manga(self, driver):
        """parse html pages for planet manga"""
        manga_filter = wait_for_element(driver, '//*[@id="c31384"]/a')
        manga_filter.click()
        wait_for_element(driver, '//*[@id="c31384"]/a[contains(@class,"active")]')

        items_x = "//div[@class='row list-group-item' and not(contains(@style,'display: none;'))]/div"
        title_x = "//h3[@class='product-name']/a/text()"
        sub_title_x = ".//small[@class='subtitle lightText']/text()"
        release_x = ".//span[@class='uscita itemValue']/text()"
        price_x = ".//div[@class='price']/text()"
        cover_x = ".//a[@class='product-image']/img/@src"

        items = wait_for_elements(driver, items_x)
        for item in items:
            element = html.fromstring(item.get_attribute("innerHTML"))
            item_values = self.data_from_elem(element,
                                              title_xpath=title_x,
                                              subtitle_xpath=sub_title_x,
                                              release_xpath=release_x,
                                              price_xpath=price_x,
                                              cover_xpath=cover_x)
            item_values['publisher'] = 'planet'
            self.data.append(item_values)

    def parse_starcomics(self, driver):
        """parse html pages for starcomics manga"""
        month_list = []
        while True:
            # Get page month
            month = wait_for_element(driver, '//td[@class="pager-count"]/span').text
            if month in month_list:
                break  # page has already been scraped
            month_list.append(month)
            pager = wait_for_elements(driver, '(//tr[@class="rigagriglia"])[2]/td')  # Get number of pages

            for i in range(len(pager[3:])):
                i_page_active_x = '(//tr[@class="rigagriglia"])[2]/td[{}][@class="pager-item active"]'.format(i + 3)
                wait_for_element(driver, i_page_active_x)  # wait for page to load

                items = wait_for_elements(driver, '//td[@itemprop="itemListElement"]')[4:]
                title_x = '//h4[@class="title"]/@title'
                release_x = '//p/span/text()'
                price_x = '//span[contains(@class,"price")]/span/text()'
                cover_x = '//div[@class="photo"]/a/img/@src'

                for item in items:
                    element = html.fromstring(item.get_attribute("innerHTML"))
                    item_values = self.data_from_elem(element,
                                                      title_xpath=title_x,
                                                      release_xpath=release_x,
                                                      price_xpath=price_x,
                                                      cover_xpath=cover_x)
                    item_values['cover'] = "https://www.starcomics.com/{}".format(item_values['cover'])
                    item_values['publisher'] = 'star'
                    self.data.append(item_values)

                wait_for_clickable(driver, '((//td[@class="pager-next"])[2]/a[1])').click()  # next page

            # go back to first page
            wait_for_clickable(driver, '(//tr[@class="rigagriglia"])[2]/td[2]/a[1]').click()
            wait_for_element(driver, '(//tr[@class="rigagriglia"])[2]/td[3][@class="pager-item active"]')
            # go to next month
            wait_for_clickable(driver, '(//td[@class="pager-next"]/a)[1]').click()

            next_month = MONTH_NEXT[re.match('(.*)\\s-\\s\\d+', month).group(1)]
            next_month_x = '//td[@class="pager-count"]/span[contains(text(),{})]'.format(next_month)
            wait_for_element(driver, next_month_x)

    def parse_jpop_news(self, driver):
        """parse jpop news"""
        news_x = '//div[@id="post_list"]/ul/li/div/h3/a[contains(text(),"Uscite") or contains(text(),"uscite")]'
        news = wait_for_elements(driver, news_x)
        while not news:
            wait_for_element(driver, '//a[@class="btn_right"]').click()
            news = wait_for_elements(driver, news_x)
        news_link = [x.get_attribute("href") for x in news[:min(len(news), 2)]]
        for link in news_link:
            driver.get(link)
            items_x = '//div[@class="rte"]/p'

            news_title = wait_for_element(driver, '//h2').text
            news_release = wait_for_element(driver, '//fieldset/p/span').text
            # extract when new volume woll be released
            release_date = self.get_release_date(news_release, news_title)

            paragraphs = wait_for_elements(driver, items_x)
            for p in [x.text for x in paragraphs[1:]]:
                item_values = {}
                p_data = [x for x in p.split('\n')]
                if not re.fullmatch('DIRECT \\d+', p_data[0]):
                    item_values['title_volume'] = p_data[0]  # title
                else:
                    continue
                item_values['subtitle'] = ''  # subtitle
                item_values['release_date'] = release_date
                temp = [x for x in p_data if '€' in x]
                item_values['price'] = ('0.00' if not temp else normalize_price(temp[0]))  # price
                item_values['cover'] = ''  # cover
                item_values['publisher'] = 'jpop'
                self.data.append(item_values)

    def parse_jpop(self, driver):
        """parse jpop releases"""
        items = wait_for_elements(driver, '//div[@id="products_wrapper"]/ul/li/div/div/div[@class="view-content"]')
        title_x = '//div[@class="name"]/a/@title'
        cover_x = '//div[@class="image"]/a/img/@src'
        price_x = '//p[@class="special-price"]/span/text()'
        for item in items:
            element = html.fromstring(item.get_attribute("innerHTML"))
            item_values = self.data_from_elem(element, title_xpath=title_x, price_xpath=price_x, cover_xpath=cover_x)
            item_values['cover'] = item_values['cover'].replace('home', 'large')
            item_values['publisher'] = 'jpop'
            self.data.append(item_values)
        next_page = wait_for_element(driver, '//a[contains(@class,"next i-next")]').get_attribute("href")
        return '' if next_page.endswith('#') else next_page

    @staticmethod
    def data_from_elem(element, title_xpath, subtitle_xpath=None, release_xpath=None, price_xpath=None,
                       cover_xpath=None):
        """get data from element given xpath"""
        data = {'title_volume': (element.xpath(title_xpath)[0]).strip(),
                'subtitle': WebScraper.value_from_xpath(element, subtitle_xpath),
                'release_date': normaliza_release_date(
                    date_str=WebScraper.value_from_xpath(element, release_xpath)),
                'price': normalize_price(WebScraper.value_from_xpath(element, price_xpath)),
                'cover': WebScraper.value_from_xpath(element, cover_xpath)
                }
        return data

    @staticmethod
    def value_from_xpath(element, xpath):
        """get value from xpath"""
        if not xpath: return ''
        values = element.xpath(xpath)
        if not values: return ''
        return values[0].strip()

    @staticmethod
    def get_release_date(news_release, news_title):
        """return release date of jpop news"""
        release = re.match('.*\\s(\\d{4})-(\\d{2})-(\\d{2})', news_release)
        release_date = (int(release.group(1)),
                        int(release.group(2)),
                        int(release.group(3)))
        title = re.match('.*[\\s|\'](\\d+)\\s([a-zA-Z]*)!?', news_title)
        title_date = (release_date[0],
                      MONTH_DICT[title.group(2).lower()],
                      int(title.group(1)))
        if release_date[1] == 12 and title_date[1] == 1:
            title_date = (title_date[0] + 1, title_date[1], title_date[2])
        return normaliza_release_date(date_tuple=title_date)


if __name__ == '__main__':
    WebScraper().main()
