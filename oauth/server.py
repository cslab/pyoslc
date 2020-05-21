from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth1 import AuthorizationServer
from authlib.integrations.sqla_oauth1 import create_query_client_func, register_nonce_hooks, \
    register_temporary_credential_hooks, register_token_credential_hooks

from oauth.models import Client, TimestampNonce, TemporaryCredential, TokenCredential
from webservice.api import db

query_client = create_query_client_func(db.session, Client)
server = AuthorizationServer()
# client = OAuth()


def init_app(app):
    # client.init_app(app)
    server.init_app(app, query_client=query_client)
    register_nonce_hooks(server, db.session, TimestampNonce)
    register_temporary_credential_hooks(server, db.session, TemporaryCredential)
    register_token_credential_hooks(server, db.session, TokenCredential)
