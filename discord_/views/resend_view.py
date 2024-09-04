import asyncio
from asyncio import AbstractEventLoop

import discord.ui
from discord import Message, Button

from clients.thread_pool_client import ThreadPoolClient

class ResendButtonView(discord.ui.View):
    def __init__(self, embed_func=None, msg: Message = None):
        super().__init__(timeout=None)
        self.__embed_func = embed_func
        self.__message = msg

        ThreadPoolClient.create_async_task(self.auto_remove_button)

    async def auto_remove_button(self):
        while True:
            if self.__message.id != await self.__get_most_recent_msg_id(self.__message.channel):
                await self.__message.edit(view=None)
                return
            await asyncio.sleep(1)

    async def __get_most_recent_msg_id(self, channel):
        async for msg in channel.history(limit=1):
            return msg.id

    @discord.ui.button(label="Reload", style=discord.ButtonStyle.primary)
    async def resend_button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=self.__embed_func(), view=self)
