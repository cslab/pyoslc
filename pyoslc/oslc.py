from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import DCTERMS, FOAF, RDF

from pyoslc.resource import ServiceProviderCatalog
from pyoslc.vocabulary import OSLCCore


class PyOSLC:

    service_provider_catalog = ServiceProviderCatalog

    def __new__(cls):
        cls.graph = Graph()
        cls.graph.bind('dcterms', DCTERMS, override=False)
        cls.graph.bind('oslc', OSLCCore.uri, override=False)

        return super(PyOSLC, cls).__new__(cls)

    def __init__(self, base_uri='http://examples.com/'):
        super(PyOSLC, self).__init__()
        self.__base_uri = base_uri

    def create_node(self, type):
        node = BNode()
        return node

    def oslc_service(self, resource_type=None, about=None):
        def decorator(function):
            def decorated(*args, **kwargs):

                if resource_type == OSLCCore.serviceProviderCatalog:

                    self.service_provider_catalog(self.graph, uri=about, title='New title')

                    spc = self.create_node(OSLCCore.term('serviceProviderCatalog'))

                    self.graph.add((spc, RDF.type, URIRef(OSLCCore.serviceProviderCatalog)))
                    self.graph.add((spc, DCTERMS.title, Literal('Service Provider Catalog')))
                    self.graph.add((spc, DCTERMS.description, Literal('Main service for the oslc adapter.')))

                    sp = self.create_node(OSLCCore.serviceProvider)

                    self.graph.add((spc, OSLCCore.ServiceProvider, sp))
                    self.graph.add((sp, RDF.type, URIRef(OSLCCore.serviceProvider)))
                    self.graph.add((sp, DCTERMS.title, Literal('Service Provider')))
                    self.graph.add((sp, DCTERMS.description, Literal('Service for managing information in the adapter.')))

                    s = self.create_node(OSLCCore.service)
                    self.graph.add((sp, OSLCCore.Service, s))
                    self.graph.add((s, RDF.type, URIRef(OSLCCore.service)))
                    self.graph.add((s, DCTERMS.title, Literal('Service')))
                    self.graph.add((s, DCTERMS.description, Literal('Service for creation of query.')))


                name = args[0]
                age = args[1]

                data = function(*args)
                print(data)
                result = self.graph.serialize()
                return result.decode('utf-8')

            return decorated
        return decorator

    def oslc_resource_shape(self, title, describes=OSLCCore.Service):
        def create_resource_shape(function):
            def decorator(*args, **kwargs):
                pass
            return decorator
        return create_resource_shape

