import datetime

from sqlitedict import SqliteDict

from model import ContentCrawlHistory


class Cache(object):
    def __init__(self, file_name, domain):
        self.file_name = file_name
        self.tables = {}

        self._crawl_history_table = f"{domain}_crawl_history"
        self._info_table = f"{domain}_info"
        self._last_crawl_date_key = f"{domain}_last_crawl_date"

    def close(self):
        for t in self.tables.values():
            t.close()

    def get(self, table, key):
        d = self._get_dict(table)
        if key not in d:
            return None
        return d[key]

    def get_crawl_history(self, content_id) -> ContentCrawlHistory:
        return self.get(self._crawl_history_table, content_id)

    def set_crawl_history(self, content_id, crawl_history: ContentCrawlHistory):
        self.set(self._crawl_history_table, content_id, crawl_history)

    def get_last_crawl_date(self) -> datetime.date:
        return self.get(self._info_table, self._last_crawl_date_key)

    def set_last_crawl_date(self, last_crawl_date: datetime.date):
        self.set(self._info_table, self._last_crawl_date_key, last_crawl_date)

    def set(self, table, key, value):
        d = self._get_dict(table)
        d[key] = value

    def _get_dict(self, table):
        if table not in self.tables:
            self.tables[table] = SqliteDict(self.file_name, tablename=table, autocommit=True)
        return self.tables[table]
