from dataclasses import dataclass

@dataclass
class WeaponStats:
    hits: int
    misses: int
    pk: float

@dataclass
class SquadronStats:
    aa_kills: int
    ag_drops: int

@dataclass
class PlayerStats(SquadronStats):
    player_name: str

@dataclass
class Debrief:
    msn_name: str
    msn_nr: int
    posted_by: str
    event_nr: str
    notes: str
    player_stats: dict[str, PlayerStats]