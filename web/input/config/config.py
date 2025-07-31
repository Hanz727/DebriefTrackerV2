import json

from web.input.config._constants import WEB_CONFIG_PATH, MAP_CONFIG_PATH
from web.input.config.contracts import WebConfig, InteractiveMapConfig


class WebConfigSingleton:
    __instance = None

    @classmethod
    def get_instance(cls) -> WebConfig:
        if cls.__instance is None:
            cls.__instance = cls.__load_config()
        return cls.__instance

    @staticmethod
    def __load_config() -> WebConfig:
        with open(WEB_CONFIG_PATH, "r") as f:
            cfg = WebConfig(**json.load(f))
            return cfg

class InteractiveMapConfigSingleton:
    __instance = None

    @classmethod
    def get_instance(cls) -> InteractiveMapConfig:
        if cls.__instance is None:
            cls.__instance = cls.__load_config()
        return cls.__instance

    @staticmethod
    def __load_config() -> InteractiveMapConfig:
        with open(MAP_CONFIG_PATH, "r") as f:
            cfg = InteractiveMapConfig(**json.load(f))
            return cfg
