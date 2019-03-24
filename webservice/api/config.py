import os

from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

SECRET_KEY = b'\xa3T\xa9\xcb\xd6R\x1b\xe1GEy\x1b\xa4d\x17\xae'

class BaseConfig:
    DEBUG = False
    MAIL_SERVER = None
    LOG_TO_STDOUT = None
