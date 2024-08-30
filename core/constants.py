from enum import Enum
from pathlib import Path
from typing import Final

DISCORD_COGS_DIRECTORY: Final[Path] = Path("cogs")
DISCORD_TOKEN_PATH: Final[Path] = Path("keys/discord.token")
MSN_DATA_FILES_PATH: Final[Path] = Path("../MissionData/")

ON_DB_INSERT_CALLBACK = "on_db_insert"


class Squadrons(Enum):
    VF103 = 'VF-103'
    VFA34 = 'VFA-34'


MODEX_TO_SQUADRON: Final[dict[int, Squadrons]] = {
    100: Squadrons.VF103,
    200: Squadrons.VFA34
}


class Weapons(Enum):
    # These names are prefixes and thus must match for all the weapon types, i.e. AIM-54(C-MK60/B-MK47), AIM-9(M/X/F)
    phoenix = 'AIM-54'
    amraam = 'AIM-120'
    sidewinder = 'AIM-9'
    sparrow = 'AIM-7'


class WeaponTypes(Enum):
    AA = "A/A"
    AG = "A/G"
    UNKNOWN = "N/A"