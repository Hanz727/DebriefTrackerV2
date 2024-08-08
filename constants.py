import asyncio
from functools import wraps
import Logger

DISCORD_TOKEN_PATH = "keys/discord.token"
GSPREAD_KEY_PATH = "keys/gspread_api_key.json"
CONFIG_PATH = "config.json"

DATA_PULL_INFO = {
    "database": "DATABASE!A1:AA",
    "entry_msn_number": "ENTRY1!C3"
}

def safe_execute(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as err:
            Logger.error(err, 4)
            return None

    return wrapper


def retryable(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    Logger.warning(f"Function {func.__name__} failed, attempt: {attempt} failed: {e}")
                    if attempt < retries:
                        await asyncio.sleep(delay)
            raise Exception(f"Function {func.__name__} failed after {retries} retries")

        return wrapper

    return decorator
