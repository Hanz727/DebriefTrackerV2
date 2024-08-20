from enum import Enum
from typing import Final, List

GOOGLE_SHEET_SPREAD_API_KEY: Final[str] = "keys/gspread_api_key.json"
MSN_DATA_FILES_PATH: Final[str] = "../MissionData/"

class Squadrons(Enum):
    VF103 = 'VF-103'
    VFA34 = 'VFA-34'

class Weapons(Enum):
    # These names are prefixes and thus must match for all the weapon types, i.e. AIM-54(C-MK60/B-MK47), AIM-9(M/X/F)
    phoenix = 'AIM-54'
    amraam = 'AIM-120'
    sidewinder = 'AIM-9'
    sparrow = 'AIM-7'

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
