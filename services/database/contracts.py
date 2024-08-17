from dataclasses import dataclass

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