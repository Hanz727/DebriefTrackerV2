from dataclasses import dataclass

@dataclass
class WebConfig:
    discord_api_base_url: str
    oauth_callback_uri: str