import json
from operator import itemgetter

from lxml import html
from slugify import slugify

from package import xpath
from package.normal import *
from package.seleniumhelper import *
from publisher_parser import star, planet, jpop


def get_title_from_search(search, publisher):
    titles = []
    if publisher == 'planet':
        driver = firefox()
        driver.get("http://comics.panini.it/store/pub_ita_it/catalogsearch/result/?q={}".format(search))
        while True:
            next_page_x = "//a[@class='next i-next']"
            items_x = "//div[@id='products-list']/div"
            items = wait_for_elements(driver, items_x)
            for item in items:
                elem = html.fromstring(item.get_attribute('innerHTML'))
                title = xpath.value_from_xpath(elem, "//h3[@class='product-name']/a/@title")
                normal_title = normalize_title(title)
                if normal_title not in titles:
                    titles.append(normal_title)
            next_page = element_exist(driver, next_page_x)
            if next_page:
                next_page.click()
            else:
                driver.quit()
                return titles
    else:
        return []


class InfoFinder:
    """get info of a manga"""

    def __init__(self):
        self.manga_info = []
        self.related_releases = []
        self.related_collection = []
        self.driver = firefox()

    def find(self, manga_id, title, search, alias, publisher, ignore):
        """find info"""
        parsed_id = manga_id.split("_")[0]
        info = self.bakaupdates(parsed_id)
        info['id'] = manga_id
        info['title'] = title
        if publisher == 'planet':
            info['publisher'] = 'planet'
            release_list = planet.new_get_info(self.driver, manga_id, title, search, alias, ignore)
        elif publisher == 'star':
            info['publisher'] = 'star'
            release_list = star.get_info(self.driver, manga_id, title, search)
        elif publisher == 'jpop':
            info['publisher'] = 'jpop'
            release_list = jpop.get_info()
        else:
            release_list = []
        self.driver.close()
        self.calculate_released_and_cover(info, release_list)
        self.adjust(info)
        self.set_cover(info, release_list)
        return {'info': info, 'releases': release_list}

    def bakaupdates(self, manga_id):
        """get info from bakaupdates"""
        self.driver.get("https://www.mangaupdates.com/series.html?id={}".format(manga_id))
        page = html.fromstring(self.driver.page_source)
        original_x = "//span[@class='releasestitle tabletitle']/text()"
        original_title = xpath.value_from_xpath(page, original_x)
        status_x = "//div[@class='sCat']/b[text()='Status in Country of Origin']/../following-sibling::div[1]/text()"
        status = xpath.value_from_xpath(page, status_x)
        match = re.match('(\\d+)\\sVolume[s]?\\s(?:.*\\s)?\\((.*)\\)', status)
        status = (int(match.group(1)), match.group(2))
        # TODO: check refactoring
        author_x = "//div[@class='sCat']/b[text()='Author(s)']/../following-sibling::div[1]/a/u/text()"
        author = [self.format_person(x) for x in page.xpath(author_x)[0].split(',')]
        artist_x = "//div[@class='sCat']/b[text()='Artist(s)']/../following-sibling::div[1]/a/u/text()"
        artist = [self.format_person(x) for x in page.xpath(artist_x)[0].split(',')]
        #
        genre_x = "//div[@class='sCat']/b[text()='Genre']/../following-sibling::div[1]/a/u/text()"
        genre = xpath.values_from_xpath(page, genre_x)
        return {'original': original_title, 'status': status, 'genre': genre, 'author': author, 'artist': artist}

    @staticmethod
    def format_person(a):
        """format author and artist name"""
        parts = a.split()
        if len(parts) > 1:
            if '(' in parts[0]:
                return parts[1]
            elif '(' in parts[1]:
                return parts[0]
            parts[len(parts) - 1], parts[0] = parts[0], parts[len(parts) - 1]
            return ' '.join(parts).title()
        return a

    @staticmethod
    def calculate_released_and_cover(info, release_list):
        """calculate released volumes and cover from releases list"""
        out_release = filter(lambda i: i['release_date'].isocalendar()[:2] <= datetime.now().isocalendar()[:2],
                             release_list)
        info['released'] = max([x['volume'] for x in out_release], default=0)

        if not info['released'] == 0:
            c = sorted(filter(lambda x: x['volume'] == info['released'], release_list),
                       key=itemgetter('release_date'))
            info['cover'] = c[0]['cover']

        for x in release_list:
            x['release_date'] = normalize_release_date(date=x['release_date'])

    @staticmethod
    def adjust(info):
        """adjust info"""
        info['volumes'] = info['status'][0]
        info['complete'] = True if info['status'][1] == 'Complete' else False
        if info['complete'] and info['released'] == info['volumes']:
            info['status'] = 'complete'
        elif info['released'] == 0:
            info['status'] = 'tba'
        else:
            info['status'] = 'ongoing'
        info['cover'] = info['cover'] if 'cover' in info else ''

    @staticmethod
    def set_cover(info, releases):
        """if cover is missign set cover to first volume if available"""
        if releases and not info['cover']:
            x = [x for x in releases if x['volume']==1]
            if x:
                info['cover'] = x[0]['cover']


if __name__ == '__main__':
    with open("input.json") as j:
        s = j.read()
    _input = json.loads(s)
    test = _input[-1]
    a = InfoFinder().find(test['id'], title=test['title'], search=test['search'], alias=test.get('alias', []),
                          publisher=test['publisher'], ignore=test.get('ignore', []))
    with open('data/{}.json'.format(slugify(test['title'])), 'w+') as f:
        f.write(json.dumps(a, indent=5))
