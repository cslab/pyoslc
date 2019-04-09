"""
    This module will create all the elements for the
    services in the oslc adapter.
"""
from collections import OrderedDict
from datetime import date

from rdflib import Literal, Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, XSD
from rdflib.resource import Resource

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

    @property
    def about(self):
        return self.__about

    @about.setter
    def about(self, about):
        self.__about = about

    @property
    def types(self):
        return self.__types

    @types.setter
    def types(self, types):
        self.__types = types

    def add_types(self, type_):
        if type_:
            self.__types.append(type_)

    @property
    def extended_properties(self):
        return self.__extended_properties

    @extended_properties.setter
    def extended_properties(self, extended_properties):
        self.__extended_properties = extended_properties

    def add_extended_propertie(self, extended_propertie):
        if extended_propertie:
            self.__extended_properties.append(extended_propertie)


class ResourceShape(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)


class Resource_(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None):
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
        self.__service_provider = service_provider if service_provider is not None else list()
        self.__relation = relation if relation is not None else None

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def identifier(self):
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier):
        self.__identifier = identifier

    @property
    def short_title(self):
        return self.__short_title

    @short_title.setter
    def short_title(self, short_title):
        self.__short_title = short_title

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if isinstance(title, str):
            self.__title = title
        else:
            raise ValueError('The title must be an instance of str')

    @property
    def contributor(self):
        return self.__contributor

    @contributor.setter
    def contributor(self, contributor):
        self.__contributor = contributor

    def add_contributor(self, contributor):
        if contributor:
            self.__contributor.append(contributor)

    @property
    def creator(self):
        return self.__creator

    @creator.setter
    def creator(self, creator):
        self.__creator = creator

    def add_creator(self, creator):
        if creator:
            self.__creator.append(creator)

    @property
    def subject(self):
        return self.__subject

    @subject.setter
    def subject(self, subject):
        self.__subject = subject

    def add_subject(self, subject):
        if subject:
            self.__subject.append(subject)

    @property
    def created(self):
        return self.__created

    @created.setter
    def created(self, created):
        self.__created = created

    @property
    def modified(self):
        return self.__modified

    @modified.setter
    def modified(self, modified):
        self.__modified = modified

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type_):
        self.__type = type_

    def add_type(self, type_):
        if type_:
            self.__type.append(type_)

    @property
    def discussed_by(self):
        return self.__discussed_by

    @discussed_by.setter
    def discussed_by(self, discussed_by):
        self.__discussed_by = discussed_by

    @property
    def instance_shape(self):
        return self.__instance_shape

    @instance_shape.setter
    def instance_shape(self, instance_shape):
        self.__instance_shape = instance_shape

    @property
    def service_provider(self):
        return self.__service_provider

    @service_provider.setter
    def service_provider(self, service_provider):
        self.__service_provider = service_provider

    def add_service_provider(self, service_provider):
        self.__service_provider.append(service_provider)
        # if isinstance(service_provider, ServiceProvider):
        #     self.__graph.add((self.__spc, OSLCCore.serviceProvider, service_provider))
        # else:
        #     return ValueError('The object must be a ServiceProvider')

    @property
    def relation(self):
        return self.__relation

    @relation.setter
    def relation(self, relation):
        self.__relation = relation


class Publisher(BaseResource):

    def __init__(self, about, types=None, properties=None,
                 uri_icon=None, identifier=None, label=None, title=None):
        """
        Resource for publisher
        """

        BaseResource.__init__(self, about=about, types=types, properties=properties)

        self.__uri_icon = uri_icon
        self.__identifier = identifier
        self.__label = label
        self.__title = title

    @property
    def uri_icon(self):
        return self.__uri_icon

    @uri_icon.setter
    def uri_icon(self, uri_icon):
        self.__uri_icon = uri_icon

    @property
    def identifier(self):
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier):
        self.__identifier = identifier

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if isinstance(title, str):
            self.__title = title
        else:
            raise ValueError('The title must be an instance of str')


class ServiceProviderCatalog(Resource_):

    def __init__(self, about, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 uri=None, publisher=None, domain=None,
                 service_provider_catalog=None, oauth_configuration=None, graph=None,):

        if not about:
            raise Exception('No base_url')

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                          identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                          creator=creator, subject=subject, created=created, modified=modified, type=type,
                          discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                          relation=relation)

        self.__uri = uri if uri is not None else build_uri(default_uri, 'serviceProviderCatalog')

        if not graph:
            self.__graph = Graph()
            self.__graph.bind('oslc', OSLCCore, override=False)
            self.__graph.bind('dcterms', DCTERMS, override=False)

        self.__publisher = publisher
        self.__domain = domain if domain is not None else OrderedDict()
        self.__service_provider_catalog = service_provider_catalog if service_provider_catalog is not None else set()
        self.__oauth_configuration = oauth_configuration

        # self.initialize_graph()

    @property
    def graph(self):
        return self.__graph

    @graph.setter
    def graph(self, graph):
        self.__graph = graph

    @property
    def publisher(self):
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher):
        self.__publisher = publisher

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, domain):
        self.__domain = domain

    def add_domain(self, domain):
        self.__domain.update(domain)

    @property
    def service_provider_catalog(self):
        return self.__service_provider_catalog

    @service_provider_catalog.setter
    def service_provider_catalog(self, service_provider_catalog):
        self.__service_provider_catalog = service_provider_catalog

    def add_service_provider_catalog(self, service_provider_catalog):
        self.__service_provider_catalog.add(service_provider_catalog)

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

    def to_rdf(self, graph):
        print('spc------')

        if not self.about:
            raise Exception("The title is missing")

        spc = Resource(graph, URIRef(self.about))
        spc.add(RDF.type, URIRef(OSLCCore.serviceProviderCatalog))

        if self.title:
            spc.add(DCTERMS.title, Literal(self.title))

        if self.description:
            spc.add(DCTERMS.description, Literal(self.description))

        if self.publisher:
            spc.add(DCTERMS.publisher, URIRef(self.publisher.about))

        if self.domain:
            for item in self.domain.items():
                spc.add(OSLCCore.domain, URIRef(item[1]))

        if self.service_provider:
            for sp in self.service_provider:
                r = sp.to_rdf(graph)
                spc.add(OSLCCore.Service, r.identifier)

        # if self.service_provider_catalog:
        #     for item in self.service_provider_catalog:
        #         spc.add(OSLCCore.serviceProviderCatalog, URIRef(item.about))

        return spc


class ServiceProvider(Resource_):

    def __init__(self, about, types=None, properties=None,
                 description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 publisher=None, service=None, details=None, prefix_definition=None, oauth_configuration=None):
        """
        Initialize ServiceProvider
        """

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                          identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                          creator=creator, subject=subject, created=created, modified=modified, type=type,
                          discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                          relation=relation)
        self.__publisher = publisher
        self.__service = service if service is not None else list()
        self.__details = details if details is not None else OrderedDict()
        self.__prefix_definition = prefix_definition if prefix_definition is not None else list()
        self.__oauth_configuration = oauth_configuration

        self.__created = date.today()
        self.__identifier = identifier if identifier is not None else None

    @property
    def publisher(self):
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher):
        self.__publisher = publisher

    @property
    def service(self):
        return self.__service

    @service.setter
    def service(self, service):
        self.__service = service

    def add_service(self, service):
        self.__service.append(service)

    def to_rdf(self, graph):
        print('sp------')
        if not self.about:
            raise Exception("The title is missing")

        sp = Resource(graph, URIRef(self.about))
        sp.add(RDF.type, URIRef(OSLCCore.serviceProvider))

        if self.title:
            sp.add(DCTERMS.title, Literal(self.title))

        if self.description:
            sp.add(DCTERMS.description, Literal(self.description))

        if self.publisher:
            sp.add(DCTERMS.publisher, URIRef(self.publisher))

        if self.service:
            for s in self.service:
                r = s.to_rdf(graph)
                sp.add(OSLCCore.Service, r.identifier)

        return sp


class Service(Resource_):

    def __init__(self, about, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 domain=None, creation_factory=None, query_capability=None,
                 selection_dialog=None, creation_dialog=None, usage=None):
        """
        Initialize Service
        """

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                          identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                          creator=creator, subject=subject, created=created, modified=modified, type=type,
                          discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                          relation=relation)
        self.__domain = domain if domain is not None else None
        self.__creation_factory = creation_factory if creation_factory is not None else list()
        self.__query_capability = query_capability if query_capability is not None else list()
        self.__selection_dialog = selection_dialog if selection_dialog is not None else list()
        self.__creation_dialog = creation_dialog if creation_dialog is not None else list()
        self.__usage = usage if usage is not None else list()

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, domain):
        self.__domain = domain

    @property
    def creation_factory(self):
        return self.__creation_factory

    @creation_factory.setter
    def creation_factory(self, creation_factory):
        self.__creation_factory = creation_factory

    def add_creation_factory(self, creation_factory):
        self.__creation_factory.append(creation_factory)

    @property
    def query_capability(self):
        return self.__query_capability

    @query_capability.setter
    def query_capability(self, query_capability):
        self.__query_capability = query_capability

    def add_query_capability(self, query_capability):
        self.__query_capability.append(query_capability)

    def to_rdf(self, graph):
        print('s------')
        if not self.about:
            raise Exception("The title is missing")

        s = Resource(graph, URIRef(self.about))
        s.add(RDF.type, URIRef(OSLCCore.service))

        if self.domain:
            s.add(OSLCCore.domain, URIRef(self.domain))

        if self.creation_factory:
            for cf in self.creation_factory:
                r = cf.to_rdf(graph)
                s.add(OSLCCore.CreationFactory, r.identifier)

        if self.query_capability:
            for qc in self.query_capability:
                r = qc.to_rdf(graph)
                s.add(OSLCCore.QueryCapability, r.identifier)

        return s


class QueryCapability(Resource_):

    def __init__(self, about, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 label=None, query_base=None, usage=None, resource_type=None, resource_shape=None):

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                          identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                          creator=creator, subject=subject, created=created, modified=modified, type=type,
                          discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                          relation=relation)

        self.__label = label if label is not None else None
        self.__query_base = query_base if query_base is not None else None
        self.__resource_shape = resource_shape if resource_shape is not None else None
        self.__resource_type = resource_type if resource_type is not None else OrderedDict()
        self.__usage = usage if usage is not None else OrderedDict()


    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def query_base(self):
        return self.__query_base

    @query_base.setter
    def query_base(self, query_base):
        self.__query_base = query_base

    @property
    def resource_shape(self):
        return self.__resource_shape

    @resource_shape.setter
    def resource_shape(self, resource_shape):
        self.__resource_shape = resource_shape

    def add_resource_shape(self, resource_shape):
        self.__resource_shape.update(resource_shape)

    @property
    def resource_type(self):
        return self.__resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self.__resource_type = resource_type

    def add_resource_type(self, resource_type):
        self.__resource_type.update(resource_type)

    @property
    def usage(self):
        return self.__usage

    @usage.setter
    def usage(self, usage):
        self.__usage = usage

    def add_usage(self, usage):
        self.__usage.update(usage)

    def to_rdf(self, graph):
        print('qc------')
        if not self.about:
            raise Exception("The title is missing")

        qc = Resource(graph, URIRef(self.about))
        qc.add(RDF.type, URIRef(OSLCCore.queryCapability))

        if self.title:
            qc.add(DCTERMS.title, Literal(self.title))

        if self.label:
            qc.add(OSLCCore.label, Literal(self.label, datatype=XSD.string))

        if self.query_base:
            qc.add(OSLCCore.queryBase, URIRef(self.query_base))

        if self.resource_shape:
            for item in self.resource_shape.items():
                qc.add(OSLCCore.resourceShape, URIRef(item[1]))

        if self.resource_type:
            for item in self.resource_shape.items():
                qc.add(OSLCCore.resourceType, URIRef(item[1]))

        if self.usage:
            for item in self.usage.items():
                qc.add(OSLCCore.usage, URIRef(item[1]))

        return qc


class CreationFactory(Resource_):

    def __init__(self, about, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 label=None, creation=None, usage=None, resource_type=None, resource_shape=None):

        """
        Creation Factory
        """

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                          identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                          creator=creator, subject=subject, created=created, modified=modified, type=type,
                          discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                          relation=relation,)

        self.__label = label if label is not None else None
        self.__creation = creation if creation is not None else None
        self.__resource_shape = resource_shape if resource_shape is not None else OrderedDict()
        self.__resource_type = resource_type if resource_type is not None else OrderedDict()
        self.__usage = usage if usage is not None else OrderedDict()


    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def creation(self):
        return self.__creation

    @creation.setter
    def creation(self, creation):
        self.__creation = creation

    @property
    def resource_shape(self):
        return self.__resource_shape

    @resource_shape.setter
    def resource_shape(self, resource_shape):
        self.__resource_shape = resource_shape

    def add_resource_shape(self, resource_shape):
        self.__resource_shape.update(resource_shape)

    @property
    def resource_type(self):
        return self.__resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self.__resource_type = resource_type

    def add_resource_type(self, resource_type):
        self.__resource_type.update(resource_type)

    @property
    def usage(self):
        return self.__usage

    @usage.setter
    def usage(self, usage):
        self.__usage = usage

    def add_usage(self, usage):
        self.__usage.update(usage)

    def to_rdf(self, graph):
        print('cf------')
        if not self.about:
            raise Exception("The title is missing")

        cf = Resource(graph, URIRef(self.about))
        cf.add(RDF.type, URIRef(OSLCCore.creationFactory))

        if self.title:
            cf.add(DCTERMS.title, Literal(self.title))

        if self.label:
            cf.add(OSLCCore.label, Literal(self.label, datatype=XSD.string))

        if self.creation:
            cf.add(OSLCCore.creation, URIRef(self.creation))

        if self.resource_shape:
            for item in self.resource_shape.items():
                cf.add(OSLCCore.resourceShape, URIRef(item[1]))

        if self.resource_type:
            for item in self.resource_shape.items():
                cf.add(OSLCCore.resourceType, URIRef(item[1]))

        if self.usage:
            for item in self.usage.items():
                cf.add(OSLCCore.usage, URIRef(item[1]))

        return cf


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
