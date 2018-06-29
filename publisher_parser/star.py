"""html parser for starcomics releases"""
import re

from lxml import html
from datetime import datetime

from package.normal import normalize_title, normalize_price
from package.seleniumhelper import *
from package.xpath import data_from_elem

MONTH_NEXT = {
    'Gennaio': 'Febbraio',
    'Febbraio': 'Marzo',
    'Marzo': 'Aprile',
    'Aprile': 'Maggio',
    'Maggio': 'Giugno',
    'Giugno': 'Luglio',
    'Luglio': 'Agosto',
    'Agosto': 'Settembre',
    'Settembre': 'Ottobre',
    'Ottobre': 'Novembre',
    'Novembre': 'Dicembre',
    'Dicembre': 'Gennaio'
}

title_x = './/h4[@class="title"]/@title'
title_search_x = './/h4[@class="title"]/a/@title'
link_x = './/h4[@class="title"]/a/@href'
release_x = './/p/span/text()'
price_x = './/span[contains(@class,"price")]/span/text()'
price_search_x = './/span[@class="price button_small"]/span/text()'
cover_x = './/div[@class="photo"]/a/img/@src'


def parse(driver):
    """get starcomics releases"""
    data = []
    driver.get("https://www.starcomics.com/UsciteMensili.aspx")
    parse_releases(driver, data)
    return data


def parse_releases(driver, data):
    """parse html pages for starcomics manga"""
    flag = "init"
    while flag:
        # Get page month
        month = wait_for_element(driver, '//td[@class="pager-count"]/span').text
        pager = wait_for_elements(driver, '(//tr[@class="rigagriglia"])[2]/td')  # Get number of pages

        for i in range(len(pager[3:])):
            i_page_active_x = '(//tr[@class="rigagriglia"])[2]/td[{}]'.format(i + 3)
            wait_for_class_change(driver, i_page_active_x, 'active')  # wait for page to load

            content = wait_for_element(driver, '//div[@class="content clearfix"]')
            parse_items_html(content.get_attribute("innerHTML"), data)

            wait_and_click(driver, '((//td[@class="pager-next"])[2]/a[1])')

        # go back to first page
        wait_and_click(driver, '(//tr[@class="rigagriglia"])[2]/td[2]/a[1]')
        wait_for_element(driver, '(//tr[@class="rigagriglia"])[2]/td[3][@class="pager-item active"]')
        # go to next month
        wait_and_click(driver, '(//td[@class="pager-next"]/a)[1]')

        next_month = MONTH_NEXT[re.match('(.*)\\s-\\s\\d+', month).group(1)]
        flag = wait_for_text_present(driver, '//td[@class="pager-count"]/span', next_month)


def parse_items_html(_html, data):
    content = html.fromstring(_html)
    items = content.xpath('//td[@itemprop="itemListElement"]')
    for item in items:
        item_values = data_from_elem(item,
                                     title_xpath=title_x,
                                     release_xpath=release_x,
                                     price_xpath=price_x,
                                     cover_xpath=cover_x)
        item_values['cover'] = "https://www.starcomics.com/{}".format(item_values['cover'])
        item_values['publisher'] = 'star'
        data.append(item_values)


def get_info(driver, _id, title, search):
    releases = []
    driver.get("https://www.starcomics.com/fumettoricerca.aspx?titolo={}".format(search))
    link = ""
    if not element_exist(driver, '//td[text(), "Nessun risultato"]'):
        page_counter = wait_for_element(driver, '//td[@class="pager-count"]/span')
        page_count = re.search("Pag\\.\\s+\\d+\\s+di\\s+(\\d+)", page_counter.text).group(1)
        for i in range(0, int(page_count)):
            i_page_active_x = '(//td[contains(@class,"pager-item")])[{}]'.format(get_active_page_numer(i+1))
            wait_for_class_change(driver, i_page_active_x, 'active')
            content = wait_for_element(driver, '//div[@class="content clearfix"]')
            temp_link = parse_search_results(content.get_attribute("innerHTML"), _id, releases, title)
            if not link:
                link = temp_link
            wait_and_click(driver, '//td[@class="pager-next"]/a[1]')
    if releases and link:
        price = get_price(driver, "https://www.starcomics.com/{}".format(link))
        for r in releases:
            r['price'] = price
    return releases


def get_releases(driver, search):
    driver.get("https://www.starcomics.com/fumettoricerca.aspx?titolo={}".format(search))
    releases = []
    if not element_exist(driver, '//td[text(), "Nessun risultato"]'):
        page_counter = wait_for_element(driver, '//td[@class="pager-count"]/span')
        page_count = re.search("Pag\\.\\s+\\d+\\s+di\\s+(\\d+)", page_counter.text).group(1)
        for i in range(0, int(page_count)):
            i_page_active_x = '(//td[contains(@class,"pager-item")])[{}]'.format(get_active_page_numer(i + 1))
            wait_for_class_change(driver, i_page_active_x, 'active')
            content = wait_for_element(driver, '//div[@class="content clearfix"]')
            releases.append(new_parse_search_info(content.get_attribute("innerHTML"), driver))
            wait_and_click(driver, '//td[@class="pager-next"]/a[1]')
    return releases


def get_active_page_numer(n):
    if n % 10 == 0:
        return 10
    return n % 10


@DeprecationWarning
def parse_search_results(_html, _id, data, title):
    content = html.fromstring(_html)
    items = content.xpath('//table//table/tbody/tr/td')
    link = ""
    for item in items:
        if not item.xpath(title_search_x):
            return link
        item_values = data_from_elem(item,
                                     title_xpath=title_search_x,
                                     release_xpath=release_x,
                                     cover_xpath=cover_x)
        set_title_volume(item_values)
        if normalize_title(item_values['title']) == normalize_title(title):
            item_values['id'] = _id
            item_values.pop('title', None)
            item_values['release_date'] = datetime.strptime(item_values['release_date'], '%Y-%m-%d')
            item_values['cover'] = "https://www.starcomics.com/{}".format(item_values['cover'])
            item_values['publisher'] = 'star'
            data.append(item_values)
            if not link:
                link = item.xpath(link_x)[0]
    return link


def new_parse_search_info(_html, driver):
    releases = []
    content = html.fromstring(_html)
    items = content.xpath('//table//table/tbody/tr/td')
    link = ""
    for item in items:
        if not item.xpath(title_search_x):
            return link
        item_values = data_from_elem(item,
                                     title_xpath=title_search_x,
                                     release_xpath=release_x,
                                     cover_xpath=cover_x)
        item_values['cover'] = "https://www.starcomics.com/{}".format(item_values['cover'])
        item_values['publisher'] = 'star'
        releases.append(item_values)
        if not link:
            link = item.xpath(link_x)[0]
    price = get_price(driver, link)
    for r in releases:
        r['price'] = price
    return releases


@DeprecationWarning
def set_title_volume(data):
    r = re.match('(.+)\\s[N|n]\\.\\s(\\d+)|(?i)(.+)\\svolume unico', data.pop('title_volume', None))
    if r.group(1):
        data['title'] = r.group(1)
        data['volume'] = int(r.group(2))
    elif r.group(3) or r.group(4):
        data['title'] = r.group(3) if r.group(3) else r.group(4)
        data['volume'] = 1


def get_price(driver, link):
    driver.get(link)
    x = html.fromstring(wait_for_element(driver, '//article[@id="dettagliofumetto"]').get_attribute('innerHTML'))
    price = x.xpath(price_search_x)[0]
    return normalize_price(price)

