from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler

msn_data_blueprint = Blueprint('msn_data_blueprint', __name__)
app = msn_data_blueprint

@app.route('/data-labels')
def data_labels():
    files: list[Path] = FileHandler.sort_files_by_date_modified(MSN_DATA_FILES_PATH)
    return jsonify({int(id_): path.name for id_, path in enumerate(files)})

@app.route('/data')
def data():
    try:
        id_ = int(request.args.get('id', 0))
    except ValueError:
        id_ = 0

    files: list[Path] = FileHandler.sort_files_by_date_modified(MSN_DATA_FILES_PATH)
    if len(files) <= id_:
        id_ = 0

    return send_file(files[id_])
