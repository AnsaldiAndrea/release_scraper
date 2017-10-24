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
from datetime import datetime
import re
from tabulate import tabulate
from lib.seleniumhelper import *
from operator import itemgetter

pp = pprint.PrettyPrinter()

class InfoFinder():

    def __init__(self):
        self.manga_info = []
        self.related_releases = []
        self.related_collection = []
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)

    def find(self,id, title, alias, publisher):
        parsed_id = id.split("_")[0]
        baka = self.bakaupdates(parsed_id)
        baka['title']=title
        if publisher is 'planet':
            self.planet(baka,title,alias)
        print(baka)

        self.driver.close()
        pass

    def bakaupdates(self,id):
        self.driver.get("https://www.mangaupdates.com/series.html?id={}".format(id))
        page = html.fromstring(self.driver.page_source)
        titleX = "//span[@class='releasestitle tabletitle']/text()"
        original_title = page.xpath(titleX)[0].strip()
        #print(page.xpath(titleX)[0].strip())
        statusX = "//div[@class='sCat']/b[text()='Status in Country of Origin']/../following-sibling::div[1]/text()"
        status = page.xpath(statusX)[0].strip()
        match = re.match('(\\d+)\\sVolumes\\s\\((\\w*)\\)',status)
        if match:
            #print('{}, {}'.format(match.group(1),match.group(2)))
            status = (int(match.group(1)),match.group(2))
        else:
            #print('error parsing string')
            status = ()
        authorX = "//div[@class='sCat']/b[text()='Author(s)']/../following-sibling::div[1]/a/u/text()"
        author = [self.format_person(x) for x in page.xpath(authorX)[0].split(',')]
        artistX = "//div[@class='sCat']/b[text()='Artist(s)']/../following-sibling::div[1]/a/u/text()"
        artist = [self.format_person(x) for x in page.xpath(artistX)[0].split(',')]
        genreX = "//div[@class='sCat']/b[text()='Genre']/../following-sibling::div[1]/a/u/text()"
        genre = page.xpath(genreX)
        return {'status':status,'genre':genre,'author':author,'artist':artist}

    def format_person(self,a):
        parts = a.split()
        if len(parts)>1:
            parts[len(parts)-1],parts[0] = parts[0],parts[len(parts)-1]
            return ' '.join(parts).title()
        return a

    def planet(self,m,title,search,alias):
        n_title = normalize_title(title)
        m['publisher']='planet'
        self.driver.get("http://comics.panini.it/store/pub_ita_it/catalogsearch/result/?q={}".format(alias[0]))
        next_pageX = "//a[@class='next i-next']"
        data = []
        while True:
            itemsX = "//div[@id='products-list']/div"
            items = wait_for_elements(self.driver, itemsX)
            for item in items:
                value = {'title':title}
                elem = html.fromstring(item.get_attribute('innerHTML'))
                p_title = elem.xpath("//h3[@class='product-name']/a/@title")[0]
                normalize_p_title = re.sub('[^\\w]*','',p_title)
                if not normalize_title == normalize_p_title: continue
                title_volume = re.sub('\\s+',' ',elem.xpath("//h3[@class='product-name']/a/text()")[0]).strip()
                try:
                    volume = int(re.sub(p_title, '', title_volume).strip())
                    value['volume']=volume
                except Exception:
                    continue
                subtitle = elem.xpath("//small[@class='subtitle lightText']/text()")
                value['subtitle'] = re.sub('\\s+',' ',subtitle[0]).strip() if subtitle else ''
                cover = elem.xpath("//a[@class='product-image']/img/@src")[0].strip().replace('small_image/200x','image')
                value['cover']=cover
                release_date = elem.xpath("//h4[@class='publication-date']/text()")[0].strip()
                value['release_date']=datetime.strptime(release_date, '%d/%m/%Y')
                price = normalize_price(elem.xpath("//p[@class='old-price']/span/text()")[0].strip())
                value['price']=price
                data.append(value)
            try:
                wait_for_element(self.driver,next_pageX).click()
            except Exception as e:
                break

        release_list = sorted(data, key=itemgetter('release_date'))

        r_v = max(filter(lambda x: x['release_date']<=datetime.now(),release_list), key=itemgetter('volume'))
        released_volume = r_v['volume']
        m['released_volume']=released_volume

        print('Release List:')
        pp.pprint(release_list)

    def star(self,title,alias):
        pass

    def jpop(self,title,alias):
        pass


    def export(self,filename):
        pass

    def tostring(self,data):
        pass

def normalize_title(title):
    return re.sub('[^\\w]*','',title).lower()

def normalize_titles(titles):
    return [normalize_title(title) for title in titles]

if __name__ == '__main__':
    #InfoFinder().find("118656","Happiness","Happiness","planet")
    InfoFinder().find("80345","One-Punch Man", ["One-Punch Man"], "planet")
    InfoFinder().find("412","Fullmetal Alchemist", search="Fullmetal Alchemist", alias=["Fullmetal Alchemist","Fullmetal Alchemist: L'Alchimista d'Acciaio"], "planet")
    print
