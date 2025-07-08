from flask import abort, session, redirect, request, render_template, Blueprint, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from clients.databases.contracts import CVW17DatabaseRow
from clients.databases.postgres.postgres_client import PostGresClient
from clients.thread_pool_client import ThreadPoolClient
from web.input._constants import BDA_IMAGE_PATH
from web.input.config.config import WebConfigSingleton
from web.input.tracker_ui.input_data_handler import InputDataHandler


config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()
ThreadPoolClient.create_task_loop(postgres_client.update, 30)

home_blueprint = Blueprint('home', __name__)
app = home_blueprint


@app.route('/bda/<int:debrief_id>/<img_name>')
def bda_img(debrief_id, img_name):
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
    debrief = {
        "debrief-id": debrief_id,
        "mission-name": "Murmansk Strike Escort",
        "mission-number": "5031",
        "mission-event": "1A2",
        "date": "08 JUL 2025",
        "callsign": "VICTORY1",
        "aircrew": [
            {
                "modex": "103",
                "aircrew": "JJ | Scarlett"
            },
            {
                "modex": "105",
                "aircrew": "Nakush | Lilo"
            },
            {
                "modex": "107",
                "aircrew": "Alexandra | Patterson"
            },
            {
                "modex": "111",
                "aircrew": "Klapo | Oscar"
            },
        ],
        "ag-drop-count": 4,
        "bda-count": 4,
        "ag": [
            {
                "modex": "103",
                "drops": [
                    {
                        "weapon-name": "GBU-12 Paveway II",
                        "DMPI": "",
                        "tgt-name": "",
                        "img-name": "1.png"
                    },
                ]
            },
            {
                "modex": "105",
                "drops": [
                    {
                        "weapon-name": "GBU-12 Paveway II",
                        "DMPI": "AJDAS-0124",
                        "tgt-name": "",
                        "img-name": "1.png"
                    }
                ]
            },
            {
                "modex": "107",
                "drops": [
                    {
                        "weapon-name": "GBU-16 Paveway II",
                        "DMPI": "",
                        "tgt-name": "SA-3",
                        "img-name": "1.png"
                    }
                ]
            },
            {
                "modex": "111",
                "drops": [
                    {
                        "weapon-name": "GBU-10 Paveway II",
                        "DMPI": "AJDAS-0126",
                        "tgt-name": "",
                        "img-name": "1.png"
                    }
                ]
            },
        ],
        "opposition": {
            "type": "2xMIG-29",
            "location": "g"
        },
        "aa": [
            {
                "modex": "103",
                "weapon": "AIM-54C",
                "target": "mig-29s",
                "hit": "TRUE"
            },
            {
                "modex": "107",
                "weapon": "AIM-54C",
                "target": "su-27",
                "hit": "TRUE"
            },
            {
                "modex": "105",
                "weapon": "AIM-54C",
                "target": "su-33",
                "hit": "FALSE"
            },
            {
                "modex": "111",
                "weapon": "AIM-54C",
                "target": "j-11",
                "hit": "TRUE"
            },
        ],
        "engagement-result": "1 - Enemy Destroyed",
        "blue-casualties": "none",
        "mission-notes": "note",
        "restrike-recommendation": "1 - No Restrike Recommended"
    }

    return render_template("view.html", debrief=debrief)

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