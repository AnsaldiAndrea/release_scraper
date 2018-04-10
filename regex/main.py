class ParsedData:
    def __init__(self):
        self.value = {"title": None, "volume": 0, "extra": []}

    def get_title(self):
        return self.value["title"]

    def set_title(self, title):
        self.value["title"] = title

    def get_volume(self):
        return self.value["volume"]

    def set_volume(self, volume):
        self.value["volume"] = volume

    def get_extra(self):
        return self.value["extra"]

    def set_extra(self, extra):
        self.value["extra"].append(extra)

    def __str__(self):
        return str(self.value)

    title = property(get_title, set_title)
    volume = property(get_volume, set_volume)
    extra = property(get_extra, set_extra)

class Parser:
    def __init__(self, obj):
        self.obj = obj

    def regex(self):
        pass

    @staticmethod
    def filterNone(tuples):
        return tuple(x for x in tuples if x is not None)
