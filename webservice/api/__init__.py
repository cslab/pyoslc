import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from webservice.config import Config

db = SQLAlchemy()
login = LoginManager()
cors = CORS()


def create_app(config=Config):
    app = Flask(__name__, instance_relative_config=False)

    if config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_object(config)

    db.init_app(app)
    login.init_app(app)
    cors.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import web
    app.register_blueprint(web.bp)
    app.add_url_rule('/', endpoint='index')

    from . import oslc
    app.register_blueprint(oslc.bp, url_prefix='/oslc')

    # TODO register cdb standard functionalities over http endpoint
    # from . import cdb
    # app.register_blueprint(cdb.bp, url_prefix='/cdb')

    from webservice.api.oauth_app import PyOSLCApplication
    pyoslc_app = PyOSLCApplication('PyOSLC Contact Software')

    import oauth as py_oauth
    py_oauth.init_app(app, pyoslc_app)

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

    return app
