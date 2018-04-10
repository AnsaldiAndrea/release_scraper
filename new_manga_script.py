"""script for easily add manga with site api"""
import json
from info import InfoFinder
from info import get_title_from_search
import requests
from slugify import slugify
from package.normal import normalize_title


def add_release(_data):
    """add release with site api"""
    r = requests.post("http://raistrike.pythonanywhere.com/api/releases", json=_data)
    return r


def add_manga_from_file(filename):
    """add manga with site api from file"""
    m = json.load(open(filename))
    return add_manga(m)


def add_manga(m):
    """add manga with site api"""
    r = requests.post("http://raistrike.pythonanywhere.com/api/manga", json=m['info'])
    if r.status_code != 200:
        return r
    for rl in m['releases']:
        r = add_release(rl)
        if not r.status_code == 200:
            return r
    return None

def add_alias(_id, alias):
    if alias:
        for a in alias:
            a_norm = normalize_title(a)
            data = {'id':_id, 'alias':a_norm}
            r = requests.post("http://raistrike.pythonanywhere.com/api/alias/", json=data)
            if not r.status_code == 200:
                return r
            return None


def check_string(text, variable_name):
    """check if string is empty and raise exception accordingly"""
    if not text:
        raise ValueError("{} cannot be empty".format(variable_name))
    return text


def check_array(text):
    """check if string is empty and returns empty array accordingly"""
    if not text:
        return []
    return text.split(',')


def get_input():
    """get InfoFinder inputs from console input"""
    _info = {'id': check_string(input("ID: "), "ID"),
             'title': check_string(input("Title: "), "Title")}
    publisher = input("Publisher (planet, star, jpop): ")
    if publisher not in ['planet', 'star', 'jpop']:
        raise ValueError("Publisher must be planet, star or jpop")
    _info['publisher'] = publisher
    _info['search'] = check_string(input("Search: "), "Search")

    print("Searching possible aliases...")
    temp = get_title_from_search(_info['search'], _info['publisher'])
    print("Possible aliases are: {}".format(temp))

    _info['alias'] = check_array(input("Alias: "))
    _info['ignore'] = check_array(input("Ignore: "))
    return _info


def close_or_continue(text):
    """close program if input is 0"""
    close = input("Press enter to {} (0 to close): ".format(text))
    if close == '0':
        quit(0)


def write_info_to_file(_info):
    """write info to file in json format"""
    _path = 'data/{}.json'.format(slugify(_info['info']['id'] + '_' + _info['info']['title']))
    with open(_path, 'w+') as _f:
        _f.write(json.dumps(_info, indent=5))
    print("File <{}> has been created".format(_path))
    return _path


def send_info(_path, _info=None):
    """aux function - add info from file"""
    print("sending data...")
    resp = add_manga_from_file(_path)
    if not resp:
        print("Manga added successfully to database")
        if _info and 'alias' in _info and _info['alias']:
            print("Adding aliases to database...")
            for al in _info['alias']:
                add_alias(_info['id'], al)
    else:
        print("{}: {}".format(resp.status_code, resp.text))


print("1- Search and Add manga from console input")
print("2- Bulk Search and Add manga from file")
print("3- Add info from file")
i = input()
if i == "1":
    input_info = get_input()
    print(input_info)
    close_or_continue("Continue")
    info = InfoFinder().find(input_info['id'],
                             title=input_info['title'],
                             publisher=input_info['publisher'],
                             search=input_info['search'],
                             alias=input_info.get('alias', []),
                             ignore=input_info.get('ignore', []))
    print(json.dumps(info, indent=4))
    path = write_info_to_file(info)
    close_or_continue("Send Info to Database")
    send_info(path, input_info)

elif i == "2":
    path = input("Path to file: ")
    with open(path) as j:
        s = j.read()
    _input = json.loads(s)
    for _in in _input:
        print(_in)
        x = input("Press enter to continue (0 to close): ")
        if x == '0':
            continue
        info = InfoFinder().find(_in['id'],
                                 title=_in['title'],
                                 search=_in['search'],
                                 alias=_in.get('alias', []),
                                 publisher=_in['publisher'],
                                 ignore=_in.get('ignore', []))
        print(json.dumps(info, indent=4))
        path = write_info_to_file(info)
        close_or_continue("Send Info to Database")
        send_info(path, _in)

elif i == "3":
    path = input("Path to file: ")
    send_info(path)
