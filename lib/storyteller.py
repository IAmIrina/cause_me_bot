import json
import logging
import typing as t

import requests

from config import settings
from lib import messages

logger = logging.getLogger(__name__)


class ChatGPT():
    TEMPERATURE = 0.7
    WORDS_FOR_TOKEN = 13

    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _get_filled_payload(self, prompt_template: str, tokens: t.List[str]) -> dict:
        prompt = prompt_template.format(
            youglish_language=settings.youglish.language,
            length=len(tokens) * self.WORDS_FOR_TOKEN,
            words=', '.join(tokens),
        )
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.TEMPERATURE
        }
        return payload

    def _generate(self, payload: dict):
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

    def gen_story(self, tokens: t.List[str]) -> str:
        payload = self._get_filled_payload(prompt=messages.GEN_STORY_PROMPT, tokens=tokens)
        return self._generate(payload=payload)

    def gen_sentence(self, token: str) -> str:
        payload = self._get_filled_payload(prompt=messages.GEN_SENTENCE_PROMPT, tokens=token)
        return self._generate(payload=payload)
