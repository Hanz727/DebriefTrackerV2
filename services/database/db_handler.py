from clients.google_sheets.contracts import CVW17Database
from services.database.constants import Squadrons, Weapons
import numpy as np

from services.database.contracts import PlayerStats, WeaponStats, PartialDebrief, Debrief
from dataclasses import asdict

class DbHandler:
    @staticmethod
    def get_player_stats(db: CVW17Database, player: str, squadron: Squadrons) -> PlayerStats:
        stats = PlayerStats(0,0,'')
        player_filter = ( (db.plt_name == player) | (db.rio_name == player) ) & (db.squadron == squadron.value)
        aa_filter = player_filter & (db.weapon_type == 'A/A') & (db.hit == 'TRUE')
        ag_filter = player_filter & (db.weapon_type == 'A/G')

        stats.player_name = player
        stats.aa_kills = sum(db.qty.astype(int)[aa_filter])
        stats.ag_drops = sum(db.qty.astype(int)[ag_filter])

        return stats

    @staticmethod
    def __get_all_player_names(db: CVW17Database, squadron: Squadrons | None) -> set[str]:
        players_filter = (db.squadron == squadron.value) if squadron else ()

        # Get unique player names (both pilots and RIOs)
        players = list(set(db.plt_name[players_filter]) | set(db.rio_name[players_filter]))

        # Remove empty strings
        return {player for player in players if player}

    @classmethod
    def get_leaderboard(cls, db: CVW17Database, squadron: Squadrons) -> dict[str, PlayerStats]:
        players = cls.__get_all_player_names(db, squadron)
        unsorted_leaderboard = {player: cls.get_player_stats(db, player, squadron) for player in players}
        return dict(sorted(unsorted_leaderboard.items(), key=lambda k: (k[1].aa_kills * 2 + k[1].ag_drops), reverse=True))

    @staticmethod
    def get_weapon_stats(db: CVW17Database, weapon: Weapons):
        weapon_filter = np.char.startswith(db.weapon, weapon.value)

        hit_filter = np.array(weapon_filter) & ((db.hit == 'TRUE') | (db.destroyed == 'TRUE'))

        hits = sum(db.qty.astype(int)[hit_filter])
        shots = sum(db.qty.astype(int)[weapon_filter])

        misses = shots - hits

        if shots > 0:
            pk = round(hits/shots, 3) * 100
        else:
            pk = 0

        return WeaponStats(hits=hits, misses=misses, pk=pk, shots=shots)

    @staticmethod
    def get_latest_entry(db: CVW17Database):
        return PartialDebrief(msn_name=db.msn_name[-1], msn_nr=db.msn_nr[-1], posted_by=db.fl_name[-1],
                              event_nr=db.event[-1], notes=db.notes[-1])

    @classmethod
    def get_latest_debrief(cls, db: CVW17Database):
        latest_entry = cls.get_latest_entry(db)

        debrief_filter = (( db.notes == latest_entry.notes ) & ( db.msn_nr == latest_entry.msn_nr ) &
                          ( db.msn_name == latest_entry.msn_name) & ( db.event == latest_entry.event_nr) &
                          ( db.fl_name == latest_entry.posted_by ))

        modexes = db.tail_number[debrief_filter]
        pilot_names = db.plt_name[debrief_filter]
        rio_names = db.rio_name[debrief_filter]

        player_stats = {}

        for modex, pilot, rio in zip(modexes, pilot_names, rio_names):
            player_stats[modex] = cls.get_player_stats(db, pilot, rio)
            player_stats[modex].player_name = f'{pilot} | {rio}'

        debrief = Debrief(**asdict(latest_entry), player_stats=player_stats)

        return debrief