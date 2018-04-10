from regex.main import ParsedData, Parser
import re

class ParserStar(Parser):
    re_volume = "(.*)\\sn\\.\\s([^0]\\d*)"
    re_unique = "(.*)\\svolume\\sunico"

    def __init__(self, obj):
        super().__init__(obj)
        self.parsed_data = ParsedData()

    def regex(self):
        title = self.obj['title_volume']
        print(title)
        if not self.regex_unique(title):
            self.regex_volume(title)
        print(self.parsed_data)
        return self.parsed_data

    def regex_unique(self, title):
        r = re.fullmatch(self.re_unique, title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            self.parsed_data.title = groups[0]
            self.parsed_data.volume = 1
            return True
        return False

    def regex_volume(self, title):
        r = re.fullmatch(self.re_volume, title, re.IGNORECASE)
        if r:
            groups = self.filterNone(r.groups())
            self.parsed_data.title = groups[0]
            self.parsed_data.volume = int(groups[1])
