from typing import override

import discord
from discord.ext.commands import Bot

from core.constants import DISCORD_COGS_DIRECTORY
from services.file_handler import FileHandler


class DebriefTrackerBot(Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix='!')

    @override
    async def setup_hook(self) -> None:
        for file in FileHandler.get_files_from_directory(DISCORD_COGS_DIRECTORY):
            if file.suffix == ".py":
                await self.load_extension(f"{DISCORD_COGS_DIRECTORY}.{file.stem}")
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
