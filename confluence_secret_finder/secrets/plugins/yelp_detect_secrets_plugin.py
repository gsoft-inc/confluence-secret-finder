from secrets.plugins.base_plugin import BasePlugin
from detect_secrets.core.usage import PluginOptions
from detect_secrets.plugins.common import initialize
import re


class YelpDetectSecretsPlugin(BasePlugin):
    PASSWORD_REPLACEMENTS = ["mot de passe", "mdp", "pwd"]

    def __init__(self):
        self.password_replacement_regex = re.compile("|".join(self.PASSWORD_REPLACEMENTS), flags=re.I)
        active_plugins = {}
        for plugin in PluginOptions.all_plugins:
            related_args = {}
            for related_arg_tuple in plugin.related_args:
                flag_name, default_value = related_arg_tuple
                related_args[flag_name[2:].replace("-", "_")] = default_value

            active_plugins[plugin.classname] = related_args

        self._plugins = initialize.from_parser_builder(active_plugins, exclude_lines_regex=None, automaton=False, should_verify_secrets=True)

    def find_secrets(self, line: str):
        for p in self._plugins:
            line = self.password_replacement_regex.sub("password", line)

            for k in p.analyze_line(line, 0, "potato"):
                # detect_secrets sometimes return a lowercase version of the secret. Find the real string.
                secret_index = line.lower().find(k.secret_value.lower())
                secret_value = line[secret_index:secret_index + len(k.secret_value)]
                yield secret_value
