import requests
import json
from info_updater import InfoUpdater


def get_ids():
    r = requests.get("http://raistrike.pythonanywhere.com/api/ids")
    data = json.loads(r.json())
    return [x['id'] for x in data]



def send_update(data):
    r = requests.post("http://raistrike.pythonanywhere.com/api/manga/update", json=data)
    return r.text


if __name__ == '__main__':
    with InfoUpdater() as i:
        for x in get_ids():
            d = i.get_updated_info(x)
            #print(d)
            print(send_update(d))
