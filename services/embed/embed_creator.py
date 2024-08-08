import discord

from datetime import datetime
import time

from clients.google_sheets.google_sheets_client import GoogleSheetsClient
from services.embed.constants import VF_103_LOGO_URL, VFA_34_LOGO_URL, AUTHOR_FOOTER


class EmbedCreator:
    def __init__(self):
        self.__google_sheets_client = GoogleSheetsClient()

    def get_embed_funcs(self):
        embed_funcs = []
        for func_name in dir(self):
            attr = getattr(self, func_name)
            if callable(attr) and func_name.startswith("_EmbedCreator__make_embed_"):
                embed_funcs.append(attr)

        return embed_funcs

    def __make_embed_103(self):
        embed = discord.Embed(
            title="VF-103 STATS",
            color=0xf1c40f,
            description="Displays the VF-103 kills leaderboard",
            timestamp=datetime.fromtimestamp(time.time()),
        )
        embed.set_thumbnail(url=VF_103_LOGO_URL)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed

    def __make_embed_34(self):
        embed = discord.Embed(
            title="VFA-34 STATS",
            color=0x3498db,
            description="Displays the VFA-34 kills leaderboard",
            timestamp=datetime.fromtimestamp(time.time()),
        )
        embed.set_thumbnail(url=VFA_34_LOGO_URL)

        embed.set_footer(text=AUTHOR_FOOTER)
        return embed
