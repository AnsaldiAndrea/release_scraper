from regex.main import ParsedData, Parser
import re


class ParserPlanet(Parser):
    re_volume = "(.*)\\s([^0]\\d*)|(.*)"
    re_box = "(.*)\\s-\\spack|cofanetto\\s(.*)"

    def __init__(self, obj):
        super().__init__(obj)
        self.fix_title()
        self.parsed_data = ParsedData()

    def fix_title(self):
        self.obj['title_volume'] = self.obj['title_volume'].replace('–', '-')

    def regex(self):
        title = str(self.obj['title_volume'])
        print(title)
        title = self.regex_box(title)
        if 'BOX' not in self.parsed_data.extra:
            self.regex_volume(title)
        print(self.parsed_data)
        return self.parsed_data

    def regex_box(self, title):
        r = re.fullmatch(self.re_box, title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            self.parsed_data.title = groups[0]
            self.parsed_data.volume = 0
            self.parsed_data.extra = 'BOX'
            return self.parsed_data.title
        return title

    def regex_volume(self, title):
        r = re.fullmatch(self.re_volume, title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            self.parsed_data.title = groups[0]
            if len(groups) > 1:
                self.parsed_data.volume = int(groups[1])
            else:
                self.parsed_data.volume = 1
