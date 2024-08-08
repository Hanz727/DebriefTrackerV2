import os

from discord import LoginFailure

from bots.debrief_tracker_bot import DebriefTrackerBot
from core.constants import DISCORD_TOKEN_PATH
from services.file_handler import FileHandler
from services import Logger


def main():
    os.makedirs("keys", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    token = FileHandler.read_file(DISCORD_TOKEN_PATH)

    try:
        DebriefTrackerBot().run(token)  # Blocking
    except LoginFailure as lf:
        Logger.error(f"Failed to login: {lf}")


if __name__ == "__main__":
    main()
