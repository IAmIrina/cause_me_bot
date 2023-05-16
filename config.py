import logging.config
import typing as t

from pydantic import BaseSettings, validator

from lib.logger import LOGGING


class EnvBaseSettings(BaseSettings):
    class Config:
        env_file = '.env'


class YDB(EnvBaseSettings):
    endpoint: str = 'grpcs://ydb.serverless.yandexcloud.net:2135'
    database: str

    class Config:
        env_prefix = 'ydb_'


class Dictionary(EnvBaseSettings):
    url: str = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
    token: str
    source_language_code: str = 'en'
    target_language_code: str = 'ru'

    class Config:
        env_prefix = 'dictionary_'

    @property
    def direction(self):
        return f'{self.source_language_code}/{self.target_language_code}'

    @validator('source_language_code', 'target_language_code')
    def to_lower_case(cls, value):
        return value.lower()


class Translate(EnvBaseSettings):
    url: str = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    token: str
    source_language_code: str = 'en'
    target_language_code: str = 'ru'

    class Config:
        env_prefix = 'translate_'

    @validator('source_language_code', 'target_language_code')
    def to_lower_case(cls, value):
        return value.lower()


class ChatGPT(EnvBaseSettings):
    url: str = 'https://api.openai.com/v1/chat/completions'
    token: str

    class Config:
        env_prefix = 'chatgpt_'


class YouGlish(EnvBaseSettings):
    language: str = 'english'
    accent: str = 'us'

    class Config:
        env_prefix = 'youglish_'

    @property
    def url_template(self):
        return 'https://youglish.com/pronounce/{word}/' + self.language.lower() + '/' + self.accent.lower()


class Telegram(EnvBaseSettings):
    endpoint: str = 'https://api.telegram.org'
    token: str

    class Config:
        env_prefix = 'telegram_'


class Settings(EnvBaseSettings):
    intervals: t.List[int] = [1, 2, 3, 5, 8, 13, 21, 32, 55, 89]
    daily_limit: int = 7
    ydb = YDB()
    telegram = Telegram()
    dictionary = Dictionary()
    translate = Translate()
    chat_gpt = ChatGPT()
    youglish = YouGlish()
    chatgpt_on = True
    dictionary_on = True


settings = Settings()

logging.config.dictConfig(LOGGING)
logging.getLogger('ydb').setLevel(logging.CRITICAL)
