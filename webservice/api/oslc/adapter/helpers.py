from rdflib import Graph
from rdflib.namespace import DCTERMS

from pyoslc.vocabulary import OSLCCore


class GraphHelper(object):

    instance = None
    graph = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(GraphHelper, cls).__new__(cls, *args, **kwargs)

            cls.graph = Graph()
            cls.graph.bind('oslc', OSLCCore, override=False)
            cls.graph.bind('dcterms', DCTERMS, override=False)

    @classmethod
    def to_rdf(cls, klass):
        return cls.graph
