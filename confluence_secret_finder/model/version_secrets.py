class VersionSecrets(object):
    def __init__(self, content, version, secrets):
        self.secrets = secrets
        self.version = version
        self.content = content
