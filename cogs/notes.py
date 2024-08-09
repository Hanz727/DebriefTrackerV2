from discord.ext.commands import Cog, Bot


from clients.google_sheets.google_sheets_client import GoogleSheetsClient
from services import Logger
from core.config.config import ConfigSingleton


class NotesEmbedManager(Cog):
    def __init__(self, bot: Bot, google_sheets_client: GoogleSheetsClient):
        self.__bot = bot
        self.__config = ConfigSingleton.get_instance()

        self.__google_sheets_client = google_sheets_client
        self.__google_sheets_client.add_db_on_insert_callback(self.on_db_insert)

    @Cog.listener()
    async def on_ready(self):
        Logger.info("Ready")

    def on_db_insert(self):
        print("elo")


async def setup(bot, google_sheets_client: GoogleSheetsClient) -> None:
    await bot.add_cog(NotesEmbedManager(bot, google_sheets_client))
