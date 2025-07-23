from abc import ABC, abstractmethod

from clients.databases.contracts import CVW17Database, CVW17DatabaseRow
from clients.databases.data_manager import DataManager
from core.constants import ON_DB_INSERT_CALLBACK, ON_REPORT_INSERT_CALLBACK


class DatabaseClient(ABC):
    def __init__(self):
        self.callbacks = {ON_DB_INSERT_CALLBACK: [], ON_REPORT_INSERT_CALLBACK: []}

    @abstractmethod
    def insert(self, to_insert: CVW17Database) -> None:
        ...

    @abstractmethod
    def remove(self, row: CVW17DatabaseRow) -> None:
        ...

    @abstractmethod
    def update_local(self) -> None:
        ...

    @abstractmethod
    def get_db(self) -> CVW17Database:
        return CVW17Database()

    def get_data_manager(self) -> DataManager:
        return DataManager(self.get_db())

    def add_listener(self, func, callback=None) -> None:
        if not callback:
            callback = func.__name__

        if callback not in self.callbacks:
            self.callbacks[callback] = []

        self.callbacks[callback].append(func)

