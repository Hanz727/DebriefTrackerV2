from typing import override

import discord
from discord.ext.commands import Bot

from clients.google_sheets.google_sheets_client import GoogleSheetsClient
from clients.thread_pool_client import ThreadPoolClient
from core.config.config import ConfigSingleton
from core.constants import DISCORD_COGS_DIRECTORY
from services.file_handler import FileHandler

from cogs import notes, stats


class DebriefTrackerBot(Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix='!')

        self.__config = ConfigSingleton.get_instance()

        self.__google_sheets_client = GoogleSheetsClient()
        ThreadPoolClient.create_task_loop(self.__google_sheets_client.update, self.__config.google_sheets_update_interval_seconds)

    @override
    async def setup_hook(self) -> None:
        await notes.setup(self, self.__google_sheets_client)
        await stats.setup(self, self.__google_sheets_client)

        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
