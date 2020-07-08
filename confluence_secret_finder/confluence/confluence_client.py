import logging
import time

import requests
from requests import RequestException
from requests.auth import HTTPBasicAuth


class ConfluenceClient(object):
    _max_retries = 5

    def __init__(self, domain, api_user, api_token):
        self._base_url = f"https://{domain}.atlassian.net/wiki"
        self._base_api_url = f"{self._base_url}/rest/api"
        self.api_token = api_token
        self.api_user = api_user

    def paginated_get(self, endpoint, params=None):
        url = f"{self._base_api_url}/{endpoint}"
        if "limit" not in params:
            params["limit"] = 25
        if "start" not in params:
            params["start"] = 0
        if "expand" in params and not isinstance(params["expand"], str):
            params["expand"] = ",".join(params["expand"])

        while True:
            r = self._get(url, params, lambda response: response.json())
            if not r:
                break
            for result in r["results"]:
                yield result
            if "next" in r["_links"]:
                params["start"] += params["limit"]
            else:
                break

    def get(self, endpoint, params=None):
        return self._get(f"{self._base_api_url}/{endpoint}", params, lambda response: response.json())

    def get_file(self, url):
        return self._get(url, None, lambda response: response.content)

    def _get(self, url, params, response_action):
        retry = 1
        while True:
            try:
                response = requests.get(url, auth=HTTPBasicAuth(self.api_user, self.api_token), headers={"Content-Type": "application/json"}, params=params)
                status_code = response.status_code

                if status_code == 200:
                    return response_action(response)
            except RequestException:
                continue

            if retry >= self._max_retries:
                logging.error("Could not get %s. Skipping." % url)
                return None

            if status_code == 429:
                sleep_time = 5
                logging.warning("Rate limit reached. Sleeping %d seconds." % sleep_time)
            else:
                sleep_time = retry * 5
                logging.error("Unhandled error. Retrying in %d seconds." % sleep_time)

            retry += 1
            if sleep_time > 0:
                time.sleep(sleep_time)


