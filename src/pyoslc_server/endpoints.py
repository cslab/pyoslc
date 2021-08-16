from six.moves.urllib.parse import urlparse

from pyoslc_server import request

from .resource import OSLCResource
from .providers import ServiceProviderCatalogSingleton
from .helpers import url_for


class ServiceProviderCatalog(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for('{}'.format(self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url)
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)