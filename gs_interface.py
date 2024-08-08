import gspread
from datetime import datetime, timedelta
import numpy as np
import os
import json
import Logger
import constants

from constants import safe_execute
from dataclasses import dataclass, field
from config import ConfigFactory


@dataclass
class Columns:
    date_column: list[str] = field(default_factory=list)
    fl_name_column: list[str] = field(default_factory=list)
    squadron_column: list[str] = field(default_factory=list)
    rio_name_column: list[str] = field(default_factory=list)
    plt_name_column: list[str] = field(default_factory=list)
    tail_number_column: list[str] = field(default_factory=list)
    weapon_type_column: list[str] = field(default_factory=list)
    weapon_column: list[str] = field(default_factory=list)
    target_column: list[str] = field(default_factory=list)
    target_angels_column: list[str] = field(default_factory=list)
    angels_column: list[str] = field(default_factory=list)
    speed_column: list[str] = field(default_factory=list)
    range_column: list[str] = field(default_factory=list)
    hit_column: list[str] = field(default_factory=list)
    destroyed_column: list[str] = field(default_factory=list)
    qty_column: list[str] = field(default_factory=list)
    msn_nr_column: list[str] = field(default_factory=list)
    msn_name_column: list[str] = field(default_factory=list)
    event_column: list[str] = field(default_factory=list)
    notes_column: list[str] = field(default_factory=list)


class GsInterface:
    def __init__(self):
        self.__gs_api = gspread.service_account("keys/gspread_api_key.json")

        self.__config = ConfigFactory.get_instance()

        self.__spreadsheet = self.__gs_api.open_by_url(self.__config.spreadsheet_url)
        self.__db_sheet = self.__spreadsheet.worksheet("DATABASE")
        self.__entry_sheets = [self.__spreadsheet.worksheet("ENTRY1")]

        # ldb stands for local database
        self.__ldb_rows = []
        self.__ldb_columns = Columns()

        print(self.__pull_data())

    @safe_execute
    def __pull_data(self):
        data = self.__spreadsheet.values_batch_get(ranges=list(constants.DATA_PULL_INFO.values()))
        values = {name: val['values'] for name, val in zip(constants.DATA_PULL_INFO.keys(), data["valueRanges"])}

        return values


class GsInterfaceFactory:
    __instance = None

    @classmethod
    def get_instance(cls) -> GsInterface:
        if cls.__instance is None:
            cls.__instance = cls.create_instance()
        return cls.__instance

    @staticmethod
    def create_instance() -> GsInterface:
        return GsInterface()
