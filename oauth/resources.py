from authlib.integrations.flask_client import OAuth
from enum import Enum


class OAuthVersion(Enum):
    OAUTH_1_0 = '1.0'
    OAUTH_1_0A = '1.0a'
    OAUTH_2_0 = '2.0'


class OAuthServiceProvider:

    def __init__(self, request_token_url=None, user_authorization_url=None, access_token_url=None):
        self.__request_token_url = request_token_url if request_token_url is not None else None
        self.__user_authorization_url = user_authorization_url if user_authorization_url is not None else None
        self.__access_token_url = access_token_url if access_token_url is not None else None

    @property
    def request_token_url(self):
        return self.__request_token_url

    @request_token_url.setter
    def request_token_url(self, request_token_url):
        self.__request_token_url = request_token_url

    @property
    def user_authorization_url(self):
        return self.__user_authorization_url

    @user_authorization_url.setter
    def user_authorization_url(self, user_authorization_url):
        self.__user_authorization_url = user_authorization_url

    @property
    def access_token_url(self):
        return self.__access_token_url

    @access_token_url.setter
    def access_token_url(self, access_token_url):
        self.__access_token_url = access_token_url


class OAuthConsumer(OAuth):

    def __init__(self, callback_url=None, consumer_key=None, consumer_secret=None, service_provider=None):
        super(OAuthConsumer, self).__init__()
        self.__callback_url = callback_url if callback_url is not None else None
        self.__consumer_key = consumer_key if consumer_key is not None else None
        self.__consumer_secret = consumer_secret if consumer_secret is not None else None
        self.__service_provider = service_provider if service_provider is not None else None
        self.__properties = dict()

    @property
    def callback_url(self):
        return self.__callback_url

    @callback_url.setter
    def callback_url(self, callback_url):
        self.__callback_url = callback_url

    @property
    def consumer_key(self):
        return self.__consumer_key

    @consumer_key.setter
    def consumer_key(self, consumer_key):
        self.__consumer_key = consumer_key

    @property
    def consumer_secret(self):
        return self.__consumer_secret

    @consumer_secret.setter
    def consumer_secret(self, consumer_secret):
        self.__consumer_secret = consumer_secret

    @property
    def service_provider(self):
        return self.__service_provider

    @service_provider.setter
    def service_provider(self, service_provider):
        self.__service_provider = service_provider

    @property
    def properties(self):
        return self.__properties

    @properties.setter
    def properties(self, properties):
        self.__properties = properties

    def add_property(self, item):
        self.__properties[item.key] = item.value

    def get_property(self, key):
        if key in self.__properties:
            return self.__properties[key]
        return None


class OSLCOAuthConsumer(OAuthConsumer):

    def __init__(self, name=None, provisional=True, trusted=None, consumer_key=None, consumer_secret=None):
        super(OSLCOAuthConsumer, self).__init__(consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.__name = name if name is not None else None
        self.__provisional = provisional
        self.__trusted = trusted if trusted is not None else False
        self.__oauth_version = OAuthVersion.OAUTH_1_0

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def provisional(self):
        return self.__provisional

    @provisional.setter
    def provisional(self, provisional):
        self.__provisional = provisional

    @property
    def trusted(self):
        return self.__trusted

    @trusted.setter
    def trusted(self, trusted):
        self.__trusted = trusted

    @property
    def oauth_version(self):
        return self.__oauth_version


class ConsumerStore:

    def __init__(self):
        pass

    def get_consumer(self, consumer_key=None):
        pass


class OAuthConfiguration(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.__instance = super(OAuthConfiguration, cls).__new__(cls, *args, **kwargs)

        return cls.instance

    def __init__(self):
        self.__consumer_store = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(OAuthConfiguration, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    @property
    def consumer_store(self):
        return self.__consumer_store

    @consumer_store.setter
    def consumer_store(self, consumer_store):
        self.__consumer_store = consumer_store

    @classmethod
    def add_consumer(cls, consumer):
        print(consumer)
        return True

