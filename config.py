import logging.config
import typing as t

from pydantic import BaseSettings, Field

from lib.logger import LOGGING


class YDB(BaseSettings):
    endpoint: str = 'grpcs://ydb.serverless.yandexcloud.net:2135'
    database: str = '/ru-central1/b1g6251p1o0qlsnpmlq3/etn3m5454ilij9q4a2e9'
    sa_key_file: str = Field(env='SA_KEY_FILE')

    class Config:
        env_prefix = 'ydb_'
        env_file = '.env'


class Dictionary(BaseSettings):
    url: str = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
    token: str

    class Config:
        env_prefix = 'dictionary_'
        env_file = '.env'


class Translate(BaseSettings):
    url: str = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    token: str

    class Config:
        env_prefix = 'translate_'
        env_file = '.env'


class Telegram(BaseSettings):
    endpoint: str = 'https://api.telegram.org'
    token: str

    class Config:
        env_prefix = 'telegram_'
        env_file = '.env'


class Settings(BaseSettings):
    intervals: t.List[int] = [1, 2, 3, 5, 8, 13, 21, 32, 55, 89]
    ydb = YDB()
    telegram = Telegram()
    dictionary = Dictionary()
    translate = Translate()


settings = Settings()

logging.config.dictConfig(LOGGING)
logging.getLogger('ydb').setLevel(logging.CRITICAL)
