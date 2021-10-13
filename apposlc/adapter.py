from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc.vocabularies.qm import OSLC_QM
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
    types = [OSLC_RM.Requirement]
    items = REQSTORE
    mapping = REQ_TO_RDF

    def __init__(self, *args, **kwargs):
        super(RequirementAdapter, self).__init__(*args, **kwargs)
        self.types = [OSLC_RM.Requirement]

    def set(self, data_items):
        self.items = data_items

    def query_capability(self, paging=False, page_no=1, *args, **kwargs):
        return len(self.items), self.items

    def creation_factory(self):
        return self.items

    def get_resource(self, resource_id):
        for item in self.items:
            if item.identifier == resource_id:
                return item

        return None


class TestCaseAdapter(ServiceResourceAdapter):
    domain = OSLC_QM
    types = [OSLC_QM.TestCase]

    def selection_dialog(self):
        pass
