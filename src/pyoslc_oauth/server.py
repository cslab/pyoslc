from authlib.integrations.flask_oauth1 import AuthorizationServer, register_nonce_hooks, \
    register_temporary_credential_hooks
from authlib.integrations.sqla_oauth1 import create_query_client_func, register_token_credential_hooks

from pyoslc_oauth.database import db
from pyoslc_oauth.models import Client, cache, TokenCredential

query_client = create_query_client_func(db.session, Client)
auth_server = AuthorizationServer(query_client=query_client)


def init_app(app):
    auth_server.init_app(app)
    register_nonce_hooks(auth_server, cache)
    register_temporary_credential_hooks(auth_server, cache)
    register_token_credential_hooks(auth_server, db.session, TokenCredential)
