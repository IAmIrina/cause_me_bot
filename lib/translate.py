import json
import logging
import typing as t
from itertools import groupby

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class YaTranslate():
    def __init__(
            self,
            url: str,
            token: str,
            source_language_code: str,
            target_language_code: str,
    ) -> None:
        self.url = url
        self.headers = {
            'Authorization': f'Api-key {token}',
            'Content-Type': 'application/json'
        }
        self.source_language_code = source_language_code
        self.target_language_code = target_language_code

    def translate(self, text):
        payload = {
            'sourceLanguageCode':  self.source_language_code,
            'targetLanguageCode': self.target_language_code,
            'texts': [text],
        }
        try:
            response = requests.post(self.url, data=json.dumps(payload), headers=self.headers)
            response.raise_for_status()
            [text, *_] = response.json().get('translations', {})
            text = text.get('text')
        except Exception:
            logger.exception('Yandex Translate API error.')
            text = 'Translation Service Unavailable at This Time'
        return text


class YaDictionary():

    EXLUDED = ['foreign word', '']

    class Translate(BaseModel):
        text: str
        fr: int = 0
        pos: str = ''

    def __init__(
        self,
        url: str,
        token: str,
        source_language_code: str,
        target_language_code: str,
    ) -> None:
        self.token = token
        self.url = url
        self.direction = f'{source_language_code}-{target_language_code}'

    def get_translates(self, text) -> str:
        meanings = self._get_from_dictionary(text)
        return self._format_to_text(meanings)

    def _get_from_dictionary(self, text: str) -> t.List[Translate]:
        params = {
            "key": self.token,
            "lang": self.direction,
            "text": text,
            "flags": "4"
        }

        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            result = json.loads(response.text)
            return [
                self.Translate(**translation) for meaning in result.get("def", [])
                for translation in meaning.get("tr", [])
            ]
        except Exception:
            logger.exception('Yandex Dictionary API error')
            return []

    def _format_to_text(self, translates: t.List[Translate]) -> str:
        translates = sorted(translates, key=lambda x: x.pos, reverse=True)
        groups = groupby(translates, key=lambda x: x.pos)
        groups = filter(lambda x: x if x[0] not in self.EXLUDED else False, groups)
        groups = [sorted(group, key=lambda x: x.fr, reverse=True) for _, group in groups]

        def format(group):
            return ', '.join([translate.text for translate in group])

        return '\n'.join([line for line in map(format, groups)])
