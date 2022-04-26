from flask import session, g
from six import PY2

if PY2:
    from flask._compat import string_types
else:
    string_types = (str,)
from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, StopValidation
from wtforms.widgets import HiddenInput

from pyoslc_oauth.models import User


class BaseForm(FlaskForm):
    def hidden_fields(self):
        for field in self._fields:
            if isinstance(field, string_types):
                field = getattr(self, field, None)

            if field and isinstance(field.widget, HiddenInput):
                yield field

    def visible_fields(self):
        for field in self._fields:
            if isinstance(field, string_types):
                field = getattr(self, field, None)

            if field and not isinstance(field.widget, HiddenInput):
                yield field


class ConfirmForm(BaseForm):
    confirm = BooleanField()


class LoginConfirmForm(ConfirmForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

    def validate_password(self, field):
        username = self.username.data.lower()
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(field.data):
            raise StopValidation("Email or password is invalid.")

        if self.confirm.data:
            # login(user, False)
            login_user(user)
            session["sid"] = user.id
            session.permanent = False
            g.current_user = user


class AdminLogin(BaseForm):
    pass
