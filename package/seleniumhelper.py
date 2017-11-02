"""Helper module for selenium related function"""
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

def wait_for_element(driver, xpath):
    """wait for first element"""
    return wait(driver, 10).until((lambda driver: driver.find_element_by_xpath(xpath)))

def wait_for_elements(driver, xpath):
    """wait for one or more elemnt"""
    return wait(driver, 10).until((lambda driver: driver.find_elements_by_xpath(xpath)))

def wait_for_clickable(driver, xpath):
    """wait for elemnt to be clickable"""
    return wait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))

def normalize_price(price):
    """return price without € and comma"""
    return price.replace('€', '').replace(',', '.').strip()
