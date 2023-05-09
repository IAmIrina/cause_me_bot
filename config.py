import logging.config
import typing as t

from pydantic import BaseSettings

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

    class Config:
        env_prefix = 'dictionary_'


class Translate(EnvBaseSettings):
    url: str = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    token: str

    class Config:
        env_prefix = 'translate_'


class Telegram(EnvBaseSettings):
    endpoint: str = 'https://api.telegram.org'
    token: str

    class Config:
        env_prefix = 'telegram_'


class Settings(EnvBaseSettings):
    intervals: t.List[int] = [1, 2, 3, 5, 8, 13, 21, 32, 55, 89]
    ydb = YDB()
    telegram = Telegram()
    dictionary = Dictionary()
    translate = Translate()


settings = Settings()

logging.config.dictConfig(LOGGING)
logging.getLogger('ydb').setLevel(logging.CRITICAL)
