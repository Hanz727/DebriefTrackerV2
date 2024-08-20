import json
from dataclasses import asdict

from clients.databases.constants import DbTypes
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
            cfg = Config(**json.load(f))

            correct_db_types = list(x.value for x in DbTypes)

            if cfg.db_type not in correct_db_types:
                raise Exception(f"db_type in config must be in: {correct_db_types}")

            return cfg
