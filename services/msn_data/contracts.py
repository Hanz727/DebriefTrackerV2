from dataclasses import dataclass

@dataclass
class MsnDataEntry:
    type: int
    weapon_name: str
    dl_callsign: str
    tail_number: str
    pilot_name: str
    rio_name: str
    tgt_name: str
    tgt_tname: str
    speed: float
    angels: int
    angels_tgt: int
    range: int
    destroyed: bool
    hit: bool