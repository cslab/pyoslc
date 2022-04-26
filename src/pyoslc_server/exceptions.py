from rdflib import Graph

from pyoslc.resources.models import Error
from pyoslc.vocabularies.core import OSLC


class OSLCException(Error):
    def __init__(self, *args, **kwargs):
        super(OSLCException, self).__init__(*args, **kwargs)
        self.graph = Graph()
        self.graph.bind("oslc", OSLC)
        self.types = [OSLC.Error]

    def to_rdf(self, graph=None):
        super(OSLCException, self).to_rdf(self.graph)
        return self.graph
