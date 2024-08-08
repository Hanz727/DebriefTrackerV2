import discord
from discord.ext import commands, tasks

import Logger
import constants
from config import ConfigFactory


class NotesEmbedManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.config = ConfigFactory.get_instance()

    @commands.Cog.listener()
    async def on_ready(self):
        Logger.info("Ready")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NotesEmbedManager(bot))
