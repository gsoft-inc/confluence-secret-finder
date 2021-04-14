import re
import os


class Blacklist(object):
    def __init__(self, predefined_blacklist, blacklist_file=None):
        regex_strings = list(predefined_blacklist)
        if blacklist_file and os.path.exists(blacklist_file):
            with open(blacklist_file, "r") as f:
                lines = (line.strip() for line in f.readlines())
                regex_strings.extend(line for line in lines if line)

        self.regexes = [re.compile(f"^{s}$", flags=re.I) for s in regex_strings]

    def matches(self, value):
        return any(r for r in self.regexes if r.match(value))
