from discord.ext.commands import Cog, Bot

from clients.google_sheets.google_sheets_client import GoogleSheetsClient
from services import Logger
from core.config.config import ConfigSingleton


class NotesEmbedManager(Cog):
    def __init__(self, bot: Bot):
        self.__bot = bot
        self.__config = ConfigSingleton.get_instance()

        self.__google_sheets_client = GoogleSheetsClient.get_instance()

        self.__google_sheets_client.add_db_on_resize_callback(self.on_resize)

    @Cog.listener()
    async def on_ready(self):
        Logger.info("Ready")

    def on_resize(self):
        print("elo")


async def setup(bot: Bot) -> None:
    await bot.add_cog(NotesEmbedManager(bot))
