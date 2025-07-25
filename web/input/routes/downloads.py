import os
import time

from flask import Blueprint, render_template, send_from_directory, session, redirect
from web.input.config.config import WebConfigSingleton

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
        formatted_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(item_mtime))

        item_name = item
        idx = item.find('DCS')
        if idx != -1:
            item_name = item[idx:]
        item_name = item_name.replace('.zip.acmi', '').replace('.trk', '')

        if item_size < 1: # 1mb min filter
            continue

        # Append file information to the list
        directory_listing.append({
            'item': item,
            'name': item_name,
            'size': round(item_size, 1),
            'date': formatted_date,
            'is_directory': os.path.isdir(item_path)
        })
        directory_listing.sort(key=lambda x: x['date'], reverse=True)

    return directory_listing

@app.route('/tacview')
def tacview():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('directory.html', files=_list_directory(config.tacview_dir),
                               title="CVW-17 Tacview Archive", route='tacview')
    return redirect('/login')


@app.route('/tracks')
def tracks():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('directory.html', files=_list_directory(config.tracks_dir),
                               title="CVW-17 Tracks Archive", route='tracks')
    return redirect('/login')

@app.route('/tracks/<filename>')
def download_track(filename):
    if session.get('authed', False) or config.bypass_auth_debug:
        if not filename.endswith('.trk'):
            return "<h1>404 File not found<h1>"
        return send_from_directory(config.tracks_dir, filename, as_attachment=True)

    return redirect('/login')

@app.route('/tacview/<filename>')
def download_tacview(filename):
    if session.get('authed', False) or config.bypass_auth_debug:
        if not filename.endswith('.acmi'):
            return "<h1>404 File not found<h1>"
        return send_from_directory(config.tacview_dir, filename, as_attachment=True)

    return redirect('/login')