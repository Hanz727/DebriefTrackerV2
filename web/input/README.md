# DebriefTracker web documentation
DebriefTracker web is a user interface made for adding entries to db (uploading a debrief).
This is a separate program from the DebriefTracker and has its own main.py file. It makes use of the already existing
framework for the base program (i.e. PostgresClient and some core definitions) to reduce code duplication.
There also is a tool (currently in progress) that allows the user to view the data on the website and filter it.
## Requirements
- Redis running on port 6379
- Python 3.12
- Postgres database
- Discord bot
- (optional) Any WSGI server like gunicorn
## Usage
**Step 1.** Start by installing all the necessary libs:
```
pip install -r requirements.txt
```
**Step 2.** To ensure you have all the required keys. Create a "keys" folder in the base dir. 

Create the following files:
- discord.token
- flask_key.txt
- gspread_api_key.json
- oauth2_credentials.json

Place a discord bot token in discord.token without any extra characters like spaces or enters.

Generate a random base64 secure key for flask to use, example generation of such code: 
```python
import os
import base64

print(base64.b64encode(os.urandom(24)).decode('utf-8'))
```
Copy the result to flask_key.txt

Generate a Google sheets api json and place its contents into gspread_api_key.json

And lastly from discord developer portal get the client secret and client id and put it into the oauth2_credentials.json
in the following format:
```json
{
  "id": "123",
  "secret": "abcd"
}
```

**Step 3.** Configure config.json and web/config.json. Despite DebriefTracker web being a separate program it requires
the base config to function. Most importantly it needs the credentials to postgres with SELECT & INSERT permissions.

Example config.json file:
```json
{
  "stats_channel": 123,
  "notes_channel": 123,
  "stats_update_interval_seconds": 60,
  "db_update_interval_seconds": 3,
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/123",
  "db_type": "postgres",
  "postgres_host": "localhost",
  "postgres_port": "5432",
  "postgres_db_name": "CVW17Debriefs",
  "postgres_user": "postgres",
  "postgres_password": "admin",
  "auto_mode": false
}
```

The web/web_config.json also requires configuration

Example web/web_config.json file:
```json
{
    "oauth_callback_uri": "http://localhost:5000/callback",
    "discord_api_base_url": "https://discord.com/api/v10",
    "auth_discord_guild_id": "747489937527406673",
    "auth_discord_role_id": "747489937573806213",
    "bypass_auth_debug": false
}
```
The used discord bot must be on the server with the specified guild_id. Also, the callback_uri must match the one in
discord developer portal (OAuth2 -> Redirects).

**Step 4.** Launch the application with ``python main.py`` (not suitable for prod) or use a WSGI of choice.