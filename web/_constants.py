from pathlib import Path
from typing import Final

from core.constants import BASE_DIR
from services.file_handler import FileHandler
from web.config.config import WebConfigSingleton

__CONFIG = WebConfigSingleton.get_instance()

REDIRECT_URI: Final[str] = __CONFIG.oauth_callback_uri
DISCORD_API_BASE_URL: Final[str]  = __CONFIG.discord_api_base_url

AUTHORIZATION_BASE_URL: Final[str] = f'{DISCORD_API_BASE_URL}/oauth2/authorize'
TOKEN_URL: Final[str] = f'{DISCORD_API_BASE_URL}/oauth2/token'

__OAUTH2_CREDENTIALS = FileHandler.load_json(BASE_DIR / "keys/oauth2_credentials.json")
CLIENT_ID = __OAUTH2_CREDENTIALS['id']
CLIENT_SECRET = __OAUTH2_CREDENTIALS['secret']
