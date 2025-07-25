from dataclasses import dataclass

@dataclass
class Config:
    notes_channel: int
    stats_channel: int
    stats_update_interval_seconds: int
    spreadsheet_url: str
    db_update_interval_seconds: int
    db_type: str
    postgres_host: str
    postgres_port: str
    postgres_db_name: str
    postgres_user: str
    postgres_password: str
    auto_mode: bool
    auto_soft_reset: bool
    auto_soft_reset_interval_days: int