import ydb
import ydb.iam
import logging

from http import HTTPStatus

from config import settings

from db import ydb_manage, database

from lib import schemas, telegram
from handlers import MSGHandler
import reminders
from tests.data import messages


logger = logging.getLogger(__name__)


def process_event(event, _) -> dict:
    try:
        message = schemas.Message(**event.get('message'))
    except BaseException as err:
        logger.warning('error to parse message: %s', err)
        return {'code': HTTPStatus.UNPROCESSABLE_ENTITY}

    with database.get_driver() as driver:
        with ydb.SessionPool(driver) as pool:
            handler = MSGHandler(pool)
            if message.text == '/start':
                response = handler.add_user(
                    chat_id=message.from_.id,
                    username=message.from_.username,
                )
            elif message.text == '/help':
                response = handler.info()
            elif message.text.startswith('-'):
                response = handler.delete_word(
                    chat_id=message.from_.id,
                    word=message.text[1:].strip(),
                )
            else:
                response = handler.add_word(
                    chat_id=message.from_.id,
                    word=message.text.strip(),
                )
    telegram.API(settings.telegram.endpoint, settings.telegram.token).send_message(
        text=response,
        chat_id=message.from_.id,
    )
    return {
        'statusCode': 200,
    }


def remind(*_):
    with database.get_driver() as driver:
        with ydb.SessionPool(driver) as pool:

            words = reminders.WordReminder(
                pool,
                telegram.API(settings.telegram.endpoint, settings.telegram.token),
            )
            words.remind_to_repeat_words(intervals=settings.intervals)
    return {
        'statusCode': 200,
    }


if __name__ == '__main__':
    with database.get_driver() as driver:
        with ydb.SessionPool(driver) as pool:
            pool.retry_operation_sync(
                ydb_manage.Schema.create_tables,
                path=settings.ydb.database,
            )
    print(process_event(event=messages.new_word_letter, _=None),
          # process_event(event=messages.delete_word, _=None),
          process_event(event=messages.new_user, _=None),
          )
    process_event(event=messages.new_word_rain, _=None)
    process_event(event=messages.new_word_lucky, _=None)
    process_event(event=messages.new_word_morning_another_user, _=None)
    remind()
    exit(0)

    # handle_event(event=messages.income, _=None)
    # result = pool.retry_operation_sync(
    #     ydb_tables.create_tables,
    #     path=settings.ydb.database,
    #     tables=ydb_tables.tables)
    # description = [
    #     pool.retry_operation_sync(ydb_tables.describe_table, path=settings.ydb.database, name=table.name)
    #     for table in ydb_tables.tables
    # ]
    # logger.info(description)
    # pool.retry_operation_sync(ydb_queries.upsert_word, chat_id=86815320, word='hello')
    # words = pool.retry_operation_sync(ydb_queries.get_by_chat_id, chat_id=86815320)
    # for row in words.rows:
    #     print("words:", row.word, ", air date:", row.repeat_at)
