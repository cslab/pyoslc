import hashlib
from datetime import date

from rdflib import URIRef, Literal, RDF, XSD, BNode
from rdflib.namespace import DCTERMS
from rdflib.resource import Resource

from pyoslc.helpers import build_uri
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_PROCESS
from pyoslc.vocabularies.jfs import JFS

default_uri = 'http://examples.com/'


class AbstractResource(object):
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

    def add_extended_property(self, extended_property):
        if extended_property:
            self.__extended_properties.append(extended_property)

    def to_rdf(self, graph):
        if not self.about:
            raise Exception("The about property is missing")

    def digestion(self):
        state = self.__about
        for attr in self.__dict__.keys():
            value = getattr(self, attr)
            if value:
                print(value)
                if isinstance(value, set):
                    if len(value) > 0:
                        for v in value:
                            if v != '':
                                state += v
                elif isinstance(value, dict):
                    for k in value:
                        state += value[k]
                elif isinstance(value, list):
                    for k in value:
                        state += k
                else:
                    state += value

        dig = hashlib.sha256()
        dig.update(state)
        return str(dig.hexdigest())


class BaseResource(AbstractResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None):
        """
        Initialize the generic resource with the about property
        """

        super(BaseResource, self).__init__(about, types, properties)
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

    @property
    def relation(self):
        return self.__relation

    @relation.setter
    def relation(self, relation):
        self.__relation = relation

    def to_rdf(self, graph):
        super(BaseResource, self).to_rdf(graph)


class ServiceProviderCatalog(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, uri=None, publisher=None,
                 domain=None, service_provider_catalog=None, oauth_configuration=None):

        super(ServiceProviderCatalog, self).__init__(about, types, properties, description, identifier, short_title,
                                                     title, contributor, creator, subject, created, modified, type,
                                                     discussed_by, instance_shape, service_provider, relation)

        self.__uri = uri if uri is not None else build_uri(default_uri, 'serviceProviderCatalog')
        self.__publisher = publisher
        self.__domain = domain if domain is not None else list()
        self.__service_provider_catalog = service_provider_catalog if service_provider_catalog is not None else set()
        self.__oauth_configuration = oauth_configuration

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
        self.__domain.append(domain)

    @property
    def service_provider_catalog(self):
        return self.__service_provider_catalog

    @service_provider_catalog.setter
    def service_provider_catalog(self, service_provider_catalog):
        self.__service_provider_catalog = service_provider_catalog

    def add_service_provider_catalog(self, service_provider_catalog):
        self.__service_provider_catalog.add(service_provider_catalog)

    @property
    def oauth_configuration(self):
        return self.__oauth_configuration

    @oauth_configuration.setter
    def oauth_configuration(self, oauth_configuration):
        self.__oauth_configuration = oauth_configuration

    def to_rdf(self, graph):
        super(ServiceProviderCatalog, self).to_rdf(graph)

        spc = Resource(graph, URIRef(self.about))
        spc.add(RDF.type, OSLC.ServiceProviderCatalog)

        if self.title:
            spc.add(DCTERMS.title, Literal(self.title))

        if self.description:
            spc.add(DCTERMS.description, Literal(self.description))

        if self.publisher:
            spc.add(DCTERMS.publisher, URIRef(self.publisher.about))

        if self.domain:
            for item in self.domain:
                spc.add(OSLC.domain, URIRef(item))

        if self.service_provider:
            for sp in self.service_provider:
                r = sp.to_rdf(graph)
                spc.add(OSLC.serviceProvider, r)

        if self.service_provider_catalog:
            for item in self.service_provider_catalog:
                spc.add(OSLC.serviceProviderCatalog, URIRef(item.about))

        if self.oauth_configuration:
            spc.add(OSLC.oauthConfiguration, URIRef(self.oauth_configuration.about))

        spc.add(OSLC.domain, JAZZ_PROCESS.uri)

        return spc


class ServiceProvider(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, publisher=None,
                 service=None, details=None, prefix_definition=None, oauth_configuration=None):
        """
        Initialize ServiceProvider
        """
        super(ServiceProvider, self).__init__(about, types, properties, description, identifier, short_title, title,
                                              contributor, creator, subject, created, modified, type, discussed_by,
                                              instance_shape, service_provider, relation)
        self.__publisher = publisher
        self.__service = service if service is not None else list()
        self.__details = details if details is not None else list()
        self.__prefix_definition = prefix_definition if prefix_definition is not None else list()
        self.__oauth_configuration = oauth_configuration if oauth_configuration is not None else None

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

    @property
    def details(self):
        return self.__details

    @details.setter
    def details(self, details):
        self.__details = details

    def add_detail(self, detail):
        self.__details.append(detail)

    @property
    def prefix_definition(self):
        return self.__prefix_definition

    @prefix_definition.setter
    def prefix_definition(self, prefix_definition):
        self.__prefix_definition = prefix_definition

    def add_prefix_definition(self, prefix_definition):
        self.__prefix_definition.append(prefix_definition)

    @property
    def oauth_configuration(self):
        return self.__oauth_configuration

    @oauth_configuration.setter
    def oauth_configuration(self, oauth_configuration):
        self.__oauth_configuration = oauth_configuration

    def to_rdf(self, graph):
        super(ServiceProvider, self).to_rdf(graph)

        uri = self.about if self.about.__contains__(self.identifier) else self.about + '/{}'.format(self.identifier) if self.identifier else ''

        sp = Resource(graph, URIRef(uri))
        sp.add(RDF.type, OSLC.ServiceProvider)

        if self.identifier:
            sp.add(DCTERMS.identifier, Literal(self.identifier, datatype=XSD.string))

        if self.title:
            sp.add(DCTERMS.title, Literal(self.title, datatype=XSD.Literal))

        if self.description:
            sp.add(DCTERMS.description, Literal(self.description))

        if self.publisher:
            sp.add(DCTERMS.publisher, URIRef(self.publisher.about))

        if self.service:
            for s in self.service:
                r = s.to_rdf(graph)
                sp.add(OSLC.service, r)

        if self.details:
            sp.add(OSLC.details, URIRef(self.details))

        if self.oauth_configuration:
            sp.add(OSLC.oauthConfiguration, URIRef(self.oauth_configuration.about))

        if self.prefix_definition:
            for pd in self.prefix_definition:
                r = pd.to_rdf(graph)
                sp.add(OSLC.prefixDefinition, r)

        sp.add(JAZZ_PROCESS.supportContributionsToLinkIndexProvider, Literal(True, datatype=XSD.boolean))
        sp.add(JAZZ_PROCESS.supportLinkDiscoveryViaLinkIndexProvider, Literal(True, datatype=XSD.boolean))
        sp.add(JAZZ_PROCESS.supportOSLCSimpleQuery, Literal(True, datatype=XSD.boolean))
        sp.add(JAZZ_PROCESS.globalConfigurationAware, Literal('yes', datatype=XSD.String))

        return sp


class Service(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, domain=None,
                 creation_factory=None, query_capability=None, selection_dialog=None, creation_dialog=None, usage=None):
        """
        Initialize Service
        """
        super(Service, self).__init__(about, types, properties, description, identifier, short_title, title,
                                      contributor, creator, subject, created, modified, type, discussed_by,
                                      instance_shape, service_provider, relation)

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

    @property
    def selection_dialog(self):
        return self.__selection_dialog

    @selection_dialog.setter
    def selection_dialog(self, selection_dialog):
        self.__selection_dialog = selection_dialog

    def add_selection_dialog(self, selection_dialog):
        self.__selection_dialog.append(selection_dialog)

    @property
    def creation_dialog(self):
        return self.__creation_dialog

    @creation_dialog.setter
    def creation_dialog(self, creation_dialog):
        self.__creation_dialog = creation_dialog

    def add_creation_dialog(self, creation_dialog):
        self.__creation_dialog.append(creation_dialog)

    def to_rdf(self, graph):
        super(Service, self).to_rdf(graph)

        uri = self.about if self.about.__contains__(self.identifier) else self.about + '/{}'.format(
            self.identifier) if self.identifier else ''

        s = Resource(graph, BNode())
        s.add(RDF.type, OSLC.Service)

        if self.title:
            s.add(DCTERMS.title, Literal(self.title, datatype=XSD.Literal))

        if self.description:
            s.add(DCTERMS.description, Literal(self.description, datatype=XSD.Literal))

        if self.domain:
            s.add(OSLC.domain, URIRef(self.domain))

        if self.creation_factory:
            for cf in self.creation_factory:
                r = cf.to_rdf(graph)
                s.add(OSLC.creationFactory, r)

        if self.query_capability:
            for qc in self.query_capability:
                r = qc.to_rdf(graph)
                s.add(OSLC.queryCapability, r)

        if self.selection_dialog:
            for sd in self.selection_dialog:
                r = sd.to_rdf(graph)
                s.add(OSLC.selectionDialog, r)

        if self.creation_dialog:
            for cd in self.creation_dialog:
                r = cd.to_rdf(graph)
                s.add(OSLC.creationDialog, r.identifier)

        return s


class QueryCapability(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, label=None,
                 query_base=None, usage=None, resource_type=None, resource_shape=None):

        super(QueryCapability, self).__init__(about, types, properties, description, identifier, short_title, title,
                                              contributor, creator, subject, created, modified, type, discussed_by,
                                              instance_shape, service_provider, relation)

        self.__label = label if label is not None else None
        self.__query_base = query_base if query_base is not None else None
        self.__resource_shape = resource_shape if resource_shape is not None else None
        self.__resource_type = resource_type if resource_type is not None else list()
        self.__usage = usage if usage is not None else list()

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
        self.__resource_type.append(resource_type)

    @property
    def usage(self):
        return self.__usage

    @usage.setter
    def usage(self, usage):
        self.__usage = usage

    def add_usage(self, usage):
        self.__usage.update(usage)

    def to_rdf(self, graph):
        super(QueryCapability, self).to_rdf(graph)

        qc = Resource(graph, BNode())
        qc.add(RDF.type, OSLC.QueryCapability)

        if self.title:
            qc.add(DCTERMS.title, Literal(self.title))

        if self.label:
            qc.add(OSLC.label, Literal(self.label, datatype=XSD.string))
        else:
            qc.add(OSLC.label, Literal(self.title, datatype=XSD.string))

        if self.query_base:
            qc.add(OSLC.queryBase, URIRef(self.query_base))

        if self.resource_shape:
            qc.add(OSLC.resourceShape, URIRef(self.resource_shape))

        if self.resource_type:
            for item in self.resource_type:
                qc.add(OSLC.resourceType, URIRef(item))

        if self.usage:
            for item in self.usage.items():
                qc.add(OSLC.usage, URIRef(item[1]))

        return qc


class CreationFactory(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, label=None,
                 creation=None, usage=None, resource_type=None, resource_shape=None):

        """
        Creation Factory
        """
        super(CreationFactory, self).__init__(about, types, properties, description, identifier, short_title, title,
                                              contributor, creator, subject, created, modified, type, discussed_by,
                                              instance_shape, service_provider, relation)

        self.__label = label if label is not None else None
        self.__creation = creation if creation is not None else None
        self.__resource_shape = resource_shape if resource_shape is not None else list()
        self.__resource_type = resource_type if resource_type is not None else list()
        self.__usage = usage if usage is not None else list()

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
        self.__resource_shape.append(resource_shape)

    @property
    def resource_type(self):
        return self.__resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self.__resource_type = resource_type

    def add_resource_type(self, resource_type):
        self.__resource_type.append(resource_type)

    @property
    def usage(self):
        return self.__usage

    @usage.setter
    def usage(self, usage):
        self.__usage = usage

    def add_usage(self, usage):
        self.__usage.update(usage)

    def to_rdf(self, graph):
        super(CreationFactory, self).to_rdf(graph)

        cf = Resource(graph, BNode())
        cf.add(RDF.type, OSLC.CreationFactory)

        if self.title:
            cf.add(DCTERMS.title, Literal(self.title))

        if self.label:
            cf.add(OSLC.label, Literal(self.label, datatype=XSD.string))

        if self.creation:
            cf.add(OSLC.creation, URIRef(self.creation))

        if self.resource_shape:
            for item in self.resource_shape:
                cf.add(OSLC.resourceShape, URIRef(item))

        if self.resource_type:
            for item in self.resource_type:
                cf.add(OSLC.resourceType, URIRef(item))

        if self.usage:
            for item in self.usage:
                cf.add(OSLC.usage, URIRef(item))

        return cf


class Dialog(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, dialog=None,
                 hint_height=None, hint_width=None, label=None, usage=None, resource_type=None):

        super(Dialog, self).__init__(about, types, properties, description, identifier, short_title, title, contributor,
                                     creator, subject, created, modified, type, discussed_by, instance_shape,
                                     service_provider, relation)

        self.__dialog = dialog if dialog is not None else None
        self.__hint_height = hint_height if hint_height is not None else None
        self.__hint_width = hint_width if hint_width is not None else None
        self.__label = label if label is not None else None
        self.__resource_type = resource_type if resource_type is not None else list()
        self.__usage = usage if usage is not None else list()

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def dialog(self):
        return self.__dialog

    @dialog.setter
    def dialog(self, dialog):
        self.__dialog = dialog

    @property
    def hint_height(self):
        return self.__hint_height

    @hint_height.setter
    def hint_height(self, hint_height):
        self.__hint_height = hint_height

    @property
    def hint_width(self):
        return self.__hint_width

    @hint_width.setter
    def hint_width(self, hint_width):
        self.__hint_width = hint_width

    @property
    def resource_type(self):
        return self.__resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self.__resource_type = resource_type

    def add_resource_type(self, resource_type):
        self.__resource_type.append(resource_type)

    @property
    def usage(self):
        return self.__usage

    @usage.setter
    def usage(self, usage):
        self.__usage = usage

    def add_usage(self, usage):
        self.__usage.append(usage)

    def to_rdf(self, graph):
        super(Dialog, self).to_rdf(graph)

        d = Resource(graph, BNode())
        d.add(RDF.type, OSLC.Dialog)

        if self.label:
            d.add(OSLC.label, Literal(self.label))

        if self.title:
            d.add(DCTERMS.title, Literal(self.title))

        if self.hint_width:
            d.add(DCTERMS.hintWidth, Literal(self.hint_width))

        if self.hint_height:
            d.add(DCTERMS.hintHeight, Literal(self.hint_height))

        if self.dialog:
            d.add(OSLC.dialog, URIRef(self.dialog))

        if self.resource_type:
            for item in self.resource_type:
                d.add(OSLC.resourceType, URIRef(item))

        if self.usage:
            for item in self.usage:
                d.add(OSLC.usage, URIRef(item))

        return d


class PrefixDefinition(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, prefix=None,
                 prefix_base=None):

        super(PrefixDefinition, self).__init__(about, types, properties, description, identifier, short_title, title,
                                               contributor, creator, subject, created, modified, type, discussed_by,
                                               instance_shape, service_provider, relation)
        self.__prefix = prefix if prefix is not None else None
        self.__prefix_base = prefix_base if prefix_base is not None else None

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, prefix):
        self.__prefix = prefix

    @property
    def prefix_base(self):
        return self.__prefix_base

    @prefix_base.setter
    def prefix_base(self, prefix_base):
        self.__prefix_base = prefix_base

    def to_rdf(self, graph):
        super(PrefixDefinition, self).to_rdf(graph)

        pd = Resource(graph, BNode())
        pd.add(RDF.type, OSLC.PrefixDefinition)

        if self.prefix:
            pd.add(OSLC.prefix, Literal(self.prefix))

        if self.prefix_base:
            pd.add(OSLC.prefixBase, URIRef(self.prefix_base.uri))

        return pd


class Publisher(AbstractResource):

    def __init__(self, about=None, types=None, properties=None, icon=None, identifier=None, label=None, title=None):
        """
        Resource for publisher
        """

        super(Publisher, self).__init__(about, types, properties)
        self.__icon = icon if icon is not None else None
        self.__identifier = identifier if identifier is not None else None
        self.__label = label if label is not None else None
        self.__title = title if title is not None else None

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, icon):
        self.__icon = icon

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

    def to_rdf(self, graph):
        super(Publisher, self).to_rdf(graph)

        graph.bind('jfs', JFS)

        p = Resource(graph, URIRef(self.about))
        p.add(RDF.type, DCTERMS.Publisher)

        if self.title:
            p.add(DCTERMS.title, Literal(self.title))

        if self.label:
            p.add(OSLC.label, Literal(self.label))

        if self.identifier:
            p.add(DCTERMS.identifier, Literal(self.identifier))

        if self.icon:
            p.add(OSLC.icon, URIRef(self.icon))

        p.add(JFS.nonLocalizedTitle, Literal('Configuration'))
        p.add(JFS.version, Literal('7.0'))
        p.add(JFS.instanceName, Literal('/pyoslc'))

        return p


class OAuthConfiguration(BaseResource):

    def __init__(self, about, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, authorization_uri=None,
                 oauth_access_token_uri=None, oauth_request_token_uri=None):
        """
        private URI authorizationURI;
        private URI oauthAccessTokenURI;
        private URI oauthRequestTokenURI;
        """

        super(OAuthConfiguration, self).__init__(about, types, properties, description, identifier, short_title, title,
                                                 contributor, creator, subject, created, modified, type, discussed_by,
                                                 instance_shape, service_provider, relation)
        self.__authorization_uri = authorization_uri if authorization_uri is not None else None
        self.__oauth_access_token_uri = oauth_access_token_uri if oauth_access_token_uri is not None else None
        self.__oauth_request_token_uri = oauth_request_token_uri if oauth_access_token_uri is not None else None

    @property
    def authorization_uri(self):
        return self.__authorization_uri

    @authorization_uri.setter
    def authorization_uri(self, authorization_uri):
        self.__authorization_uri = authorization_uri

    @property
    def oauth_access_token_uri(self):
        return self.__oauth_access_token_uri

    @oauth_access_token_uri.setter
    def oauth_access_token_uri(self, oauth_access_token_uri):
        self.__oauth_access_token_uri = oauth_access_token_uri

    @property
    def oauth_request_token_uri(self):
        return self.__oauth_request_token_uri

    @oauth_request_token_uri.setter
    def oauth_request_token_uri(self, oauth_request_token_uri):
        self.__oauth_request_token_uri = oauth_request_token_uri

    def to_rdf(self, graph):
        if not self.about:
            raise Exception("The title is missing")

        oac = Resource(graph, URIRef(self.about))
        oac.add(RDF.type, URIRef(OSLC.oauthConfiguration))

        if self.authorization_uri:
            oac.add(OSLC.authorizationURI, URIRef(self.authorization_uri))

        if self.oauth_access_token_uri:
            oac.add(OSLC.oauthAccessTokenURI, URIRef(self.oauth_access_token_uri))

        if self.oauth_request_token_uri:
            oac.add(OSLC.oauthRequestTokenURI, URIRef(self.oauth_request_token_uri))

        return oac


class FilteredResource(AbstractResource):

    def __init__(self, about, types, properties, resource):
        super(FilteredResource, self).__init__(about, types, properties)
        self.__resource = resource if resource is not None else None


class ResponseInfo(FilteredResource):

    def __init__(self, about=None, types=None, properties=None, resource=None,
                 total_count=None, next_page=None, container=None):
        super(ResponseInfo, self).__init__(about, types, properties, resource)
        self.__total_count = total_count if total_count is not None else 0
        self.__next_page = next_page if next_page is not None else None
        self.__container = container if container is not None else None

    def to_rdf(self, graph):
        super(ResponseInfo, self).to_rdf(graph)

        ri = Resource(graph, BNode())
        ri.add(RDF.type, OSLC.ResponseInfo)

        return ri


class Preview(AbstractResource):

    def __init__(self, about=None, types=None, properties=None, document=None,
                 hint_height=None, hint_width=None, initial_height=None):
        super(Preview, self).__init__(about, types, properties)

        self.__document = document if document is not None else None
        self.__hint_height = hint_height if hint_height is not None else None
        self.__hint_width = hint_width if hint_width is not None else None
        self.__initial_height = initial_height if initial_height is not None else None

    @property
    def document(self):
        return self.__document

    @document.setter
    def document(self, document):
        self.__document = document

    @property
    def hint_height(self):
        return self.__hint_height

    @hint_height.setter
    def hint_height(self, hint_height):
        self.__hint_height = hint_height

    @property
    def hint_width(self):
        return self.__hint_width

    @hint_width.setter
    def hint_width(self, hint_width):
        self.__hint_width = hint_width

    @property
    def initial_height(self):
        return self.__initial_height

    @initial_height.setter
    def initial_height(self, initial_height):
        self.__initial_height = initial_height

    def to_rdf(self, graph):
        super(Preview, self).to_rdf(graph)

        p = Resource(graph, BNode())
        p.add(RDF.type, OSLC.Preview)

        if self.document:
            p.add(OSLC.document, URIRef(self.document))

        if self.hint_height:
            p.add(OSLC.hintHeight, Literal(self.hint_height, datatype=XSD.string))

        if self.hint_width:
            p.add(OSLC.hintWidth, Literal(self.hint_width, datatype=XSD.string))

        if self.initial_height:
            p.add(OSLC.initialHeight, Literal(self.initial_height, datatype=XSD.string))

        return p


class Compact(AbstractResource):

    def __init__(self, about=None, types=None, properties=None,
                 icon=None, large_preview=None, short_title=None,
                 small_preview=None, title=None):
        super(Compact, self).__init__(about, types, properties)
        self.__icon = icon if icon is not None else None
        self.__large_preview = large_preview if large_preview is not None else Preview(about, types, properties)
        self.__short_title = short_title if short_title is not None else ''
        self.__small_preview = small_preview if small_preview is not None else Preview(about, types, properties)
        self.__title = title if title is not None else Preview(about, types, properties)

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, icon):
        self.__icon = icon

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
        self.__title = title

    @property
    def small_preview(self):
        return self.__small_preview

    @small_preview.setter
    def small_preview(self, small_preview):
        self.__small_preview = small_preview

    @property
    def large_preview(self):
        return self.__large_preview

    @large_preview.setter
    def large_preview(self, large_preview):
        self.__large_preview = large_preview

    def to_rdf(self, graph):
        super(Compact, self).to_rdf(graph)

        uri = self.about if self.about else ''

        d = Resource(graph, URIRef(uri))
        d.add(RDF.type, OSLC.Compact)

        if self.icon:
            d.add(OSLC.icon, URIRef(self.icon))

        if self.short_title:
            d.add(DCTERMS.shortTitle, Literal(self.short_title, datatype=XSD.string))

        if self.title:
            d.add(DCTERMS.title, Literal(self.title, datatype=XSD.string ))

        if self.small_preview:
            sp = self.small_preview.to_rdf(graph)
            d.add(OSLC.smallPreview, sp)

        if self.large_preview:
            sp = self.large_preview.to_rdf(graph)
            d.add(OSLC.largePreview, sp)

        return d


"""

class ResourceShape(BaseResource):
    def __init__(self, about, types, properties,
                 describes, title):
        BaseResource.__init__(self, about, types, properties)

        self.__describes = describes if describes is not None else OrderedDict()
        self.__properties = properties if properties is not None else OrderedDict()
        self.__title = title if title is not None else None

    @property
    def describes(self):
        return self.__describes

    @describes.setter
    def describes(self, describes):
        self.__describes = describes

    def add_describe(self, describe):
        if describe:
            self.__describes.append(describe)

    @property
    def properties(self):
        return self.__properties

    @properties.setter
    def properties(self, properties):
        self.__properties = properties

    def add_propertie(self, propertie):
        if propertie:
            self.__properties.append(propertie)

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title






"""

