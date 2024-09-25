import asyncio

from core.config.config import ConfigSingleton
from services import Logger

import discord.ui
from discord import Message, Button

from clients.thread_pool_client import ThreadPoolClient


class ResendButtonView(discord.ui.View):
    def __init__(self, embed_func=None, msg: Message = None):
        super().__init__(timeout=None)
        self.__embed_func = embed_func
        self.__message = msg

        self.__config = ConfigSingleton.get_instance()

        self.__remove_button_task = ThreadPoolClient.create_async_task(self.auto_remove_button)

    def __del__(self):
        try:
            asyncio.create_task(self.__remove_button())
        except Exception as err:
            Logger.warning(err)

    async def __remove_button(self):
        await self.__message.edit(view=None)

    async def __is_most_recent_msg(self):
        return self.__message.id == await self.__get_most_recent_msg_id(self.__message.channel)

    async def auto_remove_button(self):
        errors = 0
        while True:
            try:
                if not self.__message:
                    return

                if not await self.__is_most_recent_msg():
                    await self.__remove_button()
                    return

                await asyncio.sleep(self.__config.stats_update_interval_seconds)
            except asyncio.CancelledError:
                return
            except discord.errors.NotFound:
                return
            except Exception as err:
                errors += 1
                if errors >= 50:
                    Logger.error(f"Error count exceeded, {err}")
                    return
                Logger.warning(type(err))

    async def __get_most_recent_msg_id(self, channel):
        async for msg in channel.history(limit=1):
            return msg.id

    @discord.ui.button(label="Reload", style=discord.ButtonStyle.primary)
    async def resend_button_callback(self, interaction: discord.Interaction, button: Button):
        self.__message = interaction.message
        if await self.__get_most_recent_msg_id(interaction.channel) != self.__message.id:
            await self.__remove_button()

            if not self.__remove_button_task.done():
                self.__remove_button_task.cancel()

            return

        await interaction.response.edit_message(embed=self.__embed_func(), view=self)
