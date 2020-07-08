import json
import mimetypes

if not mimetypes.inited:
    mimetypes.init()


class PublicPropertiesEncoder(json.JSONEncoder):
    def default(self, o):
        return {k: v for k, v in vars(o).items() if not k.startswith("_")}


def to_json(obj):
    return json.dumps(obj, cls=PublicPropertiesEncoder)


def get_mime_type_from_file_name(file_name):
    return mimetypes.guess_type(file_name, strict=False)[0]


def get_mime_types_from_extensions(extensions):
    return [mimetypes.guess_type("a" + ext, strict=False)[0] for ext in extensions]


def get_extensions_from_mime_type(mime_type):
    return mimetypes.guess_all_extensions(mime_type, strict=False)
