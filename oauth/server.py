from authlib.integrations.flask_oauth1 import AuthorizationServer, register_nonce_hooks, \
    register_temporary_credential_hooks

from authlib.integrations.sqla_oauth1 import create_query_client_func

from oauth.models import Client, TokenCredential
from webservice.api import db

query_client = create_query_client_func(db.session, Client)
from authlib.integrations.sqla_oauth1 import register_token_credential_hooks

from oauth.models import cache

auth_server = AuthorizationServer(query_client=query_client)


def init_app(app):
    auth_server.init_app(app)
    register_nonce_hooks(auth_server, cache)
    register_temporary_credential_hooks(auth_server, cache)
    register_token_credential_hooks(auth_server, db.session, TokenCredential)
