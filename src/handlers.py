import logging

from db import ydb_manage
from lib import messages

logger = logging.getLogger(__name__)


class MSGHandler():

    def __init__(self, pool) -> None:
        self.pool = pool
        self.db = ydb_manage.Query()

    def add_word(self, chat_id: int, word: str) -> str:
        self.pool.retry_operation_sync(self.db.add_word, chat_id=chat_id, word=word)
        return messages.WORD_ADDED.format(word)

    def delete_word(self, chat_id: int, word: str) -> str:
        self.pool.retry_operation_sync(self.db.delete_word, chat_id=chat_id, word=word)
        return messages.WORD_DELETED.format(word)

    def add_user(self, chat_id: int, username: str) -> str:
        self.pool.retry_operation_sync(self.db.add_user, chat_id=chat_id, username=username)
        return messages.USER_ADDED

    def info(self) -> str:
        return messages.HELP
