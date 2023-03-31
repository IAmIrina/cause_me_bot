import json
import logging
from http import HTTPStatus

import ydb
import ydb.iam

import core.reminders as reminders
from config import settings
from core.handlers import MSGHandler
from db import database
from lib import telegram
from tests.data import messages

logger = logging.getLogger(__name__)


def process_event(event, _) -> dict:
    try:
        body = json.loads(event['body'])
    except Exception as err:
        logger.warning('error to parse message: %s', err)
        return {
            'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY
        }
    logger.debug('Incoming message')
    logger.debug(body)
    with database.get_driver() as driver:
        with ydb.SessionPool(driver) as pool:
            MSGHandler(
                pool,
                telegram.API(
                    settings.telegram.endpoint,
                    settings.telegram.token,
                ),
                settings.dictionary,
                settings.translate,
            ).process(body)
    return {
        'statusCode': HTTPStatus.OK,
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
        'statusCode': HTTPStatus.OK,
    }


if __name__ == '__main__':
    process_event(event={'body': json.dumps(messages.new_word_letter)}, _=None),
    # with database.get_driver() as driver:
    #     with ydb.SessionPool(driver) as pool:
    #         pool.retry_operation_sync(
    #             ydb_manage.Schema.create_tables,
    #             path=settings.ydb.database,
    #         )
    # print(process_event(event=messages.new_word_letter, _=None),
    #       # process_event(event=messages.delete_word, _=None),
    #       process_event(event=messages.new_user, _=None),
    #       )
    # process_event(event=messages.new_word_rain, _=None)
    # process_event(event=messages.new_word_lucky, _=None)
    # process_event(event=messages.new_word_morning_another_user, _=None)
    # remind()
    # exit(0)
    pass
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
