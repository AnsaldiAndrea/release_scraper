from info_updater import InfoFinder
from package.web_api import get_ids, send_update

if __name__ == '__main__':
    # mode = True # ALL
    mode = False  # LAST
    if mode:
        with InfoFinder() as i:
            for x in get_ids():
                d = i.get_updated_info(x)
                print(d)
                print(send_update(d))
    else:
        with InfoFinder() as info:
            for x in get_ids():
                updated = info.get_updated_info(x)
                print(updated.as_dict_all())
                print(send_update(updated.as_dict_all()))
