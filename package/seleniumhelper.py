"""Helper module for selenium related function"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium import webdriver


def firefox():
    """return a """
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
    return wait(driver, 10).until((lambda driver: driver.find_element_by_xpath(xpath)))


def wait_for_elements(driver, xpath):
    """wait for one or more elemnt"""
    return wait(driver, 10).until((lambda driver: driver.find_elements_by_xpath(xpath)))


def wait_for_clickable(driver, xpath):
    """wait for elemnt to be clickable"""
    return wait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
