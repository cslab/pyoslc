from pyoslc.vocabulary import OSLCCore


def catalog(resource_type=None, about=None):
    def decorator(function):
        def decorated(*args, **kwargs):
            if resource_type == OSLCCore.serviceProviderCatalog:
                print("asd")
                # self.service_provider_catalog(graph, uri=about, title="Service Provider Catalog")

                # spc = self.create_node(OSLCCore.term('serviceProviderCatalog'))

        return decorated

    return decorator