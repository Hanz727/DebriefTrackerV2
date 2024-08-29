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
    def add_entry_to_db(entry: MsnDataEntry, db: CVW17Database, msn_nr: int):
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
        db.date = np.append(db.date, datetime.now().strftime("%m-%d-%Y %H:%M:%S"))
        db.fl_name = np.append(db.fl_name, "AUTO")
        db.msn_name = np.append(db.msn_name, "AUTO MODE")
        db.event = np.append(db.event, "AUTO")
        db.msn_nr = np.append(db.msn_nr, msn_nr)
        db.notes = np.append(db.notes, "AUTO MODE")
        db.qty = np.append(db.qty, 1)
        db.squadron = np.append(db.squadron, MODEX_TO_SQUADRON[DataHandler.get_hundreth(int(entry.tail_number))].value)
        db.rio_name = np.append(db.rio_name, entry.rio_name)
        db.pilot_name = np.append(db.pilot_name, entry.pilot_name)
        db.tail_number = np.append(db.tail_number, int(entry.tail_number))
        db.weapon_type = np.append(db.weapon_type, "A/A" if entry.type == 1 else "A/G")
        db.weapon = np.append(db.weapon, entry.weapon_name)
        db.target = np.append(db.target, entry.tgt_name)
        db.target_angels = np.append(db.target_angels, entry.angels_tgt)
        db.angels = np.append(db.angels, entry.angels)
        db.speed = np.append(db.speed, entry.speed)
        db.range = np.append(db.range, entry.range)
        db.hit = np.append(db.hit, entry.hit)
        db.destroyed = np.append(db.destroyed, entry.destroyed)

        return db

    @classmethod
    def add_entries_to_db(cls, entries: list[MsnDataEntry], db: CVW17Database, msn_nr: int):
        for entry in entries:
           cls.add_entry_to_db(entry, db, msn_nr)
        return db

    @staticmethod
    def get_difference_between_entries(entries_old: list[MsnDataEntry], entries_new: list[MsnDataEntry]) -> list[MsnDataEntry]:
        for entry in entries_old:
            if entry in entries_new:
                entries_new.remove(entry)
        return entries_new

    @staticmethod
    def load_entries_from_dict(entries: list[dict]):
        rtn = []
        for entry in entries:
            rtn.append(MsnDataEntry(**{k.lower(): v for k, v in entry.items()}))
        return rtn

    @staticmethod
    def load_entries_from_file(path: Path) -> list[MsnDataEntry] :
        msn_data: list[dict] = FileHandler.load_json(path)
        return [MsnDataEntry(**{k.lower(): v for k, v in data.items()}) for data in msn_data]
