"""
Helper class for interacting with the RT API
Example usage:
    
with RtApiHelper("https://my.rt.server/REST/1.0/", username, password) as rt:
    tickets = rt.request("/search/ticket", {"query": "Queue = 'my-ticket-queue' AND Status = 'open'")

Return example:
{
    "1": "Request for new account",
    "3": "Quota change for my account"
}

https://gist.github.com/jasoncpatton/d26a054b5daa67c34e20733a78229106
"""

import requests
from urllib.parse import urljoin
from typing import Optional, Type
from types import TracebackType


class RtApiHelper:


    def __init__(self,
        base_uri: str,
        username: str,
        password: str
    ):
        self.base_uri = base_uri if base_uri.endswith("/") else f"{base_uri}/"
        self.session = self._login(username, password)


    def __del__(self):
        if self.session:
            self.session.close()


    def __enter__(self):
        return self


    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
            ):
        if self.session:
            self.session.close()


    def _login(self, username: str, password: str) -> requests.Session:
        session = requests.Session()
        session.post(url=self.base_uri, data={"user": username, "pass": password})
        return session


    def _parse_response(self, action: str, params={}) -> dict:
        action = action if not action.startswith("/") else action[1:]
        url = urljoin(self.base_uri, action)
        parsed = {}
        with self.session.post(url=url, data=params, stream=True) as response:
            for line in response.iter_lines(decode_unicode=True):
                tokens = line.rstrip().split(":", maxsplit=1)
                if len(tokens) < 2:
                    continue
                key, value = tokens
                parsed[key] = value.lstrip()
        return parsed


    def request(self, action: str, params={}) -> dict:
        print(params)
        return self._parse_response(action, params)
