import json
from scraper import WebScraper
import sqlite3
from package.web_api import parse_release, upload_release


class SimpleDatabase():

    def __enter__(self):
        return self

    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)
        c = self.connection.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS ENTRIES (value TEXT PRIMARY KEY )")
        self.connection.commit()

    def get_all(self):
        c = self.connection.cursor()
        tuples = c.execute("SELECT value FROM ENTRIES").fetchall()
        return [x[0] for x in tuples]

    def is_value_in(self, value):
        value = self.normal(value)
        c = self.connection.cursor()
        return c.execute("SELECT value FROM ENTRIES WHERE value=?", value).fetchone()

    def remove_value(self, value):
        value = self.normal(value)
        c = self.connection.cursor()
        c.execute("DELETE FROM ENTRIES WHERE value=?",value)
        self.connection.commit()

    def add_value(self, value):
        if not self.is_value_in(value):
            value = self.normal(value)
            c = self.connection.cursor()
            c.execute("INSERT INTO ENTRIES VALUES(?)", value)
            self.connection.commit()

    @staticmethod
    def normal(value):
        return tuple([json.dumps(value, ensure_ascii=False)])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.connection.close()


def get_cached_data():
    return json.load(open("cached.log"))


def get_data(cached=False):
    if cached:
        return get_cached_data()
    _data = WebScraper().extract(planet_old=True, star=False)
    with open("cached.log", "w+") as x:
        x.write(json.dumps(_data, ensure_ascii=False, indent=4))
    return _data


j_releases = []
j_news = []


def filter_jpop_releases(release):
    if release['publisher'] == 'jpop':
        if release['cover']:
            j_releases.append(release)
        else:
            j_news.append(release)
    else:
        return release

def adjust_releases():
    for r in j_news:
        r_c = next((x for x in j_releases if
                    x['id'] == r['id'] and x['volume'] == r['volume'] and x['subtitle'] == r['subtitle']), None)
        if r_c:
            r['cover'] = r_c['cover']
    return j_news


def re_parse():
    with SimpleDatabase('failed.db') as failed:
        for f in failed.get_all():
            value = json.loads(f)
            release = parse_release(value).json()
            if not release['id'] == 'unknown':
                failed.remove_value(value)
                release = filter_jpop_releases(release)
                if release:
                    print(release)
                    print(upload_release(release))
        print("-----------------")
        for r in adjust_releases():
            print(r)
            print(upload_release(r))
            print(r.json())


def scrape_releases():
    with SimpleDatabase('failed.db') as failed, SimpleDatabase('blacklist.db') as blacklist:
        data = get_data()
        for x in data:
            if blacklist.is_value_in(x):
                continue
            release = parse_release(x)
            if release['id'] == 'unknown':
                if not failed.is_value_in(x):
                    failed.add_value(x)
                continue
            release = filter_jpop_releases(release)
            if release:
                print(release)
                print(upload_release(release))
        print("-----------------")
        for r in adjust_releases():
            print(r)
            print(upload_release(r))


def list_all_from_db(title):
    with SimpleDatabase('failed.db') as failed:
        for x in failed.get_all():
            if title in x:
                print(x)

def add_to_blacklist(value):
    with SimpleDatabase('blacklist.db') as blacklist:
        blacklist.add_value(value)
        for x in blacklist.get_all():
            print(x)


if __name__ == '__main__':
    re_parse()
    scrape_releases()
