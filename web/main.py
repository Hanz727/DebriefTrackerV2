from datetime import timedelta
from pathlib import Path

from flask import Flask, redirect, request, session, render_template, send_file, jsonify
import os

from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
