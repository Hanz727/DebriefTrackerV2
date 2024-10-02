import os
import time

from flask import Blueprint, render_template, send_from_directory
from web.config.config import WebConfigSingleton

downloads_blueprint = Blueprint('downloads', __name__)
config = WebConfigSingleton.get_instance()
app = downloads_blueprint


def _list_directory(path):
    directory_listing = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Get the file's size in MB
        if os.path.isfile(item_path):
            item_size = os.path.getsize(item_path) / (1024 * 1024)  # Convert bytes to MB
        else:
            item_size = None

        # Get the file's last modification time
        item_mtime = os.path.getmtime(item_path)
        formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item_mtime))

        # Append file information to the list
        directory_listing.append({
            'name': item,
            'size': round(item_size, 1),
            'date': formatted_date,
            'is_directory': os.path.isdir(item_path)
        })
        directory_listing.sort(key=lambda x: x['date'], reverse=True)

    return directory_listing

@app.route('/tacview')
def tacview():
    return render_template('directory.html', files=_list_directory(config.tacview_dir),
                           title="CVW-17 Tacview Archive", route='tacview')

@app.route('/tracks')
def tracks():
    return render_template('directory.html', files=_list_directory(config.tracks_dir),
                           title="CVW-17 Tracks Archive", route='tracks')

@app.route('/tracks/<filename>')
def download_track(filename):
    if not filename.endswith('.trk'):
        return "<h1>404 File not found<h1>"
    return send_from_directory(config.tracks_dir, filename, as_attachment=True)


@app.route('/tacview/<filename>')
def download_tacview(filename):
    if not filename.endswith('.acmi'):
        return "<h1>404 File not found<h1>"
    return send_from_directory(config.tacview_dir, filename, as_attachment=True)
