class SpaceInfo(object):
    def __init__(self, key, name):
        self.key = key
        self.name = name

    def __str__(self):
        return f"{self.key}({self.name})"
