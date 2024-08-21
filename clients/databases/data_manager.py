from dataclasses import asdict

from clients.databases.google_sheets.constants import Squadrons, Weapons, WeaponTypes
from clients.databases.google_sheets.contracts import (CVW17Database, PlayerStats, SquadronStats, PartialDebrief,
    WeaponStats, Debrief)
import numpy as np

class DataManager:
    def __init__(self, db: CVW17Database):
        self.__db = db

    def get_player_stats(self, player: str, squadron: Squadrons | None = None, additional_filter = None) -> PlayerStats:
        additional_filter = np.ones(self.__db.pilot_name.shape, np.bool) if additional_filter is None else additional_filter
        squadron_filter = self.__db.squadron == squadron.value if squadron else np.ones(self.__db.pilot_name.shape, np.bool)

        player_filter = ((self.__db.pilot_name == player) | (self.__db.rio_name == player)) & squadron_filter & additional_filter
        aa_filter = player_filter & (self.__db.weapon_type == WeaponTypes.AA.value) & (self.__db.hit == True)
        ag_filter = player_filter & (self.__db.weapon_type == WeaponTypes.AG.value)

        aa_kills = sum(self.__db.qty.astype(int)[aa_filter])
        ag_drops = sum(self.__db.qty.astype(int)[ag_filter])

        return PlayerStats(aa_kills=aa_kills, ag_drops=ag_drops, player_name=player)

    def get_squadron_stats(self, squadron: Squadrons):
        squadron_filter = ( self.__db.squadron == squadron.value )
        aa_filter = ( self.__db.weapon_type == WeaponTypes.AA.value ) & ( ( self.__db.hit == True )
                                                                          | ( self.__db.destroyed == True ) )
        ag_filter = squadron_filter & ( self.__db.weapon_type == WeaponTypes.AG.value)

        aa_kills = sum(self.__db.qty.astype(int)[squadron_filter & aa_filter])
        ag_drops = sum(self.__db.qty.astype(int)[squadron_filter & ag_filter])

        return SquadronStats(aa_kills=aa_kills, ag_drops=ag_drops)

    def __get_all_player_names(self, squadron: Squadrons | None) -> set[str]:
        players_filter = (self.__db.squadron == squadron.value) if squadron else ()

        players = list(set(self.__db.pilot_name[players_filter]) | set(self.__db.rio_name[players_filter]))
        return {player for player in players if player}

    def __apply_leaderboard_weights(self, entry: (str, PlayerStats)):
        return 2 * entry[1].aa_kills + entry[1].ag_drops

    def get_leaderboard(self, squadron: Squadrons) -> dict[str, PlayerStats]:
        players = self.__get_all_player_names(squadron)
        unsorted_leaderboard = {player: self.get_player_stats(player, squadron) for player in players}
        return dict(sorted(unsorted_leaderboard.items(), key=self.__apply_leaderboard_weights, reverse=True))

    def get_weapon_stats(self, weapon: Weapons):
        weapon_filter = np.char.startswith(self.__db.weapon, weapon.value)

        hit_filter = np.array(weapon_filter) & ((self.__db.hit == True) | (self.__db.destroyed == True))

        hits = sum(self.__db.qty.astype(int)[hit_filter])
        shots = sum(self.__db.qty.astype(int)[weapon_filter])

        misses = shots - hits

        if shots > 0:
            pk = round(hits/shots * 100, 1)
        else:
            pk = 0

        return WeaponStats(hits=hits, misses=misses, pk=pk, shots=shots)

    def __get_latest_entry(self):
        return PartialDebrief(msn_name=self.__db.msn_name[-1], msn_nr=self.__db.msn_nr[-1], posted_by=self.__db.fl_name[-1],
                              event_nr=self.__db.event[-1], notes=self.__db.notes[-1])

    def get_latest_debrief(self):
        latest_entry = self.__get_latest_entry()

        debrief_filter = (( self.__db.notes == latest_entry.notes ) & ( self.__db.msn_nr == latest_entry.msn_nr ) &
                          ( self.__db.msn_name == latest_entry.msn_name) & ( self.__db.event == latest_entry.event_nr) &
                          ( self.__db.fl_name == latest_entry.posted_by ))

        modexes = self.__db.tail_number[debrief_filter]
        pilot_names = self.__db.pilot_name[debrief_filter]
        rio_names = self.__db.rio_name[debrief_filter]

        player_stats = {}

        for modex, pilot, rio in zip(modexes, pilot_names, rio_names):
            player_stats[modex] = self.get_player_stats(pilot, None, debrief_filter)
            player_stats[modex].player_name = f'{pilot} | {rio}' if rio else pilot

        debrief = Debrief(**asdict(latest_entry), player_stats=player_stats)

        return debrief
