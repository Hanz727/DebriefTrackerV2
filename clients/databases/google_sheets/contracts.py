from dataclasses import dataclass, field, asdict
import numpy as np

from clients.databases.google_sheets.constants import Squadrons, Weapons


@dataclass
class WeaponStats:
    hits: int
    misses: int
    shots: int
    pk: float

@dataclass
class SquadronStats:
    aa_kills: int
    ag_drops: int

@dataclass
class PlayerStats(SquadronStats):
    player_name: str

@dataclass
class PartialDebrief:
    msn_name: str
    msn_nr: str
    posted_by: str
    event_nr: str
    notes: str

@dataclass
class Debrief(PartialDebrief):
    player_stats: dict[str, PlayerStats]

@dataclass
class CVW17Database:
    size: int = field(default=0)
    date: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    fl_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    squadron: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    rio_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    pilot_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    tail_number: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    weapon_type: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    weapon: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    target: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    target_angels: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    angels: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    speed: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    range: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    hit: np.ndarray = field(default_factory=lambda: np.array([], dtype=bool))
    destroyed: np.ndarray = field(default_factory=lambda: np.array([], dtype=bool))
    qty: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    msn_nr: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    msn_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    event: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    notes: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))

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