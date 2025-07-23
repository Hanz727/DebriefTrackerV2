import asyncio

from discord.ext.commands import Cog, Bot
from discord import TextChannel

from clients.databases.database_client import DatabaseClient
from core.config.config import ConfigSingleton
from core.constants import ON_DB_INSERT_CALLBACK, ON_REPORT_INSERT_CALLBACK
from discord_.views.resend_view import ResendButtonView
from services import Logger
from services.embed.embed_creator import EmbedCreator


class NotesEmbedManager(Cog):
    def __init__(self, bot: Bot, database_client: DatabaseClient):
        self.__bot = bot
        self.__config = ConfigSingleton.get_instance()

        self.__database_client = database_client
        self.__database_client.add_listener(self.on_report_insert, ON_REPORT_INSERT_CALLBACK)

        self.__embed_creator = EmbedCreator(database_client)

        self.__notes_channel: TextChannel | None = None

    @Cog.listener()
    async def on_ready(self):
        await self.load_channel()
        Logger.info("Ready")

    async def load_channel(self):
        self.__notes_channel = self.__bot.get_channel(self.__config.notes_channel)

    async def send_embed(self):
        embed_func = self.__embed_creator.make_embed_notes
        msg = await self.__notes_channel.send(embed=embed_func())
        #await msg.edit(view=ResendButtonView(embed_func, msg))

    def on_report_insert(self):
        asyncio.run_coroutine_threadsafe(self.send_embed(), self.__bot.loop)

async def setup(bot, database_client: DatabaseClient) -> None:
    await bot.add_cog(NotesEmbedManager(bot, database_client))
