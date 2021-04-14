from typing import List

from detect_secrets.core.plugins.util import get_mapping_from_secret_type_to_class
from secrets.plugins.base_plugin import BasePlugin
from detect_secrets import SecretsCollection
from detect_secrets.settings import transient_settings
import re


class YelpDetectSecretsPlugin(BasePlugin):
    PASSWORD_REPLACEMENTS = ["mot de passe", "mdp", "pwd"]

    def __init__(self):
        self.password_replacement_regex = re.compile("|".join(self.PASSWORD_REPLACEMENTS), flags=re.I)

    def find_secrets(self, lines: List[str]):
        secrets_collection = SecretsCollection()
        with transient_settings({'plugins_used': [{'name': plugin_type.__name__} for plugin_type in
                                                  get_mapping_from_secret_type_to_class().values()]}) as settings:
            settings.disable_filters(
                'detect_secrets.filters.common.is_invalid_file',
            )

            # Use scan_diff since scan_line seems broken.
            line_diff = "\n".join("+" + l for l in lines)
            line_diff = self.password_replacement_regex.sub("password", line_diff)
            dummy_diff = f"--- dummy\n+++ dummy\n@@ -0,0 +1,{len(lines)} @@\n{line_diff}"
            secrets_collection.scan_diff(dummy_diff)

        for _, secret in secrets_collection:
            # detect_secrets sometimes return a lowercase version of the secret. Find the real string.
            line = lines[secret.line_number - 1]
            secret_index = line.lower().find(secret.secret_value.lower())
            secret_value = line[secret_index:secret_index + len(secret.secret_value)]
            yield secret_value
