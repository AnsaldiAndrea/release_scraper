from package.normal import normalize_price, normalize_release_date
import re


def value_from_xpath(element, xpath):
    """get value from xpath"""
    if not xpath: return ''
    values = element.xpath(xpath)
    if not values: return ''
    return remove_redundant_spaces(values[0]).strip()


def values_from_xpath(element, xpath):
    """get values from xpath"""
    if not xpath: return ''
    values = element.xpath(xpath)
    if not values: return []
    return [remove_redundant_spaces(x.strip()) for x in values]


def data_from_elem(element, title_xpath, subtitle_xpath=None, release_xpath=None, price_xpath=None,
                   cover_xpath=None):
    """get data from element given xpath"""
    data = {'title_volume': remove_redundant_spaces(element.xpath(title_xpath)[0]),
            'subtitle': value_from_xpath(element, subtitle_xpath),
            'release_date': normalize_release_date(
                date_str=value_from_xpath(element, release_xpath)),
            'price': normalize_price(value_from_xpath(element, price_xpath)),
            'cover': value_from_xpath(element, cover_xpath)
            }
    return data

def remove_redundant_spaces(text):
    return re.sub('\\s+', ' ', text).strip()