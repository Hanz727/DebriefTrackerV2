from audioop import reverse

from clients.google_sheets.contracts import CVW17Database
from services.database.constants import Squadrons, Weapons
import numpy as np

from services.database.contracts import PlayerStats, WeaponStats


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
        weapon_filter = ( db.weapon == weapon )
        hit_filter = weapon_filter & ((db.hit == 'TRUE') | (db.destroyed == 'TRUE'))

        hits = sum(db.qty.astype(int)[hit_filter])
        shots = sum(db.qty.astype(int)[weapon_filter])

        misses = shots - hits

        if shots > 0:
            pk = hits/shots
        else:
            pk = 0

        return WeaponStats(hits=hits, misses=misses, pk=pk)