from .blacklist import Blacklist
from .plugins.password_pattern_plugin import PasswordPatternPlugin
from .plugins.yelp_detect_secrets_plugin import YelpDetectSecretsPlugin


class SecretFinder(object):
    BLACKLIST = ["password", "%password%"]

    def __init__(self, blacklist_file):
        self._plugins = [PasswordPatternPlugin(), YelpDetectSecretsPlugin()]
        self.blacklist = Blacklist(self.BLACKLIST, blacklist_file)

    def find_secrets(self, content: str):
        secrets = set()
        lines = [l.strip() for l in content.splitlines()]
        for p in self._plugins:
            for s in p.find_secrets(lines):
                if len(s) >= 6 and s not in secrets and not self.blacklist.matches(s):
                    secrets.add(s)
                    yield s

