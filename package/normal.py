"""module for variouse string normalization"""
from datetime import datetime
import re


def normaliza_release_date(date_str=None, date_tuple=None, date=None):
    """return normalized release date"""
    if date_tuple:
        return datetime(date_tuple[0], date_tuple[1], date_tuple[2]).strftime('%Y-%m-%d')
    if date_str:
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    if date:
        return date.strftime('%Y-%m-%d')
    return '1900-01-01'


def normalize_price(price):
    """return price without € and comma"""
    return price.replace('€', '').replace(',', '.').strip()


def normalize_title(title):
    """returns title as lowercase alpha-numerical only string"""
    return re.sub('[^\\w]*', '', title).lower()


def normalize_titles(titles):
    """returns list of title as lowercase alpha-numerical only strings"""
    return [normalize_title(title) for title in titles]
