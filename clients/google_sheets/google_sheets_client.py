import gspread

from clients.google_sheets.constants import GOOGLE_SHEET_SPREAD_API_KEY, DATA_PULL_INFO, CVW17_RANGES
from clients.google_sheets.contracts import Columns
from core.config.config import ConfigSingleton


class GoogleSheetsClient:

    def __init__(self):
        self.__google_sheets_api = gspread.service_account(GOOGLE_SHEET_SPREAD_API_KEY)

        self.__config = ConfigSingleton.get_instance()

        self.__spreadsheet = self.__google_sheets_api.open_by_url(self.__config.spreadsheet_url)
        self.__db_sheet = self.__spreadsheet.worksheet("DATABASE")
        self.__entry_sheets = [self.__spreadsheet.worksheet("ENTRY1")]

        self.__local_db_rows = []
        self.__local_db_columns = Columns()

    def __get_values(self):
        data = self.__spreadsheet.values_batch_get(ranges=CVW17_RANGES)
        return {name: val["values"] for name, val in zip(DATA_PULL_INFO.keys(), data["valueRanges"])}

    def get_data(self):
        return self.__get_values()
