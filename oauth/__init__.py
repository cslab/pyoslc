import os

from flask_bootstrap import Bootstrap

from oauth.resources import OAuthConfiguration, FileSystemConsumerStore, OAuthApplication, OSLCOAuthConsumer
from oauth.routes import oauth_bp
from oauth.consumers import consumer_bp
from oauth import server

base_dir = os.path.abspath(os.path.dirname(__file__))

oauth_config = OAuthConfiguration()
file_consumer = FileSystemConsumerStore(os.path.join(base_dir, 'OAuthStore.rdf'))
oauth_app = OAuthApplication('PyOLSC')
client = OSLCOAuthConsumer()


def init_app(app, oslc_oauth_app=None):
    oauth_config.consumer_store = file_consumer
    oauth_config.application = oslc_oauth_app or oauth_app
    app.register_blueprint(oauth_bp)
    app.register_blueprint(consumer_bp)
    Bootstrap(app)
    server.init_app(app)
