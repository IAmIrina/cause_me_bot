import json
import logging
import typing as t

import requests

logger = logging.getLogger(__name__)

TEMPERATURE = 0.7
PROMP = "Make story (length about {length} words) with: {words}."
WORDS_FOR_TOKEN = 13


class ChatGPT():
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def gen_story(self, tokens: t.List[str]) -> str:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": PROMP.format(
                        length=len(tokens) * WORDS_FOR_TOKEN,
                        words=', '.join(tokens),
                    )
                }
            ],
            "temperature": TEMPERATURE
        }
        try:
            response = requests.post(self.url, data=json.dumps(payload), headers=self.headers)
            response.raise_for_status()
        except requests.HTTPError as err:
            logger.exception('Chat GPT API returned error %s %s', response.status_code, response.text)
            raise err
        except Exception as err:
            logger.exception('Chat GPT API error.')
            raise err
        choices = response.json().get('choices', [])
        for choice in choices:
            return choice.get('message', {}).get('content')
