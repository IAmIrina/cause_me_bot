import logging

import typing as t
import urllib.parse

from db import ydb_manage
from lib import messages

from lib import telegram

logger = logging.getLogger(__name__)


class WordReminder():

    def __init__(self, pool, bot: telegram.API) -> None:
        self.pool = pool
        self.db = ydb_manage.Query()
        self.bot = bot

    def remind_to_repeat_words(self, intervals: t.List[int]) -> str:
        ripe_words = self.pool.retry_operation_sync(self.db.get_ripe_words, max_repetition=len(intervals))
        chat_id = None
        for row in ripe_words:

            if not chat_id or chat_id != row.chat_id:
                try:
                    self.bot.send_message(
                        text=messages.TIME_TO_REPEAT_WORDS,
                        chat_id=row.chat_id,
                    )
                except Exception:
                    logger.exception(
                        'Can not send telegram message %s to chat %s',
                        messages.TIME_TO_REPEAT_WORDS,
                        row.chat_id,
                    )
                    continue
                chat_id = row.chat_id
            try:
                self.bot.send_message(
                    text=messages.REPEAR_WORD_TEMPLATE.format(word=urllib.parse.quote(row.word)),
                    chat_id=row.chat_id,
                    parse_mode='MarkdownV2',
                )
            except Exception:
                logger.exception(
                    'Can not send telegram message %s to chat %s',
                    messages.REPEAR_WORD_TEMPLATE.format(word=row.word),
                    row.chat_id,
                )
                continue
            ripe_words = self.pool.retry_operation_sync(
                self.db.upsert_word,
                chat_id=row.chat_id,
                word=row.word,
                repetition=row.repetition + 1,
                repeat_after=intervals[row.repetition],
            )
