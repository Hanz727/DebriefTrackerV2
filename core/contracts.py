from abc import abstractmethod, ABC


class IRunnable(ABC):
    @staticmethod
    @abstractmethod
    def run():
        pass
