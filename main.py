import os

import discord
from discord.ext import commands

import Logger
import constants


class DebriefTrackerBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(),
                         command_prefix='!')

        self.initial_extensions = [f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs") if
                                   filename.endswith(".py")]

    async def setup_hook(self) -> None:
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')


def create_necessary_folders():
    os.makedirs("keys", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def get_token(path=constants.DISCORD_TOKEN_PATH):
    if not os.path.exists(path):
        try:
            with open(path, "w") as f:
                f.write("")
        except:
            Logger.error("Path: " + path + " does not exist!")
            return None

    with open(path) as f:
        return f.read()


def main():
    create_necessary_folders()

    token = get_token()
    bot = DebriefTrackerBot()

    try:
        bot.run(token)
    except Exception as err:
        Logger.error(err)

        if str(err) == "Improper token has been passed.":
            Logger.info("Change the discord token in: " + constants.DISCORD_TOKEN_PATH)
            exit(-1)


if __name__ == "__main__":
    main()
