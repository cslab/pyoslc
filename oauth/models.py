from authlib.integrations.sqla_oauth1 import OAuth1ClientMixin, OAuth1TokenCredentialMixin
from flask import g, current_app
from flask_login import UserMixin
from werkzeug.contrib.cache import FileSystemCache
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash, check_password_hash

from webservice.api import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    _password = db.Column('password', db.String(100))

    def get_user_id(self):
        return self.id

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def to_dict(self):
        return dict(id=self.id, username=self.username)


class Client(db.Model, OAuth1ClientMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), nullable=False)

    # This section could be overwritten by the implementer
    # to link the Client with a functional user
    #
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    # )
    # user = db.relationship('User')

    def __init__(self, name, client_id, client_secret, default_redirect_uri):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.default_redirect_uri = default_redirect_uri


class TokenCredential(db.Model, OAuth1TokenCredentialMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    def set_user_id(self, user_id):
        self.user_id = user_id


def _get_cache():
    _cache = g.get('_oauth_cache')
    if _cache:
        return _cache
    _cache = FileSystemCache(current_app.config['OAUTH_CACHE_DIR'])
    g._oauth_cache = _cache
    return _cache


cache = LocalProxy(_get_cache)
