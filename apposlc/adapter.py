from __future__ import absolute_import

import logging
import six

from rdflib import FOAF
from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc.vocabularies.qm import OSLC_QM

from pyoslc_server.specification import ServiceResourceAdapter
from .resource import CREATORSTORE, REQSTORE, Requirement


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RequirementAdapter(ServiceResourceAdapter):

    domain = OSLC_RM
    items = REQSTORE

    def __init__(self, **kwargs):
        super(RequirementAdapter, self).__init__(**kwargs)
        self.types = [OSLC_RM.Requirement]

    def set(self, data_items):
        self.items = data_items

    def query_capability(
        self,
        paging=False,
        page_size=50,
        page_no=1,
        prefix=None,
        where=None,
        select=None,
        *args,
        **kwargs
    ):

        if paging:
            offset = (page_no - 1) * page_size
            end = offset + page_size
            result = self.get_data(where)[offset:end]
        else:
            result = self.get_data(where)

        # This is just an example, the code could be improved
        if select:
            final_result = []
            sel = self.get_select(select)
            sel.append("http://purl.org/dc/terms/identifier")
            for r in result:
                final_result.append(self.select_attribute(r, sel))
        else:
            final_result = result

        return (
            len(self.items),
            final_result,
        )

    def creation_factory(self, item):
        r = Requirement(
            identifier=item.get("identifier"),
            title=item.get("title"),
            description=item.get("description"),
            creator=item.get("creator", None),
        )
        self.items.append(r)
        return r

    def get_resource(self, resource_id):
        for item in self.items:
            if item.identifier == resource_id:
                return self.convert_req_data(item)

        return None

    def get_data(self, where=None):
        result = list()
        for item in self.items:
            data = self.convert_req_data(item)
            result.append(data)

        return result

    def convert_req_data(self, item):
        return {
            "http://purl.org/dc/terms/identifier": item.identifier,
            "http://purl.org/dc/terms/description": item.description,
            "http://purl.org/dc/terms/title": item.title,
            "http://purl.org/dc/terms/created": item.created,
            "http://open-services.net/ns/rm#discipline": item.discipline,
            "http://purl.org/dc/terms/creator": self.convert_creator_data(item.creator),
        }

    def convert_creator_data(self, item):
        if isinstance(item, list):
            return [self.convert_creator_data(i) for i in item]
        else:
            return {
                "http://purl.org/dc/terms/identifier": item.identifier,
                "http://xmlns.com/foaf/0.1/firstName": item.first_name,
                "http://xmlns.com/foaf/0.1/lastName": item.last_name,
                "http://xmlns.com/foaf/0.1/birthday": item.birth_day,
            }

    def get_select(self, select):
        result = []
        for p in select:
            if p.props:
                result += self.get_select(p.props)
            else:
                result.append(p.prop)

        return result

    def select_attribute(self, item, select):
        result = {}
        for k, v in six.iteritems(item):
            if k in select:
                result[k] = v
            else:
                if type(v) is dict:
                    value = self.select_attribute(v, select)
                    result[k] = value
                elif type(v) in (list, set):
                    lst = []
                    for i in v:
                        value = self.select_attribute(i, select)
                        lst.append(value)
                    result[k] = lst

        return result


class TestCaseAdapter(ServiceResourceAdapter):
    domain = OSLC_QM

    def __init__(self, identifier, title, mapping=None, **kwargs):
        super(TestCaseAdapter, self).__init__(identifier, title, **kwargs)
        self.types = [OSLC_QM.TestCase]


class CreatorAdapter(ServiceResourceAdapter):
    domain = FOAF
    items = CREATORSTORE

    def __init__(self, identifier, title, mapping=None, **kwargs):
        super(CreatorAdapter, self).__init__(identifier, title, **kwargs)
        self.types = [FOAF.Person]

    def query_capability(
        self,
        paging=False,
        page_size=50,
        page_no=1,
        prefix=None,
        where=None,
        select=None,
        *args,
        **kwargs
    ):

        if paging:
            offset = (page_no - 1) * page_size
            end = offset + page_size
            result = self.get_data(where)[offset:end]
        else:
            result = self.get_data(where)

        # This is just an example, the code could be improved
        if select:
            final_result = []
            sel = self.get_select(select)
            sel.append("http://purl.org/dc/terms/identifier")
            for r in result:
                final_result.append(self.select_attribute(r, sel))
        else:
            final_result = result

        return (
            len(self.items),
            final_result,
        )

    def get_data(self, where=None):
        result = list()
        for item in self.items:
            data = self.convert_creator_data(item)
            result.append(data)

        return result

    def convert_creator_data(self, item):
        return {
            "http://purl.org/dc/terms/identifier": item.identifier,
            "http://xmlns.com/foaf/0.1/firstName": item.first_name,
            "http://xmlns.com/foaf/0.1/lastName": item.last_name,
            "http://xmlns.com/foaf/0.1/birthday": item.birth_day,
        }
