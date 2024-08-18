from abc import ABC, abstractmethod

from clients.google_sheets.contracts import CVW17Database


class DatabaseClient(ABC):
    @abstractmethod
    def update(self) -> None:
        ...

    @abstractmethod
    def get_db(self) -> CVW17Database:
        ...

    @abstractmethod
    def add_listener(self, func, callback=None) -> None:
        ...
