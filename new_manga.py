import json

from info_updater import InfoFinder
from package import web_api


def get_input(path=None):
    if path:
        with open(path, encoding="utf-8") as f:
            _input = json.load(f)
        return _input
    return [{'id': input("Id: "),
             'title': input("Title: "),
             'search': input("Search: "),
             'publisher': input("Publisher: ")}]


def store_releases(release_list):
    with open("data/releases.json", "w+") as f:
        json.dump(release_list, f, indent=4)


def store_manga(manga):
    with open("data/manga.json", "w+") as f:
        json.dump(manga, f, indent=4)


def get_releases():
    with open("data/releases.json", "r") as f:
        return json.load(f)


def get_manga():
    with open("data/manga.json", "r") as f:
        return json.load(f)


def print_separator(variable=None):
    if variable:
        print(variable)
    print("------------------")


if __name__ == '__main__':
    _input_list = get_input(path="input.json")

    _input = _input_list[-1]
    # for _input in _input_list:
    with InfoFinder() as info:
        manga_info = info.get_info(_input['id'], _input['title'], _input['publisher']).as_dict()
        releases = info.get_releases(_input['search'])
        alias = info.get_alias()

    print_separator(json.dumps(manga_info, indent=4))
    print_separator(alias)
    valid_titles = input("Alias: ")
    valid_titles = valid_titles.split(',') if valid_titles.strip() else []
    print_separator(valid_titles)
    for r in releases:
        print(r)
    print_separator()
    store_manga(manga_info)
    store_releases(releases)
    print_separator("Manga saved to <data/manga.json> | Release saved to <data/releases.json>")
    up = input("Upload? (0 to close)")
    if up != "0":
        releases = get_releases()
        manga_info = get_manga()
        if web_api.upload_manga(manga_info):
            if valid_titles:
                for a in valid_titles:
                    print(web_api.upload_alias(manga_info['id'], a))
            for rel in releases:
                parsed = web_api.parse_release(rel)
                if parsed and parsed['id'] != "unknown":
                    print(web_api.upload_release(parsed))
