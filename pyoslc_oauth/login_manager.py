from flask_login import LoginManager

login = LoginManager()


def init_app(app):
    login.init_app(app)
