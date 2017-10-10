import re
import pprint
from tabulate import tabulate
import pygsheets

pp = pprint.PrettyPrinter()

class Extractor():
    def main(self):
        self.raw_data = get_work_sheet('RawData','releases')
        pp.pprint(self.raw_data)

def get_work_sheet(spreadsheet,worksheet):
    raw_data = []
    try:
        client = pygsheets.authorize(service_file='client_secret.json',no_cache=True)
        raw_data_sheet = client.open(spreadsheet)
        sheet = raw_data_sheet.worksheet(property='title', value=worksheet)
        raw_data = sheet.get_all_values()
    except Exception as e:
        print('an error occured - {}'.format(e))
    finally:
        return raw_data

def regex_planet(values):
    match = re.fullmatch('(.*)\\s(\\d+)?([^0-9]*)',values[0])


if __name__ == '__main__':
    Extractor().main()
