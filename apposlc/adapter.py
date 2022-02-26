from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc.vocabularies.qm import OSLC_QM

from pyoslc_server.specification import ServiceResourceAdapter
from .resource import REQSTORE, Requirement


class RequirementAdapter(ServiceResourceAdapter):

    domain = OSLC_RM
    items = REQSTORE

    def __init__(self, **kwargs):
        super(RequirementAdapter, self).__init__(**kwargs)
        self.types = [OSLC_RM.Requirement]

    def set(self, data_items):
        self.items = data_items

    def query_capability(self, paging=False, page_size=50, page_no=1,
                         prefix=None, where=None, select=None,
                         *args, **kwargs):

        if paging:
            offset = ((page_no - 1) * page_size)
            end = (offset + page_size)
            result = self.get_data()[offset:end]
        else:
            result = self.get_data()

        # This is just an example, the code could be improved
        if select:
            final_result = []
            sel = [p.prop for p in select]
            sel.append("http://purl.org/dc/terms/identifier")
            for r in result:
                final_result.append({k: v for k, v in r.items() if k in sel})
        else:
            final_result = result

        return len(self.items), final_result,

    def creation_factory(self, item):
        r = Requirement(
            identifier=item.get('identifier'),
            title=item.get('title'),
            description=item.get('description'),
        )
        self.items.append(r)
        return r

    def get_resource(self, resource_id):
        for item in self.items:
            if item.identifier == resource_id:
                return item

        return None

    def get_data(self):
        result = list()
        for item in self.items:
            data = {
                "http://purl.org/dc/terms/identifier": item.identifier,
                "http://purl.org/dc/terms/description": item.description,
                "http://purl.org/dc/terms/title": item.title
            }
            result.append(data)

        return result


class TestCaseAdapter(ServiceResourceAdapter):
    domain = OSLC_QM

    def __init__(self, identifier, title, mapping=None, **kwargs):
        super(TestCaseAdapter, self).__init__(identifier, title, mapping=None, **kwargs)
        self.types = [OSLC_QM.TestCase]
