"""
    This module will create all the elements for the
    services in the oslc adapter.
"""
from collections import OrderedDict

from rdflib import Literal
from rdflib.namespace import DCTERMS

from pyoslc.helpers import build_uri
from pyoslc.vocabulary import OSLCCore

default_uri = 'http://examples.com/'


class ServiceFactory:

    def __init__(self):
        pass

    def get_service(self, map):
        raise NotImplementedError()


class Link:

    def __init__(self, label=None):
        self.__label = label if label is not None else None


class BaseResource:
    """
    Class to define generic resources.
    """

    def __init__(self, about=None, types=None, properties=None):
        """
        Initialize the generic resource with the about property
        """

        self.__about = about if about is not None else default_uri
        self.__types = types if types is not None else list()
        self.__extended_properties = properties if properties is not None else dict()


class Resource(BaseResource):

    def __init__(self, about=None, types=None, properties=None,
                 description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None,
                 created=None, modified=None, type=None, discussed_by=None,
                 instance_shape=None, service_provider=None, relation=None):
        """
        Initialize the generic resource with the about property
        """

        BaseResource.__init__(self, about, types, properties)

        self.__description = description if description is not None else ''
        self.__identifier = identifier if identifier is not None else ''
        self.__short_title = short_title if short_title is not None else ''
        self.__title = title if title is not None else ''
        self.__contributor = contributor if contributor is not None else set()
        self.__creator = creator if creator is not None else set()
        self.__subject = subject if subject is not None else set()
        self.__created = created if created is not None else None
        self.__modified = modified if modified is not None else None
        self.__type = type if type is not None else set()
        self.__discussed_by = discussed_by if discussed_by is not None else None
        self.__instance_shape = instance_shape if instance_shape is not None else None
        self.__service_provider = service_provider if service_provider is not None else None
        self.__relation = relation if relation is not None else None


class ServiceProviderCatalog(Resource):

    def __init__(self,
                 graph=None,
                 uri=None,
                 title="Service Provider Catalog.",
                 description="Main service for the adapter.",
                 publisher=None,
                 domain=None,
                 service_provider=None,
                 service_provider_catalog=None,
                 oauth_configuration=None
                 ):
        self.__uri = uri if uri is not None else build_uri(default_uri, 'serviceProviderCatalog')
        super(ServiceProviderCatalog, self).__init__(about=self.__uri)

        self.__graph = graph
        self.__title = title
        self.__description = description
        self.__publisher = publisher
        self.__domain = domain if domain is not None else OrderedDict()
        self.__service_provider = service_provider if service_provider is not None else list()
        self.__service_provider_catalog = service_provider_catalog if service_provider_catalog is not None else OrderedDict()
        self.__oauth_configuration = oauth_configuration

        # self.initialize_graph()

    def initialize_graph(self):
        if self.__title is not None:
            self.__graph.add((self.__spc, DCTERMS.title, Literal(self.__title)))

        if self.__description is not None:
            self.__graph.add((self.__spc, DCTERMS.description, Literal(self.__description)))

        if self.__publisher is not None:
            for publisher in self.__publisher:
                self.__graph.add((self.__spc, DCTERMS.publisher, publisher))

        if self.__domain is not None and self.__domain.__len__() > 0:
            for domain in self.__domain:
                self.__graph.add((self.__spc, OSLCCore.domain, domain))

        if self.__service_provider is not None and self.__service_provider.__len__() > 0:
            for service_provider in self.__service_provider:
                self.__graph.add((self.__spc, OSLCCore.serviceProvider, service_provider))

        if self.__service_provider_catalog is not None and self.__service_provider_catalog.__len__() > 0:
            for service_provider_catalog in self.__service_provider_catalog:
                self.__graph.add((self.__spc, OSLCCore.serviceProviderCatalog, service_provider_catalog))

        if self.__oauth_configuration is not None and self.__oauth_configuration.__len__() > 0:
            for oauth_configuration in self.__oauth_configuration:
                self.__graph.add((self.__spc, OSLCCore.oauthConfiguration, oauth_configuration))

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if isinstance(title, str):
            self.__title = title
            self.__graph.remove((None, DCTERMS.title, None))
            self.__graph.add((self.__spc, DCTERMS.title, Literal(title)))
        else:
            raise ValueError('The title must be an instance of str')

    def add_service_provider(self, service_provider):
        if isinstance(service_provider, ServiceProvider):
            self.__graph.add((self.__spc, OSLCCore.serviceProvider, service_provider))
        else:
            return ValueError('The object must be a ServiceProvider')

    def to_rdf(self, format='application/rdf+xml'):
        return self.__graph.serialize(format=format)


# class ServiceProvider(ServiceFactory, Resource):
#     def __init__(self,
#                  title=None,
#                  description=None,
#                  publisher=None,
#                  service=None,
#                  details=None,
#                  prefix_definition=None,
#                  oauth_configuration=None
#                  ):
#         """
#         Initialize ServiceProvider
#         """
#         super(ServiceProvider, self).__init__('http://example.com/')
#         self.title = title
#         self.description = description
#         self.publisher = publisher
#         self.service = service if service is not None else list()
#         self.details = details if details is not None else OrderedDict()
#         self.prefix_definition = prefix_definition if prefix_definition is not None else list()
#         self.oauth_configuration = oauth_configuration
#
#         self.created = date.today()
#         self.identifier = BNode()
#
#     def get_service(self, map):
#         yield self
#
#
# class Service(Resource):
#
#     def __init__(self, uri_domain, creation_factory, query_capability, selection_dialog, creation_dialog, usage):
#         """
#         Initialize Service
#         """
#         super(Service, self).__init__()
#
#         self.uri_domain = uri_domain
#         self.creation_factory = creation_factory if creation_factory is not None else list()
#         self.query_capability = query_capability if query_capability is not None else list()
#         self.selection_dialog = selection_dialog if selection_dialog is not None else list()
#         self.creation_dialog = creation_dialog if creation_dialog is not None else list()
#         self.usage = usage if usage is not None else list()
#
#
# class OAuthConfiguration(Resource):
#
#     def __init__(self, autorization_uri, oaut_access_token_uri, oaut_request_token_uri):
#         """
#         private URI authorizationURI;
#         private URI oauthAccessTokenURI;
#         private URI oauthRequestTokenURI;
#         """
#         super(OAuthConfiguration, self).__init__()
#         self.autorization_uri = autorization_uri
#         self.oaut_access_token_uri = oaut_access_token_uri
#         self.oaut_request_token_uri = oaut_request_token_uri
#
#
# class Publisher(Resource):
#
#     def __init__(self, uri_icon=None, identifier=None, label=None, title=None):
#         """
#         Resource for publisher
#         """
#         super(Publisher, self).__init__()
#         self.uri_icon = uri_icon
#         self.identifier = identifier
#         self.label = label
#         self.title = title
#
#
# class CreationFactory(Resource):
#
#     def __init__(self, title, label, creation, usage, resource_type, resource_shape):
#
#         """
#         Creation Factory
#         """
#         super(CreationFactory, self).__init__()
#         self.title = title
#         self.label = label
#         self.uri_creation = creation
#         self.usage = usage if usage is not None else OrderedDict()
#         self.resource_type = resource_type if resource_type is not None else OrderedDict()
#         self.resource_shape = resource_shape if resource_shape is not None else OrderedDict()
