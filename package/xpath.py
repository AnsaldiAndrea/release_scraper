def value_from_xpath(element, xpath):
    """get value from xpath"""
    if not xpath: return ''
    values = element.xpath(xpath)
    if not values: return ''
    return values[0].strip()


def values_from_xpath(element,xpath):
    """get values from xpath"""
    if not xpath: return ''
    values = element.xpath(xpath)
    if not values: return []
    return [x.strip() for x in values]

