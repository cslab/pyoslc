from datetime import datetime

from app.api.adapter.manager import CSVImplementation
from app.api.adapter.services.factories import ContactServiceProviderFactory, ContactConfigurationFactory
from pyoslc.resources.jazz import RootService
from pyoslc.resources.models import ServiceProviderCatalog, Publisher


class ServiceProviderCatalogSingleton(object):
    instance = None
    catalog = None
    providers = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ServiceProviderCatalogSingleton, cls).__new__(cls, *args, **kwargs)

            cls.catalog = ServiceProviderCatalog()
            cls.catalog.title = 'Contact Software Platform Service Provider Catalog'
            cls.catalog.description = 'A Service Provider for the Contact Software Platform.'

        return cls.instance

    @classmethod
    def get_catalog(cls, catalog_url):
        if not cls.instance:
            cls()

        cls.catalog.about = catalog_url
        cls.initialize_providers(catalog_url)

        return cls.catalog

    @classmethod
    def get_providers(cls, request):
        cls.initialize_providers(request)
        return cls.providers

    @classmethod
    def get_provider(cls, service_provider_url, identifier):
        if not cls.instance:
            sp = 'provider/{}'.format(identifier)
            catalog_url = service_provider_url.replace(sp, 'catalog')
            cls.get_catalog(catalog_url)

        sp = cls.providers.get(identifier)
        if not sp:
            cls.get_providers(service_provider_url)
            sp = cls.providers.get(identifier)

        return sp

    @classmethod
    def initialize_providers(cls, catalog_url):

        service_providers = CSVImplementation.get_service_provider_info()

        for sp in service_providers:
            identifier = sp.get('id')
            if identifier not in cls.providers.keys():
                name = sp.get('name')
                title = '{}'.format(name)
                description = 'Service Provider for the Contact Software platform service (id: {}; kind: {})'.format(
                    identifier, sp.get('class').__name__)
                publisher = None
                parameters = {'id': sp.get('id')}
                sp = ContactServiceProviderFactory.create_service_provider(catalog_url, title, description, publisher,
                                                                           parameters)
                cls.register_service_provider(catalog_url, identifier, sp)

        return cls.providers

    @classmethod
    def register_service_provider(cls, sp_uri, identifier, provider):

        uri = cls.construct_service_provider_uri(identifier)

        domains = cls.get_domains(provider)

        provider.about = uri
        provider.identifier = identifier
        provider.created = datetime.now()
        provider.details = uri

        cls.catalog.add_service_provider(provider)

        for d in domains:
            cls.catalog.add_domain(d)

        cls.providers[identifier] = provider

        return provider

    @classmethod
    def construct_service_provider_uri(cls, identifier):
        uri = cls.catalog.about
        uri = uri.replace('catalog', 'provider') + '/' + identifier
        return uri

    @classmethod
    def get_domains(cls, provider):
        domains = set()

        for s in provider.service:
            domains.add(s.domain)

        return domains


class RootServiceSingleton(object):
    instance = None
    root_service = None
    providers = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(RootServiceSingleton, cls).__new__(cls, *args, **kwargs)

            cls.root_service = RootService()
            cls.root_service.title = 'Root services for connecting with Jazz'
            cls.root_service.description = 'Services available on the PyOSLC.'

        return cls.instance

    @classmethod
    def get_root_service(cls, rootservices_url):
        if not cls.instance:
            cls()

        cls.root_service.about = rootservices_url

        return cls.root_service


class PublisherSingleton(object):
    instance = None
    publisher = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(PublisherSingleton, cls).__new__(cls, *args, **kwargs)

            cls.publisher = Publisher()
            cls.publisher.title = 'PyOSLC'
            cls.publisher.description = 'Implementer of the PyOSLC adapter.'

        return cls.instance

    @classmethod
    def get_publisher(cls, publisher_url):
        if not cls.instance:
            cls()

        publisher_url = publisher_url.replace('catalog', 'publisher')
        cls.publisher.about = publisher_url
        cls.publisher.identifier = 'Publisher-1'

        return cls.publisher


class ConfigurationManagementSingleton(object):
    instance = None
    catalog = None
    components = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ConfigurationManagementSingleton, cls).__new__(cls, *args, **kwargs)

            cls.catalog = ServiceProviderCatalog()
            cls.catalog.title = 'Configuration Management'
            cls.catalog.description = 'Configuration Services Provided'

    @classmethod
    def get_catalog(cls, catalog_url):
        if not cls.instance:
            cls()

        cls.catalog.about = catalog_url
        cls.initialize_components(catalog_url)

        return cls.catalog

    @classmethod
    def initialize_components(cls, catalog_url):

        components = CSVImplementation.get_configuration_info()

        for component in components:
            identifier = component.get('id')
            if identifier not in cls.components.keys():
                name = component.get('name')
                description = 'Configuration Service for: {}'.format(name)
                publisher = PublisherSingleton.get_publisher(catalog_url)
                parameters = {'id': identifier}
                comp = ContactConfigurationFactory.create_components(catalog_url, name, description, publisher,
                                                                     parameters)
                cls.register_component(catalog_url, identifier, comp)

        return cls.components

    @classmethod
    def register_component(cls, uri, identifier, component):

        domains = cls.get_domains(component)

        uri = uri.replace('catalog', 'components') + '/' + identifier
        component.about = uri
        component.identifier = identifier
        component.created = datetime.now()
        component.details = uri

        cls.catalog.add_service_provider(component)

        for d in domains:
            cls.catalog.add_domain(d)

        cls.components[identifier] = component

        return component

    @classmethod
    def get_components(cls, url):
        cls.initialize_components(url)
        return cls.components

    @classmethod
    def get_component(cls, component_url, identifier):
        if not cls.instance:
            comp = 'components/{}'.format(identifier)
            catalog_url = component_url.replace(comp, 'catalog')
            cls.get_catalog(catalog_url)

        component = cls.components.get(identifier)
        if not component:
            cls.get_components(component_url)
            component = cls.components.get(identifier)

        return component

    @classmethod
    def get_domains(cls, provider):
        domains = set()

        for s in provider.service:
            domains.add(s.domain)

        return domains
