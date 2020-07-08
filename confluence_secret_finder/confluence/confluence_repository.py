import datetime
import html
import logging
from typing import Iterable

import dateutil.parser

from confluence.confluence_client import ConfluenceClient
from model import ContentInfo, VersionInfo, SpaceInfo
from util import get_mime_type_from_file_name


class ConfluenceRepository:
    def __init__(self, domain, api_user, api_token, max_attachment_size, supported_attachment_types):
        self._wiki_url = f"https://{domain}.atlassian.net/wiki"
        self._client = ConfluenceClient(domain, api_user, api_token)
        self.max_attachment_size = max_attachment_size * 1024 * 1024  # MB to B
        self.supported_attachment_types = supported_attachment_types

    def get_oldest_content_creation_date(self) -> datetime.date:
        params = {"expand": ["history"], "orderby": "history.createdDate asc"}
        oldest_date_str = next(self._client.paginated_get("content", params))["history"]["createdDate"]
        return dateutil.parser.parse(oldest_date_str).date()

    def get_content_for_date(self, date: datetime.date) -> Iterable[ContentInfo]:
        date_string = date.strftime("%Y-%m-%d")
        params = {
            "expand": ["content.version.number", "content.metadata.mediatype"],
            "includeArchivedSpaces": True,
            "cql": f"lastModified={date_string} or created={date_string} order by lastModified,created asc"
        }

        for r in self._client.paginated_get("search", params):
            content = r.get("content")
            result_global_container = r.get("resultGlobalContainer")
            if not content or not result_global_container:
                continue

            space = SpaceInfo(result_global_container["displayUrl"].split("/")[-1], result_global_container["title"])
            content_id = content["id"]
            latest_version = content["version"]["number"]
            title = ConfluenceRepository._extract_title(r)

            mime_type = None
            if content["type"] == "attachment":
                mime_type = ConfluenceRepository._extract_mime_type(r, title)
                if not mime_type.startswith("text/") and mime_type not in self.supported_attachment_types:
                    if not mime_type.startswith("image/"):
                        logging.warning(f"Content type {mime_type} not supported. Skipping attachment {title}")
                    continue

            yield ContentInfo(content_id, content["type"], latest_version, title, space, mime_type)

    def get_versions(self, content_info: ContentInfo) -> Iterable[VersionInfo]:
        for v in list(self._client.paginated_get(f"content/{content_info.id}/version", {"expand": "content.body.view"}))[::-1]:
            by = v["by"].get("email")
            if not by:
                by = v["by"].get("displayName")

            if content_info.type == "attachment":
                download = v["content"]["_links"].get("download")
                if not download:
                    continue

                url = self._wiki_url + download
                if v["content"]["extensions"]["fileSize"] > self.max_attachment_size:
                    logging.warning(f"Attachment too big. Skipping {url}")
                    continue

                yield VersionInfo(v["number"], by, lambda: self._client.get_file(url), url)
            else:
                url = f"{self._wiki_url}/pages/viewpage.action?pageId={content_info.id}&pageVersion={v['number']}"
                yield VersionInfo(v["number"], by, lambda: v["content"]["body"]["view"]["value"], url)

    @staticmethod
    def _extract_title(data):
        title = data.get("title")
        if title:
            return html.unescape(title)

        title = data.get("content", {}).get("title")
        if title:
            return html.unescape(title)

        return data.get("resultParentContainer", {}).get("title", "")

    @staticmethod
    def _extract_mime_type(data, title):
        mime = data["content"]["metadata"]["mediaType"]
        if mime == "application/octet-stream":
            title_mime_type = get_mime_type_from_file_name(title)
            if title_mime_type:
                mime = title_mime_type
        return mime
