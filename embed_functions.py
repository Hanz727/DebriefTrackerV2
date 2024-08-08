import discord
from discord.ext import commands, tasks

from datetime import datetime
import time

import Logger
from gs_interface import GsInterfaceSingleton


class EmbedCreator:
    def __init__(self):
        self.gs_interface = GsInterfaceSingleton.get_instance()

    def get_embed_funcs(self):
        embed_funcs = []
        for func_name in dir(self):
            attr = getattr(self, func_name)
            if callable(attr) and func_name.startswith("_EmbedCreator__make_embed_"):
                embed_funcs.append(attr)

        return embed_funcs

    def __make_embed_103(self):
        embed = discord.Embed(title="VF-103 STATS", color=0xf1c40f,
                              description="Displays the VF-103 kills leaderboard",
                              timestamp=datetime.fromtimestamp(time.time()))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/747840778109452480/1139912475328909332/'
                                'Fighter_Squadron_103_US_Navy_insignia_1995.png')

        embed.set_footer(text=f'Debrief Tracker bot © 2024 made by: koksem#3791')
        return embed

    def __make_embed_34(self):
        embed = discord.Embed(title="VFA-34 STATS", color=0x3498db,
                              description="Displays the VFA-34 kills leaderboard",
                              timestamp=datetime.fromtimestamp(time.time()))
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/747840778109452480/1139912500943523900/SMOL_VFA-34.png')

        embed.set_footer(text=f'Debrief Tracker bot © 2024 made by: koksem#3791')
        return embed
