from dataclasses import dataclass, field, asdict
import numpy as np

from clients.google_sheets.constants import Squadrons, Weapons


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
    plt_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
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

    def get_player_stats(self, player: str, squadron: Squadrons | None = None,
                         additional_filter=None) -> PlayerStats:
        additional_filter = np.ones(self.plt_name.shape, np.bool) if additional_filter is None else additional_filter
        squadron_filter = self.squadron == squadron.value if squadron else np.ones(self.plt_name.shape, np.bool)

        player_filter = ((self.plt_name == player) | (self.rio_name == player)) & squadron_filter & additional_filter
        aa_filter = player_filter & (self.weapon_type == 'A/A') & (self.hit == True)
        ag_filter = player_filter & (self.weapon_type == 'A/G')

        aa_kills = sum(self.qty.astype(int)[aa_filter])
        ag_drops = sum(self.qty.astype(int)[ag_filter])

        return PlayerStats(aa_kills=aa_kills, ag_drops=ag_drops, player_name=player)

    def get_squadron_stats(self, squadron: Squadrons):
        squadron_filter = ( self.squadron == squadron.value )
        aa_filter = ( self.weapon_type == 'A/A' ) & ( ( self.hit == True ) | ( self.destroyed == True ) )
        ag_filter = squadron_filter & ( self.weapon_type == 'A/G' )

        aa_kills = sum(self.qty.astype(int)[squadron_filter & aa_filter])
        ag_drops = sum(self.qty.astype(int)[squadron_filter & ag_filter])

        return SquadronStats(aa_kills=aa_kills, ag_drops=ag_drops)

    def __get_all_player_names(self, squadron: Squadrons | None) -> set[str]:
        players_filter = (self.squadron == squadron.value) if squadron else ()

        players = list(set(self.plt_name[players_filter]) | set(self.rio_name[players_filter]))
        return {player for player in players if player}

    def get_leaderboard(self, squadron: Squadrons) -> dict[str, PlayerStats]:
        players = self.__get_all_player_names(squadron)
        unsorted_leaderboard = {player: self.get_player_stats(player, squadron) for player in players}
        # the sorting is based on a point system where A/A kill is worth 2 points and A/G drop 1 point.
        return dict(sorted(unsorted_leaderboard.items(), key=lambda k: (k[1].aa_kills * 2 + k[1].ag_drops), reverse=True))

    def get_weapon_stats(self, weapon: Weapons):
        weapon_filter = np.char.startswith(self.weapon, weapon.value)

        hit_filter = np.array(weapon_filter) & ((self.hit == True) | (self.destroyed == True))

        hits = sum(self.qty.astype(int)[hit_filter])
        shots = sum(self.qty.astype(int)[weapon_filter])

        misses = shots - hits

        if shots > 0:
            pk = round(hits/shots * 100, 1)
        else:
            pk = 0

        return WeaponStats(hits=hits, misses=misses, pk=pk, shots=shots)

    def __get_latest_entry(self):
        idx = -1 # for testing, keep at -1
        return PartialDebrief(msn_name=self.msn_name[idx], msn_nr=self.msn_nr[idx], posted_by=self.fl_name[idx],
                              event_nr=self.event[idx], notes=self.notes[idx])

    def get_latest_debrief(self):
        latest_entry = self.__get_latest_entry()

        debrief_filter = (( self.notes == latest_entry.notes ) & ( self.msn_nr == latest_entry.msn_nr ) &
                          ( self.msn_name == latest_entry.msn_name) & ( self.event == latest_entry.event_nr) &
                          ( self.fl_name == latest_entry.posted_by ))

        modexes = self.tail_number[debrief_filter]
        pilot_names = self.plt_name[debrief_filter]
        rio_names = self.rio_name[debrief_filter]

        player_stats = {}

        for modex, pilot, rio in zip(modexes, pilot_names, rio_names):
            player_stats[modex] = self.get_player_stats(pilot, None, debrief_filter)
            player_stats[modex].player_name = f'{pilot} | {rio}' if rio else pilot

        debrief = Debrief(**asdict(latest_entry), player_stats=player_stats)

        return debrief

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