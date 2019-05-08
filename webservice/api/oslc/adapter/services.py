import inspect
import urllib
from datetime import datetime
from types import MethodType

from pyoslc.resource import (QueryCapability, Service, ServiceProvider,
                             ServiceProviderCatalog, CreationFactory, Dialog)
# from webservice.api.oslc.adapter.endpoints import IoTPlatformService
from webservice.api.oslc.adapter.specs import DataSpecsProjectA, DataSpecsProjectB


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

        service_providers = [{'id': 'PA', 'name': 'Project A'}, {'id': 'PB', 'name': 'Project B'}]

        for sp in service_providers:
            identifier = sp.get('id')
            if identifier not in cls.providers.keys():
                name = sp.get('name')
                title = 'Service Provider {}'.format(name)
                description = 'Service Provider for the Contact Software platform service (id: {}; kind: {})'.format(identifier, 'Specification')
                publisher = None
                parameters = {'id': sp.get('id')}
                sp = ServiceProviderFactory.create_provider(catalog_url, title, description, publisher, parameters)
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

    @classmethod
    def get_domains(cls, provider):
        domains = set()

        for s in provider.service:
            domains.add(s.domain)

        print('Domain List: {}'.format(domains))

        return domains


class ServiceProviderFactory(object):

    @classmethod
    def create_provider(cls, base_uri, title, description, publisher, parameters):
        classes = [DataSpecsProjectA, DataSpecsProjectB]
        sp = SPF.create(base_uri, 'aaa', title, description, publisher, classes, parameters)
        return sp


class SPF(object):

    @classmethod
    def create(cls, base_uri, uri, title, description, publisher, classes, parameters):
        return cls.initialize(ServiceProvider(), base_uri, uri, title, description, publisher, classes, parameters)

    @classmethod
    def initialize(cls, sp, base_uri, uri, title, description, publisher, classes, parameters):
        sp.title = title
        sp.description = description
        sp.publisher = publisher

        services = dict()

        for klass in classes:
            if not services.has_key(klass.domain):
                service = Service(domain=klass.domain)
                services[klass.domain] = service
            
                cls.handle_resource_class(base_uri, uri, klass, service, parameters)
        
        for s in services.values():
            print(s)
            sp.add_service(s)
        
        return sp
    
    @classmethod
    def handle_resource_class(cls, base_uri, generic_base_uri, klass, service, parameters):

        for item in inspect.classify_class_attrs(klass):
            if item.kind.__contains__('method') and item.defining_class == klass:

                resource_shape = None
                if item.name is 'query_capability':
                    query_capability = cls.create_query_capability(base_uri, item.object, parameters)
                    service.add_query_capability(query_capability)
                    resource_shape = query_capability.resource_shape

                if item.name is 'dialog':
                    annotation = item.name
                    dialog = cls.create_selection_dialog(base_uri, generic_base_uri, item.object, annotation, resource_shape, parameters)
                    service.add_selection_dialog(dialog)

                if item.name is 'creation_factory':
                    service.add_creation_factory(cls.create_creation_factory(base_uri, item.object, parameters))

        return True
    
    @classmethod
    def create_query_capability(cls, base_uri, method, parameters):

        attributes = method.__func__()

        title = attributes.get('title', 'OSLC Query Capability')
        label = attributes.get('label', 'Query Capability Service')
        resource_shape = attributes.get('resource_shape', '')
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        url = ''
        for k, v in parameters.items():
            url += '/' + k + '/' + v

        query = base_uri + url

        query_capability = QueryCapability(title=title, query_base=query)
        if label:
            query_capability.label = label
        
        if resource_shape:
            query_capability.resource_shape = resource_shape
        
        for rt in resource_type:
            query_capability.add_resource_type(rt)
        
        for u in usages:
            query_capability.add_usage(u)
        
        return query_capability

    @classmethod
    def create_creation_factory(cls, base_uri, method, parameters):
        return cls.creation_factory(base_uri, method, parameters, 'sa', 'sd')

    @classmethod
    def creation_factory(cls, base_uri, method, parameters, path, annotation):

        attributes = method.__func__()

        title = attributes.get('title', None)

        url = ''
        for k, v in parameters.items():
            url += '/' + k + '/' + v

        creation = base_uri + url

        creation_factory = CreationFactory(title=title, creation=creation)

        return creation_factory

    @classmethod
    def create_selection_dialog(cls, base_uri, generic_base_uri, method, annotation, resource_shape, parameters):
        return cls.create_dialog(base_uri, generic_base_uri, 'Selection', 'query_base', method, annotation, resource_shape, parameters)

    @classmethod
    def create_dialog(cls, base_uri, generic_base_uri, dialog_type, parameter_name, method, annotation, resource_shape, parameters):
        attributes = method.__func__()

        title = attributes.get('title', 'OSLC Dialog Resource Shape')
        label = attributes.get('label', 'OSLC Dialog for Service')
        dialog_uri = attributes.get('uri', None)
        hint_width = attributes.get('hint_width', 100)
        hint_height = attributes.get('hint_height', 100)
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        dialog = Dialog(title=title, dialog=dialog_uri)

        if label:
            dialog.label = label

        if hint_width:
            dialog.hint_width = hint_width

        if hint_height:
            dialog.hint_height = hint_height

        for rt in resource_type:
            dialog.add_resource_type(rt)

        for u in usages:
            dialog.add_usage(u)

        return dialog
