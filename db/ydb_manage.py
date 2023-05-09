import os
from functools import wraps
from collections import namedtuple

import ydb

from db import ydb_queries, database
from config import settings


def create_schema_decorator(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ydb.SchemeError:
            with database.get_driver() as driver:
                with ydb.SessionPool(driver) as pool:
                    pool.retry_operation_sync(
                        Schema.create_tables,
                        path=settings.ydb.database,
                    )
            return func(self, *args, **kwargs)

    return inner


class Query():
    @create_schema_decorator
    def add_user(self, session, chat_id: int, username: str) -> None:
        session.transaction().execute(
            session.prepare(ydb_queries.ADD_USER),
            {
                '$chat_id': chat_id,
                '$username': username,
            },
            commit_tx=True,
        )

    def add_word(self, session, chat_id, word) -> None:
        session.transaction().execute(
            session.prepare(ydb_queries.ADD_WORD),
            {
                '$chat_id': chat_id,
                '$word': word,
            },
            commit_tx=True,
        )

    def upsert_word(self, session, chat_id: int, word: str, repetition: int = 0, repeat_after: int = 1) -> None:
        session.transaction().execute(
            session.prepare(ydb_queries.UPSERT_WORD),
            {
                '$chat_id': chat_id,
                '$word': word,
                '$repetition': repetition,
                '$repeat_after': repeat_after,
            },
            commit_tx=True,
        )

    def delete_word(self, session, chat_id: int, word: str) -> None:
        session.transaction().execute(
            session.prepare(ydb_queries.DELETE_WORD),
            {
                '$chat_id': chat_id,
                '$word': word,
            },
            commit_tx=True,
        )

    def get_ripe_words(self, session, chat_id: int, max_repetition: int):
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            session.prepare(ydb_queries.RIPE_WORDS_BY_USER),
            {
                '$max_repetition': max_repetition,
                '$chat_id': chat_id,
                '$limit': settings.daily_limit,
            },
            commit_tx=True,
        )
        return result_sets[0].rows

    def get_users(self, session):
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            session.prepare(ydb_queries.GET_USERS),
            {},
            commit_tx=True,
        )
        return result_sets[0].rows


class Schema():
    Table = namedtuple('Table', ['name', 'decription'])
    tables = [
        Table(
            name='users',
            decription=ydb.TableDescription()
            .with_column(ydb.Column('chat_id', ydb.PrimitiveType.Int64))
            .with_column(ydb.Column('username', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
            .with_column(ydb.Column('created_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)))
            .with_primary_key('chat_id')
        ),
        Table(
            name='words',
            decription=ydb.TableDescription()
            .with_column(ydb.Column('chat_id', ydb.PrimitiveType.Int64))
            .with_column(ydb.Column('word', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
            .with_column(ydb.Column('translate', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
            .with_column(ydb.Column('created_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)))
            .with_column(ydb.Column('updated_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)))
            .with_column(ydb.Column('repeat_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)))
            .with_column(ydb.Column('repetition', ydb.OptionalType(ydb.PrimitiveType.Uint32)))
            .with_primary_key('chat_id')
            .with_primary_key('word')
        )
    ]

    @classmethod
    def create_tables(cls, session, path: str):
        for table in cls.tables:
            session.create_table(
                os.path.join(path, table.name),
                table.decription,
            )

    @classmethod
    def describe_table(cls, session, path, name):
        result = session.describe_table(os.path.join(path, name))
        print("\n> describe table: series")
        for column in result.columns:
            print("column, name:", column.name, ",", str(column.type).strip())
