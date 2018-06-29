"""html parser for planet manga releases"""

from lxml import html
from selenium.common.exceptions import TimeoutException

from package import xpath
from package.normal import *
from package.seleniumhelper import wait_for_element, wait_for_elements, wait_and_click, element_exist
from package.xpath import data_from_elem

title_search_x = "//h3[@class='product-name']/a/@title"
title_volume_search_x = "//h3[@class='product-name']/a/text()"
subtitle_search_x = "//small[@class='subtitle lightText']/text()"
cover_search_x = "//a[@class='product-image']/img/@src"
release_date_search_x = "//h4[@class='publication-date']/text()"
special_price_search_x = "//p[@class='special-price']/span/text()"
price_search_x = "//p[@class='price']/span/text()"


def parse(driver, old=False):
    """parse planet"""
    data = []
    if old:
        # previous weeks releases
        driver.get("http://comics.panini.it/calendario/uscite-scorse-settimane/")
        parse_releases(driver, data)
    # this week releases
    driver.get("http://comics.panini.it/calendario/uscite-questa-settimana/")
    # print('parsing - this week - planet')
    parse_releases(driver, data)
    # next week releases
    driver.get("http://comics.panini.it/calendario/uscite-prossime-settimane/")
    # print('parsing - next weeks - planet')
    parse_releases(driver, data)
    return data


def parse_releases(driver, data):
    """parse html pages for planet manga"""
    # New code to test
    wait_and_click(driver, '//*[@id="c31384"]/a')
    # Deprecated code
    # manga_filter = wait_for_element(driver, '//*[@id="c31384"]/a')
    # manga_filter.click()
    wait_for_element(driver, '//*[@id="c31384"]/a[contains(@class,"active")]')

    items_x = "//div[@class='row list-group-item' and not(contains(@style,'display: none;'))]/div"
    title_x = "//h3[@class='product-name']/a/text()"
    sub_title_x = ".//small[@class='subtitle lightText']/text()"
    release_x = ".//span[@class='uscita itemValue']/text()"
    price_x = ".//div[@class='price']/text()"
    cover_x = ".//a[@class='product-image']/img/@src"
    try:
        items = wait_for_elements(driver, items_x)
    except TimeoutException:
        return
    for item in items:
        element = html.fromstring(item.get_attribute("innerHTML"))
        item_values = data_from_elem(element,
                                     title_xpath=title_x,
                                     subtitle_xpath=sub_title_x,
                                     release_xpath=release_x,
                                     price_xpath=price_x,
                                     cover_xpath=cover_x)
        check_reprint(element, item_values)
        item_values['publisher'] = 'planet'
        # if item contains class="reprint": subtitle = ristampa
        data.append(item_values)


def check_reprint(elem, item):
    """check if item is a reprint"""
    reprint = elem.xpath(".//h5[@class='reprint']")
    if reprint:
        if item['subtitle']:
            item['subtitle'] = "{} - Ristampa".format(item['subtitle'])
        else:
            item['subtitle'] = "Ristampa"


def get_releases(driver, search):
    """get raw releases from search term"""
    driver.get("http://comics.panini.it/store/pub_ita_it/catalogsearch/result/?q={}".format(search))
    releases = []
    while True:
        items = wait_for_elements(driver, "//div[@id='products-list']/div")
        for item in items:
            elem = html.fromstring(item.get_attribute('innerHTML'))
            values = parse_search_item(elem)
            check_reprint(elem, values)
            values['publisher'] = 'planet'
            releases.append(values)
        next_page = element_exist(driver, "//a[@class='next i-next']")
        if next_page:
            next_page.click()
        else:
            return releases


def parse_search_item(element):
    """parse single search item"""
    values = xpath.data_from_elem(element,
                                  title_xpath=title_volume_search_x,
                                  subtitle_xpath=subtitle_search_x,
                                  release_xpath=release_date_search_x,
                                  price_xpath=special_price_search_x,
                                  cover_xpath=cover_search_x)
    if not values['price']:
        values['price'] = normalize_price(xpath.value_from_xpath(element, price_search_x))
        if not values['price']:
            values['price'] = "0"
    values['cover'] = values['cover'].replace('small_image/200x', 'image')
    return values
