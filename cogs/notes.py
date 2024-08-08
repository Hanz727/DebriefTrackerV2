from discord.ext.commands import Cog, Bot

from services import Logger
from core.config.config import ConfigSingleton


class NotesEmbedManager(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigSingleton.get_instance()

    @Cog.listener()
    async def on_ready(self):
        Logger.info("Ready")


async def setup(bot: Bot) -> None:
    await bot.add_cog(NotesEmbedManager(bot))
