from dataclasses import asdict, field

import numpy as np
from flask import session, redirect, request, render_template, Blueprint, jsonify

from clients.databases.contracts import CVW17DatabaseRow
from clients.databases.postgres.postgres_client import PostGresClient
from clients.thread_pool_client import ThreadPoolClient
from web.input.config.config import WebConfigSingleton
from web.input.tracker_ui.input_data_handler import InputDataHandler

config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()
ThreadPoolClient.create_task_loop(postgres_client.update, 30)

home_blueprint = Blueprint('home', __name__)
app = home_blueprint

@app.route('/submit', methods=['POST'])
def submit():
    if not session['authed']:
        return redirect('/login')
    form = request.form
    i = 0
    while form.get(f'tail_number_{i}', None):
        row = InputDataHandler.get_row(form, i)
        if InputDataHandler.validate_row(row):
            row.pilot_name = row.pilot_name.lower().strip()
            if row.rio_name is not None:
                row.rio_name = row.rio_name.lower().strip()

            postgres_client.insert(row)
        i += 1

    return 'Debrief uploaded!'

@app.route('/get_db')
def get():
    rows = postgres_client.get_data_manager().get_db_rows()
    filtered_rows: list[CVW17DatabaseRow] = []

    pilot_filter = request.args.get('pilot', '').lower()
    rio_filter = request.args.get('rio', '').lower()
    modex_filter = request.args.get('modex', '').lower()
    target_filter = request.args.get('target', '').lower()
    weapon_type_filter = request.args.get('weapon_type', '').lower()
    weapon_filter = request.args.get('weapon', '').lower()
    killed_filter = request.args.get('killed', '').lower()

    for row in rows:
        try:
            if pilot_filter and not row.pilot_name.lower().startswith(pilot_filter):
                continue
            if rio_filter and not row.rio_name.lower().startswith(rio_filter):
                continue
            if modex_filter and not str(row.tail_number).startswith(modex_filter):
                continue
            if target_filter and not row.target.lower().startswith(target_filter):
                continue
            if weapon_type_filter and not row.weapon_type.lower().startswith(weapon_type_filter):
                continue
            if weapon_filter and not row.weapon.lower().startswith(weapon_filter):
                continue
            if killed_filter and not str(row.hit).lower().startswith(killed_filter)\
                    and not str(row.destroyed).lower().startswith(killed_filter):
                continue

            filtered_rows.append(row)
        except Exception as e:
            pass

    return jsonify(filtered_rows)

@app.route('/')
def home():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('index.html')
    return redirect('/login')