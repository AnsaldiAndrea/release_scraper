from scraper import WebScraper
from lib import csvstring, encoder
from pastebin import PastebinAPI
import pprint

pp = pprint.PrettyPrinter()
api_key = 'bdb21db2a07cb713b7e6a1713257564d'
x = PastebinAPI()
user_key = x.generate_user_key(api_key,'Raistrike','Nuvoletta2').decode('utf-8')

def save():
	data = WebScraper().extract()
	csv_data = csvstring.values_to_csv(data)
	encoded_data = encoder.encode(csv_data, return_type='str')
	# Create pastebin paste
	api_key = 'bdb21db2a07cb713b7e6a1713257564d'
	x = PastebinAPI()
	user_key = x.generate_user_key(api_key,'Raistrike','Nuvoletta2').decode('utf-8')
	paste = x.paste(api_key,
						encoded_data,
						api_user_key=user_key,
						paste_name='data.csv',
						paste_private = 'unlisted')
	print(paste.decode('utf-8'))

def read():
	csv_data = x.raw(api_key,user_key,'nCHM7beY')
	decoded_data = encoder.decode(csv_data, return_type='str')
	return csvstring.csvstring_to_values(decoded_data)


for x in read():
	print(x)
