import logging
import urllib

import config
from core import reminders
from db import ydb_manage
from lib import messages, schemas, telegram, translate

logger = logging.getLogger(__name__)


class MSGHandler():

    def __init__(
            self,
            pool,
            bot: telegram.API,
            dictionary: config.Dictionary,
            translator: config.Translate,
            reminder: reminders.WordReminder,
    ) -> None:
        self.pool = pool
        self.bot = bot
        self.db = ydb_manage.Query()
        self.dictionary = dictionary
        self.translator = translator
        self.reminder = reminder

    def process(self, body: dict) -> None:
        callback = body.get('callback_query')
        if callback:
            callback = schemas.Callback(**callback)
            if callback.data.startswith(schemas.Commands.ADD.value):
                response = self.add_word(
                    chat_id=callback.message.chat.id,
                    word=callback.data[len(schemas.Commands.ADD.value):],
                )
            elif callback.data.startswith(schemas.Commands.DELETE.value):
                response = self.delete_word(
                    chat_id=callback.message.chat.id,
                    word=callback.data[len(schemas.Commands.DELETE.value):],
                )
            self.bot.delete_keyboard(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
            )
        else:
            try:
                message = schemas.Message(**body.get('message', {}))
            except Exception:
                logger.exception('Unable to parse message')
                return
            if message.text == schemas.Commands.START.value:
                if message.from_.username:
                    username = message.from_.username
                else:
                    username = f'{message.from_.first_name} {message.from_.last_name}'
                response = self.add_user(
                    chat_id=message.from_.id,
                    username=username,
                )
            elif message.text == schemas.Commands.HELP.value:
                response = self.info()
            elif message.text == schemas.Commands.MORE.value:
                self.reminder.send_ripe_words_to_user(chat_id=message.from_.id)
                response = None
            elif message.text == schemas.Commands.REGISTER_COMMANDS.value:
                response = self.set_my_commands()
            else:
                response = self.process_new_word(
                    chat_id=message.from_.id,
                    word=message.text.strip().lower(),
                )
            if response:
                self.bot.send_message(
                    chat_id=message.from_.id,
                    **response.dict(exclude_none=True),
                )

    def set_my_commands(self) -> schemas.TLGResponse:
        self.bot.set_my_commands()
        return schemas.TLGResponse(text=messages.COMMANDS_SET)

    def add_word(self, chat_id: int, word: str) -> schemas.TLGResponse:
        self.pool.retry_operation_sync(self.db.add_word, chat_id=chat_id, word=word)
        return schemas.TLGResponse(text=messages.WORD_ADDED.format(word))

    def delete_word(self, chat_id: int, word: str) -> schemas.TLGResponse:
        self.pool.retry_operation_sync(self.db.delete_word, chat_id=chat_id, word=word)
        return schemas.TLGResponse(text=messages.WORD_DELETED.format(word))

    def add_user(self, chat_id: int, username: str) -> schemas.TLGResponse:
        self.pool.retry_operation_sync(self.db.add_user, chat_id=chat_id, username=username)
        return schemas.TLGResponse(text=f"{messages.USER_ADDED}\n{messages.HELP}")

    def info(self) -> schemas.TLGResponse:
        return schemas.TLGResponse(text=messages.HELP)

    def process_new_word(self, chat_id: int, word: str) -> schemas.TLGResponse:
        dictionary, meaning = self._translate_word(word=word)
        examples = urllib.parse.quote(config.settings.youglish.url_template.format(word=word), safe=':/')
        if len(self.pool.retry_operation_sync(self.db.get_word, chat_id=chat_id, word=word)):
            keyboard = schemas.Keyboards.get_inline_keyboard(
                [
                    schemas.Button(text=messages.DELETE_WORD.format(word),
                                   callback_data=f'{schemas.Commands.DELETE.value}{word}')
                ],
            )
        else:
            keyboard = schemas.Keyboards.get_inline_keyboard(
                [
                    schemas.Button(text=messages.ADD_WORD.format(word),
                                   callback_data=f'{schemas.Commands.ADD.value}{word}')
                ],
            )
        return schemas.TLGResponse(text='\n\n'.join([meaning, dictionary, examples]), reply_markup=keyboard)

    def _translate_word(self, word: str) -> schemas.TLGResponse:
        dictionary = translate.YaDictionary(
            **dict(self.dictionary)).get_translates(word) if config.settings.dictionary_on else ''
        meaning = translate.YaTranslate(**dict(self.translator)).translate(word)
        return dictionary, meaning
