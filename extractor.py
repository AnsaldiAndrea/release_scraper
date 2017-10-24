import re
import pprint
#from tabulate import tabulate
import gspread
from oauth2client.service_account import ServiceAccountCredentials

pp = pprint.PrettyPrinter()

class Extractor():
    def main(self):
        self.raw_data = get_work_sheet('RawData','releases')
        #pp.pprint(self.raw_data)

def get_work_sheet(spreadsheet,worksheet):
    raw_data = []
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        raw_data_sheet = client.open(spreadsheet)
        sheet = raw_data_sheet.worksheet(worksheet)
        export_data = sheet.export()
        with open('test.csv', 'wb+') as f:
            f.write(export_data)
        raw_data = sheet.get_all_values()

        print('success')
        for x in raw_data:
            if x[5]=='planet':
                regex_planet(x)
    except Exception as e:
        print('an error occured - {}'.format(e))
    finally:
        return raw_data

def regex_planet(values):
    match = re.fullmatch('((.*)\\s(\\d+))|(.*)',values[0])
    if match and match.group(1):
        print('{}, {}'.format(match.group(2),match.group(3)))
    elif match:
        print(match.group(4))
    pass


if __name__ == '__main__':
    Extractor().main()
