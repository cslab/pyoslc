from datetime import datetime

from rdflib.namespace import DCTERMS, RDF, RDFS

from pyoslc.model.factory import ServiceProviderFactory
from pyoslc.resource import (ServiceProviderCatalog, PrefixDefinition)
from pyoslc.vocabulary import OSLCCore, OSLCData, OSLC_AM, OSLC_CM, OSLC_RM
from webservice.api.oslc.adapter.specs import DataSpecsProjectA


class ServiceProviderCatalogSingleton(object):

    instance = None
    catalog = None
    providers = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ServiceProviderCatalogSingleton, cls).__new__(cls, *args, **kwargs)

            cls.catalog = ServiceProviderCatalog()
            cls.catalog.title = 'Contact Software Platform Service Provider Catalog'
            cls.catalog.description = 'A Service Provider Catalog describing the service providers for the Contact Software Platform.'

        return cls.instance

    def __init__(self):
        pass

    @classmethod
    def get_catalog(cls, catalog_url):
        if not cls.instance:
            cls()

        cls.catalog.about = catalog_url
        cls.initialize_providers(catalog_url)

        return cls.catalog

    @classmethod
    def get_provider(cls, request, identifier):
        if not cls.instance:
            cls()

        sp = cls.providers.get(identifier)
        if not sp:
            cls.get_providers(request.base_url)
            sp = cls.providers.get(identifier)

        return sp

    @classmethod
    def initialize_providers(cls, catalog_url):
        service_providers = []  # Get information from the external container
        # GET Request for those applications

        service_providers = [{'id': 'PA', 'name': 'Project A'}]

        for sp in service_providers:
            identifier = sp.get('id')
            if identifier not in cls.providers.keys():
                name = sp.get('name')
                title = 'Service Provider {}'.format(name)
                description = 'Service Provider for the Contact Software platform service (id: {}; kind: {})'.format(identifier, 'Specification')
                publisher = None
                parameters = {'id': sp.get('id')}
                sp = ContactServiceProviderFactory.create_provider(catalog_url, title, description, publisher, parameters)
                cls.register_provider(catalog_url, identifier, sp)

        return cls.providers

    @classmethod
    def get_providers(cls, request):
        cls.initialize_providers(request)
        return cls.providers

    @classmethod
    def register_provider(cls, sp_uri, identifier, provider):

        domains = cls.get_domains(provider)

        provider.about = sp_uri
        provider.identifier = identifier
        provider.created = datetime.now()
        provider.details = sp_uri

        cls.catalog.add_service_provider(provider)

        for d in domains:
            cls.catalog.add_domain(d)

        cls.providers[identifier] = provider

        return provider

    @classmethod
    def get_domains(cls, provider):
        domains = set()

        for s in provider.service:
            domains.add(s.domain)

        return domains


class ContactServiceProviderFactory(object):

    @classmethod
    def create_provider(cls, base_uri, title, description, publisher, parameters):
        classes = [DataSpecsProjectA]
        sp = ServiceProviderFactory.create(base_uri, 'project', title, description, publisher, classes, parameters)

        sp.add_detail(base_uri)

        prefix_definitions = list()
        prefix_definitions.append(PrefixDefinition(prefix='dcterms', prefix_base=DCTERMS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc', prefix_base=OSLCCore))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_data', prefix_base=OSLCData))
        prefix_definitions.append(PrefixDefinition(prefix='rdf', prefix_base=RDF))
        prefix_definitions.append(PrefixDefinition(prefix='rdfs', prefix_base=RDFS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_am', prefix_base=OSLC_AM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_cm', prefix_base=OSLC_CM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_rm', prefix_base=OSLC_RM))

        sp.prefix_definition = prefix_definitions

        return sp
