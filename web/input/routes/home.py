import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import abort, session, redirect, request, render_template, Blueprint, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename

from clients.databases.contracts import CVW17DatabaseRow
from clients.databases.postgres.postgres_client import PostGresClient
from clients.thread_pool_client import ThreadPoolClient
from core.constants import MODEX_TO_SQUADRON, Squadrons
from services import Logger
from services.data_handler import DataHandler
from web.input._constants import DEBRIEFS_PATH
from web.input.config.config import WebConfigSingleton
from web.input.routes.dmpi_db import draw_dynamic_map, _reset_dmpi_cache
from web.input.tracker_ui.input_data_handler import InputDataHandler


config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()
ThreadPoolClient.create_task_loop(postgres_client.update_local, 30)

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
    debrief_dir = DEBRIEFS_PATH / str(debrief_id)
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
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    debrief = {}
    with open(DEBRIEFS_PATH / Path(str(debrief_id)) / 'display-data.json') as f:
        debrief = json.load(f)

    return render_template("view.html", debrief=debrief)

@app.route("/debrief-sdata/<int:debrief_id>")
def show_debrief_sdata(debrief_id):
    with open(DEBRIEFS_PATH / Path(str(debrief_id)) / 'submit-data.json') as f:
        sdata = json.load(f)

    return jsonify(sdata)

def get_submission_date(data):
    date = datetime.now()
    if data.get('form_metadata', {}).get('submission_time'):
        time_str = data.get('form_metadata', {}).get('submission_time')
        utc_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        date = utc_dt.astimezone(ZoneInfo('Europe/Berlin'))

    return date

def save_images(data, debrief_id):
    for i, weapon in enumerate(data.get('ag_weapons', [])):
        weapon['image_path'] = ''

        if not weapon.get('image_data'):
            continue

        img_path = InputDataHandler.save_bda_image(weapon['image_data'], str(debrief_id), str(i))
        if img_path is None:
            Logger.error("Image path is None")
            continue

        weapon['image_data'] = ''
        weapon['image_path'] = str(img_path.name)

def create_display_data(data, debrief_id):
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

    with open(DEBRIEFS_PATH / Path(str(debrief_id)) / Path("display-data.json"), "w") as f:
        json.dump(view_data, f, indent=2)

def ag_weapon_to_row(data, ag_weapon, debrief_id) -> (dict,CVW17DatabaseRow):
    aircrew = data.get('aircrew', [{}, {}, {}, {}])[ag_weapon.get('pilot_id', 1) - 1]

    row = CVW17DatabaseRow(
        get_submission_date(data) or None,
        data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
        MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(aircrew.get('modex')), Squadrons.NONE).value or None,
        aircrew.get('rio', "").strip().lower() or None,
        aircrew.get('pilot', "").strip().lower() or None,
        InputDataHandler.safe_int(aircrew.get('modex', "").strip()) or None,
        'A/G',
        ag_weapon.get('weapon_name', "").strip() or None,
        ag_weapon.get('target_value', "").strip() or None,
        None,
        None,
        None,
        None,
        True,
        True,
        1,
        InputDataHandler.safe_int(data.get('mission_number', "").strip()) or None,
        data.get('mission_name', "").strip() or None,
        data.get('mission_event', "").strip().upper() or None,
        data.get('mission_notes', ""),
        debrief_id
    )
    return aircrew, row

def aa_weapon_to_row(data, aa_weapon, debrief_id) -> (dict | None,CVW17DatabaseRow | None):
    aircrew = None
    for aircrew_ in data.get('aircrew', []):
        if aircrew_.get('modex') == aa_weapon.get('modex') and aa_weapon.get('modex') is not None:
            aircrew = aircrew_
            break

    if aircrew is None:
        return None

    row = CVW17DatabaseRow(
        get_submission_date(data) or None,
        data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
        MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(aircrew.get('modex')), Squadrons.NONE).value or None,
        aircrew.get('rio', '').strip().lower() or None,
        aircrew.get('pilot', '').strip().lower() or None,
        InputDataHandler.safe_int(aircrew.get('modex', "").strip()) or None,
        'A/A',
        aa_weapon.get('weapon', '').strip() or None,
        aa_weapon.get('target', '').strip() or None,
        aa_weapon.get('target_altitude', None),
        aa_weapon.get('own_altitude', None),
        aa_weapon.get('speed', None),
        aa_weapon.get('range', None),
        aa_weapon.get('hit', False),
        aa_weapon.get('hit', False),
        1,
        InputDataHandler.safe_int(data.get('mission_number', "").strip()) or None,
        data.get('mission_name', '').strip() or None,
        data.get('mission_event', '').strip().upper() or None,
        data.get('mission_notes', ''),
        debrief_id
    )

    return aircrew, row

def aircrew_to_empty_row(data, aircrew, debrief_id) -> CVW17DatabaseRow:
    return CVW17DatabaseRow(
        get_submission_date(data) or None,
        data.get('aircrew', [{}])[0].get('pilot', '').strip().lower() or None,
        MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(aircrew.get('modex')), Squadrons.NONE).value or None,
        aircrew.get('rio', '').strip().lower() or None,
        aircrew.get('pilot', '').strip().lower() or None,
        InputDataHandler.safe_int(aircrew.get('modex', '').strip()) or None,
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
        InputDataHandler.safe_int(data.get('mission_number', "").strip()) or None,
        data.get('mission_name', '').strip() or None,
        data.get('mission_event', '').strip().upper() or None,
        data.get('mission_notes', ''),
        debrief_id
    )

def insert_tracker_data(data, debrief_id):
    draw_dynamic_map()
    aircrew_presence = deepcopy(data.get('aircrew', []))

    for ag_weapon in data.get('ag_weapons', []):
        aircrew, row = ag_weapon_to_row(data, ag_weapon, debrief_id)
        if aircrew is None or row is None:
            continue

        if InputDataHandler.validate_row(row):
            if aircrew in aircrew_presence:
                aircrew_presence.remove(aircrew)
            postgres_client.insert(row)

    for aa_weapon in data.get('aa_weapons', []):
        aircrew, row = aa_weapon_to_row(data, aa_weapon, debrief_id)

        if InputDataHandler.validate_row(row):
            if aircrew in aircrew_presence:
                aircrew_presence.remove(aircrew)
            postgres_client.insert(row)

    for aircrew in aircrew_presence:
        row = aircrew_to_empty_row(data, aircrew, debrief_id)

        if InputDataHandler.validate_row(row):
            postgres_client.insert(row)


def remove_tracker_data(debrief_id):
    postgres_client.update_local()
    postgres_client.remove_by_debrief_id(debrief_id)

def format_relative_date(date_input):
    """
    Format a date as relative time or absolute date in CET timezone.

    Args:
        date_input: Can be a datetime object, date string, or timestamp

    Returns:
        str: Formatted date string in CET
    """
    cet = ZoneInfo('Europe/Berlin')  # CET/CEST timezone

    if date_input is None:
        return "INVALID DATE"

    # Convert input to datetime if it's not already
    if isinstance(date_input, str):
        # Try common date formats, including ISO formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO with microseconds and Z (UTC)
            '%Y-%m-%dT%H:%M:%SZ',  # ISO with Z, no microseconds (UTC)
            '%Y-%m-%dT%H:%M:%S.%f',  # ISO with microseconds, no Z
            '%Y-%m-%dT%H:%M:%S',  # ISO basic format
            '%Y-%m-%d %H:%M:%S.%f',  # Space separator with microseconds
            '%Y-%m-%d %H:%M:%S',  # Space separator
            '%Y-%m-%d %H:%M',  # Space separator, no seconds
            '%Y-%m-%d',  # Date only
            '%m/%d/%Y %H:%M:%S',  # US format with seconds
            '%m/%d/%Y %H:%M',  # US format
            '%m/%d/%Y'  # US format, date only
        ]

        for fmt in formats:
            try:
                target_date = datetime.strptime(date_input, fmt)
                # If format ends with 'Z', treat as UTC
                if fmt.endswith('Z'):
                    target_date = target_date.replace(tzinfo=timezone.utc)
                    target_date = target_date.astimezone(cet)
                else:
                    # Assume naive datetime is already in CET
                    target_date = target_date.replace(tzinfo=cet)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Unable to parse date string: {date_input}")
    elif isinstance(date_input, (int, float)):
        # Timestamp is assumed to be UTC
        target_date = datetime.fromtimestamp(date_input, tz=timezone.utc)
        target_date = target_date.astimezone(cet)
    else:
        # If datetime object is naive, assume it's in CET
        if date_input.tzinfo is None:
            target_date = date_input.replace(tzinfo=cet)
        else:
            # Convert to CET if it has timezone info
            target_date = date_input.astimezone(cet)

    # Get current time in CET
    now = datetime.now(cet)

    # Calculate the difference in days
    days_diff = (now.date() - target_date.date()).days

    # Format based on the difference
    if days_diff == 0:
        return f"Today at {target_date.strftime('%H:%M')}"
    elif days_diff == 1:
        return f"Yesterday at {target_date.strftime('%H:%M')}"
    elif 2 <= days_diff <= 6:
        return f"{days_diff} days ago"
    else:
        return target_date.strftime('%m/%d/%Y %H:%M')

def get_bda_list():
    bdas = []

    os.makedirs(DEBRIEFS_PATH, exist_ok=True)
    for debrief in reversed(os.listdir(DEBRIEFS_PATH)):
        if not os.path.exists(DEBRIEFS_PATH / debrief / 'submit-data.json'):
            continue

        with open(DEBRIEFS_PATH / debrief / 'submit-data.json', 'r') as f:
            data = json.load(f)

        for bda in data.get('ag_weapons', []):
            if not all(bda.get(key) for key in ['target_value', 'bda_result', 'weapon_name', 'pilot_id']):
                continue

            if not all(data.get(key) for key in ['mission_number', 'mission_event', 'callsign']):
                continue

            bdas.append(
                {
                    "id": str(debrief),
                    "msn-nr": data['mission_number'],
                    "msn-evt": data['mission_event'],
                    "date": format_relative_date(data.get('form_metadata', {}).get('submission_time')),
                    "callsign": data['callsign'] + str(bda['pilot_id']),
                    "weapon": bda['weapon_name'],
                    "target": bda['target_value'],
                    "bda-result": bda['bda_result'],
                    "img-src": "/bda/" + str(debrief) + "/" + bda.get('image_path') if bda.get('image_path') else '',
                }
            )

    return bdas

def remove_debrief_data(debrief_id):
    if os.path.exists(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json'):
        os.remove(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json')

    if os.path.exists(DEBRIEFS_PATH / str(debrief_id) / 'view-data.json'):
        os.remove(DEBRIEFS_PATH / str(debrief_id) / 'view-data.json')

    for file in os.listdir(DEBRIEFS_PATH / str(debrief_id)):
        if file.split('.')[-1] in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']:
            os.remove(DEBRIEFS_PATH / str(debrief_id) / file)

@app.route('/edit-report/<int:debrief_id>', methods=['POST'])
def edit_report(debrief_id):
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    os.makedirs(DEBRIEFS_PATH, exist_ok=True)
    if not os.path.exists(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json'):
        return jsonify({'error': 'Report data not found'}), 404

    with open(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json') as f:
        if session.get('discord_uid', -1) != json.load(f).get('form_metadata', {}).get('discord_uid'):
            if session.get('discord_uid') not in config.admin_uids:
                return jsonify({'error': 'Unauthorized'}), 401

    try:
        with open(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json') as f:
            old_data = json.load(f)

        data = request.get_json()
        if not data or not InputDataHandler.validate_data_json(data):
            return jsonify({'error': 'No data received'}), 400

        remove_debrief_data(debrief_id)
        save_images(data, debrief_id)

        old_date = old_data.get('form_metadata', {}).get('submission_time')
        if old_date:
            data['form_metadata']['submission_time'] = old_date

        old_uid = old_data.get('form_metadata', {}).get('discord_uid')
        if old_uid:
            data['form_metadata']['discord_uid'] = old_uid
        else:
            data['form_metadata']['discord_uid'] = session['discord_uid']

        with open(DEBRIEFS_PATH / Path(str(debrief_id)) / Path("submit-data.json"), "w") as f:
            json.dump(data, f, indent=2)

        create_display_data(data, debrief_id)

        remove_tracker_data(debrief_id)
        insert_tracker_data(data, debrief_id)

        return jsonify({
            'success': True,
            'message': 'Strike report updated successfully',
            'id': str(debrief_id),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/submit-report', methods=['POST'])
def submit_report():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    try:
        data = request.get_json()

        if not data or not InputDataHandler.validate_data_json(data):
            return jsonify({'error': 'No data received'}), 400

        os.makedirs(DEBRIEFS_PATH, exist_ok=True)
        debrief_id = InputDataHandler.find_latest_numbered_folder(DEBRIEFS_PATH)

        save_images(data, debrief_id)

        data['form_metadata']['discord_uid'] = session['discord_uid']

        os.makedirs(DEBRIEFS_PATH, exist_ok=True)
        with open(DEBRIEFS_PATH / Path(str(debrief_id)) / Path("submit-data.json"), "w") as f:
            json.dump(data, f, indent=2)

        create_display_data(data, debrief_id)
        insert_tracker_data(data, debrief_id)

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
def file_report():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    debrief_id = request.args.get('id')
    if debrief_id:
        with open(DEBRIEFS_PATH / str(debrief_id) / 'submit-data.json') as f:
            form_discord_uid = json.load(f).get('form_metadata', {}).get('discord_uid')

        if session.get('discord_uid', -1) != form_discord_uid:
            if session.get('discord_uid') not in config.admin_uids:
                flash('You are not authorized to edit this report!', 'error')
                return redirect(request.referrer or '/reports')

    return render_template('submit.html')


@app.route('/')
def home():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('menu.html', bdas=get_bda_list())
    return redirect('/login')
