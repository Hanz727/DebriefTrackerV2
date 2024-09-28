from dataclasses import asdict

import psycopg2
from typing import override
import numpy as np
from psycopg2._psycopg import connection, cursor

from core.config.config import ConfigSingleton
from services import Logger
from clients.databases.contracts import CVW17Database, CVW17DatabaseRow
from clients.databases.database_client import DatabaseClient
from clients.databases.postgres.constants import DB_FETCH_QUERY, DB_INSERT_QUERY
from core.constants import ON_DB_INSERT_CALLBACK
from core.wrappers import safe_execute


class PostGresClient(DatabaseClient):
    def __init__(self):
        super().__init__()
        self.__config = ConfigSingleton.get_instance()

        self.__db_connection: connection | None = None
        self.__cursor: cursor | None = None

        self.__connect_to_db()

        self.__db_snapshot = CVW17Database()
        self.__fetch_db()

    def __connect_to_db(self):
        if self.__db_connection is None or self.__db_connection.closed:
            self.__db_connection = psycopg2.connect(
                host=self.__config.postgres_host,
                port=self.__config.postgres_port,
                dbname=self.__config.postgres_db_name,
                password=self.__config.postgres_password,
                user=self.__config.postgres_user
            )

        if self.__cursor is None or self.__cursor.closed:
            self.__cursor = self.__db_connection.cursor()

    def __del__(self):
        self.__cursor.close()
        self.__db_connection.close()

    def __fetch_db(self):
        self.__cursor.execute(DB_FETCH_QUERY)
        rows = self.__cursor.fetchall()
        db_transposed = np.array(rows).T[:21]

        fetched_db = CVW17Database(len(rows), *db_transposed)

        old_db_size = self.__db_snapshot.size
        self.__db_snapshot = fetched_db
        if fetched_db.size > old_db_size > 0:
            for func in self.callbacks[ON_DB_INSERT_CALLBACK]:
                func()

    def __insert_row(self, row):
        try:
            # Execute the insert statement with the provided row values
            self.__cursor.execute(DB_INSERT_QUERY, row)

            # Commit the transaction to save the changes
            self.__cursor.connection.commit()
        except Exception as error:
            # Handle any errors and rollback the transaction
            self.__cursor.connection.rollback()
            Logger.error(error)
            Logger.error(row)

    @override
    @safe_execute
    def insert(self, to_insert: CVW17Database | CVW17DatabaseRow):
        if type(to_insert) == CVW17DatabaseRow:
            self.__insert_row(list(asdict(to_insert).values()))
            return

        rows = np.column_stack(list(asdict(to_insert).values())[1:]) # 1: to skip size param
        for row in rows:
            self.__insert_row(row)

    @override
    @safe_execute
    def update(self) -> None:
        if self.__db_connection.closed or self.__cursor.closed:
            self.__connect_to_db()

        self.__fetch_db()

    @override
    def _get_db(self) -> CVW17Database:
        return self.__db_snapshot

