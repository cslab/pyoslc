from six.moves.urllib.parse import urlparse

from pyoslc_server import request

from .resource import OSLCResource
from .providers import ServiceProviderCatalogSingleton
from .helpers import url_for, make_response


class ServiceProviderCatalog(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.providers = kwargs.get('providers', None)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for('{}'.format(self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url, self.title, self.description)
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)


class ServiceProvider(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.providers = kwargs.get('providers', None)

    def get(self, provider_id):
        super(ServiceProvider, self).get()
        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(service_provider_url, provider_id, providers=self.providers)

        if not provider:
            return make_response('No resources with ID {}'.format(provider_id), 404)

        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)
