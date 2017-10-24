from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import _find_element

def wait_for_element(driver,xpath):
    return wait(driver,10).until((lambda driver : driver.find_element_by_xpath(xpath)))

def wait_for_elements(driver,xpath):
    return wait(driver,10).until((lambda driver : driver.find_elements_by_xpath(xpath)))

def wait_for_clickable(driver,xpath):
    return wait(driver,10).until(expected_conditions.element_to_be_clickable((By.XPATH,xpath)))

def normalize_price(price):
    return price.replace('€','').replace(',','.').strip()
