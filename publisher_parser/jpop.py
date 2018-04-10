"""html parser for jpop releases"""
import re

from lxml import html

from package.normal import normalize_release_date, normalize_price
from package.seleniumhelper import wait_for_element, wait_for_elements
from package.xpath import data_from_elem

MONTH_DICT = {
    'gennaio': 1,
    'febbraio': 2,
    'marzo': 3,
    'aprile': 4,
    'maggio': 5,
    'giugno': 6,
    'luglio': 7,
    'agosto': 8,
    'settembre': 9,
    'ottobre': 10,
    'novembre': 11,
    'dicembre': 12
}


def parse(driver, news=True, releases=True):
    """get jpop releases"""
    data = []
    if news:
        driver.get('http://www.j-pop.it/blog')
        parse_news(driver, data)
    if releases:
        driver.get('http://www.j-pop.it/nuovi-prodotti')
        parse_release(driver, data)
    return data


def parse_news(driver, data, max_news=3):
    """jpop news"""
    xpath_news = '//div[@id="post_list"]//h3/a[contains(text(),"Uscite") or contains(text(),"uscite")]/@href'
    news = []
    while len(news) < max_news:
        raw_news = html.fromstring(driver.page_source)
        news += raw_news.xpath(xpath_news)
        wait_for_element(driver, '//a[@class="bt_right"]').click()
    for link in news:
        driver.get(link)
        news_title = wait_for_element(driver, '//h2').text
        news_release = wait_for_element(driver, '//fieldset/p/span').text
        # extract when new volume will be released
        release_date = get_release_date(news_release, news_title)

        page = html.fromstring(wait_for_element(driver, '//div[@class="rte"]').get_attribute('innerHTML'))
        misplaced = page.xpath("./div/div")
        parsed = []
        for m in misplaced:
            parsed.append(m)
            m.getparent().remove(m)
        parsed += [x for x in page.xpath('./*')]
        temp = [html.tostring(x).decode('utf-8').replace('<br>', '<br>\n') for x in parsed]
        parsed = [html.fromstring(x) for x in temp]
        for x in parsed:
            p = x.text_content().strip()
            lines = p.split('\n')
            if lines[0].startswith('DIRECT') or len(lines) < 2:
                continue
            value = {
                'title_volume': lines[0],
                'subtitle': '',
                'release_date': release_date,
                'price': next((normalize_price(x) for x in lines if '€' in x), '0.00'),
                'cover': '',
                'publisher': 'jpop'
            }
            data.append(value)


def parse_release(driver, data):
    """jpop releases with cover"""
    items = wait_for_elements(driver, '//div[@id="products_wrapper"]/ul/li/div/div/div[@class="view-content"]')
    title_x = '//div[@class="name"]/a/@title'
    cover_x = '//div[@class="image"]/a/img/@src'
    price_x = '//p[@class="special-price"]/span/text()'
    for item in items:
        element = html.fromstring(item.get_attribute("innerHTML"))
        item_values = data_from_elem(element, title_xpath=title_x, price_xpath=price_x, cover_xpath=cover_x)
        item_values['cover'] = item_values['cover'].replace('home', 'large')
        item_values['publisher'] = 'jpop'
        data.append(item_values)
    next_page = wait_for_element(driver, '//a[contains(@class,"next i-next")]').get_attribute("href")
    if next_page.endswith('#'):
        return
    else:
        driver.get(next_page)
        return parse_release(driver, data)


def get_release_date(news_release, news_title):
    """return release date of jpop news"""
    assert type(news_title) == str
    release = re.match('.*\\s(\\d{4})-(\\d{2})-(\\d{2})', news_release)
    release_date = (int(release.group(1)),
                    int(release.group(2)),
                    int(release.group(3)))
    string = re.sub("[^A-Za-z0-9\\s]", "", news_title).strip().lower()
    title = re.fullmatch("[^0-9]*(\\d+)\\s([a-z]+)", string)
    title_date = (release_date[0],
                  MONTH_DICT[title.group(2)],
                  int(title.group(1)))
    if release_date[1] == 12 and title_date[1] == 1:
        title_date = (title_date[0] + 1, title_date[1], title_date[2])
    return normalize_release_date(date_tuple=title_date)


def adjust_releases(news_releases, releases):
    for r in news_releases:
        r_c = next((x for x in releases if x['id']==r['id'] and x['volume']==r['volume'] and x['subtitle']==r['subtitle']), None)
        if r_c:
            r['cover'] = r_c['cover']
    return news_releases


def get_info():
    """get list of releases"""
    return []
