import gspread

from clients.google_sheets.constants import GOOGLE_SHEET_SPREAD_API_KEY, DATA_PULL_INFO, CVW17_RANGES
from clients.google_sheets.contracts import CVW17Database
from core.config.config import ConfigSingleton
from core.wrappers import safe_execute
from services.data_handler import DataHandler

import numpy as np


class GoogleSheetsClient:
    __instance = None

    def __init__(self):
        self.__google_sheets_api = gspread.service_account(GOOGLE_SHEET_SPREAD_API_KEY)

        self.__config = ConfigSingleton.get_instance()

        self.__spreadsheet = self.__google_sheets_api.open_by_url(self.__config.spreadsheet_url)
        self.__db_sheet = self.__spreadsheet.worksheet("DATABASE")
        self.__entry_sheets = [self.__spreadsheet.worksheet("ENTRY1")]

        self.__local_db = CVW17Database()
        self.__local_db_size: int = 0

        self.__db_on_resize_callback_funcs = []

        self.__db_headers: list[str] = []
        self.__update_local_db(self.__get_db_values())

    @safe_execute
    def __get_db_values(self):
        data = self.__spreadsheet.values_batch_get(ranges=CVW17_RANGES)["valueRanges"]
        return {name: val.get('values', [['']]) for name, val in zip(DATA_PULL_INFO.keys(), data)}

    @safe_execute
    def __update_local_db(self, db_values: dict[str, list]):
        if len(self.__db_headers) == 0:
            self.__db_headers = DataHandler.flatten(db_values["database_headers"])

        db = db_values["database"]

        # Pad all the rows to be the same length
        for row in db:
            DataHandler.pad(row, len(self.__db_headers), '')

        # transpose to have an array by columns not rows
        db_transposed = np.array(db).T

        # First element in LOCK column is a boolean value
        lock = db_transposed[self.__db_headers.index('LOCK')][0] == "TRUE"
        # If the db is locked, don't update the local db
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

        # run the on_resize callback
        if self.__local_db_size != len(self.__local_db.date):
            self.__local_db_size = self.__local_db.date
            for func in self.__db_on_resize_callback_funcs:
                func()

    def add_db_on_resize_callback(self, func):
        self.__db_on_resize_callback_funcs.append(func)

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance
