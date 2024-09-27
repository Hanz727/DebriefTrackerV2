import math
from datetime import timedelta, datetime
from pathlib import Path

from flask import Flask, redirect, request, session, render_template, send_file, jsonify

import requests

from clients.databases.contracts import CVW17DatabaseRow
from clients.databases.postgres.postgres_client import PostGresClient
from core.constants import MSN_DATA_FILES_PATH, MODEX_TO_SQUADRON, Squadrons
from services.data_handler import DataHandler
from services.file_handler import FileHandler
from web._constants import CLIENT_SECRET, CLIENT_ID, REDIRECT_URI, TOKEN_URL, DISCORD_API_BASE_URL, GUILD_ID, \
    DISCORD_BOT_TOKEN, ROLE_ID, AUTH_URL, FLASK_SECURE_KEY
from web.config.config import WebConfigSingleton

import redis
from flask_session import Session

app = Flask(__name__)
app.secret_key = FLASK_SECURE_KEY

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379)

server_session = Session(app)

config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()

def get_row(entries: dict, row_id):
    return CVW17DatabaseRow(datetime.now(),
            entries.get('FL_NAME', '') or None,
            MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(int(entries.get(f'tail_number_{row_id}', -100))), Squadrons.NONE)
                            .value or None, # noqa the .value returns str
            entries.get(f'rio_name_{row_id}', '') or None,
            entries.get(f'plt_name_{row_id}', None) or None,
            entries.get(f'tail_number_{row_id}', None) or None,
            entries.get(f'weapon_type_{row_id}', 'N/A').upper() or None,
            entries.get(f'weapon_{row_id}', None) or None,
            entries.get(f'target_{row_id}', None) or None,
            entries.get(f'target_angels_{row_id}', None) or None,
            entries.get(f'angels_{row_id}', None) or None,
            entries.get(f'speed_{row_id}', None) or None,
            entries.get(f'range_{row_id}', None) or None,
            entries.get(f'hit_{row_id}', False) is not False,
            entries.get(f'destroyed_{row_id}', False) is not False,
            1 if entries.get(f'weapon_type_{row_id}', 'N/A').upper() in ['A/A', 'A/G'] else 0, # QTY
            entries.get('MSN_NR', None) or None,
            entries.get('MSN_NAME', None) or None,
            entries.get('EVENT', "").upper() or None,
            entries.get('NOTES', None) or None)

def validate_row(row):
    if None in [row.pilot_name, row.fl_name, row.msn_name, row.msn_nr, row.event, row.tail_number, row.hit,
                row.destroyed, row.weapon_type, row.squadron]:
        return False
    if row.weapon_type not in ['A/A', 'A/G', 'N/A']:
        return False

    return True

@app.route('/submit', methods=['POST'])
def submit():
    if not session['authed']:
        return redirect('/login')
    form = request.form
    i = 0
    while form.get(f'tail_number_{i}', None):
        row = get_row(form, i)
        print(row)
        print(validate_row(row))
        if validate_row(row):
            postgres_client.insert(row)
        i += 1

    return 'Debrief uploaded!'

def get_access_token():
    # Get the authorization code from the callback URL
    code = request.args.get('code')
    # Exchange the authorization code for an access token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    response.raise_for_status()
    token_data = response.json()
    return token_data['access_token']

@app.route('/')
def home():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('index.html')
    return redirect('/login')

@app.route('/data-labels')
def data_labels():
    files: list[Path] = FileHandler.sort_files_by_date_created(MSN_DATA_FILES_PATH)
    return jsonify({str(id_): path.name for id_, path in enumerate(files)})

@app.route('/data')
def data():
    try:
        id_ = int(request.args.get('id', 0))
    except ValueError:
        id_ = 0

    files: list[Path] = FileHandler.sort_files_by_date_created(MSN_DATA_FILES_PATH)
    if len(files) <= id_:
        id_ = 0

    return send_file(files[id_])


@app.route('/login')
def login():
    return redirect(AUTH_URL)

@app.route('/callback')
def callback():
    access_token = get_access_token()
    # Use the access token to fetch the user's guilds
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_info_response = requests.get(f'{DISCORD_API_BASE_URL}/users/@me', headers=headers)
    user_info_response.raise_for_status()
    user_info = user_info_response.json()
    uid = user_info['id']

    user_guilds_response = requests.get(f'{DISCORD_API_BASE_URL}/users/@me/guilds', headers=headers)
    user_guilds_response.raise_for_status()
    user_guilds = user_guilds_response.json()

    # Check if the user is in the specified server (guild)
    guild_membership = next((guild for guild in user_guilds if guild['id'] == GUILD_ID), None)

    # /guilds/{id}/members/{uid} requires bot usage so we use the bot instead of oauth api
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }

    if guild_membership:
        member_response = requests.get(f'{DISCORD_API_BASE_URL}/guilds/{GUILD_ID}/members/{uid}', headers=headers)
        member_response.raise_for_status()
        member_data = member_response.json()

        user_roles = member_data.get('roles', [])

        if ROLE_ID in user_roles:
            session['authed'] = True
            return redirect('/')

    return redirect('/login_failed')

@app.route('/login_failed')
def login_failed():
    return "You do not have the permission to write a debrief, contact Oscar or Kroner to get you authenticated!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
