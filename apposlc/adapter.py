from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS

from pyoslc_server.specification import ServiceResourceAdapter
from .resource import REQSTORE

REQ_TO_RDF = {
    "identifier": DCTERMS.identifier,
    "title": DCTERMS.title,
    "description": DCTERMS.description,
}


class RequirementAdapter(ServiceResourceAdapter):

    domain = OSLC_RM
    type = [OSLC_RM.Requirement]
    service_path = 'provider/{id}/resources'
    mapping = REQ_TO_RDF

    items = REQSTORE

    def __init__(self, data_items, *args, **kwargs):
        super(RequirementAdapter, self).__init__(*args, **kwargs)
        # self.items = data_items

    def set(self, data_items):
        self.items = data_items

    def query_capability(self, provider_id):
        return self.items

    def creation_factory(self, provider_id):
        return self.items

    def get_item(self, identifier):
        for item in self.items:
            if item.identifier == identifier:
                return item

        return None

    def item_keys(self, item):
        return item.identifier
