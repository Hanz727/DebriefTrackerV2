from pathlib import Path
from typing import Final

DISCORD_COGS_DIRECTORY: Final[Path] = Path("cogs")
DISCORD_TOKEN_PATH: Final[Path] = Path("keys/discord.token")

ON_DB_INSERT_CALLBACK = "on_db_insert"