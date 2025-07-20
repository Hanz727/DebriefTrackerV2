import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from flask import abort, session, redirect, request, render_template, Blueprint, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from clients.databases.contracts import CVW17DatabaseRow
from clients.databases.postgres.postgres_client import PostGresClient
from clients.thread_pool_client import ThreadPoolClient
from core.constants import MODEX_TO_SQUADRON, Squadrons
from core.wrappers import safe_execute
from services import Logger
from services.data_handler import DataHandler
from web.input._constants import BDA_IMAGE_PATH
from web.input.config.config import WebConfigSingleton
from web.input.tracker_ui.input_data_handler import InputDataHandler


config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()
ThreadPoolClient.create_task_loop(postgres_client.update, 30)

home_blueprint = Blueprint('home', __name__)
app = home_blueprint


@app.route('/bda/<int:debrief_id>/<img_name>')
def show_bda_img(debrief_id, img_name):
    # Validate debrief_id is positive
    if debrief_id <= 0:
        abort(404)

    # Secure the filename and validate it
    secure_name = secure_filename(img_name)
    if not secure_name or secure_name != img_name:
        abort(404)

    # Validate file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if not any(secure_name.lower().endswith(ext) for ext in allowed_extensions):
        abort(404)

    # Construct paths securely
    debrief_dir = BDA_IMAGE_PATH / str(debrief_id)
    file_path = debrief_dir / secure_name

    # Ensure the resolved path is within the expected directory
    try:
        file_path = file_path.resolve()
        debrief_dir = debrief_dir.resolve()
        if not str(file_path).startswith(str(debrief_dir)):
            abort(404)
    except (OSError, ValueError):
        abort(404)

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        abort(404)

    return send_from_directory(debrief_dir, secure_name)

@app.route("/debrief/<int:debrief_id>")
def show_debrief(debrief_id):
    debrief = {}
    with open(BDA_IMAGE_PATH / Path(str(debrief_id)) / Path('display-data.json')) as f:
        debrief = json.load(f)

    return render_template("view.html", debrief=debrief)

def save_images(data, debrief_id):
    if data.get('ag_weapons'):
        for i, weapon in enumerate(data['ag_weapons']):
            data['ag_weapons'][i]['image_path'] = ""
            if weapon.get('image_data'):
                img_path = InputDataHandler.save_bda_image(weapon['image_data'], str(debrief_id), str(i))
                data['ag_weapons'][i]['image_data'] = ''
                data['ag_weapons'][i]['image_path'] = str(img_path.name)

def create_view_data(data, debrief_id):
    view_data = {
        "debrief-id": debrief_id,
        "mission-name": data['mission_name'],
        "mission-number": data['mission_number'],
        "mission-event": data['mission_event'],
        "date": data['mission_date'],
        "callsign": data['callsign'],
        "aircrew": [
            {'modex': aircrew['modex'],
             'aircrew': aircrew['pilot'] + ' | ' + aircrew['rio'] if aircrew['rio'] else aircrew['pilot']
             }
            for aircrew in data['aircrew']
        ],
        "ag-drop-count": data['form_metadata']['total_ag_weapons'],
        "bda-count": data['form_metadata']['total_bdas'],
        "ag": [
            {
                "modex": aircrew['modex'],
                "drops": [
                    {
                        "weapon-name": drop['weapon_name'],
                        "DMPI": drop['target_value'] if drop['target_type'] == "dmpi" else "",
                        "tgt-name": drop['target_value'] if drop['target_type'] == "target" else "",
                        "img-name": drop['image_path'],
                        "bda-result": drop['bda_result'],
                    } for drop in data['ag_weapons'] if drop['pilot_id'] - 1 == id_
                ]
            } for id_, aircrew in enumerate(data['aircrew'])
        ],
        "opposition": {
            "type": data['opposition_type_number'],
            "location": data['opposition_location'],
        },
        "aa": data['aa_weapons'],
        "engagement-result": data['engagement_result'],
        "blue-casualties": data['blue_casualties'],
        "mission-notes": data['mission_notes'],
        "restrike-recommendation": data['restrike_recommendation']
    }

    with open(BDA_IMAGE_PATH / Path(str(debrief_id)) / Path("display-data.json"), "w") as f:
        json.dump(view_data, f, indent=2)

def insert_tracker_data(data):
    aircrew_presence = deepcopy(data.get('aircrew', []))

    for ag_weapon in data.get('ag_weapons', []):
        aircrew = data.get('aircrew', [{}, {}, {}, {}])[ag_weapon.get('pilot_id', 1) - 1]
        row = CVW17DatabaseRow(
            datetime.now() or None,
            data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
            MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(int(aircrew.get('modex', 0))), Squadrons.NONE).value or None,
            aircrew.get('rio', "").strip().lower() or None,
            aircrew.get('pilot', "").strip().lower() or None,
            aircrew.get('modex', "") or None,
            'A/G',
            ag_weapon.get('weapon_name', "") or None,
            ag_weapon.get('target_value', "") or None,
            None,
            None,
            None,
            None,
            True,
            True,
            1,
            data.get('mission_number', "") or None,
            data.get('mission_name', "") or None,
            data.get('mission_event', "") or None,
            data.get('mission_notes', "")
        )

        if InputDataHandler.validate_row(row):
            if aircrew in aircrew_presence:
                aircrew_presence.remove(aircrew)
            postgres_client.insert(row)

    for aa_weapon in data.get('aa_weapons', []):
        aircrew = None
        for aircrew_ in data.get('aircrew', []):
            if aircrew_.get('modex') == aa_weapon.get('modex'):
                aircrew = aircrew_
                break

        if aircrew is None:
            continue

        row = CVW17DatabaseRow(
            datetime.now() or None,
            data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
            MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(int(aircrew.get('modex', 0))),
                                  Squadrons.NONE).value or None,
            aircrew.get('rio', '').strip().lower() or None,
            aircrew.get('pilot', '').strip().lower() or None,
            aircrew.get('modex', "") or None,
            'A/A',
            aa_weapon.get('weapon', '') or None,
            aa_weapon.get('target', '') or None,
            aa_weapon.get('target_altitude', None),
            aa_weapon.get('own_altitude', None),
            aa_weapon.get('speed', None),
            aa_weapon.get('range', None),
            aa_weapon.get('hit', False),
            aa_weapon.get('hit', False),
            1,
            data.get('mission_number', '') or None,
            data.get('mission_name', '') or None,
            data.get('mission_event', '') or None,
            data.get('mission_notes', '')
        )

        if InputDataHandler.validate_row(row):
            if aircrew in aircrew_presence:
                aircrew_presence.remove(aircrew)
            postgres_client.insert(row)

    for aircrew in aircrew_presence:
        row = CVW17DatabaseRow(
            datetime.now() or None,
            data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
            MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(int(aircrew.get('modex', 0))),
                                  Squadrons.NONE).value or None,
            aircrew.get('rio', '').strip().lower() or None,
            aircrew.get('pilot', '').strip().lower() or None,
            aircrew.get('modex', 0) or None,
            'N/A',
            None,
            None,
            None,
            None,
            None,
            None,
            False,
            False,
            0,
            data.get('mission_number', '') or None,
            data.get('mission_name', '') or None,
            data.get('mission_event', '') or None,
            data.get('mission_notes', '')
        )

        if InputDataHandler.validate_row(row):
            postgres_client.insert(row)

@app.route('/submit-report', methods=['POST'])
def submit_report():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        os.makedirs(BDA_IMAGE_PATH, exist_ok=True)
        debrief_id = InputDataHandler.find_latest_numbered_folder(BDA_IMAGE_PATH)

        save_images(data, debrief_id)

        data['form_metadata']['discord_uid'] = session['discord_uid']
        with open(BDA_IMAGE_PATH / Path(str(debrief_id)) / Path("submit-data.json"), "w") as f:
            json.dump(data, f, indent=2)

        create_view_data(data, debrief_id)

        insert_tracker_data(data)

        return jsonify({
            'success': True,
            'message': 'Strike report received successfully',
            'id': str(debrief_id),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

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

@app.route('/file')
def file():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('submit.html')
    return redirect('/login')

@app.route('/')
def home():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('menu.html')
    return redirect('/login')
