import re
from regex.main import ParsedData
from regex.main import Parser


class ParserJpop(Parser):
    re_box = "(.*)\\sbox\\s[(]\\d+-\\d+[)]|(.*)\\s[(]box\\s\\d+-\\d+[)]|(.*)\\sbox"
    re_manga = "(.*)\\s-\\sil manga(\\s.*)?|(.*)\\sil manga(\\s.*)?"
    re_volume = "(.*)\\s(\\d+)(?:\\s[(]di\\s\\d+[)])?|" \
                "(.*)\\s(\\d+)\\s(?:[(]([A-Za-z\\s]*)[)])?|" \
                "(.*)\\s(\\d+)\\s-\\s([A-Za-z\\s]*)\\s(?:[(][A-Za-z\\s]*[)])|" \
                "(.*)\\s(?:[(]([A-Za-z\\s]*)[)])?|" \
                "(.*)"

    def __init__(self, obj):
        super().__init__(obj)
        self.parsed_data = ParsedData()

    def regex(self):
        title = str(self.obj['title_volume'])
        print(title)
        title = self.regex_box(title)
        title = self.regex_manga(title)
        if 'BOX' not in self.parsed_data.extra:
            self.regex_volume(title)
        print(self.parsed_data)
        return self.parsed_data

    def regex_box(self, _title):
        _title = _title.strip()
        r = re.fullmatch(self.re_box, _title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            self.parsed_data.title = groups[0].strip()
            self.parsed_data.extra = "BOX"
            return self.parsed_data.title
        return _title.strip()

    def regex_volume(self, _title):
        _title = _title.strip()
        r = re.fullmatch(self.re_volume, _title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            if len(groups) == 2:
                self.parsed_data.title = groups[0]
                if groups[1].isdigit():
                    self.parsed_data.volume = int(groups[1])
                elif 'light novel' in groups[1].lower():
                    self.parsed_data.volume = 1
                    self.parsed_data.extra = 'LIGHT NOVEL'
            elif len(groups) == 3:
                self.parsed_data.title = groups[0]
                self.parsed_data.volume = int(groups[1])
                if 'light novel' in groups[2].lower():
                    self.parsed_data.extra = 'LIGHT NOVEL'
                elif 'ultimo' not in groups[2].lower():
                    self.parsed_data.title = "{} - {}".format(groups[0], groups[2])
            else:
                self.parsed_data.title = groups[0]
                self.parsed_data.volume = 1

    def regex_manga(self, _title):
        r = re.fullmatch(self.re_manga, _title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            if len(groups) > 1:
                g = re.sub("\\s+", " ", groups[0] + groups[1])
            else:
                g = groups[0]
            self.parsed_data.title = g.strip()
            self.parsed_data.extra = "MANGA"
            return self.parsed_data.title
        return _title.strip()
