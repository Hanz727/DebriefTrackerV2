import requests
from flask import Blueprint, request, redirect, session, jsonify

from web.input._constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKEN_URL, AUTH_URL, DISCORD_API_BASE_URL, GUILD_ID, \
    DISCORD_BOT_TOKEN, ROLE_ID
from web.input.config.config import WebConfigSingleton

auth_blueprint = Blueprint('auth', __name__)
app = auth_blueprint
config = WebConfigSingleton.get_instance()

def _get_access_token():
    code = request.args.get('code')
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


@app.route('/login')
def login():
    return redirect(AUTH_URL)

@app.route('/callback')
def callback():
    access_token = _get_access_token()
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
            session['discord_uid'] = uid
            session['discord_nick'] = member_data.get('nick')
            if session['discord_nick'] is None or session['discord_nick'].strip() == '':
                session['discord_nick'] = member_data.get('user', {}).get('global_name')

            return redirect('/')

    return redirect('/login_failed')


@app.route('/login_failed')
def login_failed():
    return "You do not have the permission to write a debrief, contact Oscar or Kroner to get you authenticated!"

@app.route('/reset-session')
def reset_session():
    if not session.get('discord_uid') in config.admin_uids:
        return "400 Unauthorized"

    session.clear()
    return redirect('/')