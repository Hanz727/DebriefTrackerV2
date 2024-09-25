from datetime import timedelta
from pathlib import Path

from flask import Flask, redirect, request, session, render_template, send_file, jsonify
import os

import requests

from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler
from web._constants import CLIENT_SECRET, CLIENT_ID, REDIRECT_URI, TOKEN_URL, DISCORD_API_BASE_URL, GUILD_ID, \
    DISCORD_BOT_TOKEN, ROLE_ID, AUTH_URL
from web.config.config import WebConfigSingleton

app = Flask(__name__)
app.secret_key = os.urandom(24)

config = WebConfigSingleton.get_instance()

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

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

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
