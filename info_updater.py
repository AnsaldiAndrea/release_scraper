from lxml import html

from package import xpath
from package.normal import *
from package.seleniumhelper import *
from publisher_parser import star, planet, jpop
from publisher_parser.release_parser import ReleaseObject


class MangaInfo:
    def __init__(self):
        self.info = {"id": "", "original": "", "publisher": "planet", "status": "tba", "volumes": 0,
                     "released": 0, "author": [], "artist": [],
                     "cover": "", "genre": [], "complete": False}

    def get_id(self):
        return self.info['id']

    def set_id(self, id):
        self.info['id'] = id

    def get_title(self):
        return self.info['title']

    def set_title(self, title):
        self.info['title'] = title

    def get_original(self):
        return self.info['original']

    def set_original(self, original):
        self.info['original'] = original

    def get_publisher(self):
        return self.info['publisher']

    def set_publisher(self, publisher):
        self.info['publisher'] = publisher

    def get_status(self):
        return self.info['status']

    def set_status(self, status):
        self.info['status'] = status

    def get_volumes(self):
        return self.info['volumes']

    def set_volumes(self, volumes):
        self.info['volumes'] = volumes

    def get_released(self):
        return self.info['released']

    def set_released(self, released):
        self.info['released'] = released

    def get_author(self):
        return self.info['author']

    def set_author(self, author):
        self.info['author'] = author

    def get_artist(self):
        return self.info['artist']

    def set_artist(self, artist):
        self.info['artist'] = artist

    def get_cover(self):
        return self.info['cover']

    def set_cover(self, cover):
        self.info['cover'] = cover

    def get_genre(self):
        return self.info['genre']

    def set_genre(self, genre):
        self.info['genre'] = genre

    def get_complete(self):
        return self.info['complete']

    def set_complete(self, complete):
        self.info['complete'] = complete

    def as_dict(self):
        return self.info

    def as_dict_all(self):
        return {"id": self.manga_id, "original": self.original, "volumes": self.volumes,
                "author": self.author, "artist": self.artist, "complete": self.complete,
                "status": self.status}

    def as_dict_min(self):
        return {"id": self.manga_id, "volumes": self.volumes, "complete": self.complete}

    manga_id = property(get_id, set_id)
    title = property(get_title, set_title)
    original = property(get_original, set_original)
    status = property(get_status, set_status)
    publisher = property(get_publisher, set_publisher)
    volumes = property(get_volumes, set_volumes)
    released = property(get_released, set_released)
    author = property(get_author, set_author)
    artist = property(get_artist, set_artist)
    cover = property(get_cover, set_cover)
    genre = property(get_genre, set_genre)
    complete = property(get_complete, set_complete)


class InfoFinder:
    """get info of a manga"""

    def __init__(self):
        self.driver = firefox()
        self.manga_id = self.title = self.publisher = ""
        self.info = MangaInfo()
        self.release_list = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def get_info(self, manga_id, title, publisher):
        """get manga info"""
        self.manga_id = manga_id
        self.title = title
        self.publisher = publisher
        parsed_id = self.manga_id.split("_")[0]
        self.info = self.bakaupdates(parsed_id)
        self.info.manga_id = self.manga_id
        self.info.title = self.title
        self.info.publisher = self.publisher
        return self.info

    def get_updated_info(self, manga_id):
        parsed_id = manga_id.split("_")[0]
        self.info = self.bakaupdates(parsed_id)
        self.info.manga_id = manga_id

        return self.info

    def bakaupdates(self, manga_id):
        """get info from bakaupdates"""
        original_x = "//span[@class='releasestitle tabletitle']/text()"
        status_x = "//div[@class='sCat']/b[text()='Status in Country of Origin']/../following-sibling::div[1]/text()"
        author_x = "//div[@class='sCat']/b[text()='Author(s)']/../following-sibling::div[1]/a/u/text()"
        artist_x = "//div[@class='sCat']/b[text()='Artist(s)']/../following-sibling::div[1]/a/u/text()"
        genre_x = "//div[@class='sCat']/b[text()='Genre']/../following-sibling::div[1]/a/u/text()"

        self.driver.get("https://www.mangaupdates.com/series.html?id={}".format(manga_id))
        page = html.fromstring(self.driver.page_source)

        info = MangaInfo()
        info.original = xpath.value_from_xpath(page, original_x)
        status = xpath.value_from_xpath(page, status_x)
        match = re.match('^(\\d+)\\sVolume[s]?', status)
        info.volumes = int(match.group(1))
        info.complete = "Complete" in status
        info.author = [self.fix_name(x) for x in page.xpath(author_x)[0].split(',')]
        info.artist = [self.fix_name(x) for x in page.xpath(artist_x)[0].split(',')]
        info.genre = xpath.values_from_xpath(page, genre_x)
        return info

    @staticmethod
    def fix_name(name):
        """remove string in parentesis from name"""
        return re.sub("[(].*[)]", '', name).strip().title()

    def get_releases(self, search):
        """get releases given a search term"""
        if self.publisher == 'planet':
            self.release_list = planet.get_releases(self.driver, search)
        elif self.publisher == 'star':
            self.release_list = star.get_info(self.driver, 0, "title", search)
        elif self.publisher == 'jpop':
            self.release_list = jpop.get_info()
        return self.release_list

    def get_alias(self):
        """get all titles from searched releases"""
        alias = []
        if self.release_list:
            for r in self.release_list:
                release = ReleaseObject(r)
                release.publisher = self.info.publisher
                release.parse()
                if normalize_title(release.title) not in alias:
                    alias.append(normalize_title(release.title))
        return alias
