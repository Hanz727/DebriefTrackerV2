import asyncio

from discord.ext.commands import Cog, Bot
from discord import TextChannel, Message, Embed

from clients.google_sheets.google_sheets_client import GoogleSheetsClient
from core.constants import ON_DB_INSERT_CALLBACK
from services import Logger
from core.config.config import ConfigSingleton
from services.database.db_handler import DbHandler
from services.embed.embed_creator import EmbedCreator


class NotesEmbedManager(Cog):
    def __init__(self, bot: Bot, google_sheets_client: GoogleSheetsClient):
        self.__bot = bot
        self.__config = ConfigSingleton.get_instance()

        self.__google_sheets_client = google_sheets_client
        self.__google_sheets_client.add_listener(self.on_db_insert, ON_DB_INSERT_CALLBACK)

        self.__embed_creator = EmbedCreator(google_sheets_client)

        self.__notes_channel: TextChannel | None = None

    @Cog.listener()
    async def on_ready(self):
        await self.load_channel()
        Logger.info("Ready")

    async def load_channel(self):
        self.__notes_channel = self.__bot.get_channel(self.__config.notes_channel)

    def on_db_insert(self):
        asyncio.run_coroutine_threadsafe(self.__notes_channel.send(embed=self.__embed_creator.make_embed_notes()),
                                         self.__bot.loop)


async def setup(bot, google_sheets_client: GoogleSheetsClient) -> None:
    await bot.add_cog(NotesEmbedManager(bot, google_sheets_client))
