class VersionInfo(object):
    def __init__(self, version_id, by, content_accessor, url):
        self.url = url
        self._content_accessor = content_accessor
        self.by = by
        self.id = version_id

    def get_content(self):
        return self._content_accessor()

    def __str__(self):
        return f"{self.url} - {self.by}"
