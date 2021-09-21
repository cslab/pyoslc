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
    type = [OSLC_RM.Requirement]
    items = REQSTORE

    def set(self, data_items):
        self.items = data_items

    def query_capability(self, paging=False, page_no=1, *args, **kwargs):
        return self.items

    def creation_factory(self):
        return self.items

    def get_resource(self, resource_id):
        for item in self.items:
            if item.identifier == resource_id:
                return item

        return None

    def item_keys(self, item):
        return item.identifier


class TestCaseAdapter(ServiceResourceAdapter):
    domain = OSLC_QM
    type = [OSLC_QM.TestCase]

    def selection_dialog(self):
        pass
