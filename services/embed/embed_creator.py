import discord

from datetime import datetime
import time

from clients.databases.database_client import DatabaseClient
from core.constants import Squadrons, Weapons
from services.embed.constants import VF_103_LOGO_URL, VFA_34_LOGO_URL, AUTHOR_FOOTER, CVW_17_LOGO_URL, VFA_81_LOGO_URL


class EmbedCreator:
    def __init__(self, database_client: DatabaseClient):
        self.__database_client = database_client

        self.__embed_funcs = [
            self.make_embed_103, self.make_embed_34, self.make_embed_81, self.make_embed_17, self.make_embed_phoenix,
            self.make_embed_amraam, self.make_embed_sparrow, self.make_embed_sidewinder
        ]

    def get_embed_funcs(self):
        return self.__embed_funcs

    def make_embed_103(self):
        embed = discord.Embed(title="VF-103 STATS", color=0xf1c40f,
                              description="Displays the VF-103 kills leaderboard",
                              timestamp=datetime.fromtimestamp(time.time()))
        embed.set_thumbnail(url=VF_103_LOGO_URL)

        names = ""
        aa_kills = ""
        ag_drops = ""

        leaderboard = self.__database_client.get_data_manager().get_leaderboard(Squadrons.VF103)
        for player, player_stats in leaderboard.items():
            names += player + "\n"
            aa_kills += str(player_stats.aa_kills) + "\n"
            ag_drops += str(player_stats.ag_drops) + "\n"

        embed.add_field(name="Name", value=names, inline=True)
        embed.add_field(name="A/A kills", value=aa_kills, inline=True)
        embed.add_field(name="A/G drops", value=ag_drops, inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_34(self):
        embed = discord.Embed(
            title="VFA-34 STATS",
            color=0x3498db,
            description="Displays the VFA-34 kills leaderboard",
            timestamp=datetime.fromtimestamp(time.time()),
        )
        embed.set_thumbnail(url=VFA_34_LOGO_URL)

        names = ""
        aa_kills = ""
        ag_drops = ""

        leaderboard = self.__database_client.get_data_manager().get_leaderboard(Squadrons.VFA34)
        for player, player_stats in leaderboard.items():
            names += player + "\n"
            aa_kills += str(player_stats.aa_kills) + "\n"
            ag_drops += str(player_stats.ag_drops) + "\n"

        embed.add_field(name="Name", value=names, inline=True)
        embed.add_field(name="A/A kills", value=aa_kills, inline=True)
        embed.add_field(name="A/G drops", value=ag_drops, inline=True)


        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_81(self):
        embed = discord.Embed(
            title="VFA-81 STATS",
            color=0xa54500,
            description="Displays the VFA-81 kills leaderboard",
            timestamp=datetime.fromtimestamp(time.time()),
        )
        embed.set_thumbnail(url=VFA_81_LOGO_URL)

        names = ""
        aa_kills = ""
        ag_drops = ""

        leaderboard = self.__database_client.get_data_manager().get_leaderboard(Squadrons.VFA81)
        for player, player_stats in leaderboard.items():
            names += player + "\n"
            aa_kills += str(player_stats.aa_kills) + "\n"
            ag_drops += str(player_stats.ag_drops) + "\n"

        embed.add_field(name="Name", value=names, inline=True)
        embed.add_field(name="A/A kills", value=aa_kills, inline=True)
        embed.add_field(name="A/G drops", value=ag_drops, inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_17(self):
        embed = discord.Embed(
            title="CVW-17 STATS", color=0x206694,
            description="Displays the CVW-17 kills",
            timestamp=datetime.fromtimestamp(time.time())
        )
        embed.set_thumbnail(url=CVW_17_LOGO_URL)

        stats_103 = self.__database_client.get_data_manager().get_squadron_stats(Squadrons.VF103)
        embed.add_field(name="VF-103", value=f"Jolly Rogers", inline=True)
        embed.add_field(name='A/A kills', value=str(stats_103.aa_kills), inline=True)
        embed.add_field(name='A/G drops', value=str(stats_103.ag_drops), inline=True)

        embed.add_field(name='▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', value=" ", inline=False)

        stats_34 = self.__database_client.get_data_manager().get_squadron_stats(Squadrons.VFA34)
        embed.add_field(name="VFA-34", value=f"Blue Blasters", inline=True)
        embed.add_field(name='A/A kills', value=str(stats_34.aa_kills), inline=True)
        embed.add_field(name='A/G drops', value=str(stats_34.ag_drops), inline=True)

        embed.add_field(name='▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', value=" ", inline=False)

        stats_81 = self.__database_client.get_data_manager().get_squadron_stats(Squadrons.VFA81)
        embed.add_field(name="VFA-81", value=f"Sunliners", inline=True)
        embed.add_field(name='A/A kills', value=str(stats_81.aa_kills), inline=True)
        embed.add_field(name='A/G drops', value=str(stats_81.ag_drops), inline=True)

        embed.add_field(name='▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', value=" ", inline=False)

        embed.add_field(name="CVW-17", value=f"Team Quicksand", inline=True)
        embed.add_field(name='A/A kills', value=str(stats_34.aa_kills + stats_103.aa_kills + stats_81.aa_kills), inline=True)
        embed.add_field(name='A/G drops', value=str(stats_34.ag_drops + stats_103.ag_drops + stats_81.ag_drops), inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_phoenix(self):
        embed = discord.Embed(
            title="AIM-54 Phoenix stats", color=0xf1c40f,
            description="Displays the AIM-54 Phoenix statistics",
            timestamp=datetime.fromtimestamp(time.time())
        )

        weapons_stats = self.__database_client.get_data_manager().get_weapon_stats(Weapons.phoenix)
        embed.add_field(name="Shots", value=str(weapons_stats.shots), inline=True)
        embed.add_field(name='Hits', value=str(weapons_stats.hits), inline=True)
        embed.add_field(name='PK%', value=str(weapons_stats.pk) + "%", inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_amraam(self):
        embed = discord.Embed(
            title="AIM-120 Amraam stats", color=0x3498db,
            description="Displays the AIM-120 Amraam statistics",
            timestamp=datetime.fromtimestamp(time.time())
        )

        weapons_stats = self.__database_client.get_data_manager().get_weapon_stats(Weapons.amraam)
        embed.add_field(name="Shots", value=str(weapons_stats.shots), inline=True)
        embed.add_field(name='Hits', value=str(weapons_stats.hits), inline=True)
        embed.add_field(name='PK%', value=str(weapons_stats.pk) + "%", inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_sparrow(self):
        embed = discord.Embed(
            title="AIM-7 Sparrow stats", color=0xf1c40f,
            description="Displays the AIM-7 Sparrow statistics",
            timestamp=datetime.fromtimestamp(time.time())
        )

        weapons_stats = self.__database_client.get_data_manager().get_weapon_stats(Weapons.sparrow)
        embed.add_field(name="Shots", value=str(weapons_stats.shots), inline=True)
        embed.add_field(name='Hits', value=str(weapons_stats.hits), inline=True)
        embed.add_field(name='PK%', value=str(weapons_stats.pk) + "%", inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_sidewinder(self):
        embed = discord.Embed(
            title="AIM-9 Sidewinder stats", color=0xf1c40f,
            description="Displays the AIM-9 Sidewinder statistics",
            timestamp=datetime.fromtimestamp(time.time())
        )

        weapons_stats = self.__database_client.get_data_manager().get_weapon_stats(Weapons.sidewinder)
        embed.add_field(name="Shots", value=str(weapons_stats.shots), inline=True)
        embed.add_field(name='Hits', value=str(weapons_stats.hits), inline=True)
        embed.add_field(name='PK%', value=str(weapons_stats.pk) + "%", inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def make_embed_notes(self):
        debrief = self.__database_client.get_data_manager().get_latest_debrief()

        embed = discord.Embed(title=f"{debrief.msn_name}  |  {debrief.msn_nr}  |  {debrief.posted_by}  |  "
                                    f"{debrief.event_nr}",
                              color=0x206694,
                              description=str(debrief.notes),
                              timestamp=datetime.fromtimestamp(time.time()))

        for modex, player_stats in debrief.player_stats.items():
            embed.add_field(name=modex, value=player_stats.player_name, inline=True)
            embed.add_field(name='A/A kills', value=player_stats.aa_kills, inline=True)
            embed.add_field(name='A/G drops', value=player_stats.ag_drops, inline=True)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed
