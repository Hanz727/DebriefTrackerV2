from flask import session, redirect, request, render_template, Blueprint

from clients.databases.postgres.postgres_client import PostGresClient
from web.config.config import WebConfigSingleton
from web.tracker_ui.input_data_handler import InputDataHandler

config = WebConfigSingleton.get_instance()
postgres_client = PostGresClient()

home_blueprint = Blueprint('main', __name__)
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
            postgres_client.insert(row)
        i += 1

    return 'Debrief uploaded!'

@app.route('/')
def home():
    if session.get('authed', False) or config.bypass_auth_debug:
        return render_template('index.html')
    return redirect('/login')