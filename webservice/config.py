import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'oauth.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = None,
    LOG_TO_STDOUT = None,
    SECRET_KEY = 'd3v3L0p',

    AUTHLIB_INSECURE_TRANSPORT = True
    OAUTHLIB_INSECURE_TRANSPORT = True

    OAUTH1_PROVIDER_ENFORCE_SSL = False
    OAUTH1_PROVIDER_KEY_LENGTH = (10, 100)

    BASE_URI = 'http://examples.org/'

