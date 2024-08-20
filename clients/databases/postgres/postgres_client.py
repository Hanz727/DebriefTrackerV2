import psycopg2
from typing import override
import numpy as np
from clients.databases.database_client import DatabaseClient
from clients.databases.google_sheets.contracts import CVW17Database
from clients.databases.postgres.constants import DB_HOST, DB_PORT, DB_NAME, DB_PASSWORD, DB_USER, DB_FETCH_QUERY
from core.constants import ON_DB_INSERT_CALLBACK


class PostGresClient(DatabaseClient):
    def __init__(self):
        super().__init__()
        self.__db_connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            password=DB_PASSWORD,
            user=DB_USER
        )
        self.__cursor = self.__db_connection.cursor()

        self.__db_snapshot = CVW17Database()
        self.__fetch_db()

    def __del__(self):
        self.__cursor.close()
        self.__db_connection.close()

    def __fetch_db(self):
        self.__cursor.execute(DB_FETCH_QUERY)
        rows = self.__cursor.fetchall()
        db_transposed = np.array(rows).T

        fetched_db = CVW17Database(len(rows), *db_transposed)

        old_db_size = self.__db_snapshot.size
        self.__db_snapshot = fetched_db
        if fetched_db.size > old_db_size > 0:
            for func in self.callbacks[ON_DB_INSERT_CALLBACK]:
                func()

    @override
    def update(self) -> None:
        self.__fetch_db()

    @override
    def get_db(self) -> CVW17Database:
        return self.__db_snapshot
