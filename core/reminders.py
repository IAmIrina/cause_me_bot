import logging
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
        self.intervals = settings.intervals

    def _send_message(self, chat_id: int, **kwargs) -> None:
        """Send message to messager."""
        try:
            self.bot.send_message(
                chat_id=chat_id,
                **kwargs,
            )
        except Exception as err:
            logger.exception(
                'Can not send telegram message %s to chat %s', kwargs, chat_id)
            raise err

    def _send_story(self, chat_id, words):
        try:
            story = self.text_generator.gen_story(words)
            if story:
                self._send_message(
                    chat_id=chat_id,
                    text=story,
                )
        except Exception:
            pass

    def _send_word(self, chat_id: int, word: str):
        examples = urllib.parse.quote(settings.youglish.url_template.format(
            word=word), safe=':/').replace('.', '\\.')
        try:
            example_sentence = self.text_generator.gen_sentence(word)
        except Exception:
            example_sentence = ''
        keyboard = schemas.Keyboards.get_inline_keyboard(
            [
                schemas.Button(
                    text=messages.REPEATED,
                    callback_data=f'{schemas.Commands.REPEATED.value}{word}',
                )
            ],
        )
        message = schemas.TLGResponse(
            text=f'{messages.REPEAR_WORD_TEMPLATE.format(word=word)}{example_sentence}{examples}',
            reply_markup=keyboard,
            parse_mode='MarkdownV2',
        )
        try:
            self._send_message(
                chat_id=chat_id,
                **message.dict(exclude_none=True),
            )
        except Exception:
            pass

    def _load_ripe_words(self, chat_id: int):
        ripe_words = self.pool.retry_operation_sync(
            self.db.get_ripe_words,
            max_repetition=len(self.intervals),
            chat_id=chat_id,
        )
        return ripe_words

    def _load_repeat_words_count(self, chat_id: int):
        count_ripe_words = self.pool.retry_operation_sync(
            self.db.get_repeat_words_count,
            max_repetition=len(self.intervals),
            chat_id=chat_id,
        )
        return count_ripe_words[0].words

    def _load_new_words_count(self, chat_id: int):
        count_new_words = self.pool.retry_operation_sync(
            self.db.get_new_words_count,
            chat_id=chat_id,
        )
        return count_new_words[0].words

    def _send_words_to_user(self, chat_id: int, words) -> None:
        for row in words:
            try:
                self._send_word(chat_id=chat_id, word=row.word)
            except Exception as err:
                logger.exception(
                    'Can not send telegram message %s to chat %s',
                    messages.REPEAR_WORD_TEMPLATE.format(word=row.word),
                    chat_id,
                )
                raise err
            self.pool.retry_operation_sync(
                self.db.upsert_word,
                chat_id=chat_id,
                word=row.word,
                repetition=row.repetition + 1,
                repeat_after=self.intervals[row.repetition],
            )

        if words and settings.chatgpt_on:
            self._send_story(chat_id, [row.word for row in words])

    def send_ripe_words_to_user(self, chat_id: int):
        ripe_words = self._load_ripe_words(chat_id=chat_id)
        if not ripe_words:
            self._send_message(
                chat_id=chat_id,
                text=messages.NOTHING_TO_REPEAT,
            )
            return
        self._send_words_to_user(chat_id, ripe_words)
        self._send_message(
            chat_id=chat_id,
            text=messages.WORDS_LEFT.format(
                repeat_words_count=self._load_repeat_words_count(chat_id=chat_id),
                new_words_count=self._load_new_words_count(chat_id=chat_id),
            ),
        )

    def remind_to_repeat_words(self) -> str:
        users = self.pool.retry_operation_sync(self.db.get_users)

        for user in users:
            ripe_words = self._load_ripe_words(chat_id=user.chat_id)
            if not ripe_words:
                continue
            try:
                self._send_message(
                    chat_id=user.chat_id,
                    text=messages.TIME_TO_REPEAT_WORDS,
                )
                self._send_words_to_user(user.chat_id, ripe_words)
                self._send_message(
                    chat_id=user.chat_id,
                    text=messages.WORDS_LEFT.format(
                        repeat_words_count=self._load_repeat_words_count(chat_id=user.chat_id),
                        new_words_count=self._load_new_words_count(chat_id=user.chat_id),
                    ),
                )
            except Exception:
                pass
