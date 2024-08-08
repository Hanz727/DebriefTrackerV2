import json

from core.config._constants import CONFIG_PATH
from core.config.contracts import Config


class ConfigSingleton:
    __instance = None

    @classmethod
    def get_instance(cls) -> Config:
        if cls.__instance is None:
            cls.__instance = cls.__load_config()
        return cls.__instance

    @staticmethod
    def __load_config() -> Config:
        with open(CONFIG_PATH, "r") as f:
            return Config(**json.load(f))
