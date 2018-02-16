import re
from lxml import html
from package.seleniumhelper import firefox
from package.xpath import value_from_xpath, values_from_xpath


def set_status(page, data):
    status = value_from_xpath(page,
                              "//div[@class='sCat']/b[text()='Status in Country of Origin']/../following-sibling::div[1]/text()")
    match = re.match('(\\d+)\\sVolume[s]?\\s(?:.*\\s)?\\((.*)\\)', status)
    if match:
        data['volumes'] = int(float(match.group(1)))
        data['complete'] = 'Complete' in match.group(2)


class InfoUpdater:
    def __init__(self):
        self.driver = firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def get_updated_info(self, manga_id):
        parsed_id = manga_id.split("_")[0]
        """get info from bakaupdates"""
        data = {'id': manga_id}
        self.driver.get("https://www.mangaupdates.com/series.html?id={}".format(parsed_id))
        page = html.fromstring(self.driver.page_source)
        data['original'] = value_from_xpath(page,
                                            "//span[@class='releasestitle tabletitle']/text()")
        set_status(page, data)
        data['genre'] = values_from_xpath(page,
                                         "//div[@class='sCat']/b[text()='Genre']/../following-sibling::div[1]/a/u/text()")
        data['genre'] = ','.join(data['genre'])
        return data
