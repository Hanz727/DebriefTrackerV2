from dataclasses import dataclass, field
from datetime import datetime

import numpy as np


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
    id_: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))

@dataclass
class CVW17DatabaseRow:
    date: str | datetime
    fl_name: str | None
    squadron: str | None
    rio_name: str | None
    pilot_name: str | None
    tail_number: int | None
    weapon_type: str | None # A/A | A/G | N/A
    weapon: str | None
    target: str | None
    target_angels: int | None
    angels: int | None
    speed: float | None
    range: int | None
    hit: bool | None
    destroyed: bool | None
    qty: int | None
    msn_nr: str | None
    msn_name: str | None
    event: str | None
    notes: str | None