from dataclasses import asdict

import numpy as np

from clients.databases.contracts import CVW17Database, PlayerStats, SquadronStats, WeaponStats, PartialDebrief, Debrief, \
    CVW17DatabaseRow
from core.config.config import ConfigSingleton
from core.constants import Squadrons, WeaponTypes, Weapons
from discord_.cogs.constants import SOFT_RESET_DATA_PATH
from services.file_handler import FileHandler


class DataManager:
    def __init__(self, db: CVW17Database):
        self.__db = db
        self.__config = ConfigSingleton.get_instance()

        self.__soft_reset_anchor_id = 0
        if self.__config.auto_soft_reset:
            self.__soft_reset_anchor_id = dict(FileHandler.load_json(SOFT_RESET_DATA_PATH)).get('id', 0)

    def get_latest_entry_id(self):
        return self.__db.id_[-1]

    def get_db_rows(self) -> list[CVW17DatabaseRow]:
        rows: list[CVW17DatabaseRow] = []
        keys = list(asdict(self.__db).keys())[1:-1]
        values = np.stack(list(asdict(self.__db).values())[1:], axis=1)
        for row in values:
            rows.append(CVW17DatabaseRow(**{key: value for key,value in zip(keys, row)}))
        return rows

    def __get_soft_reset_filter(self):
        return self.__db.id_ > self.__soft_reset_anchor_id

    def __get_squadron_filter(self, squadron: Squadrons | None, additional_filter = None):
        additional_filter = np.ones(self.__db.pilot_name.shape, np.bool) \
            if additional_filter is None else additional_filter
        squadron_filter = self.__db.squadron == squadron.value \
            if squadron else np.ones(self.__db.pilot_name.shape, np.bool)
        return squadron_filter & additional_filter

    def __get_player_filter(self, player: str):
        lowercase_pilots = np.char.lower(self.__db.pilot_name)
        lowercase_rios = np.char.lower(self.__db.rio_name)
        player = player.lower()
        return (lowercase_pilots == player) | (lowercase_rios == player)

    def __get_weapon_type_filter(self, weapon_type: WeaponTypes):
        return self.__db.weapon_type == weapon_type

    def __get_killed_filter(self):
        return ( self.__db.hit == True ) | ( self.__db.destroyed == True )

    def __get_weapon_filter(self, weapon: Weapons):
        cleaned_array = np.where(self.__db.weapon == None, 'NONE', self.__db.weapon).astype(np.str_)
        return np.char.startswith(cleaned_array, prefix=weapon.value)

    def get_player_stats(self, player: str, squadron: Squadrons | None = None, additional_filter = None) -> PlayerStats:
        squadron_filter = self.__get_squadron_filter(squadron, additional_filter)
        player_filter = self.__get_player_filter(player)
        aa_filter = self.__get_weapon_type_filter(WeaponTypes.AA.value)
        ag_filter = self.__get_weapon_type_filter(WeaponTypes.AG.value)
        killed_filter = self.__get_killed_filter()

        soft_reset_filter = self.__get_soft_reset_filter()

        aa_kills_filter = squadron_filter & player_filter & aa_filter & killed_filter & soft_reset_filter
        ag_drops_filter = squadron_filter & player_filter & ag_filter & soft_reset_filter

        aa_kills = sum(self.__db.qty.astype(int)[aa_kills_filter])
        ag_drops = sum(self.__db.qty.astype(int)[ag_drops_filter])

        return PlayerStats(aa_kills=aa_kills, ag_drops=ag_drops, player_name=player)

    def get_squadron_stats(self, squadron: Squadrons):
        squadron_filter = self.__get_squadron_filter(squadron)
        aa_filter = self.__get_weapon_type_filter(WeaponTypes.AA.value)
        ag_filter = self.__get_weapon_type_filter(WeaponTypes.AG.value)
        killed_filter = self.__get_killed_filter()

        aa_kills_filter = squadron_filter & aa_filter & killed_filter
        ag_drops_filter = squadron_filter & ag_filter

        aa_kills = sum(self.__db.qty.astype(int)[aa_kills_filter])
        ag_drops = sum(self.__db.qty.astype(int)[ag_drops_filter])

        return SquadronStats(aa_kills=aa_kills, ag_drops=ag_drops)

    def __capitalize_name(self, name):
        if name is None:
            return None

        name = name.lower()
        if len(name) == 2:
            return name.upper()

        return name[0].upper() + name[1:]


    def __get_all_player_names(self, squadron: Squadrons | None) -> set[str]:
        filter_ = self.__get_squadron_filter(squadron)

        players = list(set(self.__db.pilot_name[filter_]) | set(self.__db.rio_name[filter_]))
        return {self.__capitalize_name(player) for player in players if player}

    def __apply_leaderboard_weights(self, entry: (str, PlayerStats)):
        return 2 * entry[1].aa_kills + entry[1].ag_drops

    def get_leaderboard(self, squadron: Squadrons) -> dict[str, PlayerStats]:
        players = self.__get_all_player_names(squadron)
        unsorted_leaderboard = {player: self.get_player_stats(player, squadron) for player in players}
        return dict(sorted(unsorted_leaderboard.items(), key=self.__apply_leaderboard_weights, reverse=True))

    def get_weapon_stats(self, weapon: Weapons):
        weapon_filter = self.__get_weapon_filter(weapon)
        killed_filter = self.__get_killed_filter()

        soft_reset_filter = self.__get_soft_reset_filter()

        hits = sum(self.__db.qty.astype(int)[weapon_filter & killed_filter & soft_reset_filter])
        shots = sum(self.__db.qty.astype(int)[weapon_filter & soft_reset_filter])

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
