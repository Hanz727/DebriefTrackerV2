from enum import Enum
from typing import Final, List

GOOGLE_SHEETS_KEY_PATH: Final[str] = "keys/gspread_api_key.json"

class GoogleSheetsRanges(Enum):
    database_headers = "DATABASE!A1:AA1"
    database = "DATABASE!A2:AA"
    msn_data_files = "MISC1!D2:D6"
    msn_data_file = "ENTRY1!E13"
    id_table = "ENTRY1!K4:L13"
    entry_modexes = "ENTRY1!J4:J13"
    entry_dataview = "ENTRY1!N4:X126"
    entry_should_update = "ENTRY1!C13"

    def get_cell_range(self):
        return self.value.split('!')[-1]

# Must be in the same order as the DATA_PULL_INFO
CVW17_RANGES: Final[List[str]] = [range_.value for range_ in GoogleSheetsRanges]
