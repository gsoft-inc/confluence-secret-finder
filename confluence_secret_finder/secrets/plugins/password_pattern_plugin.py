from secrets.plugins.base_plugin import BasePlugin
import re
from secrets.plugins.blacklist import Blacklist


class PasswordPatternPlugin(BasePlugin):
    BLACKLIST = [r"[A-Z0-9]{8}-([A-Z0-9]{4}-){3}[A-Z0-9]{12}",  # Guid
                 "RFC[0-9]{3}", "ES201[56]", "Office365", "System32", "log4net",
                 "VS20[0-9]{2}", "word2vec", "Graphics2D", r"[CS]A\d{4}", "Base64",
                 "AES256CBC", "ISO27001", r"\d+GB", r"\d+IOPS", "python3",
                 r"\d{2,4}(x\d{2,4})px", r"\d{2,4}x\d{2,4}", r"\d{1,2}mins", r"\d{1,2}min\d{1,2}s?", r"\d{1,2}days",
                 r"ConsoleApp\d", r"\d{1,4}(k|m)bps", r"\d{1,4}ms", "KB\d+"]

    def __init__(self):
        self.password_regex = re.compile(r"(?:^|\s)(\w*(?:\d+[a-zA-Z]|[a-zA-Z]+\d)\w*!?)(?:$|\s)")
        self.blacklist = Blacklist(self.BLACKLIST)

    def find_secrets(self, line: str):
        for m in self.password_regex.findall(line):
            if not self.blacklist.matches(m):
                yield m
