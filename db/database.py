import logging

import ydb
import ydb.iam

from config import settings

logger = logging.getLogger(__name__)


def get_driver():
    driver = ydb.Driver(
        endpoint=settings.ydb.endpoint,
        database=settings.ydb.database,
        credentials=ydb.iam.MetadataUrlCredentials(),
    )
    try:
        driver.wait(fail_fast=True, timeout=5)
    except TimeoutError as err:
        logger.error("Connect failed to YDB. Last reported errors by discovery: %s", driver.discovery_debug_details())
        raise err
    return driver
