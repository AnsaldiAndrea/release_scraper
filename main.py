from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.common.exceptions import TimeoutException
from lxml import html
from io import StringIO, BytesIO
import pprint
import locale
import datetime
import re
from tabulate import tabulate
import pygsheets

pp = pprint.PrettyPrinter()

month_dict = {
    'gennaio':1,
    'febbraio':2,
    'marzo':3,
    'aprile':4,
    'maggio':5,
    'giugno':6,
    'luglio':7,
    'agosto':8,
    'settembre':9,
    'ottobre':10,
    'novembre':11,
    'dicembre':12
}

month_next = {
    'Gennaio':'Febbraio',
    'Febbraio':'Marzo',
    'Marzo':'Aprile',
    'Aprile':'Maggio',
    'Maggio':'Giugno',
    'Giugno':'Luglio',
    'Luglio':'Agosto',
    'Agosto':'Settembre',
    'Settembre':'Ottobre',
    'Ottobre':'Novembre',
    'Novembre':'Dicembre',
    'Dicembre':'Gennaio'
}


class WebScraper():

    def main(self):
        self.setUp()
        self.planet()
        self.star()
        self.jpop()
        self.tearDown()

    def setUp(self):
        # PhantomJS driver -- service_args=['--load-images=no']
        '''
            self.driver = webdriver.PhantomJS(service_args=['--load-images=no'])
        '''
        # Firefox driver without image loading
        #'''
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        #'''
        self.data = []
        client = pygsheets.authorize(service_file='client_secret.json',no_cache=True)

        # Find a workbook by name
        self.mainsheet = client.open("RawData")

    def planet(self):
        # this week releases
        self.driver.get("http://comics.panini.it/calendario/uscite-questa-settimana/")
        print('parsing - this week - planet')
        self.parse_planet_manga(self.driver)
        # next week releases
        self.driver.get("http://comics.panini.it/calendario/uscite-prossime-settimane/")
        print('parsing - next weeks - planet')
        self.parse_planet_manga(self.driver)

    def star(self):
        self.driver.get("https://www.starcomics.com/UsciteMensili.aspx")
        self.parse_starcomics(self.driver)

    def jpop(self):
        self.driver.get('http://www.j-pop.it/blog/category/2-ultime-uscite')
        self.parse_jpop_news(self.driver)
        self.driver.get('http://www.j-pop.it/nuovi-prodotti')
        print('parsing - http://www.j-pop.it/nuovi-prodotti - jpop')
        path = self.parse_jpop(self.driver)
        while path:
            print('parsing - {} - jpop'.format(path))
            self.driver.get(path)
            path=self.parse_jpop(self.driver)

    def tearDown(self):
        #print(tabulate(self.data))
        self.driver.quit()
        print('updating sheet')
        sheet = self.mainsheet.worksheet(property='title', value='releases')
        sheet.resize(len(self.data)-1,6)
        sheet.clear()
        sheet.insert_rows(row=0,values=self.data)
        sheet.sync()

    def parse_planet_manga(self,driver):
        mangaFilterXpath = '//*[@id="c31384"]/a'
        mangaFilterElement = wait_for_element(driver,mangaFilterXpath)
        mangaFilterElement.click()
        wait_for_element(driver, '//*[@id="c31384"]/a[contains(@class,"active")]')

        itemsX = "//div[@class='row list-group-item' and not(contains(@style,'display: none;'))]/div"
        titleX = "//h3[@class='product-name']/a/text()"
        subTitleX = ".//small[@class='subtitle lightText']/text()"
        releaseX = ".//span[@class='uscita itemValue']/text()"
        priceX = ".//div[@class='old-price']/text()"
        coverX = ".//a[@class='product-image']/img/@src"

        items = wait_for_elements(driver,itemsX)
        for item in items:
            item_values = []
            element = html.fromstring(item.get_attribute("innerHTML"))
            item_values.append(element.xpath(titleX)[0].strip())
            try:
                item_values.append(element.xpath(subTitleX)[0].strip())
            except Exception:
                item_values.append('')
            item_values.append(element.xpath(releaseX)[0])
            item_values.append(normalize_price(element.xpath(priceX)[0]))
            item_values.append(element.xpath(coverX)[0])
            item_values.append('planet')
            self.data.append(item_values)

    def parse_starcomics(self,driver):
        month_list = []
        while True:
            monthX = '//td[@class="pager-count"]/span'
            # Get page month
            month = wait_for_element(driver,monthX)
            month_name = month.text
            # If mont_list contains month stop otherwise add month to mont_list
            if month_name in month_list:
            # page has already been scraped
                break
            else:
                month_list.append(month_name)
            # Get number of pages
            pagerX = '(//tr[@class="rigagriglia"])[2]/td'
            pager = wait_for_elements(driver, pagerX)
            page_count = len(pager[3:])
            #print(page_count)

            itemsX = '//td[@itemprop="itemListElement"]'
            for i in range(page_count):
                # wait for page to load
                i_page_activeX = '(//tr[@class="rigagriglia"])[2]/td[{}][@class="pager-item active"]'.format(i+3)
                wait_for_element(driver,i_page_activeX)
                print('parsing - {} p.{} - starcomics'.format(month_name, i+1))

                items = wait_for_elements(driver,itemsX)
                items = items[4:]

                titleX = '//h4[@class="title"]/@title'
                releaseX = '//p/span/text()'
                priceX = '//span[contains(@class,"price")]/span/text()'
                coverX = '//div[@class="photo"]/a/img/@src'

                #print('\n\tPage = {}'.format(i+1))
                for item in items:
                    item_values = []
                    element = html.fromstring(item.get_attribute("innerHTML"))
                    try:
                        item_values.append(element.xpath(titleX)[0].strip())
                        item_values.append('')
                        item_values.append(element.xpath(releaseX)[0])
                        item_values.append(normalize_price(element.xpath(priceX)[0]))
                        item_values.append("https://www.starcomics.com/{}".format(element.xpath(coverX)[0]))
                        item_values.append('star')
                    except Exception:
                        print('skipped release - starcomics')
                        item_values.clear()
                        continue
                    self.data.append(item_values)

                #wait_for_element(driver,'((//td[@class="pager-next"])[2]/a[1]/span[@class="wrap"]/span[@class="icon"])')
                next_pageX = '((//td[@class="pager-next"])[2]/a[1])'
                next_page = wait_for_clickable(driver,next_pageX)
                next_page.click()
                print('next page clicked')

            # go back to first page
            wait_for_clickable(driver,'(//tr[@class="rigagriglia"])[2]/td[2]/a[1]').click()
            wait_for_element(driver,'(//tr[@class="rigagriglia"])[2]/td[3][@class="pager-item active"]')
            print('first page clicked')
            #go to next month
            next_month = wait_for_clickable(driver,'(//td[@class="pager-next"]/a)[1]')
            next_month.click()
            print('next month clicked')

            wait(driver, 10)
            next_month_name = month_next[re.match('(.*)\\s-\\s\\d+',month_name).group(1)]
            next_month_nameX = '//td[@class="pager-count"]/span[contains(text(),{})]'.format(next_month_name)
            wait_for_element(driver,next_month_nameX)

    def parse_jpop_news(self,driver):
        news = wait_for_elements(driver,'//div[@id="post_list"]/ul/li/div/h3/a[contains(text(),"Uscite") or contains(text(),"uscite")]')
        if(len(news)==0):
            elem = wait_for_element(driver, '//a[@class="btn_right"]')
            elem.click()
            self.parse_jpop_news(driver)
            pass
        news_link = [x.get_attribute("href") for x in news[:min(len(news),2)]]
        for link in news_link:
            success=False
            while not success:
                driver.get(link)
                print('parsing - {} - jpop'.format(driver.current_url))
                itemsX = '//div[@class="rte"]/p'
                news_titleX = '//h2'
                news_releaseX = '//fieldset/p/span'

                news_title = wait_for_element(driver,news_titleX).text
                news_release = wait_for_element(driver,news_releaseX).text
                #print([news_title,news_release])

                # extract when new volume woll be released
                try:
                    release_date = re.match('.*\\s(\\d{4})-(\\d{2})-(\\d{2})', news_release)
                    release_tuple = (int(release_date.group(1)),int(release_date.group(2)),int(release_date.group(3)))
                    title_date = re.match('.*\\s(\\d+)\\s([a-zA-Z]*)!?', news_title)
                    title_tuple = (release_tuple[0], month_dict[title_date.group(2).lower()], int(title_date.group(1)))
                    if release_tuple[1]==12 and title_tuple[1]==1:
                        title_tuple[0]+=1
                    #print([title_tuple,release_tuple])
                except Exception:
                    print('failed release date parsing at {} - trying again - jpop'.format(driver.current_url))
                    continue

                paragraphs = wait_for_elements(driver, itemsX)
                p_text = [x.text for x in paragraphs[1:]]
                for p in p_text:
                    item_values = []
                    p_data = [x for x in p.split('\n')]
                    if not re.fullmatch('DIRECT \\d+', p_data[0]):
                        item_values.append(p_data[0])	# title
                    else:
                        continue
                    item_values.append('')			# subtitle
                    item_values.append(datetime.datetime(title_tuple[0],title_tuple[1],title_tuple[2]).strftime('%d/%m/%Y'))	# release date
                    temp = [x for x in p_data if '€' in x]
                    item_values.append('0.00' if len(temp)==0 else normalize_price(temp[0]))	# price
                    item_values.append('')			# cover
                    item_values.append('jpop')
                    self.data.append(item_values)
                    success=True

    def parse_jpop(self,driver):
        itemsX = '//div[@id="products_wrapper"]/ul/li/div/div/div[@class="view-content"]'
        items = wait_for_elements(driver,itemsX)
        titleX = '//div[@class="name"]/a/@title'
        coverX = '//div[@class="image"]/a/img/@src'
        priceX = '//p[@class="special-price"]/span/text()'
        for item in items:
            item_values = []
            element = html.fromstring(item.get_attribute("innerHTML"))
            item_values.append(element.xpath(titleX)[0])
            item_values.append('')
            item_values.append('')
            item_values.append(normalize_price(element.xpath(priceX)[0]))
            item_values.append(element.xpath(coverX)[0])
            item_values.append('jpop')
            self.data.append(item_values)
        next_page = wait_for_element(driver,'//a[contains(@class,"next i-next")]').get_attribute("href")
        return '' if next_page.endswith('#') else next_page


def wait_for_element(driver,xpath):
    return wait(driver,10).until((lambda driver : driver.find_element_by_xpath(xpath)))

def wait_for_elements(driver,xpath):
    return wait(driver,10).until((lambda driver : driver.find_elements_by_xpath(xpath)))

def wait_for_clickable(driver,xpath):
    return wait(driver,10).until(expected_conditions.element_to_be_clickable((By.XPATH,xpath)))

def normalize_price(price):
    return price.replace('€','').replace(',','.').strip()

if __name__ == '__main__':
    WebScraper().main()
