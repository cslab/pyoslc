from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS, RDF, Literal, Graph, URIRef
from rdflib.resource import Resource

REQ_TO_RDF = {
    "identifier": DCTERMS.identifier,
    "title": DCTERMS.title,
    "description": DCTERMS.description,
}


class RequirementAdapter:

    domain = [OSLC_RM]
    type = [OSLC_RM.Requirement]

    items = None

    def __init__(self, data_items):
        self.items = data_items

    def set(self, data_items):
        self.items = data_items

    def query_capability(self):
        pass

    def get_item(self, identifier):
        for item in self.items:
            if item.identifier == identifier:
                return item
                # return self.to_rdf(Graph(), 'http://localhost/oslc/requirements/' + item.identifier, item)

    def item_keys(self, item):
        return item.identifier

    def to_rdf(self, graph, subject, item):
        graph.bind('rdf', RDF)
        graph.bind('dcterms', DCTERMS)
        graph.bind('oslc_rm', OSLC_RM)
        r = Resource(graph, URIRef(subject))
        r.add(RDF.type, OSLC_RM.Requirement)

        for field, property in REQ_TO_RDF.items():
            r.add(property, Literal(getattr(item, field)))

        return graph

    def __iter__(self):
        pass

