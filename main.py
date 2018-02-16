import json
import requests

from scraper import WebScraper


def get_data(cached=False):
    if cached:
        return get_cached_data()
    _data = WebScraper().extract()
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
                return r
        return r
    return r


if __name__ == '__main__':
    data = get_data()
    for x in data:
        ret = json.loads(parse_release(x).text)
        print(ret)
        if not ret['id'] == 'unknown':
            add_release(ret)
