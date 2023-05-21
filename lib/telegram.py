import json
import logging
import types

import requests

logger = logging.getLogger(__name__)


class API():
    HEADERS = types.MappingProxyType({'Content-Type': 'application/json'})
    COMMANDS = {
        "commands": [
            {
                "command": "start",
                "description": "Start using bot"
            },
            {
                "command": "help",
                "description": "Display help"
            },
            {
                "command": "more",
                "description": "Get more words to repeat"
            }
        ],
        "language_code": "en"
    }

    def __init__(self, endpoint: str, token: str) -> None:
        self.telegram_url = f"{endpoint}/bot{token}"

    def _make_post_request(self, url: str, payload: dict) -> None:
        response = requests.post(
            url,
            headers=self.HEADERS,
            data=json.dumps(payload)
        )
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(response.text)
            raise err

    def set_my_commands(self) -> None:
        self._make_post_request(
            url=f"{self.telegram_url}/setMyCommands",
            payload=self.COMMANDS,
        )

    def send_message(self, chat_id: int, **kwargs) -> None:
        self._make_post_request(
            url=f"{self.telegram_url}/sendMessage",
            payload=dict(
                chat_id=chat_id,
                **kwargs,
            ),
        )

    def delete_keyboard(self, chat_id, message_id):
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": json.dumps({'remove_inline_keyboard': True})
        }
        response = requests.get(f"{self.telegram_url}/editMessageReplyMarkup?", params=params)
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(response.text)
            raise err
