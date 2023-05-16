import logging
import typing as t
import urllib.parse

from db import ydb_manage
from lib import messages, telegram, schemas, storyteller

from config import settings

logger = logging.getLogger(__name__)


class WordReminder():

    def __init__(
            self,
            pool,
            bot: telegram.API,
            text_generator: storyteller.ChatGPT,
    ) -> None:
        self.pool = pool
        self.db = ydb_manage.Query()
        self.bot = bot
        self.text_generator = text_generator

    def send_message(self, chat_id: int, text: str, keyboard: dict = None) -> None:
        message = schemas.TLGResponse(
            text=text,
            reply_markup=keyboard,
            parse_mode='MarkdownV2',
        )
        self.bot.send_message(
            chat_id=chat_id,
            **message.dict(exclude_none=True),
        )

    def send_story(self, chat_id, words):
        try:
            story = self.text_generator.gen_story(words)
        except Exception:
            pass
        else:
            if story:
                self.bot.send_message(
                    chat_id=chat_id,
                    **schemas.TLGResponse(text=story).dict(exclude_none=True),
                )

    def remind_to_repeat_words(self, intervals: t.List[int]) -> str:
        users = self.pool.retry_operation_sync(self.db.get_users)

        for user in users:
            ripe_words = self.pool.retry_operation_sync(
                self.db.get_ripe_words,
                max_repetition=len(intervals),
                chat_id=user.chat_id,
            )
            if not ripe_words:
                continue
            try:
                self.bot.send_message(
                    text=messages.TIME_TO_REPEAT_WORDS,
                    chat_id=user.chat_id,
                )
            except Exception:
                logger.exception(
                    'Can not send telegram message %s to chat %s',
                    messages.TIME_TO_REPEAT_WORDS,
                    user.chat_id,
                )
                continue

            for row in ripe_words:
                examples = urllib.parse.quote(settings.youglish.url_template.format(
                    word=row.word), safe=':/').replace('.', '\\.')
                keyboard = schemas.Keyboards.get_inline_keyboard(
                    [
                        schemas.Button(
                            text=messages.REPEATED,
                            callback_data=f'{schemas.Commands.REPEATED.value}{row.word}',
                        )
                    ],
                )
                message = schemas.TLGResponse(
                    text=f'{messages.REPEAR_WORD_TEMPLATE.format(word=row.word)}{examples}',
                    reply_markup=keyboard,
                    parse_mode='MarkdownV2',
                )
                try:
                    self.bot.send_message(
                        chat_id=user.chat_id,
                        **message.dict(exclude_none=True),
                    )
                except Exception:
                    logger.exception(
                        'Can not send telegram message %s to chat %s',
                        messages.REPEAR_WORD_TEMPLATE.format(word=row.word),
                        row.chat_id,
                    )
                    continue
                self.pool.retry_operation_sync(
                    self.db.upsert_word,
                    chat_id=row.chat_id,
                    word=row.word,
                    repetition=row.repetition + 1,
                    repeat_after=intervals[row.repetition],
                )

            if settings.chatgpt_on:
                self.send_story(user.chat_id, [row.word for row in ripe_words])
