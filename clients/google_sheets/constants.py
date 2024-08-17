from dataclasses import astuple
from enum import Enum
from typing import Final, List, Dict

GOOGLE_SHEET_SPREAD_API_KEY: Final[str] = "keys/gspread_api_key.json"
MSN_DATA_FILES_PATH: Final[str] = "../MissionData/"

class GoogleSheetsRanges(Enum):
    database_headers = "DATABASE!A1:AA1"
    database = "DATABASE!A2:AA"
    msn_data_files = "MISC1!D2:D6"
    msn_data_file = "ENTRY1!E13"


# Must be in the same order as the DATA_PULL_INFO
CVW17_RANGES: Final[List[str]] = [range_.value for range_ in GoogleSheetsRanges]
