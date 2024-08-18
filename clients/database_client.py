from abc import ABC, abstractmethod


class DatabaseClient(ABC):
    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def get_db(self):
        ...

    @abstractmethod
    def add_listener(self, func, callback=None):
        ...
