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
