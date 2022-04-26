import pyoslc_oauth
from app.api.oauth.pyoslc_app import PyOSLCApplication

pyoslc = PyOSLCApplication("PyOSLC Contact Software")


def init_app(app):
    pyoslc_oauth.init_app(app, pyoslc)
