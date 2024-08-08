import asyncio

import discord
from discord.ext import commands, tasks

import Logger
from config import ConfigFactory

from embed_functions import EmbedCreator


class StatsEmbedManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.__config = ConfigFactory.get_instance()

        # embeds will be sent to this channel, there is only 1 server and 1 channel that this cog handles
        self.__stats_channel: discord.TextChannel | None = None

        self.__embed_creator = EmbedCreator()
        self.__embed_funcs = self.__embed_creator.get_embed_funcs()
        self.__sent_messages: list[discord.Message] = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.__load_stats_channel()

        await self.__clear_channel(self.__stats_channel)

        await self.__populate_channel(self.__stats_channel)

        await self.__restart_tasks()

        Logger.info("Ready")

    async def __restart_tasks(self):
        self.__update_sent_messages.stop()
        while self.__update_sent_messages.is_running():
            Logger.info("Waiting for update_sent_messages task to finish.")
            await asyncio.sleep(1)

        self.__update_sent_messages.start()

    async def __load_stats_channel(self):
        self.__stats_channel = self.bot.get_channel(self.__config.stats_channel)

    async def __clear_channel(self, channel: discord.TextChannel):
        async for msg in channel.history(limit=10):
            if msg:
                await msg.delete()

    async def __populate_channel(self, stats_channel: discord.TextChannel):
        for embed_func in self.__embed_funcs:
            embed = embed_func()
            if not embed:
                Logger.error("Embed func: " + embed_func.__name__ + " returned None")
                exit(-1)

            msg = await stats_channel.send(embed=embed_func())
            self.__sent_messages.append(msg)

    @tasks.loop()
    async def __update_sent_messages(self):
        try:
            for msg, embed_func in zip(self.__sent_messages, self.__embed_funcs):
                embed = embed_func()
                if embed:
                    await msg.edit(embed=embed)

            # Not using the built-in argument for sleeping, because it doesn't allow you to access self.__config
            await asyncio.sleep(self.__config.stats_update_interval_seconds)
        except Exception as err:
            Logger.error(err)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsEmbedManager(bot))
