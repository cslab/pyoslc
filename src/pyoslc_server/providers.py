from datetime import datetime

from pyoslc.resources.models import ServiceProviderCatalog
from pyoslc_server.factories import ContactServiceProviderFactory


class ServiceProviderCatalogSingleton(object):
    instance = None
    catalog = None
    providers = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ServiceProviderCatalogSingleton, cls).__new__(cls, *args, **kwargs)
            cls.catalog = ServiceProviderCatalog()

        return cls.instance

    @classmethod
    def get_catalog(cls, catalog_url, title=None, description=None, providers=None):
        if not cls.instance:
            cls()

        cls.catalog.about = catalog_url
        cls.catalog.title = title if title else 'Service Provider Catalog'
        cls.catalog.description = description if description else 'Service Provider Catalog for the PyOSLC application.'

        cls.initialize_providers(catalog_url, providers if providers else [])

        return cls.catalog

    @classmethod
    def get_providers(cls, request, providers=None):
        cls.initialize_providers(request, providers=providers)
        return cls.providers

    @classmethod
    def get_provider(cls, service_provider_url, identifier, title=None, description=None, providers=None):
        if not cls.instance:
            sp = 'provider/{}'.format(identifier)
            catalog_url = service_provider_url.replace(sp, 'catalog')
            cls.get_catalog(catalog_url, providers=providers)

        sp = cls.providers.get(identifier)
        if not sp:
            cls.get_providers(service_provider_url, providers=providers)
            sp = cls.providers.get(identifier)

        return sp

    @classmethod
    def initialize_providers(cls, catalog_url, providers=None):

        service_providers = providers  # CSVImplementation.get_service_provider_info()

        for sp in service_providers:
            identifier = sp.get('id')
            if identifier not in list(cls.providers.keys()):
                name = sp.get('name')
                title = '{}'.format(name)
                description = 'Service Provider for the Contact Software platform service (id: {})'.format(
                    identifier)
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
