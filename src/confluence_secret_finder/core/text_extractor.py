import logging
import os
import tempfile
from itertools import chain

import textract
from bs4 import BeautifulSoup
from textract.exceptions import ExtensionNotSupported

from .model import ContentInfo, VersionInfo
from .util import get_mime_types_from_extensions, get_extensions_from_mime_type


class TextExtractor:
    textract_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]
    text_extensions = [".js", ".json", ".xml"]  # Mime types starting with text/ are automatically supported.

    def __init__(self):
        self.supported_mime_types = get_mime_types_from_extensions(chain(self.textract_extensions, self.text_extensions))
        self.supported_mime_types.append('application/octet-stream')

    def extract_text_from_version(self, content_info: ContentInfo, version_info: VersionInfo) -> str:
        content = version_info.get_content()
        if content_info.type != "attachment":
            return self.extract_text_from_html(content)

        extensions = [ext for ext in get_extensions_from_mime_type(content_info.mime_type) if ext in self.textract_extensions]
        file_name_extension = os.path.splitext(content_info.title)[1].lower()
        if file_name_extension and file_name_extension not in extensions and file_name_extension in self.textract_extensions:
            extensions.append(file_name_extension)

        if extensions:
            errors = []
            f = tempfile.NamedTemporaryFile(delete=False)
            try:
                f.write(content)
                f.close()

                for extension in extensions:
                    try:
                        return textract.process(f.name, extension=extension).decode("utf-8")
                    except ExtensionNotSupported:
                        pass
                    except Exception as e:
                        errors.append(e)
            finally:
                f.close()
                os.unlink(f.name)
            if any(errors):
                logging.error(errors[0])
        else:
            try:
                return content.decode("utf-8")  # Assume that the content is text.
            except UnicodeDecodeError:
                pass

        return ""

    @staticmethod
    def extract_text_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(lambda tag: tag.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]'], texts)
        content = u"\n".join(t.strip() for t in visible_texts if not t.isspace())
        content = content.replace(":\n", ": ")
        return content
