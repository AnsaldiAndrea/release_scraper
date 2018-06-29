"""API call function"""
import requests

from package.normal import normalize_title
import json


def upload_alias(_id, alias):
    """upload alias via API"""
    alias = normalize_title(alias)
    data = {"id": _id, "alias": alias}
    r = requests.post("http://raistrike.pythonanywhere.com/api/alias/", json=data)
    if r.status_code == 200:
        return r.json()
    return r


def upload_manga(manga):
    """upload manga via API"""
    r = requests.post("http://raistrike.pythonanywhere.com/api/manga", json=manga)
    if r.status_code == 200:
        return r.json()
    print("Error: Could not upload manga!")
    return None


def parse_release(_data):
    """send raw release for parsing via API"""
    r = requests.post("http://raistrike.pythonanywhere.com/api/releases/parse", json=_data)
    if r.status_code == 200:
        return r.json()
    return None


def upload_release(_data):
    """upload release via API"""
    r = requests.post("http://raistrike.pythonanywhere.com/api/releases", json=_data)
    if r.status_code == 200:
        return r.json()
    return r


def get_ids():
    r = requests.get("http://raistrike.pythonanywhere.com/api/ids")
    data = json.loads(r.json())
    return [d['id'] for d in data]


def send_update(data):
    r = requests.post("http://raistrike.pythonanywhere.com/api/manga/update", json=data)
    if r.status_code == 200:
        return r.json()
    return r

