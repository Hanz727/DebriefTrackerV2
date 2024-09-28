from pathlib import Path
from typing import Final

DELAY_BETWEEN_MESSAGES_SENT: Final[bool] = True
DELAY_BETWEEN_MESSAGES_SENT_DURATION: Final[float] = 2.0

SOFT_RESET_DATA_PATH: Final[Path] = Path("discord_/cogs/soft_reset_data.json")