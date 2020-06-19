from flask import request
from flask_login import login_user

from oauth import OAuthApplication
from oauth.models import User
from oauth.resources import OAuthException


class PyOSLCApplication(OAuthApplication):

    def get_realm(self):
        pass

    def is_authenticated(self):
        pass

    def login(self, username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise OAuthException('Email or password is invalid.')

        login_user(user)

    def is_admin_session(self):
        return request.args.get('admin')
