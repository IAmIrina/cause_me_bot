import ydb
import ydb.iam
import logging

from config import settings

logger = logging.getLogger(__name__)


def get_driver():
    driver = ydb.Driver(
        endpoint=settings.ydb.endpoint,
        database=settings.ydb.database,
        credentials=ydb.iam.ServiceAccountCredentials.from_file(
            settings.ydb.sa_key_file,
        ),
    )
    try:
        driver.wait(fail_fast=True, timeout=5)
    except TimeoutError as err:
        logger.error("Connect failed to YDB")
        logger.error("Last reported errors by discovery:")
        logger.error(driver.discovery_debug_details())
        raise err
    return driver
