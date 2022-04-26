import os

from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, ".env"))


class Config(object):
    FLASK_ENV = os.environ.get("FLASK_ENV")
    SECRET_KEY = os.environ.get("SECRET_KEY") or "this_value_should_be_updated"
    FLASK_DEBUG = True

    DATABASE_URL = os.environ.get("DATABASE_URL", None)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///" + os.path.join(
        base_dir, "oauth.sqlite"
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    OAUTH_CACHE_DIR = "_cache"

    MAIL_SERVER = (None,)
    LOG_TO_STDOUT = (None,)

    # AUTHLIB_INSECURE_TRANSPORT = True
    # OAUTHLIB_INSECURE_TRANSPORT = True

    # OAUTH1_PROVIDER_ENFORCE_SSL = False
    # OAUTH1_PROVIDER_KEY_LENGTH = (10, 100)


#     BASE_URI = 'http://examples.org/'
