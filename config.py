from dataclasses import dataclass
from typing import Optional
import json
import os
import Logger
import constants


@dataclass
class Config:
    notes_channel: int
    stats_channel: int
    stats_update_interval_seconds: int
    spreadsheet_url: str


class ConfigSingleton:
    __instance = None

    @classmethod
    def get_instance(cls) -> Config:
        if cls.__instance is None:
            cls.__instance = cls.__load_config()
        return cls.__instance

    @staticmethod
    def __load_config(path=constants.CONFIG_PATH) -> Config:
        if not os.path.exists(path):
            Logger.error("Unable to load config, path: " + path + " does not exist!")
            exit(-1)

        with open(path, "r") as f:
            return Config(**json.load(f))
