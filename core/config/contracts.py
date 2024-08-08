from dataclasses import dataclass


@dataclass
class Config:
    notes_channel: int
    stats_channel: int
    stats_update_interval_seconds: int
    spreadsheet_url: str
    google_sheets_update_interval_seconds: int
