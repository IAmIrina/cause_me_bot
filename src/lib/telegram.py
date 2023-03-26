import requests
import json

import types

from lib import backoff


class API():
    HEADERS = types.MappingProxyType({'Content-Type': 'application/json'})

    def __init__(self, endpoint: str, token: str) -> None:
        self.telegram_url = f"{endpoint}/bot{token}"

    @backoff.backoff_method(max_retries=3)
    def send_message(self, text: str, chat_id: int, **kwargs) -> None:
        msg = dict(
            text=text,
            chat_id=chat_id,
            **kwargs,
        )
        response = requests.post(
            f"{self.telegram_url}/sendMessage",
            headers=self.HEADERS,
            data=json.dumps(msg)
        )
        response.raise_for_status()
