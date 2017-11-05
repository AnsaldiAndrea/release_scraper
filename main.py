"""main module"""
from scraper import WebScraper
from mypackage import csvstring, encoder
from pastebin import PastebinAPI
from lxml import etree


def save():
    """get data from scraper and save to paste"""
    data = WebScraper().extract()
    csv_data = csvstring.values_to_csv(data)
    encoded_data = encoder.encode(csv_data, return_type='str')
    # Create pastebin paste
    api_key = 'bdb21db2a07cb713b7e6a1713257564d'
    pastebin = PastebinAPI()
    user_key = pastebin.generate_user_key(api_key, 'Raistrike', 'Nuvoletta2').decode('utf-8')
    paste = pastebin.pastes_by_user(api_key, user_key).decode('utf-8')
    root = etree.fromstring(paste)
    paste_key = root.xpath('paste_key')[0].text
    delete = pastebin.delete_paste(api_key, user_key, paste_key)
    print('{} : {}'.format(delete, paste_key))
    paste = pastebin.paste(api_key,
                           encoded_data,
                           api_user_key=user_key,
                           paste_name='data.csv',
                           paste_private='unlisted')
    print(paste.decode('utf-8'))


save()
