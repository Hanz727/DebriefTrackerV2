import json
import os
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file, render_template

from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler
from web.input._constants import BDA_IMAGE_PATH

reports_blueprint = Blueprint('reports_blueprint', __name__)
app = reports_blueprint

@app.route('/reports')
def reports():
    reports_ = []

    for debrief in os.listdir(BDA_IMAGE_PATH):
        with open(BDA_IMAGE_PATH / debrief / "submit-data.json", 'r') as f:
            submit_data = json.load(f)
            reports_row = {'event': submit_data['mission_event'], 'date': submit_data['mission_date'],
                           'mission-name': submit_data['mission_name'], 'mission-number': submit_data['mission_number'],
                           'callsign': submit_data['callsign'] + "1", 'debrief-id': debrief}
            reports_.append(reports_row)

    return render_template('reports.html', reports=reports_)

