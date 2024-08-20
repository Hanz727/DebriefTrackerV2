from dataclasses import dataclass

@dataclass
class Config:
    notes_channel: int
    stats_channel: int
    stats_update_interval_seconds: int
    spreadsheet_url: str
    google_sheets_update_interval_seconds: int
    db_type: str
    postgres_host: str
    postgres_port: str
    postgres_db_name: str
    postgres_user: str
    postgres_password: str