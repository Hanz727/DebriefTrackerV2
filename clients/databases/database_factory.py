from clients.databases.constants import DbTypes
from clients.databases.database_client import DatabaseClient
from clients.databases.google_sheets.google_sheets_client import GoogleSheetsClient
from clients.databases.postgres.postgres_client import PostGresClient
from core.config.config import ConfigSingleton


class DatabaseFactory:
    def __init__(self):
        self.__config = ConfigSingleton.get_instance()

    def create_database(self) -> DatabaseClient:
        if self.__config.db_type == DbTypes.google_sheets.value:
            return GoogleSheetsClient()
        if self.__config.db_type == DbTypes.postgres.value:
            return PostGresClient()

        raise Exception(f"db_type: {self.__config.db_type} doesn't exist!")