import asyncio
from datetime import datetime, timedelta

from discord import TextChannel, Message
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

from clients.databases.database_client import DatabaseClient
from core.config.contracts import Config
from discord_.cogs.constants import DELAY_BETWEEN_MESSAGES_SENT_DURATION, DELAY_BETWEEN_MESSAGES_SENT, \
    SOFT_RESET_DATA_PATH
from services import Logger
from core.config.config import ConfigSingleton
from services.embed.embed_creator import EmbedCreator
from services.file_handler import FileHandler


class StatsEmbedManager(Cog):
    def __init__(self, bot: Bot, database_client: DatabaseClient):
        self.__bot = bot

        self.__config: Config = ConfigSingleton.get_instance()

        # embeds will be sent to this channel, there is only 1 server and 1 channel that this cog handles
        self.__stats_channel: TextChannel | None = None

        self.__database_client: DatabaseClient = database_client
        self.__embed_creator = EmbedCreator(self.__database_client)
        self.__embed_funcs = self.__embed_creator.get_embed_funcs()
        self.__sent_messages: list[Message] = []

        if self.__config.auto_soft_reset:
            self.__update_soft_reset()

    @Cog.listener()
    async def on_ready(self):
        await self.__load_stats_channel()
        await self.__clear_channel(self.__stats_channel)
        await self.__populate_channel(self.__stats_channel)
        await self.__restart_tasks()

        Logger.info("Ready")

    async def __restart_tasks(self):
        self.__update_task.stop()
        while self.__update_task.is_running():
            Logger.info("Waiting for update_sent_messages task to finish.")
            await asyncio.sleep(2)

        self.__update_task.start()

    async def __load_stats_channel(self):
        self.__stats_channel = self.__bot.get_channel(self.__config.stats_channel)

    @staticmethod
    async def __clear_channel(channel: TextChannel):
        async for msg in channel.history(limit=10):
            if msg:
                await msg.delete()

    async def __populate_channel(self, stats_channel: TextChannel):
        for embed_func in self.__embed_funcs:
            embed = embed_func()
            if not embed:
                Logger.error("Embed func: " + embed_func.__name__ + " returned None")
                raise Exception()

            msg = await stats_channel.send(embed=embed_func())
            self.__sent_messages.append(msg)

            # Prevents annoying DISCORD RATE LIMIT messages
            if DELAY_BETWEEN_MESSAGES_SENT:
                await asyncio.sleep(DELAY_BETWEEN_MESSAGES_SENT_DURATION)

    def __update_soft_reset(self):
        soft_reset_data = dict(FileHandler.load_json(SOFT_RESET_DATA_PATH))
        last_update = soft_reset_data.get('date', "01/01/1970 12:00:00")

        if (datetime.now() - datetime.strptime(last_update,"%m/%d/%Y %H:%M:%S") >
                timedelta(days=self.__config.auto_soft_reset_interval_days)):
            soft_reset_data['date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            soft_reset_data['id'] = self.__database_client.get_data_manager().get_latest_entry_id()
            FileHandler.save_json(SOFT_RESET_DATA_PATH, soft_reset_data)

    @tasks.loop()
    async def __update_task(self):
        try:
            if self.__config.auto_soft_reset:
                self.__update_soft_reset()

            for msg, embed_func in zip(self.__sent_messages, self.__embed_funcs):
                embed = embed_func()
                if embed:
                    await msg.edit(embed=embed)

                await asyncio.sleep(DELAY_BETWEEN_MESSAGES_SENT_DURATION)

            # Not using the built-in argument for sleeping, because it doesn't allow you to access self.__config
            await asyncio.sleep(self.__config.stats_update_interval_seconds)
        except Exception as err:
            Logger.error(err)


async def setup(bot: Bot, database_client: DatabaseClient) -> None:
    await bot.add_cog(StatsEmbedManager(bot, database_client))
