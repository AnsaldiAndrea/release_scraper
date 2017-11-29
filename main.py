"""main module"""
import json

import requests

from scraper import WebScraper

fail = [{
    "title_volume": "Boruto – Naruto the movie",
    "subtitle": "",
    "release_date": "2017-12-07",
    "price": "8.91",
    "cover": "http://comics.panini.it/store/media/catalog/product/cache/80/thumbnail/9df78eab33525d08d6e5fb8d27136e95/M/N/MNARO013ISBN_0.jpg",
    "publisher": "planet"
}]

correct = [{"test":"ok"}]


def send_data(_data):
    r = requests.post("http://raistrike.pythonanywhere.com/api/parse_releases", json=_data)
    return r


def get_cached_data():
    return json.load(open("cached.log"))


if __name__ == '__main__':
    #data = WebScraper().extract()
    data = get_cached_data()
    #json_data= json.dumps(data, ensure_ascii=False)
    #test = [x for x in data if x['publisher'] == 'jpop']
    #test_json = json.dumps(correct)
    print(send_data(data).text)
