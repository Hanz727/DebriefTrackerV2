from datetime import datetime
from pathlib import Path

import numpy as np

from clients.databases.contracts import CVW17Database
from core.constants import MODEX_TO_SQUADRON
from services.data_handler import DataHandler
from services.file_handler import FileHandler
from services.msn_data.contracts import MsnDataEntry


class MsnDataHandler:
    @staticmethod
    def entry_to_db(entry: MsnDataEntry, db: CVW17Database, msn_nr: int):
        """
            The MSN DATA FILE format is:
            {
            "TYPE": 1, "WEAPON_NAME": "AIM-54C-Mk60",
            "DL_CALLSIGN": "SR31", "TAIL_NUMBER": "107",
            "PILOT_NAME": "Alexandra", "RIO_NAME": "Leikner",
            "TGT_NAME": "F-16C_50", "TGT_TNAME": "F-16C_50",
            "SPEED": 0.95, "ANGELS": 32,
            "ANGELS_TGT": 21, "RANGE": 43,
            "DESTROYED": false, "HIT": false
            }

            TYPE is either 1 or 2, where 1 is A/A and 2 is A/G
            TAIL_NUMBER is a string not int like in db
        """
        db.size += 1
        np.append(db.date, datetime.now().strftime("%m-%d-%Y %H%M"))
        np.append(db.fl_name, "AUTO")
        np.append(db.msn_name, "AUTO MODE")
        np.append(db.event, "AUTO")
        np.append(db.msn_nr, msn_nr)
        np.append(db.notes, "AUTO MODE")
        np.append(db.qty, 1)

        np.append(db.squadron, MODEX_TO_SQUADRON[DataHandler.get_hundreth(int(entry.tail_number))].value)
        np.append(db.rio_name, entry.rio_name)
        np.append(db.pilot_name, entry.pilot_name)
        np.append(db.tail_number, int(entry.tail_number))
        np.append(db.weapon_type, "A/A" if entry.type == 1 else "A/G")
        np.append(db.weapon, entry.weapon_name)
        np.append(db.target, entry.tgt_name)
        np.append(db.target_angels, entry.angels_tgt)
        np.append(db.angels, entry.angels)
        np.append(db.speed, entry.speed)
        np.append(db.range, entry.range)
        np.append(db.hit, entry.hit)
        np.append(db.destroyed, entry.destroyed)

        return db

    @staticmethod
    def load_entries_from_file(path: Path) -> list[MsnDataEntry] :
        msn_data: list[dict] = FileHandler.load_json(path)
        return [MsnDataEntry(**{k.lower(): v for k,v in data.items()}) for data in msn_data]
