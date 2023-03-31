import json
import logging
import types

import requests

logger = logging.getLogger(__name__)


class API():
    HEADERS = types.MappingProxyType({'Content-Type': 'application/json'})

    def __init__(self, endpoint: str, token: str) -> None:
        self.telegram_url = f"{endpoint}/bot{token}"

    def send_message(self, chat_id: int, **kwargs) -> None:
        payload = dict(
            chat_id=chat_id,
            **kwargs,
        )
        response = requests.post(
            f"{self.telegram_url}/sendMessage",
            headers=self.HEADERS,
            data=json.dumps(payload)
        )
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(response.text)
            raise err

    def delete_keyboard(self, chat_id, message_id):
        delete_keyboard = {'remove_inline_keyboard': True}
        response = requests.get(
            f"{self.telegram_url}/editMessageReplyMarkup?"
            f"chat_id={chat_id}&message_id={message_id}&"
            f"reply_markup={json.dumps(delete_keyboard)}"
        )
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(response.text)
            raise err
