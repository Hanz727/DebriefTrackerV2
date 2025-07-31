from dataclasses import dataclass
from pathlib import Path


@dataclass
class WebConfig:
    discord_api_base_url: str
    oauth_callback_uri: str
    auth_discord_guild_id: str
    auth_discord_role_id: str
    bypass_auth_debug: bool # disables auth
    tacview_dir: Path
    tracks_dir: Path
    admin_uids: list[str]
    missions_path: Path
    deployment_msn_prefix: str
    maps: list[Path]
    current_map: Path
    map_origin_x: list[int]
    map_origin_y: list[int]
    map_scale_mpp: list[float]
    map_reference: list[str]