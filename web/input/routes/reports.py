import json
import os
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file, render_template, session, redirect

from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler
from web.input._constants import BDA_IMAGE_PATH
from web.input.config.config import WebConfigSingleton

reports_blueprint = Blueprint('reports_blueprint', __name__)
app = reports_blueprint
config = WebConfigSingleton.get_instance()

@app.route('/reports')
def reports():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    reports_ = []

    for debrief in os.listdir(BDA_IMAGE_PATH):
        with open(BDA_IMAGE_PATH / debrief / "submit-data.json", 'r') as f:
            submit_data = json.load(f)
            reports_row = {'event': submit_data['mission_event'], 'date': submit_data['mission_date'],
                           'mission-name': submit_data['mission_name'], 'mission-number': submit_data['mission_number'],
                           'callsign': submit_data['callsign'] + "1", 'debrief-id': debrief}
            reports_.append(reports_row)

    return render_template('reports.html', reports=reports_)

