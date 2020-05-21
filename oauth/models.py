from authlib.integrations.sqla_oauth1 import OAuth1ClientMixin, OAuth1TemporaryCredentialMixin, \
    OAuth1TokenCredentialMixin, OAuth1TimestampNonceMixin

from webservice.api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def get_user_id(self):
        return self.id


class Client(db.Model, OAuth1ClientMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class TemporaryCredential(db.Model, OAuth1TemporaryCredentialMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class TokenCredential(db.Model, OAuth1TokenCredentialMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    def set_user_id(self, user_id):
        self.user_id = user_id


class TimestampNonce(db.Model, OAuth1TimestampNonceMixin):
    id = db.Column(db.Integer, primary_key=True)
