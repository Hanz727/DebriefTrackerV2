import os
from importlib.metadata import files
from pathlib import Path

import gspread
from gspread.utils import Dimension

from clients.google_sheets.constants import GOOGLE_SHEET_SPREAD_API_KEY, CVW17_RANGES, MSN_DATA_FILES_PATH, \
    GoogleSheetsRanges
from clients.google_sheets.contracts import CVW17Database
from core.constants import ON_DB_INSERT_CALLBACK
from core.config.config import ConfigSingleton
from core.wrappers import safe_execute
from services.data_handler import DataHandler

import numpy as np

from services.database.db_handler import DbHandler
from services.file_handler import FileHandler


class GoogleSheetsClient:
    def __init__(self):
        self.__google_sheets_api = gspread.service_account(GOOGLE_SHEET_SPREAD_API_KEY)

        self.__config = ConfigSingleton.get_instance()

        self.__spreadsheet = self.__google_sheets_api.open_by_url(self.__config.spreadsheet_url)
        self.__db_sheet = self.__spreadsheet.worksheet("DATABASE")
        self.__entry_sheets = [self.__spreadsheet.worksheet("ENTRY1")]
        self.__misc_sheets = [self.__spreadsheet.worksheet("MISC1")]

        self.__local_db = CVW17Database()

        self.__callbacks = {ON_DB_INSERT_CALLBACK: []}

        self.__db_headers: list[str] = []
        self.__update_local_db(self.__get_db_values())


    @safe_execute
    def __get_db_values(self) -> dict[GoogleSheetsRanges, list]:
        data = self.__spreadsheet.values_batch_get(ranges=CVW17_RANGES)["valueRanges"]
        return {enum_item: val.get('values', [[]]) for enum_item, val in zip(GoogleSheetsRanges, data)}

    @safe_execute
    def __update_local_db(self, values: dict[GoogleSheetsRanges, list]):
        if len(self.__db_headers) == 0:
            self.__db_headers = DataHandler.flatten(values[GoogleSheetsRanges.database_headers])

        db = values[GoogleSheetsRanges.database]

        for row in db:
            DataHandler.pad(row, len(self.__db_headers), '')

        db_transposed = np.array(db).T

        lock = db_transposed[self.__db_headers.index('LOCK')][0] == "TRUE"
        if lock:
            return

        self.__local_db.date = db_transposed[self.__db_headers.index('DATE')]
        self.__local_db.fl_name = db_transposed[self.__db_headers.index('FL NAME')]
        self.__local_db.squadron = db_transposed[self.__db_headers.index('SQUADRON')]
        self.__local_db.rio_name = db_transposed[self.__db_headers.index('RIO NAME')]
        self.__local_db.plt_name = db_transposed[self.__db_headers.index('PLT NAME')]
        self.__local_db.tail_number = db_transposed[self.__db_headers.index('TAIL NUMBER')]
        self.__local_db.weapon_type = db_transposed[self.__db_headers.index('WEAPON TYPE')]
        self.__local_db.weapon = db_transposed[self.__db_headers.index('WEAPON')]
        self.__local_db.target = db_transposed[self.__db_headers.index('TARGET')]
        self.__local_db.target_angels = db_transposed[self.__db_headers.index('TARGET ANGELS')]
        self.__local_db.angels = db_transposed[self.__db_headers.index('ANGELS')]
        self.__local_db.speed = db_transposed[self.__db_headers.index('SPEED')]
        self.__local_db.range = db_transposed[self.__db_headers.index('RANGE')]
        self.__local_db.hit = db_transposed[self.__db_headers.index('HIT')]
        self.__local_db.destroyed = db_transposed[self.__db_headers.index('DESTROYED')]
        self.__local_db.qty = db_transposed[self.__db_headers.index('QTY')]
        self.__local_db.msn_nr = db_transposed[self.__db_headers.index('MSN NR')]
        self.__local_db.msn_name = db_transposed[self.__db_headers.index('MSN NAME')]
        self.__local_db.event = db_transposed[self.__db_headers.index('EVENT')]
        self.__local_db.notes = db_transposed[self.__db_headers.index('NOTES')]

        if self.__local_db.size != len(self.__local_db.date):
            self.__local_db.size = len(self.__local_db.date)
            for func in self.__callbacks[ON_DB_INSERT_CALLBACK]:
                func()

    def __update_data_files(self, values: dict[GoogleSheetsRanges, list]):
        remote_msn_data_files = DataHandler.flatten(values[GoogleSheetsRanges.msn_data_files])[:5]

        local_msn_data_paths: list[Path] = FileHandler.sort_files_by_date_created(Path(MSN_DATA_FILES_PATH))[:5]
        local_msn_data_files: list[str] = DataHandler.pad([str(x.with_suffix('')) for x in local_msn_data_paths],
                                                          5, '')

        if remote_msn_data_files == local_msn_data_files:
            return

        files_range = GoogleSheetsRanges.msn_data_files.value.split('!')[1]

        self.__misc_sheets[0].update(
            range_name= files_range,
            major_dimension=Dimension.cols,
            values=[local_msn_data_files]
        )

        if (local_msn_data_files[0] == remote_msn_data_files[0] or
            values[GoogleSheetsRanges.msn_data_file][0][0] == local_msn_data_files[0]):
            return

        file_range = GoogleSheetsRanges.msn_data_file.value.split('!')[1]

        self.__entry_sheets[0].update(
            range_name= file_range,
            values=[[local_msn_data_files[0]]]
        )

    @safe_execute
    def update(self):
        values = self.__get_db_values()
        if not values:
            return

        self.__update_data_files(values)
        self.__update_local_db(values)

    def get_db(self):
        return self.__local_db

    def add_listener(self, func, callback=None):
        if not callback:
            callback = func.__name__

        if callback not in self.__callbacks:
            self.__callbacks[callback] = []

        self.__callbacks[callback].append(func)
