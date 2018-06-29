"""Helper module for selenium related function"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait as wait


def firefox():
    """return headless firefox driver"""
    option = Options()
    option.headless = True
    firefox_profile = webdriver.FirefoxProfile(
        "C:/Users/ansal/AppData/Roaming/Mozilla/Firefox/Profiles/6g14qr6y.Selenium")
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    return webdriver.Firefox(firefox_options=option, firefox_profile=firefox_profile)


def firefox_no_image():
    """return firefox driver without image loading"""
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    return webdriver.Firefox(firefox_profile=firefox_profile)


def element_exist(driver, xpath):
    """check if element exist"""
    try:
        return driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False


def wait_for_element(driver, xpath):
    """wait for first element"""
    return wait(driver, 50).until((lambda driver: driver.find_element_by_xpath(xpath)))


def wait_for_elements(driver, xpath):
    """wait for one or more elemnt"""
    return wait(driver, 10).until((lambda driver: driver.find_elements_by_xpath(xpath)))


def wait_for_clickable(driver, xpath):
    """wait for elemnt to be clickable"""
    try:
        return wait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
    except Exception:
        wait_for_ajax(driver)
        return wait_for_clickable(driver, xpath)


def ajax_complete(driver):
    """aux method for wait_for_ajax"""
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass


def wait_for_ajax(driver):
    """wait for ajax to complete"""
    wait(driver, 10).until(ajax_complete, "Timeout waiting for page to load")


def wait_for_text_present(driver, xpath, text):
    """wait for text in element to be present"""
    try:
        return wait(driver, 10).until(expected_conditions.text_to_be_present_in_element((By.XPATH, xpath), text))
    except TimeoutException:
        return ""


def wait_for_class_change(driver, xpath, _class):
    """wait for element class to contain _class"""
    try:
        return wait(driver, 10).until(ElementHasClass((By.XPATH, xpath), _class))
    except StaleElementReferenceException:
        wait_for_ajax(driver)
        return wait_for_class_change(driver, xpath, _class)


class ElementHasClass(object):
    """An expectation for checking that an element has a particular class.

    locator - used to find the element
    returns the WebElement once it has the particular class
    """

    def __init__(self, locator, _class):
        self.locator = locator
        self._class = _class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if self._class in element.get_attribute("class"):
            return element
        else:
            return False


def wait_and_click(driver, xpath):
    """wait for element to be clicable then click it"""
    wait_for_clickable(driver, xpath).click()
    wait_for_ajax(driver)
