from typing import override

import discord
from discord.ext.commands import Bot

from clients.databases.database_factory import DatabaseFactory
from clients.thread_pool_client import ThreadPoolClient
from core.config.config import ConfigSingleton

from discord_.cogs import stats, notes
from services.msn_data.auto_mode.auto_mode_handler import AutoModeHandler

class DebriefTrackerBot(Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix='!')

        self.__config = ConfigSingleton.get_instance()

        self.__database_client = DatabaseFactory().create_database()
        ThreadPoolClient.create_task_loop(self.__database_client.update,
                                          self.__config.db_update_interval_seconds)

        if self.__config.auto_mode:
            self.__auto_mode_handler = AutoModeHandler(self.__database_client)
            ThreadPoolClient.create_task_loop(self.__auto_mode_handler.update,
                                              self.__config.db_update_interval_seconds)

    @override
    async def setup_hook(self) -> None:
        if not self.__config.auto_mode:
            await notes.setup(self, self.__database_client)
        await stats.setup(self, self.__database_client)

        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
