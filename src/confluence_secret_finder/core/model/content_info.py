from .space_info import SpaceInfo


class ContentInfo(object):
    def __init__(self, content_id, content_type, latest_version, title, space: SpaceInfo, mime_type):
        self.mime_type = mime_type
        self.space = space
        self.type = content_type
        self.title = title
        self.latest_version = latest_version
        self.id = content_id

    def __str__(self):
        return f"{self.space}: {self.id}({self.title})"
