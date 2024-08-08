from pathlib import Path
from typing import List


class FileHandler:
    @staticmethod
    def get_files_from_directory(directory: Path) -> List[Path]:
        return [file for file in directory.iterdir() if file.is_file()]

    @staticmethod
    def read_file(file: Path) -> str:
        with open(file, "r") as f:
            return f.read()
