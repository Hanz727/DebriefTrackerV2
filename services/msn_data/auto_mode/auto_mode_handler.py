from clients.databases.database_client import DatabaseClient
from services.msn_data.auto_mode.msn_data_monitor import MsnDataMonitor


class AutoModeHandler:
    def __init__(self, database_client: DatabaseClient):
        self.__monitor = MsnDataMonitor()
        self.__database_client = database_client

    def update(self):
        self.__monitor.update()
        self.__monitor.insert_data_into(self.__database_client)
