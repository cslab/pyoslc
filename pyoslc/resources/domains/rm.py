from rdflib import Graph, DCTERMS
from rdflib.extras.describer import Describer

from pyoslc.resources.models import BaseResource
from pyoslc.vocabularies.rm import OSLC_RM


class Requirement(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, elaborated_by=None,
                 elaborates=None, specified_by=None, specifies=None, affected_by=None, tracked_by=None,
                 implemented_by=None, validated_by=None, satisfied_by=None, satisfies=None, decomposed_by=None,
                 decomposes=None, constrained_by=None, constrains=None):

        super(Requirement, self).__init__(about, types, properties, description, identifier, short_title, title,
                                          contributor, creator, subject, created, modified, type, discussed_by,
                                          instance_shape, service_provider, relation)

        self.__elaborated_by = elaborated_by if elaborated_by is not None else set()
        self.__elaborates = elaborates if elaborates is not None else set()
        self.__specified_by = specified_by if specified_by is not None else set()
        self.__specifies = specifies if specifies is not None else set()
        self.__affected_by = affected_by if affected_by is not None else set()
        self.__tracked_by = tracked_by if tracked_by is not None else set()
        self.__implemented_by = implemented_by if implemented_by is not None else set()
        self.__validated_by = validated_by if validated_by is not None else set()
        self.__satisfied_by = satisfied_by if satisfied_by is not None else set()
        self.__satisfies = satisfies if satisfies is not None else set()
        self.__decomposed_by = decomposed_by if decomposed_by is not None else set()
        self.__decomposes = decomposes if decomposes is not None else set()
        self.__constrained_by = constrained_by if constrained_by is not None else set()
        self.__constrains = constrains if constrains is not None else set()

    def update(self, data, attributes):
        assert attributes is not None, 'The mapping for attributes is required'
        for k, v in data.items():
            if k in attributes:
                attribute = attributes[k]['attribute']
                if hasattr(self, attribute):
                    attr = getattr(self, attribute, None)
                    if isinstance(attr, set):
                        attr.add(v if v is not '' else 'Empty')
                    else:
                        setattr(self, attribute, v)

    @staticmethod
    def get_absolute_url(base_url, identifier):
        return base_url + "/" + identifier

    def to_rdf(self, base_url, attributes):
        assert attributes is not None, 'The mapping for attributes is required'

        graph = Graph()
        graph.bind('dcterms', DCTERMS)
        graph.bind('oslc_rm', OSLC_RM)

        d = Describer(graph, base=base_url)
        if getattr(self, '_BaseResource__identifier') not in base_url.split('/'):
            base_url = self.get_absolute_url(base_url, getattr(self, '_BaseResource__identifier'))

        d.about(base_url)
        d.rdftype(OSLC_RM.Requirement)

        for attribute_key in self.__dict__.keys():
            item = {attribute_key: v.values() for k, v in attributes.iteritems() if v['attribute'] == attribute_key}

            if item.values() and attribute_key in item.values()[0]:
                predicate = eval(item.values()[0][1])
                attr = getattr(self, attribute_key)
                if isinstance(attr, set):
                    if len(attr) > 0:
                        d.value(predicate, attr.pop())
                    else:
                        d.value(predicate, set())
                else:
                    d.value(predicate, getattr(self, attribute_key))

        return graph

    def from_json(self, data, attributes):
        for key in data.iterkeys():
            item = {key: v.values() for k, v in attributes.iteritems() if k.lower() == key.lower()}

            if item:
                attribute_name = item[key][0]
                if hasattr(self, attribute_name):
                    attribute_value = getattr(self, attribute_name)
                    if isinstance(attribute_value, set):
                        attribute_value.clear()
                        attribute_value.add(data[key])
                    else:
                        setattr(self, attribute_name, data[key])

    def to_mapped_object(self, attributes):
        specification = dict()

        for key in attributes:

            attribute_name = attributes[key]['attribute']
            if hasattr(self, attribute_name):
                attribute_value = getattr(self, attribute_name)
                if attribute_value:
                    if isinstance(attribute_value, set):
                        specification[key] = attribute_value.pop()
                    else:
                        specification[key] = attribute_value

        return specification


class RequirementCollection(BaseResource):
    pass
