from pyoslc.vocabulary import OSLCCore


def catalog(self, resource_type=None, about=None):
    def decorator(function):
        def decorated(*args, **kwargs):
            if resource_type == OSLCCore.serviceProviderCatalog:
                print("asd")
                # self.service_provider_catalog(graph, uri=about, title="Service Provider Catalog")
                # spc = self.create_node(OSLCCore.term('serviceProviderCatalog'))

            data = function(*args)
            print(data)
            result = data.data
            return result.decode('utf-8')

        return decorated

    return decorator