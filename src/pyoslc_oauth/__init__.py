import os

from flask_bootstrap import Bootstrap

from pyoslc_oauth import database, server
from pyoslc_oauth.login_manager import login
from pyoslc_oauth.resources import (
    OAuthConfiguration,
    FileSystemConsumerStore,
    OAuthApplication,
    OSLCOAuthConsumer,
)
from pyoslc_oauth.routes.consumer import consumer_bp
from pyoslc_oauth.routes.oauth import oauth_bp

base_dir = os.path.abspath(os.path.dirname(__file__))


oauth_config = OAuthConfiguration()
file_consumer = FileSystemConsumerStore(os.path.join(base_dir, "OAuthStore.rdf"))
oauth_app = OAuthApplication("PyOLSC")
client = OSLCOAuthConsumer()


def init_app(app, oslc_oauth_app=None):
    database.init_app(app)
    login.init_app(app)
    oauth_config.consumer_store = file_consumer
    oauth_config.application = oslc_oauth_app or oauth_app
    app.register_blueprint(oauth_bp)
    app.register_blueprint(consumer_bp)
    Bootstrap(app)
    server.init_app(app)
