from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS

from pyoslc_server.specification import ServiceResourceAdapter

REQ_TO_RDF = {
    "identifier": DCTERMS.identifier,
    "title": DCTERMS.title,
    "description": DCTERMS.description,
}


class RequirementAdapter(ServiceResourceAdapter):

    domain = OSLC_RM
    type = [OSLC_RM.Requirement]
    service_path = 'provider/{id}/resources'

    items = None

    def __init__(self, data_items, *args, **kwargs):
        super(RequirementAdapter, self).__init__(*args, **kwargs)
        self.items = data_items

    def set(self, data_items):
        self.items = data_items

    @staticmethod
    def query_capability(self, identifier):
        return self.get_item(identifier)

    def get_item(self, identifier):
        for item in self.items:
            if item.identifier == identifier:
                return item

    def item_keys(self, item):
        return item.identifier


class RQAdapter(ServiceResourceAdapter):

    def query_capability(self):
        pass

    def creation_factory(self):
        pass
