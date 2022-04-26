from base64 import b64encode

import six
from authlib.integrations.flask_client import OAuth
from enum import Enum
from rdflib import Graph, RDF, URIRef, Literal, BNode, XSD
from rdflib.resource import Resource

from pyoslc_oauth.vocabulary import OAUTH


class OAuthVersion(Enum):
    OAUTH_1_0 = "1.0"
    OAUTH_1_0A = "1.0a"
    OAUTH_2_0 = "2.0"


class OAuthServiceProvider:
    def __init__(
        self, request_token_url=None, user_authorization_url=None, access_token_url=None
    ):
        self.__request_token_url = (
            request_token_url if request_token_url is not None else None
        )
        self.__user_authorization_url = (
            user_authorization_url if user_authorization_url is not None else None
        )
        self.__access_token_url = (
            access_token_url if access_token_url is not None else None
        )

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
    def __init__(
        self,
        callback_url=None,
        consumer_key=None,
        consumer_secret=None,
        service_provider=None,
    ):
        super(OAuthConsumer, self).__init__()
        self.__callback_url = callback_url if callback_url is not None else None
        self.__key = consumer_key if consumer_key is not None else None
        self.__secret = consumer_secret if consumer_secret is not None else None
        self.__service_provider = (
            service_provider if service_provider is not None else None
        )
        self.__properties = dict()

    @property
    def callback_url(self):
        return self.__callback_url

    @callback_url.setter
    def callback_url(self, callback_url):
        self.__callback_url = callback_url

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, key):
        self.__key = key

    @property
    def secret(self):
        return self.__secret

    @secret.setter
    def secret(self, secret):
        self.__secret = secret

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
    def __init__(
        self,
        name=None,
        provisional=True,
        trusted=None,
        consumer_key=None,
        consumer_secret=None,
    ):
        super(OSLCOAuthConsumer, self).__init__(
            consumer_key=consumer_key, consumer_secret=consumer_secret
        )
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

    def __repr__(self):
        return "<OSLCOAuthConsumer {}>".format(self.name)


class OAuthConfiguration(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OAuthConfiguration, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        if not self._instance:
            self._instance = super(OAuthConfiguration, self).__init__()

        self.__consumer_store = None
        self.__application = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls()

        return cls._instance

    @property
    def consumer_store(self):
        return self.__consumer_store

    @consumer_store.setter
    def consumer_store(self, consumer_store):
        self.__consumer_store = consumer_store

    @property
    def application(self):
        return self.__application

    @application.setter
    def application(self, application):
        self.__application = application


class FileSystemConsumerStore(object):

    _graph = None
    _consumers = dict()

    def __init__(self, oauth_store_path):
        self.__oauth_store_path = oauth_store_path
        self.__create_graph()
        self.__load_consumers()

    def __create_graph(self):
        try:
            self._graph = Graph().parse(self.__oauth_store_path, format="turtle")
        except IOError:
            self._graph = Graph()
            self._graph.bind("oslc_oauth", OAUTH)

    def __load_consumers(self):
        subjects = self._graph.subjects(RDF.type, URIRef(OAUTH.Consumer))
        for s in subjects:
            r = self.__from_resource(s)
            self._consumers[str(r.key)] = r

    def __remove_consumer(self, key):
        if (None, OAUTH.consumerKey, Literal(key)) in self._graph:
            consumer = self._graph.subjects(OAUTH.consumerKey, Literal(key))
            for s in consumer:
                self._graph.remove((s, None, None))

    def add_consumer(self, consumer):
        if self._graph is None:
            raise Exception("Consumer store not initialized")

        self.__remove_consumer(consumer.key)
        # resource = self.__to_resource(consumer)
        self._consumers[consumer.key] = consumer
        self.__save_graph()

        return consumer

    def update_consumer(self, consumer):
        return self.add_consumer(consumer)

    @property
    def consumers(self):
        return self._consumers

    @property
    def consumer_values(self):
        return list(self._consumers.values())

    def __from_resource(self, resource):
        oslc_auth_consumer = OSLCOAuthConsumer()

        name = self._graph.value(resource, OAUTH.consumerName) or None
        key = self._graph.value(resource, OAUTH.consumerKey) or None
        secret = self._graph.value(resource, OAUTH.consumerSecret) or None
        provisional = bool(self._graph.value(resource, OAUTH.provisional))
        trusted = bool(self._graph.value(resource, OAUTH.trusted))

        oslc_auth_consumer.name = name
        oslc_auth_consumer.key = key
        oslc_auth_consumer.secret = secret
        oslc_auth_consumer.provisional = provisional
        oslc_auth_consumer.trusted = trusted

        return oslc_auth_consumer

    def __to_resource(self, consumer):

        if six.PY2:
            consumer.secret = b64encode(consumer.secret.encode("utf-8"))

        if six.PY3:
            consumer.secret = b64encode(consumer.secret)

        resource = Resource(self._graph, BNode())
        resource.add(RDF.type, OAUTH.Consumer)
        resource.add(OAUTH.consumerName, Literal(consumer.name))
        resource.add(OAUTH.consumerKey, Literal(consumer.key))
        resource.add(OAUTH.consumerSecret, Literal(consumer.secret))
        resource.add(
            OAUTH.provisional, Literal(consumer.provisional, datatype=XSD.boolean)
        )
        resource.add(OAUTH.trusted, Literal(consumer.trusted, datatype=XSD.boolean))

        return resource

    def __save_graph(self):
        self._graph.serialize(destination=self.__oauth_store_path, format="turtle")


class OAuthApplication(object):
    def __init__(self, name):
        self.__name = name or None

    @property
    def name(self):
        return self.__name

    def login(self, username, password):
        raise NotImplementedError()

    def is_authenticated(self):
        raise NotImplementedError()

    def is_admin_session(self):
        raise NotImplementedError()

    def get_realm(self):
        raise NotImplementedError()


class OAuthException(Exception):
    """
    Causes the validation chain to stop.

    If StopValidation is raised, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """

    def __init__(self, message="", *args, **kwargs):
        Exception.__init__(*args, **kwargs)
