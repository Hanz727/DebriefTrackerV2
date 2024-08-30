import psycopg2
from typing import override
import numpy as np

from clients.databases.contracts import CVW17Database
from clients.databases.database_client import DatabaseClient
from clients.databases.postgres.constants import DB_FETCH_QUERY
from core.config.config import ConfigSingleton
from core.constants import ON_DB_INSERT_CALLBACK
from core.wrappers import safe_execute


class PostGresClient(DatabaseClient):
    def __init__(self):
        super().__init__()
        self.__config = ConfigSingleton.get_instance()

        self.__db_connection = psycopg2.connect(
            host=self.__config.postgres_host,
            port=self.__config.postgres_port,
            dbname=self.__config.postgres_db_name,
            password=self.__config.postgres_password,
            user=self.__config.postgres_user
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
        db_transposed = np.array(rows).T[:20]

        fetched_db = CVW17Database(len(rows), *db_transposed)

        old_db_size = self.__db_snapshot.size
        self.__db_snapshot = fetched_db
        if fetched_db.size > old_db_size > 0:
            for func in self.callbacks[ON_DB_INSERT_CALLBACK]:
                func()

    @safe_execute
    @override
    def insert(self, rows: CVW17Database):
        print(rows)

    @safe_execute
    @override
    def update(self) -> None:
        self.__fetch_db()

    @override
    def _get_db(self) -> CVW17Database:
        return self.__db_snapshot
