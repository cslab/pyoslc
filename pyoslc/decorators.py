from pyoslc.vocabulary import OSLCCore


def oslc_service_provider_catalog(self, resource_type=None, about=None):

    def decorator(function):
        def decorated(*args, **kwargs):
            if resource_type == OSLCCore.serviceProviderCatalog:

                self.service_provider_catalog(self.graph, uri=about, title="Service Provider Catalog")

                spc = self.create_node(OSLCCore.term('serviceProviderCatalog'))

        return decorated
    return decorator