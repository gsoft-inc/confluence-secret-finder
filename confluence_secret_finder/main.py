#!/usr/bin/env python3

import argparse
import datetime
import logging
from typing import Iterable

from cache import Cache
from confluence import ConfluenceRepository
from model import VersionSecrets, ContentCrawlHistory
from secrets import SecretFinder
from text_extractor import TextExtractor
from util import to_json


class App(object):
    def __init__(self, domain, api_user, api_token, blacklist_file, max_attachment_size):
        self._domain = domain
        self._text_extractor = TextExtractor()
        self._repository = ConfluenceRepository(domain, api_user, api_token, max_attachment_size, self._text_extractor.supported_mime_types)
        self._secret_finder = SecretFinder(blacklist_file)

    def __enter__(self):
        self._cache = Cache("cache.sqlite")
        return self

    def __exit__(self, *args):
        self._cache.close()

    def get_secrets_from_versions(self, content, start_version) -> Iterable[VersionSecrets]:
        for version in self._repository.get_versions(content):
            if version.id <= start_version:
                continue

            version_content = self._text_extractor.extract_text_from_version(content, version)
            secrets = set()
            for secret in self._secret_finder.find_secrets(version_content):
                secrets.add(secret)

            if any(secrets):
                yield VersionSecrets(content, version, secrets)

    def find_secrets_from_date(self, date) -> Iterable[VersionSecrets]:
        today = datetime.datetime.now().date()
        while date <= today:
            logging.info(f"Fetching changes for {date}...")
            for content in self._repository.get_content_for_date(date):
                crawl_history = self._cache.get_crawl_history(content.id)
                if crawl_history:
                    new_version_secrets = []
                    if crawl_history.latest_version != content.latest_version:
                        logging.info(f"Fetching versions {crawl_history.latest_version}-{content.latest_version} from {content}...")
                        new_version_secrets = list(self.get_secrets_from_versions(content, crawl_history.latest_version))
                else:
                    logging.info(f"Fetching {content.latest_version} versions from {content}...")
                    new_version_secrets = list(self.get_secrets_from_versions(content, 0))
                    crawl_history = ContentCrawlHistory()

                for version_secrets in new_version_secrets:
                    version_secrets.secrets = [s for s in version_secrets.secrets if s not in crawl_history.secrets]
                    crawl_history.secrets.extend(version_secrets.secrets)

                crawl_history.latest_version = content.latest_version
                self._cache.set_crawl_history(content.id, crawl_history)
                for s in new_version_secrets:
                    if any(s.secrets):
                        yield s

            self._cache.set_last_crawl_date(date)
            date += datetime.timedelta(days=1)

    def find_secrets(self) -> Iterable[VersionSecrets]:
        for s in self.find_secrets_from_date(self._get_start_date()):
            yield s

    def _get_start_date(self) -> datetime.date:
        cached_date = self._cache.get_last_crawl_date()
        if cached_date:
            return cached_date
        return self._repository.get_oldest_content_creation_date()


def main():
    parser = argparse.ArgumentParser(description='Confluence Secret Finder')
    parser.add_argument('--domain', '-d', action="store", dest='domain', help="Confluence domain.", required=True)
    parser.add_argument('--user', '-u', action="store", dest='user', help="Confluence user.", required=True)
    parser.add_argument('--token', '-t', action="store", dest='token', help="API token for the user.", required=True)
    parser.add_argument('--max-attachment-size', '-s', action="store", dest='max_attachment_size', default=10, help="Max attachment size to download in MB. Defaults to 10MB.", required=False)
    parser.add_argument('--blacklist', '-b', action='store', dest='blacklist_file', default=None, help='File containing regexes to blacklist secrets.')
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help="Increases output verbosity.")
    parser.add_argument('-vv', action="store_true", dest='verbose_debug', default=False, help="Increases output verbosity even more.")
    parser.add_argument('--json', '-j', action="store_true", dest='json', default=False, help="Outputs the results as json.")

    args = parser.parse_args()

    if args.verbose or args.verbose_debug:
        logging.getLogger("sqlitedict").setLevel(logging.ERROR)
        logging.getLogger("chardet.charsetprober").setLevel(logging.ERROR)
        logging.getLogger().setLevel(logging.DEBUG if args.verbose_debug else logging.INFO)

    with App(args.domain, args.user, args.token, args.blacklist_file, args.max_attachment_size) as app:
        for s in app.find_secrets():
            if args.json:
                j = to_json(s)
                print(j)
            else:
                print(f"{s.content.space}): {s.version}: {s.secrets}")


if __name__ == "__main__":
    main()
