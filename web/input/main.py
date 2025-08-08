import logging
import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS

from web.input._constants import FLASK_SECURE_KEY

#import redis
#from flask_session import Session

from web.input.routes.auth import auth_blueprint
from web.input.routes.dmpi_db import dmpi_db_blueprint, dmpi_db, draw_dynamic_map_threaded
from web.input.routes.downloads import downloads_blueprint
from web.input.routes.home import home_blueprint
from web.input.routes.msn_data import msn_data_blueprint
from web.input.routes.reports import reports_blueprint

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.secret_key = FLASK_SECURE_KEY

    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename='logs/input-log.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    #app.config['SESSION_USE_SIGNER'] = True
    #app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379)

    #server_session = Session(app)

    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(msn_data_blueprint)
    app.register_blueprint(downloads_blueprint)
    app.register_blueprint(reports_blueprint)
    app.register_blueprint(dmpi_db_blueprint)

    draw_dynamic_map_threaded()

    logger.info('app created')
    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5000, debug=False)
