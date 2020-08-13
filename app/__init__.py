import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_cors import CORS

from app import config

cors = CORS()


def create_app(app_config=None):
    app = Flask(__name__, instance_relative_config=False)
    cors.init_app(app)

    if app_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_object(app_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            """
            Implementation for Mail notifications
            """
            pass

    if app.debug and app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/pysolc.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s '
                                                    '%(levelname)s: %(message)s '
                                                    '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('---------- Initializing PyOSL WS-API ----------')

    from web.routes import bp as website
    app.register_blueprint(website)

    from app.api.adapter import oslc
    oslc.init_app(app)

    from app.api.oauth import oslc_oauth
    oslc_oauth.init_app(app)

    return app

