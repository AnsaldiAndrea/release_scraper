import json
import requests
import logging
from scraper import WebScraper
from regex import jpop


def get_data(cached=False):
    if cached:
        return get_cached_data()
    _data = WebScraper().extract(planet=False, star=False, jpop_news=False)
    with open("cached.log", "w+") as x:
        x.write(json.dumps(_data, ensure_ascii=False, indent=4))
    return _data


def parse_release(_data):
    r = requests.post("http://raistrike.pythonanywhere.com/api/releases/parse", json=_data)
    return r


def add_release(_data):
    r = requests.post("http://raistrike.pythonanywhere.com/api/releases", json=_data)
    return r


def get_cached_data():
    return json.load(open("cached.log"))


def add_manga(filename):
    m = json.load(open(filename))
    r = requests.post("http://raistrike.pythonanywhere.com/api/manga", json=m['info'])
    if r.status_code == 200:
        for x in m['releases']:
            r = add_release(x)
            if not r.status_code == 200:
                break
    return r


def test_regex():
    data = get_data()
    for x in data:
        jpop.regex(x['title_volume'])


if __name__ == '__main__':
    logging.basicConfig(filename='scrap.log', level=logging.INFO)
    test_regex()
    """
    data = get_data()
    j_releases = []
    j_news = []
    for x in data:
        ret = json.loads(parse_release(x).text)
        #ret = {'id': 'unknown'}
        print(ret)
        if not ret['id'] == 'unknown':
            if ret['publisher'] == 'jpop':
                if ret['cover']:
                    j_releases.append(ret)
                else:
                    j_news.append(ret)
            else:
                add_release(ret)
        else:
            if "1" in x['title_volume'] or "volume unico" in x['title_volume'].lower():
                logging.info(x)
    j_releases = adjust_releases(j_news, j_releases)
    print("-----------------")
    for r in j_releases:
        add_release(r)
    """