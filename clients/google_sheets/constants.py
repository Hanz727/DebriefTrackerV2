from typing import Final, List, Dict

GOOGLE_SHEET_SPREAD_API_KEY: Final[str] = "keys/gspread_api_key.json"

GSPREAD_KEY_PATH: Final[str] = "keys/gspread_api_key.json"

DATA_PULL_INFO: Final[Dict[str, str]] = {
    "database": "DATABASE!A1:AA",
    "entry_msn_number": "ENTRY1!C3"
}

CVW17_DATABASE_RANGE: Final[str] = "DATABASE!A1:AA"
CVW17_MSN_ENTRY_NUM_RANGE: Final[str] = "ENTRY1!C3"

CVW17_RANGES: Final[List[str]] = [CVW17_DATABASE_RANGE, CVW17_MSN_ENTRY_NUM_RANGE]
