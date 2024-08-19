from abc import ABC, abstractmethod

from clients.google_sheets.contracts import CVW17Database
from core.constants import ON_DB_INSERT_CALLBACK


class DatabaseClient(ABC):
    def __init__(self):
        self.callbacks = {ON_DB_INSERT_CALLBACK: []}

    @abstractmethod
    def update(self) -> None:
        ...

    @abstractmethod
    def get_db(self) -> CVW17Database:
        ...

    def add_listener(self, func, callback=None) -> None:
        if not callback:
            callback = func.__name__

        if callback not in self.callbacks:
            self.callbacks[callback] = []

        self.callbacks[callback].append(func)

