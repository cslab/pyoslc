from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS

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
