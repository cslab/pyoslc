from rdflib import RDF
from rdflib.extras.describer import Describer

from pyoslc.resources.models import BaseResource
from pyoslc.vocabularies.rm import OSLC_RM
import six


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
                attribute_name = attributes[k]['attribute']
                if hasattr(self, attribute_name):
                    attribute_value = getattr(self, attribute_name)
                    if isinstance(attribute_value, set):
                        attribute_value.clear()
                        attribute_value.add(data[k])
                    else:
                        setattr(self, attribute_name, data[k])

    @staticmethod
    def get_absolute_url(base_url, identifier):
        return base_url + "/" + identifier

    def to_rdf(self, graph, base_url, attributes):
        assert attributes is not None, 'The mapping for attributes is required'

        d = Describer(graph, base=base_url)
        if getattr(self, '_BaseResource__identifier') not in base_url.split('/'):
            base_url = self.get_absolute_url(base_url, getattr(self, '_BaseResource__identifier'))

        d.about(base_url)
        d.rdftype(OSLC_RM.Requirement)

        for attribute_key in self.__dict__.keys():
            item = {attribute_key: list(v.values()) for k, v in six.iteritems(attributes) if v['attribute'] == attribute_key}

            if list(item.values()) and attribute_key in list(item.values())[0]:
                predicate = eval(list(item.values())[0][1])
                attr = getattr(self, attribute_key)
                if isinstance(attr, set):
                    if len(attr) > 0:
                        d.value(predicate, attr.pop())
                else:
                    d.value(predicate, getattr(self, attribute_key))

        return graph

    def from_json(self, data, attributes):
        for key in six.iterkeys(data):
            item = {key: list(v.values()) for k, v in six.iteritems(attributes) if k.lower() == key.lower()}

            if item:
                attribute_name = item[key][0]
                if hasattr(self, attribute_name):
                    attribute_value = getattr(self, attribute_name)
                    if isinstance(attribute_value, set):
                        attribute_value.clear()
                        attribute_value.add(data[key])
                    else:
                        setattr(self, attribute_name, data[key])

    def from_rdf(self, g, attributes):

        for r in g.subjects(RDF.type, OSLC_RM.Requirement):

            reviewed = list()

            for k, v in six.iteritems(attributes):
                reviewed.append(v['attribute'])
                item = {v['attribute']: a for a in self.__dict__.keys() if a.lower() == v['attribute'].lower()}
                if item:
                    try:
                        predicate = eval(v['oslc_property'])
                    except AttributeError:
                        pass
                else:
                    ns, ln = v['oslc_property'].split('.')
                    predicate = eval(ns).uri + ln

                for i in g.objects(r, predicate=predicate):
                    attribute_name = v['attribute']
                    if hasattr(self, attribute_name):
                        attribute_value = getattr(self, attribute_name)
                        if isinstance(attribute_value, set):
                            attribute_value.clear()
                            # attribute_value.add(data[key])
                        else:
                            setattr(self, attribute_name, i)

            no_reviewed = [a for a in self.__dict__.keys() if a not in reviewed]

            for attr in no_reviewed:
                item = {attr: v for k, v in six.iteritems(attributes) if v['attribute'].lower() == attr.lower()}

                if item:
                    for i in g.objects(r, eval(item.get(attr)['oslc_property'])):
                        attribute_name = item.get(attr)['attribute']
                        if hasattr(self, attribute_name):
                            attribute_value = getattr(self, attribute_name)
                            if isinstance(attribute_value, set):
                                attribute_value.clear()
                                # attribute_value.add(data[key])
                            else:
                                setattr(self, attribute_name, i)

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
