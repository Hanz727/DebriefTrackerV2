from typing import Final, List, Dict

GOOGLE_SHEET_SPREAD_API_KEY: Final[str] = "keys/gspread_api_key.json"

GSPREAD_KEY_PATH: Final[str] = "keys/gspread_api_key.json"

DATA_PULL_INFO: Final[Dict[str, str]] = {
    "database_headers": "DATABASE!A1:AA1",
    "database": "DATABASE!A2:AA",
    "entry_msn_number": "ENTRY1!C3"
}

CVW17_DATABASE_HEADERS_RANGE: Final[str] = DATA_PULL_INFO["database_headers"]
CVW17_DATABASE_RANGE: Final[str] = DATA_PULL_INFO["database"]
CVW17_MSN_ENTRY_NUM_RANGE: Final[str] = DATA_PULL_INFO["entry_msn_number"]

# Must be in the same order as the DATA_PULL_INFO
CVW17_RANGES: Final[List[str]] = [CVW17_DATABASE_HEADERS_RANGE, CVW17_DATABASE_RANGE, CVW17_MSN_ENTRY_NUM_RANGE]
