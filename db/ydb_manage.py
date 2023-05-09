# import ydb

import os
from collections import namedtuple

import ydb

from db import ydb_queries


class Query():

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

    def get_ripe_words(self, session, max_repetition: int):
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            session.prepare(ydb_queries.RIPE_WORDS),
            {
                '$max_repetition': max_repetition,
            },
            commit_tx=True,
        )
        return result_sets[0].rows


class Schema():
    Table = namedtuple('Table', ['name', 'decription'])
    tables = [
        Table(
            name='users',
            decription=ydb.TableDescription()
            # .with_column(ydb.Column('user_id', ydb.PrimitiveType.Uint64, nullable=False))
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