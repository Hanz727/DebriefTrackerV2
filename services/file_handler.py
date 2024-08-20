import json
import os
from pathlib import Path
from typing import List

from clients.databases.google_sheets.contracts import MsnDataEntry


class FileHandler:
    @staticmethod
    def get_files_from_directory(directory: Path) -> List[Path]:
        return [file for file in directory.iterdir() if file.is_file()]

    @staticmethod
    def read_file(file: Path) -> str:
        with open(file, "r") as f:
            return f.read()

    @staticmethod
    def sort_files_by_date_created(path: Path) -> list[Path]:
        all_files = os.listdir(path)
        file_info = [
            (file, os.path.getmtime(os.path.join(path, file)))
            for file in all_files
            if os.path.isfile(os.path.join(path, file))
        ]
        return [Path(x[0]) for x in sorted(file_info, key=lambda x: x[1], reverse=True)]

    @staticmethod
    def load_json(path: Path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def load_entries_from_file(path: Path) -> list[MsnDataEntry] :
        msn_data: list[dict] = FileHandler.load_json(path)
        return [MsnDataEntry(**{k.lower(): v for k,v in data.items()}) for data in msn_data]