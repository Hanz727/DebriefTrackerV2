import base64
from pathlib import Path
from typing import Final

from core.constants import BASE_DIR, DISCORD_TOKEN_PATH
from services.file_handler import FileHandler
from web.input.config.config import WebConfigSingleton

__CONFIG = WebConfigSingleton.get_instance()

REDIRECT_URI: Final[str] = __CONFIG.oauth_callback_uri
DISCORD_API_BASE_URL: Final[str]  = __CONFIG.discord_api_base_url

AUTHORIZATION_BASE_URL: Final[str] = f'{DISCORD_API_BASE_URL}/oauth2/authorize'
TOKEN_URL: Final[str] = f'{DISCORD_API_BASE_URL}/oauth2/token'

__OAUTH2_CREDENTIALS = FileHandler.load_json(BASE_DIR / "keys/oauth2_credentials.json")
CLIENT_ID: Final[str] = __OAUTH2_CREDENTIALS['id']
CLIENT_SECRET: Final[str] = __OAUTH2_CREDENTIALS['secret']

AUTH_URL: Final[str] = (f'{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&'
            f'response_type=code&scope=identify+guilds+guilds.members.read')

GUILD_ID: Final[str] = __CONFIG.auth_discord_guild_id
ROLE_ID: Final[str] = __CONFIG.auth_discord_role_id

DISCORD_BOT_TOKEN: Final[str] = FileHandler.read_file(DISCORD_TOKEN_PATH)

FLASK_SECURE_KEY_PATH: Final[Path] = BASE_DIR / Path("keys/flask_key.txt")
FLASK_SECURE_KEY: Final[bytes] = base64.b64decode(FileHandler.read_file(FLASK_SECURE_KEY_PATH))
