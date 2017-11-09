import json
import pprint
from operator import itemgetter
from lxml import html
from package.normal import *
from package.seleniumhelper import *

pp = pprint.PrettyPrinter()
default_cover_planet = 'http://comics.panini.it/store/media/catalog/product/cache/80/image/9df78eab33525d08d6e5fb8d27136e95/placeholder/default/no-photo_265x265.jpg'


class InfoFinder:
    """get info of a manga"""

    def __init__(self):
        self.manga_info = []
        self.related_releases = []
        self.related_collection = []
        self.driver = firefox()

    def find(self, manga_id, title, search, alias, publisher):
        """find info"""
        parsed_id = manga_id.split("_")[0]
        info = self.bakaupdates(parsed_id)
        info['title'] = title
        if publisher == 'planet':
            release_list = self.planet(info, title, search, alias)
        else:
            release_list = []
        self.driver.close()
        self.adjust(info)
        cll = self.collection(release_list)
        return info, release_list, cll

    def bakaupdates(self, manga_id):
        """get info from bakaupdates"""
        self.driver.get("https://www.mangaupdates.com/series.html?id={}".format(manga_id))
        page = html.fromstring(self.driver.page_source)
        title_x = "//span[@class='releasestitle tabletitle']/text()"
        # original_title = page.xpath(title_x)[0].strip()
        status_x = "//div[@class='sCat']/b[text()='Status in Country of Origin']/../following-sibling::div[1]/text()"
        status = page.xpath(status_x)[0].strip()
        match = re.match('(\\d+)\\sVolumes\\s\\((\\w*)\\)', status)
        status = (int(match.group(1)), match.group(2))
        author_x = "//div[@class='sCat']/b[text()='Author(s)']/../following-sibling::div[1]/a/u/text()"
        author = [self.format_person(x) for x in page.xpath(author_x)[0].split(',')]
        artist_x = "//div[@class='sCat']/b[text()='Artist(s)']/../following-sibling::div[1]/a/u/text()"
        artist = [self.format_person(x) for x in page.xpath(artist_x)[0].split(',')]
        genre_x = "//div[@class='sCat']/b[text()='Genre']/../following-sibling::div[1]/a/u/text()"
        genre = page.xpath(genre_x)
        return {'id': manga_id, 'status': status, 'genre': genre, 'author': author, 'artist': artist}

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

    def planet(self, m, title, search, alias):
        """get all releases for a planetmanga manga"""
        normal_title = normalize_title(title)
        normal_alias = normalize_titles(alias)
        m['publisher'] = 'planet'
        self.driver.get("http://comics.panini.it/store/pub_ita_it/catalogsearch/result/?q={}".format(search))
        next_page_x = "//a[@class='next i-next']"
        data = []
        while True:
            items_x = "//div[@id='products-list']/div"
            items = wait_for_elements(self.driver, items_x)
            for item in items:
                value = {'title': title}
                elem = html.fromstring(item.get_attribute('innerHTML'))
                title_raw = elem.xpath("//h3[@class='product-name']/a/@title")[0]
                normal_title_raw = normalize_title(title_raw)
                if not normal_title == normal_title_raw and normal_title_raw not in normal_alias: continue
                title_volume = re.sub('\\s+', ' ', elem.xpath("//h3[@class='product-name']/a/text()")[0]).strip()
                try:
                    volume = int(re.sub(title_raw, '', title_volume).strip())
                    value['volume'] = volume
                except ValueError:
                    continue
                subtitle = elem.xpath("//small[@class='subtitle lightText']/text()")
                value['subtitle'] = re.sub('\\s+', ' ', subtitle[0]).strip() if subtitle else ''
                cover = elem.xpath("//a[@class='product-image']/img/@src")[0].strip().replace('small_image/200x',
                                                                                              'image')
                value['cover'] = cover
                release_date = elem.xpath("//h4[@class='publication-date']/text()")[0].strip()
                value['release_date'] = datetime.strptime(release_date, '%d/%m/%Y')
                price = normalize_price(elem.xpath("//p[@class='special-price']/span/text()")[0].strip())
                value['price'] = price
                data.append(value)

            next_page = element_exist(self.driver, next_page_x)
            if next_page:
                next_page.click()
            else:
                break

        release_list = sorted(data, key=itemgetter('release_date'))

        out_release = filter(lambda i: i['release_date'] <= datetime.now(), release_list)
        m['released_volumes'] = max([x['volume'] for x in out_release], default=0)

        if not m['released_volumes'] == 0:
            c = sorted(filter(lambda x: x['volume'] == m['released_volumes'], release_list),
                       key=itemgetter('release_date'))
            m['cover'] = c[0]['cover']

        for x in release_list:
            x['release_date'] = normaliza_release_date(date=x['release_date'])
        return release_list

    def star(self, title, alias):
        """star"""
        pass

    def jpop(self, title, alias):
        """jpop"""
        pass

    @staticmethod
    def adjust(info):
        """adjust info"""
        info['volumes'] = info['status'][0]
        info['complete'] = True if info['status'][1] == 'Complete' else False
        if info['complete'] and info['released_volumes'] == info['volumes']:
            info['status'] = 'Complete'
        elif info['released_volumes'] == 0:
            info['status'] = 'TBR'
        else:
            info['status'] = 'Ongoing'
        info['cover'] = info['cover'] if 'cover' in info else ''

    @staticmethod
    def collection(release_list):
        """get collection from list of releases"""
        cll = []
        if not release_list: return []
        volumes = max(release_list, key=itemgetter("volume"))
        if not volumes: return []
        volumes = volumes["volume"]
        dummy = release_list[0]
        for i in range(volumes):
            c = sorted(filter(lambda x: x['volume'] == i + 1, release_list), key=itemgetter('release_date'))
            if c:
                if len(c) > 1 and c[0]["cover"] == default_cover_planet:
                    cll.append(
                        {"title": c[1]["title"], "subtitle": c[1]["subtitle"], "volume": i + 1, "cover": c[1]["cover"]})
                else:
                    cll.append(
                        {"title": c[0]["title"], "subtitle": c[0]["subtitle"], "volume": i + 1, "cover": c[0]["cover"]})
            else:
                temp = {"title": dummy["title"], "subtitle": "", "volume": i + 1, "cover": ""}
                cll.append(temp)
        return cll


if __name__ == '__main__':
    with open("input.json") as j:
        s = j.read()
    _input = json.loads(s)
    test = _input[3]
    a = InfoFinder().find(test['id'], title=test['title'], search=test['search'], alias=test['alias'],
                          publisher=test['publisher'])
    print('info')
    print(json.dumps(a[0]))
    print('release')
    print(json.dumps(a[1]))
    print('collection')
    print(json.dumps(a[2]))
