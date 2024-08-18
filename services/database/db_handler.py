from clients.google_sheets.contracts import CVW17Database
from services.database.constants import Squadrons, Weapons
import numpy as np

from services.database.contracts import PlayerStats, WeaponStats, PartialDebrief, Debrief, SquadronStats
from dataclasses import asdict

class DbHandler:
    @staticmethod
    def get_player_stats(db: CVW17Database, player: str, squadron: Squadrons | None = None, additional_filter = None) -> PlayerStats:
        additional_filter = np.ones(db.plt_name.shape, np.bool) if additional_filter is None else additional_filter
        squadron_filter = db.squadron == squadron.value if squadron else np.ones(db.plt_name.shape, np.bool)

        player_filter = ( (db.plt_name == player) | (db.rio_name == player) ) & squadron_filter & additional_filter
        aa_filter = player_filter & (db.weapon_type == 'A/A') & (db.hit == 'TRUE')
        ag_filter = player_filter & (db.weapon_type == 'A/G')

        aa_kills = sum(db.qty.astype(int)[aa_filter])
        ag_drops = sum(db.qty.astype(int)[ag_filter])

        return PlayerStats(aa_kills=aa_kills, ag_drops=ag_drops, player_name=player)

    @staticmethod
    def get_squadron_stats(db: CVW17Database, squadron: Squadrons):
        squadron_filter = ( db.squadron == squadron.value )
        aa_filter = ( db.weapon_type == 'A/A' ) & ( ( db.hit == 'TRUE' ) | ( db.destroyed == 'TRUE' ) )
        ag_filter = squadron_filter & ( db.weapon_type == 'A/G' )

        aa_kills = sum(db.qty.astype(int)[squadron_filter & aa_filter])
        ag_drops = sum(db.qty.astype(int)[squadron_filter & ag_filter])

        return SquadronStats(aa_kills=aa_kills, ag_drops=ag_drops)

    @staticmethod
    def __get_all_player_names(db: CVW17Database, squadron: Squadrons | None) -> set[str]:
        players_filter = (db.squadron == squadron.value) if squadron else ()

        players = list(set(db.plt_name[players_filter]) | set(db.rio_name[players_filter]))
        return {player for player in players if player}

    @classmethod
    def get_leaderboard(cls, db: CVW17Database, squadron: Squadrons) -> dict[str, PlayerStats]:
        players = cls.__get_all_player_names(db, squadron)
        unsorted_leaderboard = {player: cls.get_player_stats(db, player, squadron) for player in players}
        # the sorting is based on a point system where A/A kill is worth 2 points and A/G drop 1 point.
        return dict(sorted(unsorted_leaderboard.items(), key=lambda k: (k[1].aa_kills * 2 + k[1].ag_drops), reverse=True))

    @staticmethod
    def get_weapon_stats(db: CVW17Database, weapon: Weapons):
        weapon_filter = np.char.startswith(db.weapon, weapon.value)

        hit_filter = np.array(weapon_filter) & ((db.hit == 'TRUE') | (db.destroyed == 'TRUE'))

        hits = sum(db.qty.astype(int)[hit_filter])
        shots = sum(db.qty.astype(int)[weapon_filter])

        misses = shots - hits

        if shots > 0:
            pk = round(hits/shots * 100, 1)
        else:
            pk = 0

        return WeaponStats(hits=hits, misses=misses, pk=pk, shots=shots)

    @staticmethod
    def __get_latest_entry(db: CVW17Database):
        idx = -1 # for testing, keep at -1
        return PartialDebrief(msn_name=db.msn_name[idx], msn_nr=db.msn_nr[idx], posted_by=db.fl_name[idx],
                              event_nr=db.event[idx], notes=db.notes[idx])

    @classmethod
    def get_latest_debrief(cls, db: CVW17Database):
        latest_entry = cls.__get_latest_entry(db)

        debrief_filter = (( db.notes == latest_entry.notes ) & ( db.msn_nr == latest_entry.msn_nr ) &
                          ( db.msn_name == latest_entry.msn_name) & ( db.event == latest_entry.event_nr) &
                          ( db.fl_name == latest_entry.posted_by ))

        modexes = db.tail_number[debrief_filter]
        pilot_names = db.plt_name[debrief_filter]
        rio_names = db.rio_name[debrief_filter]

        player_stats = {}

        for modex, pilot, rio in zip(modexes, pilot_names, rio_names):
            player_stats[modex] = cls.get_player_stats(db, pilot, None, debrief_filter)
            player_stats[modex].player_name = f'{pilot} | {rio}' if rio else pilot

        debrief = Debrief(**asdict(latest_entry), player_stats=player_stats)

        return debrief