from pathlib import Path
from typing import Final

from core.constants import BASE_DIR

WEB_CONFIG_PATH: Final[Path] = BASE_DIR / Path("web/input/web_config.json")
MAP_CONFIG_PATH: Final[Path] = BASE_DIR / Path("web/input/map_config.json")
